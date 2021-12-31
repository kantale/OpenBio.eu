# Create and run workflow

import os
import json
import urllib

import couler.argo as couler
from couler.argo_submitter import ArgoSubmitter
from . import cargo

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
        if 'image_cache_path' not in executor_parameters:
            executor_parameters['image_cache_path'] = None
        if 'work_path' not in executor_parameters:
            executor_parameters['work_path'] = '/work'

        super().__init__(workflow, executor_parameters)

    def build(self, output, output_format='argo', workflow_id=None, obc_client=False):
        self.decompose(
            break_down_on_tools=True,
            update_server_status=True,
        )
        json_wf = json.dumps(self.decomposed)
        #print ('JSON DAG:')
        #print (json.dumps(self.decomposed, indent=4))

        ret = cargo.pipeline(json_wf, self.workflow_name, self.image_registry, self.image_cache_path, self.work_path)
        #print ('ARGO WORKFLOW:')
        #print (ret)
        
        return ret


def dispatch(*,
    nice_id,
    client_parameters,
    workflow_object,
    server_url,
    ):

    executor_parameters = {
        'workflow_name': 'openbio-' + nice_id,
        'image_registry': client_parameters['ARGO_IMAGE_REGISTRY'],
        'image_cache_path': client_parameters['ARGO_IMAGE_CACHE_PATH'],
        'work_path': os.path.join(client_parameters['ARGO_WORK_PATH'], nice_id)
    }

    namespace = client_parameters['ARGO_NAMESPACE_PREFIX'] + 'admin' # self.request.user.username

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
    visualization_url = urllib.parse.urlparse(client_parameters['ARGO_BASE_URL'])._replace(path='/workflows/%s/%s' % (namespace, result['metadata']['name'])).geturl()


    return {
        'visualization_url': visualization_url,
    }

