
import os
import json
import requests

os.environ['DJANGO_SETTINGS_MODULE'] = 'OpenBioC.settings'

import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
#from rest_framework.authtoken.models import DoesNotExist

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.test.client import RequestFactory

import app.views
app.views.g['TEST'] = True

from app.models import Tool, OBC_user, VisibilityOptions

rf = RequestFactory()

def get_test_user():
   return OBC_user.objects.get(user__username='test_user')

def decode_response(response):
   r_s = str(response.content, encoding='utf8')
   return json.loads(r_s)

def get_access_token():
   u = get_test_user()
   app.views.delete_user_access_token(u)
   try:
      t = Token.objects.get(user=u.user)
      return t.key
   except:
      response = decode_response(app.views.create_user_access_token(u))
      return response['profile_access_token']

def create_tool(*, 
      name, 
      version="1", 
      visibility='public', 
      dependencies=None, 
      edit=False, 
      edit_number=None, 
      assert_success=True,
   ):
   '''
   {'description_html': 'test', 'edit': 4, 'created_at': 'Fri, 23 Jul 2021 12:47:07', 'tool_pk': 147, 'tool_thread': [], 'score': 0, 'voted': {'up': False, 'down': False}, 'success': True}
   '''

   d = {
      'tool_description': 'test',
      'tools_search_name': name,
      'tools_search_version': version,
      'tool_edit_state': edit,
      'tool_visibility': visibility,
      'tool_dependencies': [] if not dependencies else dependencies, # [Tool.objects.get(name=t['name'], version=t['version'], edit=int(t['edit'])) for t in tool_dependencies]
      'tool_os_choices': [{'value': 'posix'}],
      'tool_installation_commands': '1234',
      'tool_validation_commands': '1234',
      'tool_variables': [], # 'x['name'] and x['value'] and x['description']'
      'tool_keywords': [],
   }

   if edit:
      d['tools_search_edit'] = int(edit_number)

   d = {k:json.dumps(v) for k,v in d.items()}

   r = rf.get('/tools_add/', d)
   r.user = get_test_user().user
   response = app.views.tools_add(r)
   ret = (decode_response(response))

   if assert_success:
      print (ret)
      assert ret.get('success', False)

   ret['name'] = name
   ret['version'] = version

   print (ret)
   return ret

def create_workflow(*, 
      name, 
      visibility='public', 
      includes_workflows=None, 
      includes_tools = None,
      edit_number = None,
      edit=False,
   ):

   with open('tests/empty_workflow.json') as f:
      workflow = json.load(f) 

   if includes_workflows:
      for inc_workflow in includes_workflows:
         workflow['elements']['nodes'].append(create_workflow_node(name=inc_workflow['name'], edit=inc_workflow['edit']))
         workflow['elements']['nodes'].append(create_submain_step_node(name=inc_workflow['name'], edit=inc_workflow['edit']))
         workflow['elements']['edges'].append(create_submain_workflow_edge(name=inc_workflow['name'], edit=inc_workflow['edit']))
         workflow['elements']['edges'].append(create_workflow_workflow_edge(name=inc_workflow['name'], edit=inc_workflow['edit']))

   if includes_tools:
      for inc_tool in includes_tools:
         workflow['elements']['nodes'].append(create_tool_node(name=inc_tool['name'], version=inc_tool['version'], edit=inc_tool['edit']))
         workflow['elements']['edges'].append(create_workflow_tool_edge(name=inc_tool['name'], version=inc_tool['version'], edit=inc_tool['edit']))

   #print (json.dumps(workflow))

   d = {
      'workflow_info_name': name,
      'workflow_info_forked_from': {}, # 
      'workflow_edit_state': edit,
      'workflow_visibility': visibility,
      'workflow_json': workflow,
      'workflow_description': 'test',
      'workflow_keywords': [],
   }

   if edit:
      d['workflow_info_edit'] = edit_number

   d = {k:json.dumps(v) for k,v in d.items()}

   r = rf.get('/workflows_add/', d)
   r.user = get_test_user().user
   response = app.views.workflows_add(r)
   ret = decode_response(response)
   ret['name'] = name
   print (ret)
   return ret

def delete_workflow(workflow):

   d={
      'ro': 'workflow',
      'action': 'DELETE',
      'workflow_info_name': workflow['name'],
      'workflow_info_edit': workflow['edit'],
   }
   d = {k:json.dumps(v) for k,v in d.items()}

   r = rf.get('/ro_finalize_delete/', d)
   r.user = get_test_user().user
   response = app.views.ro_finalize_delete(r)

   ret = decode_response(response)
   assert ret.get('success')
   print (ret)
   return ret

def delete_tool(tool):

   d={
      'ro': 'tool',
      'action': 'DELETE',
      'tools_info_name': tool['name'],
      'tools_info_version': tool['version'],
      'tools_info_edit': tool['edit'],
   }
   d = {k:json.dumps(v) for k,v in d.items()}

   r = rf.get('/ro_finalize_delete/', d)
   r.user = get_test_user().user
   response = app.views.ro_finalize_delete(r)

   ret = decode_response(response)
   assert ret.get('success')
   print (ret)
   return ret


def API(*, workflow=None, assert_not_ok=False, access_token=None):
   '''
   curl -H 'Accept: application/text' "http://0.0.0.0:8200/platform/rest/workflows/w1/1/?workflow_id=xyz&format=bash"
   '''
   headers = {
      'Accept': 'application/text',
   }

   if access_token:
      headers['Authorization'] = f'Token {access_token}'

   if workflow:
      params = (('workflow_id', 'xyz'), ('format', 'bash'))
      url = 'http://0.0.0.0:8200/platform/rest/workflows/{name}/{edit}'.format(name=workflow['name'], edit=workflow['edit'])

   r = requests.get(url, params=params, headers=headers)

   if assert_not_ok:
      assert r.status_code != requests.codes.ok
      return 
   else:
      assert r.status_code == requests.codes.ok
   text = r.text
   assert type(text) is str

   return text


def create_workflow_node(*, name, edit, draft=True):
   return {
             "data": {
                 "id": f"{name}__{edit}",
                 "name": name,
                 "edit": int(edit),
                 "label": f"{name}/{edit}",
                 "type": "workflow",
                 "draft": draft,
                 "disconnected": False,
                 "belongto": {
                     "name": "root",
                     "edit": None
                 }
             },
             "position": {
                 "x": 535.1666666666667,
                 "y": 238.79999999999998
             },
             "group": "nodes",
             "removed": False,
             "selected": False,
             "selectable": True,
             "locked": False,
             "grabbable": True,
             "classes": ""
         }

def create_tool_node(*, name, version, edit):
   return {
    "data": {
        "id": f"{name}__{version}__{edit}__2",
        "text": f"{name}/{version}/{edit}",
        "label": f"{name}/{version}/{edit}",
        "name": name,
        "version": str(version),
        "edit": int(edit),
        "type": "tool",
        "installation_commands": "# Insert the BASH commands that install this tool\n# You can use these environment variables: \n# ${OBC_TOOL_PATH}: path to tools directory \n# ${OBC_DATA_PATH}: path to data directory\n\n",
        "validation_commands": "# Insert the BASH commands that confirm that this tool is correctly installed\n# In success, this script should return 0 exit code.\n# A non-zero exit code, means failure to validate installation.\n\nexit 1\n",
        "os_choices": [
            "posix"
        ],
        "dependencies": [],
        "root": "yes",
        "dep_id": "#",
        "variables": [],
        "draft": True,
        "disconnected": False,
        "belongto": {
            "name": "root",
            "edit": None
        }
    },
    "position": {
        "x": 535.1666666666667,
        "y": 335.8125
    },
    "group": "nodes",
    "removed": False,
    "selected": False,
    "selectable": True,
    "locked": False,
    "grabbable": True,
    "classes": ""
   }

def create_submain_step_node(*,name, edit):
   return {
       "data": {
           "id": f"step__main_step__{name}__{edit}",
           "name": "main_step",
           "label": "main_step",
           "type": "step",
           "bash": "# Insert the BASH commands for this step.\n# You can use the variable ${OBC_WORK_PATH} as your working directory.\n# Also read the Documentation about the REPORT and the PARALLEL commands.\n\n",
           "main": False,
           "sub_main": True,
           "tools": [],
           "steps": [],
           "inputs": [],
           "outputs": [],
           "belongto": {
               "name": name,
               "edit": int(edit)
           }
       },
       "position": {
           "x": 338,
           "y": 378.09999999999997
       },
       "group": "nodes",
       "removed": False,
       "selected": False,
       "selectable": True,
       "locked": False,
       "grabbable": True,
       "classes": ""
   }

def create_submain_workflow_edge(*,name, edit):
   return {
       "data": {
           "source": f"{name}__{edit}",
           "target": f"step__main_step__{name}__{edit}",
           "id": f"{name}__{edit}..step__main_step__{name}__{edit}",
           "edgebelongto": "true"
       },
       "position": {
           "x": 0,
           "y": 0
       },
       "group": "edges",
       "removed": False,
       "selected": False,
       "selectable": True,
       "locked": False,
       "grabbable": True,
       "classes": ""
   }

def create_workflow_workflow_edge(*, name, edit):
   return {
       "data": {
           "source": "root__null",
           "target": f"{name}__{edit}",
           "id": f"root__null..{name}__{edit}",
           "edgebelongto": "true"
       },
       "position": {
           "x": 0,
           "y": 0
       },
       "group": "edges",
       "removed": False,
       "selected": False,
       "selectable": True,
       "locked": False,
       "grabbable": True,
       "classes": ""
   }

def create_workflow_tool_edge(*, name, version, edit):
   return {
       "data": {
           "source": "root__null",
           "target": f"{name}__{version}__{edit}__2",
           "id": f"root__null..{name}__{version}__{edit}__2",
           "edgebelongto": "true"
       },
       "position": {
           "x": 0,
           "y": 0
       },
       "group": "edges",
       "removed": False,
       "selected": False,
       "selectable": True,
       "locked": False,
       "grabbable": True,
       "classes": ""
   }




######################## TESTS ######################

def test_217_1():
   '''
   Access Public Workflow from API
   '''

   w1 = create_workflow(name='w1', visibility='public')
   response = API(workflow=w1)
   assert 'OBC_WORKFLOW_NAME' in response

   delete_workflow(w1)

def test_217_2():
   '''
   Access Private Workflow without token from API
   '''

   w1 = create_workflow(name='w1', visibility='private')
   response = API(workflow=w1, assert_not_ok=True)
   delete_workflow(w1)


def test_217_3():
   '''
   Access Private Workflow with token from API
   '''

   w1 = create_workflow(name='w1', visibility='private')
   access_token = get_access_token()

   response = API(workflow=w1, access_token=access_token)
   assert 'OBC_WORKFLOW_NAME' in response
   delete_workflow(w1)

def test_217_create_public_wf_containing_private_wf():
   '''
   create_public_wf_containing_private_wf
   '''
   w1 = create_workflow(name='w1', visibility='private')
   w2 = create_workflow(name='w2', visibility='public', includes_workflows=[{'name': 'w1', 'edit': 1}])

   assert 'error_message' in w2
   assert w2['error_message'] == 'This public workflow contains the private workflow: w1/1. Public workflows cannot include private workflows.'

   delete_workflow(w1)

def test_217_convert_from_private_to_public_workflow_containing_private_tool():
   '''
   '''
   w1 = create_workflow(name='w1', visibility='private')
   w2 = create_workflow(name='w2', visibility='private', includes_workflows=[{'name': 'w1', 'edit': 1}])

   w3 = create_workflow(name='w2', visibility='public', includes_workflows=[{'name': 'w1', 'edit': 1}], edit=True, edit_number=w2['edit'])
   assert 'error_message' in w3
   assert w3['error_message'] == 'This public workflow contains the private workflow: w1/1. Public workflows cannot include private workflows.'

   delete_workflow(w2)
   delete_workflow(w1)


def test_217_convert_wf_from_public_to_private_that_is_contained_in_public_wf():
   w1 = create_workflow(name='w1', visibility='public')
   w2 = create_workflow(name='w2', visibility='public', includes_workflows=[{'name': 'w1', 'edit': 1}])
   w3 = create_workflow(name='w1', visibility='private', edit=True, edit_number=w1['edit'])

   assert 'error_message' in w3
   assert w3['error_message'] == 'Cannot convert this Workflow to private. It is contained in the public workflow w2/1'

   delete_workflow(w2)
   delete_workflow(w1)

def test_217_create_public_tool_with_private_dependency():
   '''
   '''
   t1 = create_tool(name='t1', version="1", visibility='private')
   t2 = create_tool(name='t2', version="2", visibility='public', dependencies = [{'name': 't1', 'version': "1", 'edit': t1['edit']}], assert_success=False)


   assert t2.get('error_message', '') == 'This tool depends from the private tool: t1/1/1. Cannot create a public tool with private dependencies.'
   delete_tool(t1)

def test_217_create_public_wf_containing_private_tool():
   '''
   '''
   t1 = create_tool(name='t1', version="1", visibility='private')
   w1 = create_workflow(name='w1', visibility='public', includes_tools=[t1])

   assert w1.get('error_message', '') == 'This public workflow contains the private tool: t1/1/1. Public workflows cannot include private tools.'

   delete_tool(t1)

def test_217_convert_from_public_to_private_tool_that_exists_in_public_wf():
   '''
   '''
   t1 = create_tool(name='t1', version="1", visibility='public')
   w1 = create_workflow(name='w1', visibility='public', includes_tools=[t1])

   t1_error = create_tool(name='t1', version="1", visibility='private', edit=True, edit_number = t1['edit'], assert_success=False)
   #print (t1_error)
   assert t1_error.get('error_message', '') == 'Cannot make this tool private. Workflow w1/1 contains this Tool and is public.'

   delete_workflow(w1)
   delete_tool(t1)

def test_217_convert_from_private_to_public_tool_has_a_private_dependency():
   t1 = create_tool(name='t1', version="1", visibility='private')
   t2 = create_tool(name='t2', version="2", visibility='private', dependencies=[t1])

   t2_error = create_tool(name='t2', version='2', visibility='public', edit=True, edit_number=t2['edit'], assert_success=False)
   assert t2_error.get('error_message') == 'Cannot make this tool public. It depends from the private tool: t1/1/1'

   delete_tool(t2)
   delete_tool(t1)

def test_217_convert_from_public_to_private_tool_that_is_a_dependency_to_public_tool():
   t1 = create_tool(name='t1', version="1", visibility='public')
   t2 = create_tool(name='t2', version="2", visibility='public', dependencies=[t1])

   t1_error = create_tool(name='t1', version="1", visibility='private', edit=True, edit_number=t1['edit'], assert_success=False)

   assert t1_error.get('error_message') == 'Cannot make this tool private. Tool t1/1/1 depends from this tool and is public.'

   delete_tool(t2)
   delete_tool(t1)


#############################################################

def t():
   '''
   Test the tester
   '''

   test_217_convert_from_public_to_private_tool_that_is_a_dependency_to_public_tool()


