import os
import argparse
import enum
import json
import logging
from collections import OrderedDict
from pathlib import Path
import atexit

import couler.argo as couler
import pyaml
from couler.core import states, step_update_utils, utils
from couler.core.templates import (Container, Job, Output, OutputArtifact,
                                   OutputJob, Script)
from couler.core.templates.artifact import LocalArtifact
from couler.core.templates.output import (_container_output, _job_output,
                                          _script_output)
from couler.core.templates.step import Step
from couler.core.templates.volume import VolumeMount
from six import MAXSIZE

try:
    from couler.core import proto_repr
except Exception:
    proto_repr = None


class step_type(enum.Enum):
    simple = 1
    tool_invocation = 2
    tool_installation = 3
    initial = 4


class workflow():
    def __init__(self):
        self.containers: dict[container] = []
        self.dag = []
        self.image_registry = ""
        self.image_cache_path = None
        self.work_path = ""
        self.builders = []

        # couler.run_container()


class sb_step:
    global_steps = []

    def __init__(self, name:str = "", bash:str = "", st_type: step_type = step_type.simple):
        self.name = name
        self.type = st_type
        self.bash = bash
        self.dependencies = []
        self.global_steps.append(self)
        self.container: container = None


class tool_installation_step(sb_step):
    installation_steps = []

    def __init__(self, name:str = "", bash:str = ""):
        self.tool_to_install:str = name
        self.installation_steps.append(self)
        super().__init__(name, bash, step_type.tool_installation)


class tool_invocation_step(sb_step):
    def __init__(self, name:str = "", bash:str = "", tool:str = ""):
        self.tool_to_call:str = tool
        super().__init__(name, bash, step_type.tool_invocation)


class container:
    def __init__(self, name:str = ""):
        self.name = name
        self.tool_deps = []  # has to have dependencies in installation order
        self.image = ""  # to be generated
        self.artifacts = []

    def add_dependency(self, dep:str):
        if dep not in self.tool_deps:
            self.tool_deps.append(dep)


def find_step(given_name:str) -> sb_step:
    for step in sb_step.global_steps:
        if step.name == given_name:
            return step
    logging.error("Could not find step ", given_name)


def get_container_with_tool(wfl:workflow, tool:str) -> dict:
    arr = []
    for c in wfl.containers:
        if tool in c.tool_deps:
            arr.append(c)
    return arr


class rawArtifact(LocalArtifact):
    def __init__(self, path, raw_data):
        self.raw_data = raw_data
        self.type = couler.ArtifactType.LOCAL
        super().__init__(path, False)
        self.id = "input-local-" + utils._get_uuid()

    def to_yaml(self):
        yaml_output = OrderedDict(
            {"name": self.id, "path": self.path, "raw": {"data": self.raw_data}}
        )
        return yaml_output


def get_container_with_least_dependencies(wfl:workflow, step:sb_step):
    min_container_deps = MAXSIZE
    min_container_deps_container = None
    for c in wfl.containers:
        if len(c.tool_deps) < min_container_deps:
            min_container_deps = len(c.tool_deps)
            min_container_deps_container = c
    if min_container_deps_container == None:
        logging.error("could not get a container with the least requirements(tool_dependencies")
    return min_container_deps_container


def sb_step_call(wfl, step:sb_step):
    c = get_container_with_least_dependencies(wfl, step)
    if(step.type == step_type.tool_invocation):
        conts = get_container_with_tool(wfl, step.tool_to_call)
        c = conts[0]
    elif (step.type == step_type.tool_installation):
        return
    artifact = rawArtifact("/root/step_bash.sh", step.bash)
    sb_step_name = utils.argo_safe_name(step.name)
    obc_env = {
        "OBC_WORK_PATH": wfl.work_path,
        "OBC_TOOL_PATH": wfl.work_path,
        "OBC_DATA_PATH": wfl.work_path
    }
    return couler.run_container(c.image, command=["/bin/bash"], args="/root/step_bash.sh", input=[artifact], step_name=sb_step_name, env=obc_env)


def get_steps(data, wfl: workflow):
    for step in data['steps']:
        if data['steps'][step]['type'] == "tool_installation":
            s = tool_installation_step(step, data['steps'][step]['bash'])
            installation_script_path = os.path.join(wfl.work_path, "install-tool-"+s.name+".sh")
            artifact = rawArtifact(installation_script_path, s.bash)
            for c in get_container_with_tool(wfl, s.tool_to_install):
                idx = wfl.containers.index(c)
                c.image = wfl.image_registry + "/image" + c.name + ":v1"
                c.artifacts.append(artifact)
                wfl.containers[idx] = c
        elif data['steps'][step]['type'] == "tool_invocation":
            tool_invocation_step(step, data['steps'][step]['bash'], data['steps'][step]['tool_to_call'])
        elif data['steps'][step]['type'] == "initial":
            sb_step(step, data['steps'][step]['bash'], step_type.initial)
        else:
            sb_step(step, data['steps'][step]['bash'])


def builder_phase(c:container, wfl:workflow):
    obc_env = {
        "OBC_WORK_PATH": wfl.work_path,
        "OBC_TOOL_PATH": wfl.work_path,
        "OBC_DATA_PATH": wfl.work_path
    }
    dockerfile_path = os.path.join(wfl.work_path, "Dockerfile")
    dockerfile = """
FROM ubuntu:18.04
ADD . /root/
WORKDIR /root
    """
    dockerfile += "\nENV " + "OBC_WORK_PATH=" + obc_env["OBC_WORK_PATH"]
    dockerfile += "\nENV " + "OBC_TOOL_PATH=" + obc_env["OBC_TOOL_PATH"]
    dockerfile += "\nENV " + "OBC_DATA_PATH=" + obc_env["OBC_DATA_PATH"]
    for art in c.artifacts:
        dockerfile += "\nRUN chmod +x " + art.path + " && " + art.path
    # print(dockerfile)
    c.artifacts.append(rawArtifact(dockerfile_path, dockerfile))
    wfl.builders.append("builder" + c.name)

    # tmpl = Container("executor"+c.name,c.image, command=["/bin/bash", "-c"], env=obc_env)
    # couler.workflow.add_template(tmpl)
    # wfl.templates.append(tmpl)
    kaniko_args = [
        "--dockerfile=Dockerfile",
        "--cache=true",
        "--context=dir://%s/" % wfl.work_path.rstrip("/"),
        "--insecure",
        "--destination=" + c.image
    ]
    if wfl.image_cache_path:
        kaniko_args += ["--cache-dir=%s" % wfl.image_cache_path]
    tmpl = couler.run_container(image="gcr.io/kaniko-project/executor:latest",
                                args=kaniko_args,
                                input=c.artifacts,
                                step_name="builder"+c.name,
                                env=obc_env)


def get_environment(data, wfl:workflow):
    for env in data['environments']:
        c = container(env)
        for tool in data['environments'][env]:
            for dependency in data['environments'][env][tool]:
                # find step and add it to container
                # s = find_step(dependency)
                c.add_dependency(dependency)
            # s = find_step(tool)
            c.add_dependency(tool)
        wfl.containers.append(c)


def get_dag(data):
    for dag_step in data['DAG']:
        step = find_step(dag_step)
        for dag_step_dep in data['DAG'][dag_step]:
            step.dependencies.append(find_step(dag_step_dep))


def parse(input:str, wfl:workflow):
    data = json.loads(input)
    get_environment(data, wfl)
    get_steps(data, wfl)
    get_dag(data)


def dag_phase(data, wfl:workflow, last_builder):
    for step in sb_step.global_steps:
        if(step.type == tool_invocation_step):
            step.container = get_container_with_tool(wfl, step.tool_to_call)
        else:
            step.container = get_container_with_least_dependencies(wfl, step)
    last_elem = None
    for step in sb_step.global_steps:
        if(step.type == step_type.initial):
            couler.set_dependencies(lambda:  sb_step_call(wfl, step), dependencies=last_builder)
            continue
        if len(step.dependencies) == 0:
            key = len(list(couler.workflow.dag_tasks.keys())) - 1
            if key >= 0:
                last_elem = list(couler.workflow.dag_tasks.keys())[key]
            sb_step_name = utils.argo_safe_name(last_elem)
            couler.set_dependencies(lambda: sb_step_call(wfl, step), dependencies=sb_step_name)
        else:
            for dep in step.dependencies:
                key = None
                initial = None
                for tmp in sb_step.global_steps:
                    if tmp.name == dep.name:
                        key = tmp
                    if tmp.type == step_type.initial:
                        initial = tmp
                if(key.type == step_type.tool_installation):
                    sb_step_name = utils.argo_safe_name(initial.name)
                    couler.set_dependencies(lambda:  sb_step_call(wfl, step), dependencies=sb_step_name)
                else:
                    sb_step_name = utils.argo_safe_name(dep.name)
                    couler.set_dependencies(lambda:  sb_step_call(wfl, step), dependencies=sb_step_name)
                # print(step.name, " depends on ", dep.name)

def workflow_yaml():
    return states.workflow.to_dict()

def yaml():
    yaml_str = pyaml.dump(workflow_yaml())

    # The maximum size of an etcd request is 1.5MiB:
    # https://github.com/etcd-io/etcd/blob/master/Documentation/dev-guide/limit.md#request-size-limit # noqa: E501
    if len(yaml_str) > 1573000:
        raise ValueError(
            "The size of workflow YAML file should not be more \
            than 1.5MiB."
        )

    # TODO(weiyan): add unittest for verifying multiple secrets outputs
    for secret in states._secrets.values():
        if not secret.dry_run:
            yaml_str += "\n---\n" + pyaml.dump(secret.to_yaml())

    if states._enable_print_yaml:
        return yaml_str

def pipeline(data:str, workflow_name:str, image_registry:str, image_cache_path:str, work_path:str):
    wfl = workflow()
    wfl.image_registry = image_registry
    wfl.image_cache_path = image_cache_path
    wfl.work_path = work_path
    data = parse(data, wfl)
    if workflow_name:
        couler.workflow.name = workflow_name
    couler.workflow.dag_mode = True
    last_builder = None
    for c in wfl.containers:
        couler.set_dependencies(lambda: builder_phase(c, wfl), dependencies=last_builder)
        last_builder = "builder" + c.name
    dag_phase(data, wfl, last_builder)
    return yaml()

def pipeline_from_file(filename:str, workflow_name:str, image_registry:str, image_cache_path:str, work_path:str):
    with open(filename, 'r') as f:
        return pipeline(f.read(), workflow_name, image_registry, image_cache_path, work_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Add a json workflow to be converted into argo')

    parser.add_argument('-f', metavar='<file_path>', type=str, required=False)
    parser.add_argument('-r', metavar='<image_registry>', type=str, required=False)
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    if args.f is not None:
        pipeline(args.f, args.r)
    else:
        parser.print_help()

atexit._clear()
