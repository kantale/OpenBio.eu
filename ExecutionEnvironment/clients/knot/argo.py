import os
import argparse
import json
import logging
import yaml
import random
import string
import re

from .artifacts import S3ArtifactRepository

class WorkflowPart:
    def compile(self):
        raise NotImplementedError

class RawArtifact(WorkflowPart):
    '''
    An artifact with an embedded file.
    '''
    def __init__(self, path, raw_data):
        self.path = path
        self.raw_data = raw_data
        self.id = 'input-' + ''.join([random.choice(string.ascii_lowercase) for i in range(8)])

    def compile(self):
        result = {'name': self.id, 'path': self.path, 'raw': {'data': self.raw_data}}
        return result

class RawArtifactFactory:
    def new_artifact(self, path, raw_data):
        return RawArtifact(path, raw_data)

class S3Artifact(WorkflowPart):
    '''
    An artifact that references an S3 object.
    '''
    def __init__(self, object_prefix, path):
        self.path = path
        self.object_prefix = object_prefix
        self.id = 'input-' + ''.join([random.choice(string.ascii_lowercase) for i in range(8)])
        self.object_name = '%s/%s' % (self.object_prefix, self.id)

    def compile(self):
        result = {'name': self.id, 'path': self.path, 's3': {'key': self.object_name}}
        return result

class S3ArtifactFactory:
    def __init__(self, workflow_name, artifact_repository_url, namespace):
        self.workflow_name = workflow_name
        self.artifact_repository = S3ArtifactRepository(artifact_repository_url, namespace)

    def new_artifact(self, path, raw_data):
        s3_artifact = S3Artifact(self.workflow_name, path)
        self.artifact_repository.upload_data(s3_artifact.object_name, raw_data)
        return s3_artifact

class SecretVolume(WorkflowPart):
    def __init__(self, name, secret_name):
        self.name = name
        self.secret_name = secret_name

    def compile(self):
        result = {'name': self.name, 'secret': {'secretName': self.secret_name}}
        return result

class Environment(WorkflowPart):
    def __init__(self, name):
        self.name = name
        self.tools = []
        self.artifacts = [] # Artifacts in installation order.

    def add_tool(self, tool):
        if tool not in self.tools:
            self.tools.append(tool)

    def has_tool(self, tool):
        return tool in self.tools

    def add_artifact(self, artifact):
        self.artifacts.append(artifact)

    def image_name(self, workflow_name, image_registry):
        return '%s/%s/env%s:1' % (image_registry, workflow_name, self.name)

    def compile(self, workflow_name, image_registry, work_path, artifact_factory):
        dockerfile_path = os.path.join(work_path, 'Dockerfile.env%s' % self.name)
        dockerfile_data = 'FROM chazapis/openbio-env:2\nRUN apt-get update -y\n'
        for artifact in self.artifacts:
            artifact_filename = os.path.basename(artifact.path)
            dockerfile_data += '\nADD tools/' + artifact_filename + ' .'
            dockerfile_data += '\nRUN chmod +x ' + artifact_filename + ' && ./' + artifact_filename
        dockerfile_artifact = artifact_factory.new_artifact(dockerfile_path, dockerfile_data)

        result = {'name': 'builder' + self.name,
                  'inputs': {'artifacts': [artifact.compile() for artifact in self.artifacts] + [dockerfile_artifact.compile()]},
                  'container': {'image': 'gcr.io/kaniko-project/executor:latest',
                                'args': ['--dockerfile=Dockerfile.env%s' % self.name,
                                         '--cache=true',
                                         '--cache-repo=%s/openbio-cache' % image_registry,
                                         '--context=dir://%s/' % work_path.rstrip('/'),
                                         '--insecure',
                                         '--skip-tls-verify',
                                         '--destination=%s' % self.image_name(workflow_name, image_registry)],
                                'volumeMounts': [{'name': 'docker-registry-secret',
                                                  'mountPath': '/kaniko/.docker/config.json',
                                                  'subPath': '.dockerconfigjson'}]}}
        return result

class StepTemplate(WorkflowPart):
    def __init__(self, name, image_name, script_data):
        self.name = name
        self.image_name = image_name
        self.script_data = script_data

    def compile(self, workflow_name, work_path, artifact_factory):
        script_artifact = artifact_factory.new_artifact('/root/step.sh', self.script_data)
        nice_id = workflow_name if not workflow_name.startswith('openbio-') else workflow_name[8:]

        result = {'name': self.name,
                  'inputs': {'artifacts': [script_artifact.compile()]},
                  'container': {'image': self.image_name,
                                'command': ['/bin/bash'],
                                'args': ['/root/step.sh'],
                                'env': [{'name': 'OBC_NICE_ID', 'value': nice_id},
                                        {'name': 'OBC_WORK_PATH', 'value': work_path}]}}
        return result

class Workflow(WorkflowPart):
    '''
    A Workflow in Argo format.
    '''
    def __init__(self, name, data, image_registry, work_path, artifact_repository='', namespace=''):
        self.name = name
        self.data = data

        # Internal variables.
        self.image_registry = image_registry
        self.work_path = work_path
        self.artifact_repository = artifact_repository
        self.namespace = namespace

        if self.artifact_repository and self.namespace:
            self.artifact_factory = S3ArtifactFactory(self.name, self.artifact_repository, self.namespace)
        else:
            self.artifact_factory = RawArtifactFactory()

    def get_environment_with_tool(self, tool):
        for environment in self.environments.values():
            if environment.has_tool(tool):
                return environment

    def safe_name(self, name):
        return re.sub(r'_|\.', '-', name)

    def compile(self):
        # Get environments.
        self.environments = {}
        for env in self.data['environments']:
            environment = Environment(str(env))
            for tool in self.data['environments'][env]:
                for tool_dependency in self.data['environments'][env][tool]:
                    environment.add_tool(tool_dependency)
                environment.add_tool(tool)
            self.environments[env] = environment

        # Get tools to install in each environment.
        for step in self.data['steps']:
            if self.data['steps'][step]['type'] == 'tool_installation':
                script_name = step
                script_data = self.data['steps'][step]['bash']
                script_path = os.path.join(self.work_path, 'tools/install-%s.sh' % script_name)

                environment = self.get_environment_with_tool(script_name)
                environment.add_artifact(self.artifact_factory.new_artifact(script_path, script_data))

        # Start populating workflow.
        tasks = []
        templates = []
        volumes = [SecretVolume('docker-registry-secret', 'docker-registry-secret').compile()]

        # First add the build and variable copy phases (one for each environment).
        for environment in self.environments.values():
            # Build task.
            task = {'name': 'builder' + environment.name,
                    'template': 'builder' + environment.name}
            tasks.append(task)
            templates.append(environment.compile(self.name, self.image_registry, self.work_path, self.artifact_factory))

            # Copy task.
            task = {'name': 'copyvars' + environment.name,
                    'template': 'copyvars' + environment.name,
                    'depends': 'builder%s.Succeeded' % environment.name}
            tasks.append(task)
            template = {'name': 'copyvars' + environment.name,
                        'container': {'image': environment.image_name(self.name, self.image_registry),
                                      'command': ['/bin/bash'],
                                      'args': ['-c',
                                               'cp -r /openbio/work/. $OBC_WORK_PATH'],
                                      'env': [{'name': 'OBC_WORK_PATH', 'value': self.work_path}]}}

            templates.append(template)

        # Find initial step.
        for step in self.data['steps']:
            if self.data['steps'][step]['type'] == 'initial':
                initial_step = step

        # Then add the other steps.
        for step in self.data['steps']:
            if self.data['steps'][step]['type'] == 'tool_installation':
                continue

            if self.data['steps'][step]['type'] == 'initial':
                # Depend on completion of all previous copy phases.
                step_dependencies = ' && '.join([('copyvars%s.Succeeded' % environment.name) for environment in self.environments.values()])
            else:
                if step == self.data['first_step']:
                    step_dependencies = self.safe_name(initial_step)
                else:
                    step_dependencies = ' && '.join([self.safe_name(s) for s in self.data['DAG'][step]])
            step_name = self.safe_name(step) # For Argo safety.
            task = {'name': step_name,
                    'template': step_name,
                    'depends': step_dependencies}
            tasks.append(task)

            if self.data['steps'][step]['type'] == 'tool_invocation':
                environment = self.get_environment_with_tool(self.data['steps'][step]['tool_to_call'])
                image_name = environment.image_name(self.name, self.image_registry)
            else:
                image_name = 'chazapis/openbio-env:2'
            script_data = self.data['steps'][step]['bash']
            step_template = StepTemplate(step_name, image_name, script_data)
            templates.append(step_template.compile(self.name, self.work_path, self.artifact_factory))

        # Compile.
        result = {'apiVersion': 'argoproj.io/v1alpha1',
                  'kind': 'Workflow',
                  'metadata': {'name': self.name},
                  'spec': {'entrypoint': self.name,
                           'templates': [{'name': self.name, 'dag': {'tasks': tasks}}] + templates,
                           'volumes': volumes}}
        if isinstance(self.artifact_factory, S3ArtifactFactory):
            result['spec']['artifactRepositoryRef'] = {'configMap': self.artifact_factory.artifact_repository.config_map}

        return result

def pipeline(data, workflow_name, image_registry, work_path, artifact_repository, namespace):
    name = workflow_name if workflow_name else 'workflow'
    workflow = Workflow(name, data, image_registry, work_path, artifact_repository, namespace)

    return yaml.dump(workflow.compile())

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Convert a JSON workflow into Argo YAML', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--identifier', '-i', metavar='<workflow_identifier>', type=str, required=False, default='test-workflow', help='unique identifier for the workflow')
    parser.add_argument('--registry', '-r', metavar='<image_registry>', type=str, required=False, default='127.0.0.1:5000', help='image registry host and port')
    parser.add_argument('--path', '-p', metavar='<work_path>', type=str, required=False, default='/private/test-workflow', help='folder for intermediate files')
    parser.add_argument('--artifacts', '-a', metavar='<artifact_repository>', type=str, required=False, default='', help='artifact repository URL')
    parser.add_argument('--namespace', '-n', metavar='<namespace>', type=str, required=False, default='', help='create artifact configuration in this namespace')
    parser.add_argument('file_path', metavar='<file_path>', type=str)
    args = parser.parse_args()

    with open(args.file_path, 'r') as f:
        data = json.loads(f.read())

    print(pipeline(data, args.identifier, args.registry, args.path, args.artifacts, args.namespace))
