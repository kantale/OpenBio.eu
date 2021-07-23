
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

def create_tool(name, version="1", visibility='public'):
   '''
   {'description_html': 'test', 'edit': 4, 'created_at': 'Fri, 23 Jul 2021 12:47:07', 'tool_pk': 147, 'tool_thread': [], 'score': 0, 'voted': {'up': False, 'down': False}, 'success': True}
   '''

   d = {
      'tool_description': 'test',
      'tools_search_name': name,
      'tools_search_version': version,
      'tool_edit_state': False,
      'tool_visibility': visibility,
      'tool_dependencies': [],
      'tool_os_choices': [{'value': 'posix'}],
      'tool_installation_commands': '1234',
      'tool_validation_commands': '1234',
      'tool_variables': [], # 'x['name'] and x['value'] and x['description']'
      'tool_keywords': [],

   }
   d = {k:json.dumps(v) for k,v in d.items()}

   r = rf.get('/tools_add/', d)
   r.user = get_test_user().user
   response = app.views.tools_add(r)
   ret = (decode_response(response))
   ret['name'] = name
   print (ret)
   return ret

def create_workflow(name, visibility='public'):

   with open('tests/empty_workflow.json') as f:
      workflow = json.load(f) 

   d = {
      'workflow_info_name': name,
      'workflow_info_forked_from': {}, # 
      'workflow_edit_state': False,
      'workflow_visibility': visibility,
      'workflow_json': workflow,
      'workflow_description': 'test',
      'workflow_keywords': [],
   }

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


######################## TESTS ######################

def test_217_1():
   '''
   Access Public Workflow
   '''

   w1 = create_workflow(name='w1', visibility='public')
   response = API(workflow=w1)
   assert 'OBC_WORKFLOW_NAME' in response

   delete_workflow(w1)

def test_217_2():
   '''
   Access Private Workflow without token
   '''

   w1 = create_workflow(name='w1', visibility='private')
   response = API(workflow=w1, assert_not_ok=True)
   delete_workflow(w1)


def test_217_3():
   '''
   Access Private Workflow with token
   '''

   w1 = create_workflow(name='w1', visibility='private')
   access_token = get_access_token()

   response = API(workflow=w1, access_token=access_token)
   assert 'OBC_WORKFLOW_NAME' in response
   delete_workflow(w1)



#############################################################

def t():
   '''
   Test the tester
   '''

   #get_access_token()
   #create_tool(name='t1')
   #w1 = create_workflow(name='w1', visibility='public')
   access_token = get_access_token()

   headers = {
      'Accept': 'application/text',
   }

   # curl -H 'Accept: application/text' "http://0.0.0.0:8200/platform/rest/workflows/w1/1/?workflow_id=xyz&format=bash"
   r = requests.get(
      #'http://0.0.0.0:8200/platform/rest/workflows/{name}/{edit}'.format(name=w1['name'], edit=w1['edit']),
      'http://0.0.0.0:8200/platform/rest/workflows/w1/1',
      params = (('workflow_id', 'xyz'), ('format', 'bash')),
      headers=headers,
   )
   print (r.text)
   print (type(r.text))

   #curl -H 'Accept: application/text' "https://openbio.eu/platform/rest/workflows/hapmap3_pca/1/?workflow_id=xyz&format=bash" 


   #delete_workflow(w1)


   #w2 = create_workflow(name='w2', visibility='private')




