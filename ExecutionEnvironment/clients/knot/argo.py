import os
import argparse
import enum
import json
import logging
import pyaml
import couler.argo as couler

from collections import OrderedDict, defaultdict
from couler.core import states, utils
from couler.core.templates.artifact import TypedArtifact
from couler.core.templates.volume import Volume, VolumeMount

from artifacts import S3ArtifactRepository


class step_type(enum.Enum):
    simple = 1
    tool_invocation = 2
    tool_installation = 3
    initial = 4

class sb_step:
    '''
    Represent a DAG step
    '''
    global_steps = [] # all steps of the workflow

    def __init__(self, name: str = "", bash: str = "", st_type: step_type = step_type.simple):
        self.name = name
        self.type = st_type
        self.bash = bash
        self.dependencies = []
        self.global_steps.append(self)
        self.container: container = None

class tool_installation_step(sb_step):
    '''
    Represents a tool installation step
    '''
    installation_steps = []

    def __init__(self, name: str = "", bash: str = ""):
        self.tool_to_install: str = name
        self.installation_steps.append(self)
        super().__init__(name, bash, step_type.tool_installation)

class tool_invocation_step(sb_step):
    '''
    Represents a tool invocation step
    '''
    def __init__(self, name: str = "", bash: str = "", tool: str = ""):
        self.tool_to_call: str = tool
        super().__init__(name, bash, step_type.tool_invocation)

class container:
    def __init__(self, name: str = ""):
        self.name = name
        self.tool_deps = []  # has to have dependencies in installation order
        self.image = ""  # to be generated
        self.artifacts = []

    def add_dependency(self, dep: str):
        if dep not in self.tool_deps:
            self.tool_deps.append(dep)

class RawArtifact(TypedArtifact):
    '''
    Creates an artifact with a raw bash script
    '''
    def __init__(self, path, raw_data):
        super().__init__(artifact_type=couler.ArtifactType.LOCAL, path=path, is_global=False)
        self.raw_data = raw_data
        self.id = "input-local-" + utils._get_uuid()

    def to_yaml(self):
        yaml_output = OrderedDict(
            {"name": self.id, "path": self.path, "raw": {"data": self.raw_data}}
        )
        return yaml_output

class RawArtifactFactory:
    def new_artifact(self, path, raw_data):
        return RawArtifact(path, raw_data)

class S3Artifact(TypedArtifact):
    def __init__(self, object_prefix, path):
        super().__init__(artifact_type=couler.ArtifactType.S3, path=path, is_global=False)
        self.object_prefix = object_prefix
        self.id = "input-local-" + utils._get_uuid()
        self.object_name = '%s/%s' % (self.object_prefix, self.id)

    def to_yaml(self):
        yaml_output = OrderedDict(
            {"name": self.id, "path": self.path, "s3": {"key": self.object_name}}
        )
        return yaml_output

class S3ArtifactFactory:
    def __init__(self, workflow_name, artifact_repository_url, namespace):
        self.workflow_name = workflow_name
        self.artifact_repository = S3ArtifactRepository(artifact_repository_url, namespace)

    def new_artifact(self, path, raw_data):
        s3_artifact = S3Artifact(self.workflow_name, path)
        self.artifact_repository.upload_data(s3_artifact.object_name, raw_data)
        return s3_artifact

class SecretVolume(Volume):
    def __init__(self, name, secret_name):
        self.name = name
        self.secret_name = secret_name

    def to_dict(self):
        return OrderedDict({'name': self.name,
                            'secret': {'secretName': self.secret_name}})

class VolumeMountWithSubPath(VolumeMount):
    def __init__(self, name, mount_path, sub_path):
        super().__init__(name, mount_path)
        self.sub_path = sub_path

    def to_dict(self):
        result = super().to_dict()
        result['subPath'] = self.sub_path
        return result

class workflow():
    def __init__(self):
        self.containers: dict[container] = []
        self.dag = []
        self.image_registry = ""
        self.work_path = ""
        self.builders = []
        simple_container = container("simple")
        simple_container.image = "kantale/openbio-env:1"
        self.simple_container = simple_container
        couler.add_volume(SecretVolume('docker-registry-secret', 'docker-registry-secret'))

        self.artifact_factory = None # to be initialized later

    def parse(self, input: str):
        if self.artifact_repository and self.namespace:
            self.artifact_factory = S3ArtifactFactory(couler.workflow.name, self.artifact_repository, self.namespace)
        else:
            self.artifact_factory = RawArtifactFactory()

        data = json.loads(input)
        self.get_environment(data,)
        self.get_steps(data,)
        self.get_dag(data)

    def get_environment(self, data):
        for env in data['environments']:
            c = container(env)
            for tool in data['environments'][env]:
                for dependency in data['environments'][env][tool]:
                    # find step and add it to container
                    # s = find_step(dependency)
                    c.add_dependency(dependency)
                # s = find_step(tool)
                c.add_dependency(tool)
            self.containers.append(c)

    def get_steps(self, data):
        for step in data['steps']:
            if data['steps'][step]['type'] == "tool_installation":
                s = tool_installation_step(step, data['steps'][step]['bash'])
                installation_script_path = os.path.join(self.work_path, "install-tool-" + s.name + ".sh")
                artifact = self.artifact_factory.new_artifact(installation_script_path, s.bash)
                for c in self.get_container_with_tool(s.tool_to_install):
                    idx = self.containers.index(c)
                    c.image = self.image_registry + ("/%s/image" % (couler.workflow.name)) + c.name + ":v1"
                    c.artifacts.append(artifact)
                    self.containers[idx] = c
            elif data['steps'][step]['type'] == "tool_invocation":
                tool_invocation_step(step, data['steps'][step]['bash'], data['steps'][step]['tool_to_call'])
            elif data['steps'][step]['type'] == "initial":
                sb_step(step, data['steps'][step]['bash'], step_type.initial)
            else:
                sb_step(step, data['steps'][step]['bash'])

    def get_container_with_tool(self, tool: str) -> dict:
        arr = []
        for c in self.containers:
            if tool in c.tool_deps:
                arr.append(c)
        return arr

    def find_step(self, given_name: str) -> sb_step:
        for step in sb_step.global_steps:
            if step.name == given_name:
                return step
        logging.error("Could not find step ", given_name)

    def get_dag(self, data):
        for dag_step in data['DAG']:
            step = self.find_step(dag_step)
            for dag_step_dep in data['DAG'][dag_step]:
                step.dependencies.append(self.find_step(dag_step_dep))

    def sb_step_call(self, step: sb_step):
        c = self.simple_container
        if (step.type == step_type.tool_invocation):
            conts = self.get_container_with_tool(step.tool_to_call)
            c = conts[0]
        elif (step.type == step_type.tool_installation):
            return
        artifact = self.artifact_factory.new_artifact("/root/step_bash.sh", step.bash)
        sb_step_name = utils.argo_safe_name(step.name)
        obc_env = {
            "OBC_WORK_PATH": self.work_path,
            "OBC_TOOL_PATH": self.work_path,
            "OBC_DATA_PATH": self.work_path
        }
        return couler.run_container(c.image, command=["/bin/bash"], args="/root/step_bash.sh", input=[artifact], step_name=sb_step_name, env=obc_env)

    def dag_phase(self, data, last_builder):
        for step in sb_step.global_steps:
            if (step.type == tool_invocation_step):
                step.container = self.get_container_with_tool(step.tool_to_call)
            else:
                step.container = self.simple_container
        last_elem = None

        # Keys: Step nmes. Values a list with tuples:
        # A tuple contains the step object and the dependency
        step_dependencies = defaultdict(list)

        for step in sb_step.global_steps:
            if (step.type == step_type.initial):
                couler.set_dependencies(lambda: self.sb_step_call(step), dependencies=last_builder)
                continue

            if len(step.dependencies) == 0:
                key = len(list(couler.workflow.dag_tasks.keys())) - 1
                if key >= 0:
                    last_elem = list(couler.workflow.dag_tasks.keys())[key]
                sb_step_name = utils.argo_safe_name(last_elem)
                couler.set_dependencies(lambda: self.sb_step_call(step), dependencies=sb_step_name)
            else:
                for dep in step.dependencies:
                    key = None
                    initial = None
                    for tmp in sb_step.global_steps:
                        if tmp.name == dep.name:
                            key = tmp
                        if tmp.type == step_type.initial:
                            initial = tmp
                    if (key.type == step_type.tool_installation):
                        sb_step_name = utils.argo_safe_name(initial.name)
                        couler.set_dependencies(lambda: self.sb_step_call(step), dependencies=sb_step_name)
                    else:
                        sb_step_name = utils.argo_safe_name(dep.name)
                        # Do not set dependencies here. This dependenciy might belong to more than on step
                        # couler.set_dependencies(lambda:  sb_step_call(wfl, step), dependencies=sb_step_name)
                        step_dependencies[step.name].append((step, sb_step_name))

        # Add step dependencies
        for k, v in step_dependencies.items():
            couler.set_dependencies(lambda: self.sb_step_call(v[0][0]), dependencies=' && '.join(x[1] for x in v))

    def builder_phase(self, c: container):
        obc_env = {
            "OBC_WORK_PATH": self.work_path,
            "OBC_TOOL_PATH": self.work_path,
            "OBC_DATA_PATH": self.work_path
        }
        dockerfile_path = os.path.join(self.work_path, "Dockerfile")
        dockerfile = """
    FROM kantale/openbio-env:1
    RUN apt-get update

    ADD . /root/
    WORKDIR /root
        """
        dockerfile += "\nENV " + "OBC_WORK_PATH=" + obc_env["OBC_WORK_PATH"]
        dockerfile += "\nENV " + "OBC_TOOL_PATH=" + obc_env["OBC_TOOL_PATH"]
        dockerfile += "\nENV " + "OBC_DATA_PATH=" + obc_env["OBC_DATA_PATH"]
        for art in c.artifacts:
            dockerfile += "\nRUN chmod +x " + art.path + " && " + art.path
        c.artifacts.append(self.artifact_factory.new_artifact(dockerfile_path, dockerfile))
        self.builders.append("builder" + c.name)

        kaniko_args = [
            "--dockerfile=Dockerfile",
            "--cache=true",
            "--cache-repo=%s/openbio-cache" % self.image_registry,
            "--context=dir://%s/" % self.work_path.rstrip("/"),
            "--insecure",
            "--skip-tls-verify",
            "--destination=" + c.image
        ]
        couler.run_container(image="gcr.io/kaniko-project/executor:latest",
                             args=kaniko_args,
                             volume_mounts=[VolumeMountWithSubPath('docker-registry-secret', '/kaniko/.docker/config.json', '.dockerconfigjson')],
                             input=c.artifacts,
                             step_name="builder" + c.name,
                             env=obc_env)

def workflow_yaml(uses_artifacts=False):
    result = states.workflow.to_dict()
    if uses_artifacts:
        # XXX Get value from workflow.artifact_factory.artifact_repository.config_map...
        result['spec']['artifactRepositoryRef'] = {'configMap': 'openbio-artifact-repository'}
    return result

def yaml(uses_artifacts=False):
    yaml_str = pyaml.dump(workflow_yaml(uses_artifacts))

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

def pipeline(data: str, workflow_name: str, image_registry: str, work_path: str, artifact_repository: str, namespace: str):
    '''
    This is the main entry point
    Called from __init__ ArgoExecutor
    '''
    couler._cleanup()
    sb_step.global_steps = []
    couler.workflow.name = workflow_name if workflow_name else "workflow"

    wfl = workflow()
    wfl.image_registry = image_registry
    wfl.work_path = work_path
    wfl.artifact_repository = artifact_repository
    wfl.namespace = namespace
    data = wfl.parse(data)
    couler.workflow.dag_mode = True

    builder_as_deps = []
    for c in wfl.containers:
        couler.set_dependencies(lambda: wfl.builder_phase(c), dependencies=None)
        # From Argo documntation: https://github.com/argoproj/argo-workflows/blob/master/docs/enhanced-depends-logic.md
        # Create a string representing the enhanced depends logic that specifies dependencies based on their statuses.
        builder_as_deps.append(f"builder{c.name}.Succeeded")
    builder_as_deps = ' && '.join(builder_as_deps)
    wfl.dag_phase(data, builder_as_deps)
    ret = yaml(uses_artifacts=(artifact_repository and namespace))

    return ret

def pipeline_from_file(filename: str, workflow_name: str, image_registry: str, work_path: str, artifact_repository: str, namespace: str):
    with open(filename, 'r') as f:
        return pipeline(f.read(), workflow_name, image_registry, work_path, artifact_repository, namespace)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Convert a JSON workflow into Argo YAML', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--identifier', '-i', metavar='<workflow_identifier>', type=str, required=False, default='test-workflow', help='unique identifier for the workflow')
    parser.add_argument('--registry', '-r', metavar='<image_registry>', type=str, required=False, default='127.0.0.1:5000', help='image registry host and port')
    parser.add_argument('--path', '-p', metavar='<work_path>', type=str, required=False, default='/private/test-workflow', help='folder for intermediate files')
    parser.add_argument('--artifacts', '-a', metavar='<artifact_repository>', type=str, required=False, default='', help='artifact repository URL')
    parser.add_argument('--namespace', '-n', metavar='<namespace>', type=str, required=False, default='', help='create artifact configuration in this namespace')
    parser.add_argument('file_path', metavar='<file_path>', type=str)
    args = parser.parse_args()

    print(pipeline_from_file(args.file_path, args.identifier, args.registry, args.path, args.artifacts, args.namespace))
