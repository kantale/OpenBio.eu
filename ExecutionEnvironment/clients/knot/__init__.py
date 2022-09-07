'''
Create and run workflow
Uses
https://github.com/couler-proj/couler
'''

import os
import json
import urllib

import couler.argo as couler
from couler.argo_submitter import ArgoSubmitter
from . import argo

from ExecutionEnvironment.executor import (
    setup_bash_patterns,
    BaseExecutor,
    Workflow,
)


class ArgoExecutor(BaseExecutor):
    def __init__(self, workflow, executor_parameters=None):
        # Set defaults
        if not executor_parameters:
            executor_parameters = {}
        if 'workflow_name' not in executor_parameters:
            executor_parameters['workflow_name'] = ''
        if 'image_registry' not in executor_parameters:
            executor_parameters['image_registry'] = '127.0.0.1'
        if 'work_path' not in executor_parameters:
            executor_parameters['work_path'] = '/work'
        if 'argo_artifact_repository_url' not in executor_parameters:
            executor_parameters['argo_artifact_repository_url'] = ''
        if 'namespace' not in executor_parameters:
            executor_parameters['namespace'] = ''

        super().__init__(workflow, executor_parameters)

    def build(self, output, output_format='argo', workflow_id=None, obc_client=False):
        self.decompose(
            break_down_on_tools=True,
            update_server_status=True,
        )
        # json_wf = json.dumps(self.decomposed)
        # print ('JSON DAG:')
        # print (json.dumps(self.decomposed, indent=4))
        # print ('='*20)

        ret = argo.pipeline(self.decomposed, self.workflow_name, self.image_registry, self.work_path, self.argo_artifact_repository_url, self.namespace)
        # print ('ARGO WORKFLOW:')
        # print (ret)
        # print ('='*20)

        return ret


def dispatch(*,
    nice_id,
    client_parameters,
    workflow_object,
    server_url,
    ):

    executor_parameters = {
        'workflow_name': 'openbio-' + nice_id,
        'image_registry': client_parameters['image_registry'],
        'work_path': os.path.join(client_parameters['work_path'], nice_id),
        'argo_artifact_repository_url': client_parameters['argo_artifact_repository_url'],
        'namespace': client_parameters['namespace']
    }

    namespace = client_parameters['namespace']

    # Setup bash scripts
    args = type('A', (), {
        'server': server_url,
        'insecure': False,
    })
    setup_bash_patterns(args)

    # Parse cytoscape workflow
    w = Workflow(workflow_object = workflow_object, askinput='NO', obc_server=server_url, workflow_id=None)

    # Create argo scripts
    e = ArgoExecutor(w, executor_parameters)
    e.build(output=None, output_format='argo', workflow_id=None, obc_client=server_url)

    # Submit with couler
    submitter = ArgoSubmitter(namespace=namespace)
    result = couler.run(submitter=submitter)

    # Get visualization url
    visualization_url = urllib.parse.urlparse(client_parameters['argo_url'])._replace(path='/workflows/%s/%s' % (namespace, result['metadata']['name'])).geturl()


    return {
        'visualization_url': visualization_url,
    }

