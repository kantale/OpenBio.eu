# Django imports
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings # Access to project settings

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login # To distinguish from AJAX called login
from django.contrib.auth import logout as django_logout # To distinguish from AJAX called logout

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import URLValidator
from django.core.mail import send_mail

from django.db.models import Q # https://docs.djangoproject.com/en/2.1/topics/db/queries/#complex-lookups-with-q-objects
from django.db.models import Max # https://docs.djangoproject.com/en/2.1/topics/db/aggregation/
from django.db.models import Count # https://stackoverflow.com/questions/7883916/django-filter-the-model-on-manytomany-count

from django.utils import timezone
#from django.utils.html import escape # https://docs.djangoproject.com/en/2.2/ref/utils/#module-django.utils.html
from django.views.decorators.csrf import csrf_exempt # https://stackoverflow.com/questions/17716624/django-csrf-cookie-not-set/51398113

# Get csrf_token
# https://stackoverflow.com/questions/3289860/how-can-i-embed-django-csrf-token-straight-into-html
from django.middleware.csrf import get_token

from django.test.client import RequestFactory # We need this to simulate a request when uploading a workflow

#Import database objects
from app.models import (
    OBC_user, 
    Tool, 
    Workflow, 
    Variables, 
    ToolValidations, 
    OS_types, 
    Keyword, 
    Report, 
    ReportToken, 
    Reference, 
    ReferenceField, 
    Comment,
    UpDownCommentVote, 
    UpDownToolVote, 
    UpDownWorkflowVote, 
    ExecutionClient,
    VisibilityOptions,
)

from rest_framework.authtoken.models import Token # https://www.django-rest-framework.org/api-guide/authentication/#setting-the-authentication-scheme

from app.models import create_nice_id

#Import executor
from ExecutionEnvironment.executor import (
    create_bash_script, 
    OBC_Executor_Exception,
    Workflow as Workflow_executor,
)

# Email imports
import smtplib
from email.message import EmailMessage

# Social Core Authentication
#import social_core
from social_core.pipeline.social_auth import social_details

# System imports
import io
import os
import re
import six
import copy
import time # for time.sleep
import uuid
import hashlib
#import datetime # Use timezone.now()

import logging # https://docs.djangoproject.com/en/2.1/topics/logging/

from collections import Counter, defaultdict
from pprint import pprint 
import urllib.parse # https://stackoverflow.com/questions/40557606/how-to-url-encode-in-python-3/40557716

# Installed packages imports
import simplejson
from ansi2html import Ansi2HTMLConverter # https://github.com/ralphbean/ansi2html/

#https://pybtex.org/
from pybtex.database import parse_string as parse_reference_string
import pybtex.database.input.bibtex
import pybtex.plugin

import requests # Used in DOI resolution

# https://github.com/lepture/mistune
import mistune


__version__ = '0.2.0'

# Get an instance of a logger
logger = logging.getLogger(__name__)

#GLOBAL CONSTANTS
g = {
    'LOGIN_BACKEND': settings.LOGIN_BACKEND,
    'TITLE': settings.TITLE,
    'SERVER': settings.SERVER,
    'EMAIL': settings.EMAIL,
    'ADMIN': settings.ADMIN,
    'TERMS': settings.TERMS,
    'PRIVACY': settings.PRIVACY,
    'FUNDING_LOGOS': settings.FUNDING_LOGOS,
    'TEST': settings.TEST,

    'DEFAULT_DEBUG_PORT': 8200,
    'SEARCH_TOOL_TREE_ID': '1',
    'DEPENDENCY_TOOL_TREE_ID': '2',
    'VARIABLES_TOOL_TREE_ID': '3',
    'SEARCH_WORKFLOW_TREE_ID': '4',
    'SEARCH_REPORT_TREE_ID': '5',
    'format_time_string' : '%a, %d %b %Y %H:%M:%S', # RFC 2822 Internet email standard. https://docs.python.org/2/library/time.html#time.strftime   # '%Y-%m-%d, %H:%M:%S'

    'instance_settings' : {
        'cb62fc6f-f203-4525-bf40-947cbf51bda3': {
            'port': 8200,
            'controller_url': 'http://139.91.190.79:8080/post',
        },
        '341422c9-36c4-477e-81b7-26a76c77dd9a': {
            'port': 8201,
            'controller_url': 'http://139.91.190.79:8081/post'
        },
        'default': {
            'port': 8200,
            'controller_url': 'http://139.91.190.79:8080/post',
        },
    },
    'instance_setting_not_found_printed': False,
    'ansi2html_converter': Ansi2HTMLConverter(), # https://github.com/ralphbean/ansi2html/
    'markdown': mistune.Markdown(escape=True), # If you care about performance, it is better to re-use the Markdown instance:
                                                # escape=True should be the default option for mistune...

#    'pybtex': {
#        'pybtex_style': pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')(),
#        'pybtex_html_backend': pybtex.plugin.find_plugin('pybtex.backends', 'html')(),
#        'pybtex_parser': pybtex.database.input.bibtex.Parser()
#    }
    # materialize js tree icons
    # https://materializecss.com/icons.html
    'jstree_icons': {
        'tools': 'settings',
        'variables': 'chevron_right', # Tool variables
        'workflows': 'device_hub',
        'reports': 'description',
        'references': 'link',
        'users': 'person',
        'qas': 'forum',
        'private': 'lock',
    },
    'url_validator': URLValidator(), # Can be customized: URLValidator(schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))
    'client_name_regex': r'^[\w]+$', # The regular expression to validate the name of exutation client
    'client_max': 10, # Max number of execution clients
    # Create the URL for the report generated in the OBC client
    'create_client_download_report_url': lambda client_url, nice_id : urllib.parse.urljoin(client_url + '/', 'download/{NICE_ID}'.format(NICE_ID=nice_id)),
    'create_client_download_log_url': lambda client_url, nice_id: urllib.parse.urljoin(client_url + '/', 'logs/{NICE_ID}'.format(NICE_ID=nice_id)),
    'create_client_check_status_url': lambda client_url, nice_id: urllib.parse.urljoin(client_url + '/', 'check/id/{NICE_ID}'.format(NICE_ID=nice_id)),
    'create_client_pause_url': lambda client_url, nice_id: urllib.parse.urljoin(client_url + '/', 'workflow/{NICE_ID}/paused/true'.format(NICE_ID=nice_id)),
    'create_client_resume_url': lambda client_url, nice_id: urllib.parse.urljoin(client_url + '/', 'workflow/{NICE_ID}/paused/false'.format(NICE_ID=nice_id)),
    'create_client_abort_url': lambda client_url, nice_id: urllib.parse.urljoin(client_url + '/', 'workflow/delete/{NICE_ID}'.format(NICE_ID=nice_id)),
    'create_client_airflow_url': lambda client_url, nice_id: urllib.parse.urljoin(client_url + '/', 'admin/airflow/graph?dag_id={NICE_ID}&execution_date='.format(NICE_ID=nice_id)),
    'maximum_workflow_file_upload': 1 , # Maximum file size for workflow upload in megabytes  
}

### HELPING FUNCTIONS AND DECORATORS #####

def md5(t):
    '''
    Return the md5 hash of this string
    '''
    return hashlib.md5(t.encode("utf-8")).hexdigest()

def decode_response(response):
   r_s = str(response.content, encoding='utf8')
   return simplejson.loads(r_s)

def valid_url(url):
    '''
    Is url valid?
    Uses django's URLvalidator
    '''

    try:
        g['url_validator'](url)
    except ValidationError:
        return False
    else:
        return True

def user_is_validated(request):
    '''
    Is the email of the user validated?
    Returns True/False
    '''

    if request.user.is_anonymous:
        #print ('User is anonymous')
        return False

    try:
        obc_user = OBC_user.objects.get(user=request.user)
    except ObjectDoesNotExist:
        #print ('User does not exist')
        return False # This should never happen

    ret = obc_user.email_validated
    #print ('User is validated:', ret)

    return ret

def get_obc_user(request):
    '''
    Get the obc_user
    instead of def get_user
    '''

    if request.user.is_anonymous:
        return None

    try:
        obc_user = OBC_user.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return None

    return obc_user

def str_boolean(b):
    '''
    For testing. Testing passes Booleans as strings
    '''

    return {'False': False, 'True': True}.get(b, b) # Testing passes strings

def resolve_doi(doi):
    '''
    https://gist.github.com/jrsmith3/5513926
    Return a bibTeX string of metadata for a given DOI.
    Used in references_process_doi
    '''

    url = "http://dx.doi.org/" + doi
    headers = {"accept": "application/x-bibtex"}
    r = requests.get(url, headers = headers)

    if r.status_code == requests.codes.ok:
        return r.text

    return None

def replace_interlinks(text):
    '''
    Search for interlinks and replace with javascript calls
    '''

    ret = text

    def javascript_call(matched_string, arguments):
        '''
        Create the javascript call
        '''

        func_call = '''window.OBCUI.interlink({});'''.format(simplejson.dumps(arguments))
        pattern = '''<a href="javascript:void(0);" onclick='{}'>{}</a>'''.format(func_call, matched_string)
        return pattern

    interlink_options = {
        'tools': {
            'findall': r'[^\w]([td]/[\w]+/[\w\.]+/[\d]+)',
            'arguments': r'(?P<type>[td])/(?P<name>[\w]+)/(?P<version>[\w\.]+)/(?P<edit>[\d]+)',
            'exists': lambda arguments: Tool.objects.filter(name__iexact=arguments['name'], version__iexact=arguments['version'], edit=int(arguments['edit'])).exists()
        },
        'workflows': {
            'findall': r'[^\w](w/[\w]+/[\d]+)',
            'arguments': r'(?P<type>w)/(?P<name>[\w]+)/(?P<edit>[\d]+)',
            'exists': lambda arguments: Workflow.objects.filter(name__iexact=arguments['name'], edit=int(arguments['edit'])).exists()
        },
        'references': {
            'findall': r'[^\w](r/[\w]+)',
            'arguments': r'(?P<type>r)/(?P<name>[\w]+)',
            'exists': lambda arguments: Reference.objects.filter(name__iexact=arguments['name']).exists()
        },
        'users': {
            'findall': r'[^\w](u/[\w]+)',
            'arguments': r'(?P<type>u)/(?P<username>[\w]+)',
            'exists': lambda arguments: OBC_user.objects.filter(user__username__iexact=arguments['username']).exists()
        },
        'comment': {
            'findall': r'[^\w](c/[\d]+)',
            'arguments': r'(?P<type>c)/(?P<id>[\d]+)',
            'exists': lambda arguments: Comment.objects.filter(pk=int(arguments['id'])).exists()
        }
    }

    for interlink_key, interlink_value in interlink_options.items():
        calls = set(re.findall(interlink_value['findall'], ' ' + text)) # We add a space (' ') so that we catch interlinks at the beginning of string
        for call in calls:
            #print ('call:', call)
            #print ('regexp:', interlink_value['arguments'])
            arguments = re.search(interlink_value['arguments'], call).groupdict()
            if interlink_value['exists'](arguments):
                ret = ret.replace(call, javascript_call(call, arguments))

#    tool_calls = set(re.findall(interlink_options['tools']['findall'], text))
#    for tool_call in tool_calls:
#        arguments = re.search(interlink_options['tools']['arguments'], tool_call).groupdict()
#        # Does this tool exists?
#        if Tool.objects.filter(name=arguments['name'], version=arguments['version'], edit=arguments['edit']).exists():
#            ret = ret.replace(tool_call, javascript_call(tool_call, arguments))

    return ret



def markdown(t):
    '''
    https://github.com/lepture/mistune
    '''
    md = g['markdown'](t)
    # Remove <p> at the start and </p> at the end
    s =  re.search(r'^<p>(.*)</p>\n$', md, re.M | re.S)
    if s:
        ret = s.group(1)
    else:
        ret = md

    # Check for interlinks
    ret = replace_interlinks(ret)
    return ret

def jstree_icon_html(t):
    '''
    Create a html tags for materialize icon
    '''
    return '<i class="material-icons jsTreeMaterialIcons left md-18">{}</i>'.format(g['jstree_icons'][t])

def fail(error_message=None):
    '''
    Failed AJAX request
    '''

    ret = {'success': False, 'error_message': error_message}
    json = simplejson.dumps(ret)

    return HttpResponse(json, content_type='application/json')

def success(data={}):
    '''
    success Ajax request
    '''
    data['success'] = True
    json = simplejson.dumps(data)
    return HttpResponse(json, content_type='application/json')

def has_data(f):
    '''
    Decorator that passes AJAX data to a function parameters
    '''
    def wrapper(*args, **kwargs):

            request = args[0]

            if request.method == 'POST':
                    if len(request.POST):
                            for k in request.POST:
                                kwargs[k] = request.POST[k]
                    else:
                            try:
                                POST = simplejson.loads(request.body)
                            except simplejson.errors.JSONDecodeError as e:
                                return fail('Could not parse JSON data')

                            for k in POST:
                                kwargs[k] = POST[k]
            elif request.method == 'GET':
                    for k in request.GET:
                        if not k in kwargs: # Perhaps the function has already been called specifically with a value in kwargs
                            kwargs[k] = request.GET[k]
                            #print ("GET: {} == {}".format(k, kwargs[k]))

            if g['TEST']:
                kwargs = {
                    k:simplejson.loads(v)
                    for k,v in kwargs.items()
                }

            return f(*args, **kwargs)

    return wrapper

def username_exists(username):
    '''
    Checks if a username exists
    '''

    return User.objects.filter(username__iexact=username).exists()

def datetime_to_str(d):
    '''
    String format
    '''

    return d.strftime(g['format_time_string'])

def convert_ansi_to_html(ansi):
    '''
    Create a nice standalone html page from stdout
    https://github.com/ralphbean/ansi2html/
    '''
    return g['ansi2html_converter'].convert(ansi)

def create_uuid_token():
    '''
    Create a uuid token for email validation
    Length: 32 characters
    '''
    # return str(uuid.uuid4()).split('-')[-1] # Last part: 12 characters
    return str(uuid.uuid4()).replace('-', '') # 32 characters

def uuid_is_valid(uuid_token):
    '''
    https://gist.github.com/ShawnMilo/7777304
    '''

    try:
        val = uuid.UUID(uuid_token, version=4)
    except ValueError:
        return False

    return val.hex == uuid_token.replace('-', '')

def send_mail_smtplib(from_, to, subject, body):
    '''
    Standard email send function with SMTP

    Adjusted from here:
    https://docs.python.org/3/library/email.examples.html
    NOT USED!
    '''

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = to
    s = smtplib.SMTP('localhost') # Send the message via our own SMTP server.
    s.send_message(msg)
    s.quit()

def request_port_to_url(request):
    '''
    Do we have to append a url with the port?
    '''

    port = request.META['SERVER_PORT'] # This is a string
    if port in ['80', '443']: # Do not add port info when http default or https default
        return ''

    return ':' + port # For example ':8080'


def create_validation_url(token, port=''):
    '''
    https://stackoverflow.com/a/5767509/5626738
    http://www.example.com/?param1=7&param2=seven.

    FIXME: "platform" should be derived from request.
    SEE: https://stackoverflow.com/questions/2491605/how-to-get-the-current-url-name-using-django
    '''
    ret = '{server}{port}/platform/?validation_token={token}'.format(server=g['SERVER'], token=token, port=port)
    return ret


def create_password_email_url(token, port=''):
    '''
    See also create_validation_url for FIXME issue
    '''

    ret = '{server}{port}/platform/?password_reset_token={token}'.format(server=g['SERVER'], token=token, port=port)
    return ret


def confirm_email_body(token, port=''):
    '''
    The mail verification mail body
    '''
    ret = '''
Thank you for signing up to {server}

To complete your registration please click (or copy-paste to your browser) the following link:
{validation_url}

Regards,
The openbio.eu admin team.
'''

    return ret.format(server=g['SERVER'], validation_url=create_validation_url(token, port))

def reset_password_email_body(token, port=''):
    '''
    The email for resetting a password
    '''
    ret = '''
Dear user,

Someone (hopefully you) has requested to reset the password at {server} .
If this is you, please go to the following link to complete the process:
{password_reset_url}

Otherwise please ignore this email!

Regards,
The openbio.eu admin team.
'''

    return ret.format(server=g['SERVER'], password_reset_url=create_password_email_url(token, port))

def validate_user(token):
    '''
    Validates a user
    Returns: True/False, message
    '''

    try:
        obc_user = OBC_user.objects.get(email_validation_token=token)
    except ObjectDoesNotExist:
        obc_user = None

    if obc_user:
        if obc_user.email_validated:
            return False, "User's email is already validated"

        else:
            #Validate user
            obc_user.email_validated = True
            #Delete validation token
            obc_user.email_validation_token = None

            obc_user.save()
            return True, 'Email successfully validated'
    else:
        return False, 'Unknown or deleted email validation token'

def password_reset_check_token(token):
    '''
    Check the token for password reset
    '''

    try:
        obc_user = OBC_user.objects.get(password_reset_token=token)
    except ObjectDoesNotExist:
        obc_user = None

    if obc_user:
        timestamp = obc_user.password_reset_timestamp
        seconds = (now() - timestamp).total_seconds()
        if seconds > 3600 * 2: # 2 Hours
            return False, 'Password Reset Token expires after 2 Hours', None
        else:
            return True, '', obc_user
    else:
        return False, "Unknown token", None


def now():
    '''
    https://stackoverflow.com/a/415519/5626738
    https://stackoverflow.com/questions/18622007/runtimewarning-datetimefield-received-a-naive-datetime
    '''
    #return datetime.datetime.now()
    return timezone.now()

def check_password(password):
    '''
    Check for password correctness
    '''
    if len(password) < 6:
        return False, 'Minimum password length is 6'

    return True, ''

def send_validation_email_inner(request, email):
    '''
    Send an email validation email
    Returns
    suc, error_message, uuid_token
    '''

    uuid_token = create_uuid_token()

    if settings.DEBUG:
        #print ('VALIDATION EMAIL TOKEN:', uuid_token)
        #print ('URL: http://0.0.0.0:{}/platform/?validation_token={}'.format(request.META['SERVER_PORT'], uuid_token))
        return True, '', uuid_token

    try:
        send_mail(
            '[{server}] Please confirm your email'.format(server=g['SERVER']), # subject
            confirm_email_body(uuid_token, port=request_port_to_url(request)), # body message
            g['EMAIL'], # Sender, FROM
            [email], # List of recipients
        )
    except Exception as e:
        return False, 'Could not send an email to {email}. Contact {ADMIN}'.format(email=email, ADMIN=g['ADMIN']), None # Better to add None

    return True, '', uuid_token


def None_if_empty_or_nonexisting(d, key):
    '''
    Useful if want to set None values to empty values that we got from Ajax
    '''

    if not key in d:
        return None

    value = d[key].strip()
    if not value:
        return None

    return value

def tool_to_json(tool):
    if not tool:
        return None

    return {
        'name': tool.name,
        'version': tool.version,
        'edit': tool.edit,
    }

def workflow_to_json(workflow):
    if not workflow:
        return None

    return {
        'name': workflow.name,
        'edit': workflow.edit,
    }


def tool_text_jstree(tool):
    '''
    The JS tree tool text
    The id should have 4 fields.
    '''
    return '/'.join(map(str, [tool.name, tool.version, tool.edit]))

def tool_node_jstree(tool):
    '''
    The HTML that is node in a jstree that contains a tool
    '''
    return (
        tool_text_jstree(tool) +
        (' <span class="red lighten-3">DRAFT</span>' if tool.draft else '') +
        jstree_icon_html('tools') +
        (jstree_icon_html('private') if tool.visibility == str(VisibilityOptions.PRIVATE_CODE) else '')
    )


def workflow_text_jstree(workflow):
    '''
    The JS tree workflow text
    '''
    return '/'.join(map(str, [workflow.name, workflow.edit]))

def workflow_node_jstree(workflow):
    '''
    The HTML that is node in a jstree that contains a workflow
    '''
    return (
        workflow_text_jstree(workflow) +
        (' <span class="red lighten-3">DRAFT</span>' if workflow.draft else '') +
        jstree_icon_html('workflows') +
        (jstree_icon_html('private') if workflow.visibility == str(VisibilityOptions.PRIVATE_CODE) else '')
    )

def report_text_jstree(report):
    '''
    The JS tree report text
    '''
    return workflow_text_jstree(report.workflow) + '/' + report.nice_id

def tool_id_jstree(tool, id_):
    '''
    The JS tree tool id
    Return a JSON string so that it can have many fields
    '''
    #return tool_text_jstree(tool) + '/' + str(id_)
    return simplejson.dumps([tool.name, tool.version, str(tool.edit), str(id_)])

def tool_id_cytoscape(tool):
    '''
    The cytoscape tool id
    '''
    if isinstance(tool, Tool):
        return '__'.join([tool.name, tool.version, str(tool.edit), g['DEPENDENCY_TOOL_TREE_ID']])
    elif type(tool) is dict:
        return '__'.join([tool['name'], tool['version'], str(tool['edit']), g['DEPENDENCY_TOOL_TREE_ID']])
    else:
        raise Exception('Error: 8151')


def step_id_cytoscape(step_name, workflow, name, edit):
    '''
    cytoscape step id
    '''

    return 'step' + '__' + step_name + '__' + workflow_id_cytoscape(workflow, name, edit)

def step_id_label(step_name):
    '''
    cytoscape step label
    '''

    return step_name


def tool_label_cytoscape(tool):
    '''
    The cytoscape tool label
    '''
    if isinstance(tool, Tool):
        return '/'.join([tool.name, tool.version, str(tool.edit)])
    elif type(tool) is dict:
        return '/'.join([tool['name'], tool['version'], str(tool['edit'])])
    else:
        raise Exception('Error: 9810')

def tool_label_cytoscape_to_object(tool_label):
    '''
    The inverse of tool_label_cytoscape
    '''
    name, version, edit = tool_label.split('/')
    return {
        'name': name,
        'version': version,
        'edit': int(edit),
    }

def workflow_id_cytoscape(workflow, name, edit):
    '''
    The cytoscape workflow id
    '''

    if type(workflow) is dict:
        return workflow['name'] + '__' + str(workflow['edit'])

    if workflow:
        return workflow.name + '__' + str(workflow.edit)

    return name + '__' + str(edit)

def workflow_label_cytoscape_name_edit(name, edit):
    return f'{name}/{str(edit)}'

def workflow_label_cytoscape(workflow, name=None, edit=None):
    '''
    The cytoscape workflow label
    '''
    if workflow is None:
        return workflow_label_cytoscape_name_edit(name, edit)

    if isinstance(workflow, Workflow):
        return workflow_label_cytoscape_name_edit(workflow.name, workflow.edit)

    if type(workflow) is dict:
        return workflow_label_cytoscape_name_edit(workflow['name'], workflow['edit'])


    raise Exception('Error: 9811')


def workflow_id_jstree(workflow, id_):
    '''
    The JS Tree workflow id
    Return a JSON string so that it can have many fields
    '''
    return simplejson.dumps([workflow.name, str(workflow.edit), str(id_)])

def report_id_jstree(report, id_):
    '''
    The JS Tree Report id
    Return a JSON string so that it can have many fields
    '''

    return simplejson.dumps([report.workflow.name, str(report.workflow.edit), str(report.nice_id), str(id_)])

def tool_variable_node_jstree(variable):
    '''
    The JSTree variable html
    '''
    return '{}:{}'.format(variable.name, variable.description) + jstree_icon_html('variables')

def tool_variable_id_jstree(variable, tool, id_):
    '''
    The JSTree variable id
    Returns a JSON string, so that it can have many fields.
    It also contains information from the tool
    '''

    #return variable.name + '/' + variable.value + '/' + variable.description + '/' + str(id_)
    return simplejson.dumps([
        variable.name, variable.value, variable.description,
        str(id_),
        tool.name, tool.version, tool.edit])

def tool_get_dependencies_internal(tool, include_as_root=False):
    '''
    Get the dependencies of this tool in a flat list
    Recursive
    include_as_root: Should we add this tool as root?

    'dependant' needs dependencies..
    '''

    if include_as_root:
        ret = [{'dependant': None, 'dependency': tool}]
    else:
        ret = []

    for dependent_tool in tool.dependencies.all():
        ret.append({
            'dependant': tool,
            'dependency': dependent_tool
        })
        ret.extend(tool_get_dependencies_internal(dependent_tool, include_as_root=False))

    return ret

def tool_build_dependencies_jstree(tool_dependencies, add_variables=False, add_installation_commands=False):
    '''
    Build JS TREE from tool_dependencies

    add_variables:  Also add tool/data variables
    add_installation_commands: All installation_commands + validation_commands + os_choices

    ATTENTION: THIS IS NOT GENERIC!!!
    IT uses g['DEPENDENCY_TOOL_TREE_ID'].
    '''

    tool_dependencies_jstree = []
    for tool_dependency in tool_dependencies:
        to_append = {

            'data': {
#                    'name': tool_dependency['dependency'].name,
#                    'version': tool_dependency['dependency'].version,
#                    'edit': tool_dependency['dependency'].edit,
                    'type': 'tool',
             },
            'text': tool_node_jstree(tool_dependency['dependency']), # tool_text_jstree(tool_dependency['dependency']), # This is what is shown on the tree
            'cy_label': tool_label_cytoscape(tool_dependency['dependency']), # Label to show in the cytoscape graph
            'id': tool_id_jstree(tool_dependency['dependency'], g['DEPENDENCY_TOOL_TREE_ID']), # This is a unique id
            'parent': tool_id_jstree(tool_dependency['dependant'], g['DEPENDENCY_TOOL_TREE_ID']) if tool_dependency['dependant'] else '#',
            'type': 'tool', ### This is redundant with ['data']['type'], but we need it because
                            ### The node[0].data.type is checked in $scope.tools_var_jstree_model.
                            ### See also issue #93

            'name': tool_dependency['dependency'].name,
            'version': tool_dependency['dependency'].version,
            'edit': tool_dependency['dependency'].edit,
            'draft': tool_dependency['dependency'].draft,

        }
        if add_installation_commands:
            to_append['installation_commands'] = tool_dependency['dependency'].installation_commands
            to_append['validation_commands'] = tool_dependency['dependency'].validation_commands
            to_append['os_choices'] = [choice.os_choices for choice in tool_dependency['dependency'].os_choices.all()]
            to_append['dependencies'] = [str(t) for t in tool_dependency['dependency'].dependencies.all()]

            # https://github.com/kantale/OpenBio.eu/issues/225
            to_append['description'] = tool_dependency['dependency'].description
            to_append['website'] = tool_dependency['dependency'].website
            to_append['keywords'] = [k.keyword for k in tool_dependency['dependency'].keywords.all()]
            to_append['visibility'] = VisibilityOptions.VISIBILITY_OPTIONS_CODE_dic[tool_dependency['dependency'].visibility] 

        tool_dependencies_jstree.append(to_append)

        # Add the variables of this tool
        if add_variables:
            for variable in tool_dependency['dependency'].variables.all():
                tool_dependencies_jstree.append({
                    'data': {
                        'type': 'variable',
                        'name': variable.name,
                        'value': variable.value,
                        'description': variable.description,
                    },
                    'text': tool_variable_node_jstree(variable),
                    'id': tool_variable_id_jstree(variable, tool_dependency['dependency'], g['VARIABLES_TOOL_TREE_ID']),
                    'parent': tool_id_jstree(tool_dependency['dependency'], g['DEPENDENCY_TOOL_TREE_ID']),
                    'type': 'variable', # TODO: FIX REDUNDANCY WITH ['data']['type']
                })

    return tool_dependencies_jstree


### HELPING FUNCTIONS AND DECORATORS END #######


### VIEWS ############

def get_instance_settings():
    '''
    Gets the id of this local installation
    We are running multiple server instances for development
    Each instance should have their own port
    '''

    if not os.path.exists('id.txt'):
        if not g['instance_setting_not_found_printed']:
            logger.warning('Could not find id.txt setting default')
            g['instance_setting_not_found_printed'] = True

        return g['instance_settings']['default']
    with open('id.txt') as f:
        this_id = f.read().strip()

    return g['instance_settings'][this_id]

### USERS

def get_orcid_data(user):
    '''
    Retrieve orcid data from the database.
    https://stackoverflow.com/questions/24221117/get-access-token-from-python-social-auth

    social.extra_data structure:
    {
        'auth_time': 1618581152,
        'id': '0000-0002-0077-7296',
        'expires': 631138518,
        'refresh_token': '4d039eb0-e7f5-49e4-a2e4-f07ce8c22715',
        'access_token': '2a1ad4d3-32f0-45b0-822c-a52295caae15',
        'token_type': 'bearer'
    }

    '''
    try:
        #social = user.social_auth.get(provider="orcid-sandbox")
        social = user.social_auth.get(provider="orcid")
    except ObjectDoesNotExist:
        # User does not have ORCID
        return None

    return social.extra_data['id']
    #return social

def get_doi_from_orcid(orcid_id):
    '''
    Get an orcid_id and return a set with all DOIs of this user
    '''
    url = f"https://orcid.org/{orcid_id}/worksPage.json?offset=0&sort=date&sortAsc=false&pageSize=1000"

    def get_doi_from_externalIdentifier(ei):
        ret = set()

        indexes = ['externalIdentifierId', 'url', 'normalized', 'normalizedUrl']


        for index in indexes:
            if index in ei:
                if 'value' in ei[index]:
                    ret.add(ei[index]['value'])

        #print (ret)
        return ret

    def get_doi_from_orcid_object(j):
        ret = set()

        if 'groups' in j:
            for group in j['groups']:

                if 'externalIdentifiers' in group:
                    for ei in group['externalIdentifiers']:
                        ret |= get_doi_from_externalIdentifier(ei)

                if 'works' in group:
                    for work in group['works']:
                        if 'workExternalIdentifiers' in work:
                            for wei in work['workExternalIdentifiers']:
                                ret |= get_doi_from_externalIdentifier(wei)

        return ret


    try:
        r = requests.get(url)
        if not r.ok:
            raise Exception
    except:
        return None

    j = r.json()

    doi_set = get_doi_from_orcid_object(j)
    return doi_set

@has_data
def references_orcid_claim_pressed(request, **kwargs):
    '''
    Called when ORCID icon pressed in reference right panel
    '''

    references_name = kwargs.get('references_name')
    if not references_name:
        return fail('Error 7567')

    OBC_user = get_obc_user(request)
    if not OBC_user:
        return fail('Error 7568. User not found.')

    orcid_id = get_orcid_data(OBC_user.user)
    if not orcid_id:
        return fail('You have not connected your profile with ORCID')


    # Get DOI of publication
    try:
        reference = Reference.objects.get(name=references_name)
    except ObjectDoesNotExist:
        return fail('Error 7569. Could not find reference object')

    doi = reference.doi
    if not doi:
        return fail('This publication does not have a DOI field')

    # Check if this doi exists in user's references
    if OBC_user.references.filter(pk=reference.pk).exists():
        return fail('You have already claimed this publication')

    doi_set = get_doi_from_orcid(orcid_id)
    if doi_set is None:
        return fail('Could not Retrieve DOIs from ORCID')

    if not doi_set:
        return fail('ORCID returned an empty set for your ID')

    if not doi in doi_set:
        return fail('Could not find the DOI of this paper in your ORCID profile.')

    # Add this reference to this user
    OBC_user.references.add(reference)
    OBC_user.save()


    ret = {
        'doi': doi,
        'orcid_id': orcid_id,
    }
    return success(ret)

@has_data
def references_orcid_unclaim_pressed(request, **kwargs):
    '''
    Called when ORCID unclaim pressed in reference right panel
    '''

    references_name = kwargs.get('references_name')
    if not references_name:
        return fail('Error 7667')

    OBC_user = get_obc_user(request)
    if not OBC_user:
        return fail('Error 7668. User not found.')

    # Reference
    try:
        reference = Reference.objects.get(name=references_name)
    except ObjectDoesNotExist:
        return fail('Error 7669. Could not find reference object')

    # Confirm that this reference belongs to user
    if not OBC_user.references.filter(pk=reference.pk).exists():
        return fail('Error 7670.') # This paper is not linked to this user ????

    # Unlink it!!!
    OBC_user.references.remove(reference)
    OBC_user.save()

    ret = {}
    return success(ret)

def get_user_access_token(obc_user):
    '''
    Get the access token for private API access
    ### TEST 217_access_token
    '''

    try:
        t = Token.objects.get(user = obc_user.user)
    except ObjectDoesNotExist:
        return None

    return t

def delete_user_access_token(obc_user):
    token = get_user_access_token(obc_user)
    if not token:
        return fail('Error. 5891 Could not find the access token of this user.')

    token.delete()

    return success()


@has_data
def profile_delete_access_token(request, **kwargs):
    '''
    Delete the access token of a user
    ### TEST 217_access_token
    '''

    obc_user = get_obc_user(request)
    return delete_user_access_token(obc_user)

def create_user_access_token(obc_user):
    if not obc_user:
        return fail('Error 5892. Could not find user.')

    token = Token.objects.create(user=obc_user.user)

    ret = {
        'profile_access_token': token.key,
    }

    return success(ret)


@has_data
def profile_issue_access_token(request, **kwargs):
    '''
    Generate a new access token
    ### TEST 217_access_token
    '''
    profile_delete_access_token(request)
    obc_user = get_obc_user(request)
    return create_user_access_token(obc_user)

@has_data
def users_search_3(request, **kwargs):
    '''
    Get profile info for a single user.
    This is called from:
    * Click on profile
    * Click on a user node in left panel jstree
    '''

    username = kwargs.get('username', '')
    if not username:
        return fail('Could not get username')

    u = get_obc_user(request)
    if not u:
        return fail('Could not find user with this username')

    ret = {
        'profile_username': username,
        'profile_firstname': u.first_name,
        'profile_lastname': u.last_name,
        'profile_website': u.website,
        'profile_affiliation': u.affiliation,
        'profile_publicinfo': u.public_info,
        'profile_created_at': datetime_to_str(u.user.date_joined), # https://docs.djangoproject.com/en/2.2/ref/contrib/auth/#django.contrib.auth.models.User.date_joined
        'profile_ORCID': get_orcid_data(u.user),
        'profile_access_token' : getattr(get_user_access_token(u), 'key', None),
    }

    # only for registered user:
    # * get mail
    # * get ExecutionClients
    if username == request.user.username:
        ret['profile_email'] = u.user.email
        ret['profile_clients'] = [{'name': client.name, 'parameters': client.parameters} for client in u.clients.all()]
    else:
        ret['profile_email'] = ''

    return success(ret)

@has_data
def user_add_client(request, **kwargs):
    '''
    Called from $scope.profile_add_client when user adds a new Execution Client
    URL: user_add_client/
    '''

    # Get the user
    try:
        obc_user = OBC_user.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return fail('Error 8619'); # This should never happen

    #Get and validate the name
    name = kwargs.get('name', '')
    if not re.match(g['client_name_regex'], name):
        return fail('Invalid client name (allowed characters, a-z, A-Z, 0-9, _)')

    # Get and validate the client
    parameters = kwargs.get('parameters', '')
    try:
        parameters_parsed = simplejson.loads(parameters)
    except simplejson.errors.JSONDecodeError as e:
        return fail(f'Invalid JSON data in Parameters: {str(e)}')

    #Parameters should have a type field. This is the only obligatory field
    if not 'type' in parameters_parsed:
        return fail('"type" field not present in client parameters')

    # Check that the name and the client does not exist and that maximum number has not been reached
    existing_clients = [{'name':x.name, 'parameters': x.parameters} for x in obc_user.clients.all()]
    if len(existing_clients) >= g['client_max']:
        return fail('Maximum number of Execution Clients has been reached')

    existing_names = {x['name'] for x in existing_clients}
    if name in existing_names:
        return fail('There is already an Execution Client with this name')

    ## Add the execution environment
    new_execution_client = ExecutionClient(name=name, parameters=simplejson.dumps(parameters_parsed))
    new_execution_client.save()
    obc_user.clients.add(new_execution_client)

    # Return all the profile clients
    ret = {
        'profile_clients' : [
            {
            'name': client.name, 
            'parameters': client.parameters
            } 
            for client in obc_user.clients.all()
        ],
    }

    obc_user.save()

    return success(ret)

@has_data
def user_delete_client(request, **kwargs):
    '''
    Called from $scope.profile_delete_client
    URL:  user_delete_client
    '''

    name = kwargs.get('name', '')
    if not name:
        return fail('Error 3498')

    # Get the user
    try:
        obc_user = OBC_user.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return fail('Error 8686'); # This should never happen

    # Get the Execution Client
    try:
        ec = ExecutionClient.objects.get(obc_user=obc_user, name=name)
    except ObjectDoesNotExist as e:
        return fail('Error 4555')

    # Delete the Execution Client
    ec.delete()

    # Return all the profile clients
    ret = {
        'profile_clients' : [{'name': client.name, 'parameters': client.parameters} for client in obc_user.clients.all()]
    }

    return success(ret)


@has_data
def users_edit_data(request, **kwargs):
    '''
    Called by users_edit_data/
    Edit user's profile data
    '''
    username = kwargs.get('username', '')
    if not username:
        return fail('Could not get username')

    try:
        obc_user = OBC_user.objects.get(user__username=username)
    except ObjectDoesNotExist as e:
        return fail('Could not find user with this username')


    obc_user.first_name = kwargs.get('profile_firstname', '')
    obc_user.last_name = kwargs.get('profile_lastname', '')

    website = kwargs.get('profile_website', '')
    if website:
        if not valid_url(website):
            return fail('website is not a valid URL')
    obc_user.website = website

    obc_user.affiliation = kwargs.get('profile_affiliation', '')
    obc_user.public_info = kwargs.get('profile_publicinfo', '')

    #Save edits
    obc_user.save()

    #Confirm by getting new data
    return users_search_3(request, **kwargs)

def users_search_2(
    main_search,
    ):
    '''
    Collect all users from main search
    '''

    username_Q = Q(user__username__icontains=main_search)
    affiliation_Q = Q(affiliation__icontains=main_search)
    publicinfo_Q = Q(public_info__icontains=main_search)

    results = OBC_user.objects.filter(username_Q | affiliation_Q | publicinfo_Q)

    users_search_jstree = []
    for result in results:
        to_add = {
            'data': {'username': result.user.username},
            'text': result.user.username + jstree_icon_html('users'),
            'id': result.user.username,
            'parent': '#',
            'state': { 'opened': True},
        }
        users_search_jstree.append(to_add)

    ret = {
        'main_search_users_number': results.count(),
        'users_search_jstree': users_search_jstree,
    }

    return ret

def get_scheme(request):
    '''
    https://stackoverflow.com/a/36817763/5626738
    http or https ?
    '''
    scheme = 'https' if request.is_secure() else "http"
    return scheme

def get_server_url(request):
    '''
    Get the URL of the server
    '''

    return '{}://{}/platform'.format(get_scheme(request), request.get_host())

def get_execution_clients(request):
    '''
    Get all execution clients of the user
    '''

    if request.user.is_anonymous:
        return []

    obc_user = OBC_user.objects.get(user=request.user)

    ret = list(obc_user.clients.values('parameters', 'name'))

    return ret

def get_execution_clients_angular(request):
    '''
    Angular expects an empty entry at the end
    '''

    return get_execution_clients(request) + [{'name': '', 'parameters': ''}];

### END OF USERS

def index(request, **kwargs):
    '''
    View url: ''
    '''
    #print ('kwargs')
    #print (kwargs)

    context = {}
    context['profile_ORCID'] = None

    # Is this a redirect from Django Social Auth?
    orcid_success = ''
    if (request.method == 'GET' and
        request.GET.get('orcid', '') == 'success' and
        not request.user.is_anonymous):
        # We are redirected from social auth

        # Is it provided by ORCID ?
        profile_ORCID = get_orcid_data(request.user)
        if profile_ORCID:
            context['profile_ORCID'] = profile_ORCID
            orcid_success = 'Successfully linked your account with ORCID'
        else:
            # Is it provided by another plugin ?
            # Is this user logging in or Signing up??
            if OBC_user.objects.filter(user=request.user).exists():
                # Logging in. Do nothing
                orcid_success = 'Successfully logged in'
            else:
                # Signing up. This user does not have a OBC_user object. Create it!
                create_obc_user(user=request.user, email_validation_token=None)
                orcid_success = 'Successfully signed up'


    context['general_alert_message'] = ''
    context['general_success_message'] = ''
    context['LOGIN_BACKEND'] = g.get('LOGIN_BACKEND')
    context['TITLE'] = g.get('TITLE')
    context['TERMS'] = g.get('TERMS')
    context['PRIVACY'] = g.get('PRIVACY')
    context['FUNDING_LOGOS'] = g.get('FUNDING_LOGOS')


    #print (social_core.pipeline.social_auth.social_details)
    #print (social_details())

    # Are we linking to a specific RO?
    init_interlink_args = {}
    # tool linking
    tool_name = kwargs.get('tool_name', '')
    tool_version = kwargs.get('tool_version', '')
    tool_edit = kwargs.get('tool_edit', 0)
    if tool_name and tool_version and tool_edit:
        Qs = [Q(name=tool_name, version=tool_version, edit=int(tool_edit))]
        Qs.extend(get_visibility_Q_objects(request))
        if Tool.objects.filter(*Qs).exists():
            init_interlink_args = {
                'type': 't',
                'name': tool_name,
                'version': tool_version,
                'edit': int(tool_edit),
            }
        else:
            context['general_alert_message'] = 'Tool {}/{}/{} does not exist'.format(tool_name, tool_version, tool_edit)

    # workflow linking
    workflow_name = kwargs.get('workflow_name', '')
    workflow_edit = kwargs.get('workflow_edit', 0)
    if workflow_name and workflow_edit:
        Qs = [Q(name=workflow_name, edit=int(workflow_edit))]
        Qs.extend(get_visibility_Q_objects(request))
        if Workflow.objects.filter(*Qs).exists():
            init_interlink_args = {
                'type': 'w',
                'name': workflow_name,
                'edit': int(workflow_edit),
            }
        else:
            context['general_alert_message'] = 'Workflow {}/{} does not exist'.format(workflow_name, workflow_edit)

    #references linking
    reference_name = kwargs.get('reference_name', '')
    if reference_name:
        if Reference.objects.filter(name__iexact=reference_name).exists():
            init_interlink_args = {
                'type': 'r',
                'name': reference_name,
            }
        else:
            context['general_alert_message'] = 'Reference {} does not exist'.format(reference_name)

    # user linking
    user_username = kwargs.get('user_username', '')
    if user_username:
        if OBC_user.objects.filter(user__username=user_username).exists():
            init_interlink_args = {
                'type': 'u',
                'username': user_username,
            }
        else:
            context['general_alert_message'] = 'User {} does not exist'.format(user_username)

    # comment link
    comment_id = kwargs.get('comment_id', '')
    if comment_id:
        if Comment.objects.filter(pk=int(comment_id)).exists():
            init_interlink_args = {
                'type': 'c',
                'id': int(comment_id),
            }
        else:
            context['general_alert_message'] = 'Comment with id={} does not exist'.format(comment_id)

    # Report link
    report_run = kwargs.get('report_run', '')
    if report_run:
        if Report.objects.filter(nice_id=report_run).exists():
            init_interlink_args = {
                'type': 'report',
                'run': report_run,
            }
        else:
            context['general_alert_message'] = 'Report {} does not exist'.format(report_run)

    context['init_interlink_args'] = simplejson.dumps(init_interlink_args)


    # Is this user already logged in?
    # https://stackoverflow.com/questions/4642596/how-do-i-check-whether-this-user-is-anonymous-or-actually-a-user-on-my-system
    if request.user.is_anonymous:
        #print ('User is anonumous')
        username = ''
    else:
        username = request.user.username
        #print ('Username: {}'.format(username))

    context['username'] = username
    context['password_reset_token'] = ''
    context['reset_signup_username'] = ''
    context['reset_signup_email'] = ''

    # Get orcid_id
    if username and not context['profile_ORCID']:
        context['profile_ORCID'] = get_orcid_data(request.user)

    #Check for GET variables
    GET = request.GET

    # EMAIL VALIDATION
    validation_token = GET.get('validation_token', '')
    if validation_token:
        validation_success, validation_message = validate_user(validation_token)
        if validation_success:
            context['general_success_message'] = validation_message
        else:
            context['general_alert_message'] = validation_message

    #Is user validated
    context['user_is_validated'] = user_is_validated(request)

    # PASSWORD RESET
    password_reset_token = GET.get('password_reset_token', '')
    context['password_reset_token'] = '' # It will be set after checks
    if password_reset_token:
        password_reset_check_success, password_reset_check_message, obc_user = password_reset_check_token(password_reset_token)
        if password_reset_check_success:
            context['password_reset_token'] = password_reset_token
            context['reset_signup_username'] = obc_user.user.username
            context['reset_signup_email'] = obc_user.user.email
        else:
            context['general_alert_message'] = password_reset_check_message

    # Show warning when running in default Django port
    port = int(request.META['SERVER_PORT'])
    if settings.DEBUG:
        # Running with DEBUG True
        if port == 8000:
            logger.warning('WARNING: YOU ARE RUNNING IN DEFAULT DJANGO PORT (8000)')
        if port != g['DEFAULT_DEBUG_PORT']:
            logger.warning(f'WARNING: You are not runining on port {g["DEFAULT_DEBUG_PORT"]}')
    context['debug'] = settings.DEBUG # If this is True, then we include tests.js

    # Add port information or other insrtance settings on template
    instance_settings = get_instance_settings()
    context['port'] = instance_settings['port']
    context['controller_url'] = instance_settings['controller_url']

    # Get OS choices
    context['os_choices'] = simplejson.dumps(OS_types.get_angular_model())

    # Get User clients
    context['profile_clients'] = get_execution_clients_angular(request)

    # Is this a redirect from ORCID ?
    context['orcid_success'] = orcid_success

    # Add version
    context['version'] = __version__

    return render(request, 'app/index.html', context)


def create_obc_user(*, user, email_validation_token):
    '''
    '''
    #If we are running in DEBUG, then new users are validated. If we set this to False then we need a send mail service to testing platform
    #In production new users are not validated by default

    obc_user = OBC_user(user=user, email_validated=bool(settings.DEBUG), email_validation_token=email_validation_token)
    obc_user.save()

@has_data
def register(request, **kwargs):
    '''
    View url: 'register/'
    add user add
    '''

    if not 'signup_username' in kwargs:
        return fail('username is required')
    signup_username = kwargs['signup_username']

    if not re.match(r'^\w+$', signup_username):
        return fail('username can only contain alphanumeric characters')

    if username_exists(signup_username):
        return fail('username: {} exists already'.format(signup_username))

    if not 'signup_password' in kwargs:
        return fail('password is required')
    signup_password = kwargs['signup_password']

    check_password_success, check_password_message = check_password(signup_password)
    if not check_password_success:
        return fail(check_password_message)

    if not 'signup_confirm_password' in kwargs:
        return fail('confirm password is required')
    signup_confirm_password = kwargs['signup_confirm_password']
    if signup_password != signup_confirm_password:
        return fail('Confirm password does not match password')

    if not 'signup_email' in kwargs:
        return fail('email is required')
    signup_email = kwargs['signup_email'] # https://www.tecmint.com/setup-postfix-mail-server-in-ubuntu-debian/

    ##  Do we allow users with the same email address?
    try:
        OBC_user.objects.get(user__email = signup_email)
    except ObjectDoesNotExist:
        pass # This is ok!
    else:
        # An exception did NOT happen (as it should)
        return fail('A user with this email already exists')

    ## smtplib method
#    try:
#        send_mail(
#            from_=g['EMAIL'],
#            to=signup_email,
#            subject='[{server}] Please confirm your email'.format(server=g['SERVER']),
#            body=confirm_email_body(uuid_token, port=request_port_to_url(request)),
#        )
#    except smtplib.SMTPRecipientsRefused:
#        return fail('Could not sent an email to {}'.format(signup_email))
#    except Exception as e:
#        pass ## FIXME

    ## django send_mail

    suc, error_message, uuid_token = send_validation_email_inner(request, signup_email)
    if not suc:
        return fail(error_message)

    #Create user
    user = User.objects.create_user(signup_username, signup_email, signup_password, last_login=now()) # https://stackoverflow.com/questions/33683619/null-value-in-column-last-login-violates-not-null-constraint/42502311

    #Create OBC_user
    create_obc_user(user=user, email_validation_token=uuid_token)

    return success()

@has_data
def reset_password_email(request, **kwargs):
    if not 'reset_password_email' in kwargs:
        return fail('Please enter an email')

    email = kwargs['reset_password_email']
    try:
        obc_user = OBC_user.objects.get(user__email=email)
    except ObjectDoesNotExist:
        obc_user = None

    if not obc_user:
        return fail('This email does not belong to any user') # Isn't this a breach of privacy?

    # reset_password_email_body

    # Save token
    token = create_uuid_token()
    obc_user.password_reset_token = token
    obc_user.password_reset_timestamp = now()
    obc_user.save()

#    #Send email with SMTPLIB
#    try:
#        send_mail(
#            from_ = g['EMAIL'],
#            to = email,
#            subject = '[{server}] Reset your password'.format(server=g['SERVER']),
#            body = reset_password_email_body(token, port=request_port_to_url(request))
#        )
#    except smtplib.SMTPRecipientsRefused:
#        return fail('Could not send an email to: {}'.format(email))
#    except Exception as e:
#        pass # FIX ME

    # With Django send_mail
    try:
        send_mail(
            '[{server}] Reset your password'.format(server=g['SERVER']), # subject
            reset_password_email_body(token, port=request_port_to_url(request)), # body message
            g['EMAIL'], # from
            [email], # to
        )
    except Exception as e:
        return fail('Could not send email to {email}. Please contact {ADMIN}'.format(email=email, ADMIN=g['ADMIN']))

    return success()

@has_data
def password_reset(request, **kwargs):
    if not 'password_reset_password' in kwargs:
        return fail('password is required')
    password_reset_password = kwargs['password_reset_password']

    if not 'password_reset_confirm_password' in kwargs:
        return fail('confirm password is required')
    password_reset_confirm_password = kwargs['password_reset_confirm_password']

    if password_reset_password != password_reset_confirm_password:
        return fail('Confirm password does not match password')

    check_password_success, check_password_message = check_password(password_reset_password)
    if not check_password_success:
        return fail(check_password_message)

    password_reset_token = kwargs['password_reset_token'] # This should be always present in kwargs

    #Change the password
    obc_user = OBC_user.objects.get(password_reset_token=password_reset_token)
    user = obc_user.user
    user.set_password(password_reset_password) # https://docs.djangoproject.com/en/2.1/topics/auth/default/
    user.save()

    #Invalidate token
    obc_user.password_reset_token = None
    obc_user.save()

    return success()

@has_data
def send_validation_email(request, **kwargs):
    '''
    url: send_validation_email/
    '''

    if request.user.is_anonymous:
        return fail('Error 8912'); # This should never happen

    try:
        obc_user = OBC_user.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return fail('Error 8711'); # This should never happen

    email = request.user.email

    suc, error_message, uuid_token = send_validation_email_inner(request, email)
    if not suc:
        return fail(error_message)

    #Set the validation token
    obc_user.email_validation_token = uuid_token
    obc_user.save()

    #print ('Validation token:', uuid_token)

    ret = {
        'email': request.user.email
    }

    return success(ret)


@has_data
def login(request, **kwargs):
    '''
    View url: 'login/'
    '''

    if not 'login_username' in kwargs:
        return fail('username is required')
    login_username = kwargs['login_username']

    if not 'login_password' in kwargs:
        return fail('password is required')
    login_password = kwargs['login_password']

    user = authenticate(username=login_username, password=login_password)

    if user is None:
        return fail('Invalid username or password')

    django_login(request, user)

    obc_user = OBC_user.objects.get(user=user)

    #print ('LOGIN: user_is_validated', obc_user.email_validated)

    # Since we logged in the csrf token has changed.
    ret = {
        'username': login_username,
        'csrf_token': get_token(request),
        'user_is_validated': obc_user.email_validated,
        'profile_clients': get_execution_clients_angular(request),
    }

    return success(ret)

def logout(request):
    '''
    View url: 'logout/'
    This is NOT called by AJAX
    '''

    django_logout(request)
    return redirect('/platform/')

#def user_data_get(request):
#    '''
#    View url: user_data_get
#    GET THE DATA OF THE LOGGED-IN USER
#    It does not have the @has_data decorator because it has.. no data
#    '''
#
#    user = request.user
#    obc_user = OBC_user.objects.get(user=user)
#    ret = {
#        'user_first_name': obc_user.first_name,
#        'user_last_name': obc_user.last_name,
#        'user_email': user.email,
#        'user_website': obc_user.website,
#        'user_public_info': obc_user.public_info,
#    }
#
#    return success(ret)

#@has_data
#def user_data_set(request, **kwargs):
#    '''
#    Deprecated
#    '''
#    user = request.user
#    obc_user = OBC_user.objects.get(user=user)
#
#    obc_user.first_name = None_if_empty_or_nonexisting(kwargs, 'user_first_name')
#    obc_user.last_name = None_if_empty_or_nonexisting(kwargs, 'user_last_name')
#    obc_user.website = None_if_empty_or_nonexisting(kwargs, 'user_website')
#    obc_user.public_info = None_if_empty_or_nonexisting(kwargs, 'user_public_info')
#
#    obc_user.save()
#
#    return success()

@has_data
def tools_search_1(request, **kwargs):
    '''
    Get tool counts
    NOT CURRENTLY USED!
    '''
    queries = []

    ret = {
        'tools_search_tools_number': Tool.objects.count(),
        'workflows_search_tools_number': Workflow.objects.count(),
    }

    return success(ret)

def is_visibility_allowed(*, obc_user, ro):
    '''
    Return True/False if this user is allowed to see this RO
    '''
    is_public = ro.visibility == str(VisibilityOptions.PUBLIC_CODE)
    if obc_user:
        if not is_public:
            return obc_user == ro.obc_user

    return is_public


def get_visibility_Q_objects(request):
    '''
    See Issue #217
    '''

    obc_user = get_obc_user(request)
    Q1 = Q(visibility = VisibilityOptions.PUBLIC_CODE)

    if not obc_user:
        # If the user is not logged in only public ROs are allowed
        return [Q1]

    Q2 = Q(visibility = VisibilityOptions.PRIVATE_CODE, obc_user = obc_user) # <-- Private ROs that belong to me

    # If user is logged in, then return:
    # (All PUBLIC) OR (PRIVATE that belong to me)
    Q3 = Q(Q1 | Q2)

    return [Q3]


def tools_search_2(tools_search_name, tools_search_version, tools_search_edit, *, request):
    '''
    This is triggered when there is a key-change on the main-search
    '''

    Qs = []
    if tools_search_name:
        Q1 = Q(name__icontains=tools_search_name)
        Q2 = Q(obc_user__user__username__icontains=tools_search_name)
        Qs.append(Q1 | Q2)

    if tools_search_version:
        Qs.append(Q(version__icontains=tools_search_version))

    if tools_search_edit:
        Qs.append(Q(edit = int(tools_search_edit)))

    # Extend with visibility (private/public) filters
    Qs.extend(get_visibility_Q_objects(request))

    # This applies an AND operator. https://docs.djangoproject.com/en/2.2/topics/db/queries/#complex-lookups-with-q-objects
    # For the order_by part see issue #120
    results = Tool.objects.filter(*Qs).order_by('created_at')

    # { id : 'ajson1', parent : '#', text : 'KARAPIPERIM', state: { opened: true} }

    obc_user = get_obc_user(request)

    # Build JS TREE structure
    tools_search_jstree = []
    for x in results:

        # Get the id of the parent
        if x.forked_from and is_visibility_allowed(obc_user=obc_user, ro=x.forked_from):
            parent_id = tool_id_jstree(x.forked_from, g['SEARCH_TOOL_TREE_ID'])
        else:
            parent_id = '#'

        to_add = {
            'data': {'name': x.name, 'version': x.version, 'edit': x.edit},
            'text': tool_node_jstree(x), #  tool_text_jstree(x) + (' <span class="red lighten-3">DRAFT</span>' if x.draft else '') + jstree_icon_html('tools'),
            'id': tool_id_jstree(x, g['SEARCH_TOOL_TREE_ID']),
            'parent':  parent_id,
            'state': { 'opened': True},
        }
        tools_search_jstree.append(to_add)

    ret = {
        'tools_search_tools_number' : results.count(),
        #'tools_search_list': [{'name': x.name, 'version': x.version, 'edit': x.edit} for x in results], # We do not need a list, we need a tree!
        'tools_search_jstree' : tools_search_jstree,
    }

    return ret

def workflows_search_2(workflows_search_name, workflows_search_edit, *, request):
    '''
    Called by all_search_2
    '''

    Qs = []
    #workflows_search_name = kwargs.get('workflows_search_name', '')
    if workflows_search_name:
        Q1 = Q(name__icontains=workflows_search_name)
        Q2 = Q(obc_user__user__username__icontains=workflows_search_name)
        Qs.append(Q1 | Q2)

    #workflows_search_edit = kwargs.get('workflows_search_edit', '')
    if workflows_search_edit:
        Qs.append(Q(edit = int(workflows_search_edit)))

    # Extend with visibility (private/public) filters.
    Qs.extend(get_visibility_Q_objects(request))


    # For the order_by part see issue #120
    results = Workflow.objects.filter(*Qs).order_by('created_at')

    obc_user = get_obc_user(request)

    # Build JS TREE structure
    workflows_search_jstree = []
    for x in results:

        # Get the id of the parent
        if x.forked_from and is_visibility_allowed(obc_user=obc_user, ro=x.forked_from):
            parent_id = workflow_id_jstree(x.forked_from, g['SEARCH_WORKFLOW_TREE_ID'])
        else:
            parent_id = '#'

        to_add = {
            'data': {'name': x.name, 'edit': x.edit},
            'text': workflow_node_jstree(x),
            'id': workflow_id_jstree(x, g['SEARCH_WORKFLOW_TREE_ID']),
            'parent': parent_id,
            'state': { 'opened': True},
        }
        workflows_search_jstree.append(to_add)


    ret = {
        'workflows_search_tools_number' : results.count(),
        'workflows_search_jstree' : workflows_search_jstree,
    }

    return ret

@has_data
def tools_search_3(request, **kwargs):
    '''
    Triggered when a tool is clicked on the tool-search-jstree
    '''

    tool_name = kwargs.get('tool_name', '')
    tool_version = kwargs.get('tool_version', '')
    tool_edit = int(kwargs.get('tool_edit', -1))

    tool = Tool.objects.get(name__iexact=tool_name, version__iexact=tool_version, edit=tool_edit)

    obc_user = get_obc_user(request)

    if not is_visibility_allowed(obc_user=obc_user, ro=tool):
        return fail('This tool is private.')

    #Get the dependencies of this tool and build a JSTREE
    tool_dependencies_jstree = []
    for dependency in tool.dependencies.all():
        dependency_js_tree = tool_build_dependencies_jstree(tool_get_dependencies_internal(dependency, include_as_root=True))
        tool_dependencies_jstree.extend(dependency_js_tree)

    #Get the dependencies of this tool AND the variables and build a JSTREE
    #FIXME: Duplicate code
    tool_variables_jstree = []
    for dependency in tool.dependencies.all():
        variables_js_tree = tool_build_dependencies_jstree(tool_get_dependencies_internal(dependency, include_as_root=True), add_variables=True)
        tool_variables_jstree.extend(variables_js_tree)

    #print ('LOGGG DEPENDENIES + VARIABLES')
    #print (tool_variables_jstree)
    #print (simplejson.dumps(tool_variables_jstree, indent=4))

    #Get the variables of this tool
    tool_variables = []
    for variable in tool.variables.all():
        tool_variables.append({'name': variable.name, 'value': variable.value, 'description': variable.description})


    #Is it voted?
    if obc_user:
        try:
            v = UpDownToolVote.objects.get(obc_user=obc_user, tool=tool)
        except ObjectDoesNotExist as e:
            # It is not voted
            tool_voted = {'up': False, 'down': False}
        else:
            # It is noted
            tool_voted = {'up': v.upvote, 'down': not v.upvote}

    else:
        tool_voted = {'up': False, 'down': False}

    ret = {
        'website': tool.website,
        'description': tool.description,
        'description_html': tool.description_html,
        'username': tool.obc_user.user.username,
        'created_at': datetime_to_str(tool.created_at),
        'forked_from': tool_to_json(tool.forked_from),
        'changes': tool.changes,

        'tool_keywords': [keyword.keyword for keyword in tool.keywords.all()],

        'dependencies_jstree': tool_dependencies_jstree,
        'variables_jstree': tool_variables_jstree,

        'variables': tool_variables,
        'tool_os_choices': OS_types.get_angular_model([x.os_choices for x in tool.os_choices.all()]),
        'installation_commands': tool.installation_commands,
        'validation_commands': tool.validation_commands,

        'validation_status': tool.last_validation.validation_status if tool.last_validation else 'Unvalidated',
        'visibility': VisibilityOptions.VISIBILITY_OPTIONS_CODE_dic[tool.visibility],
        # Show stdout, stderr and error code when the tool is clicked on the tool-search-jstree
        'stdout' : tool.last_validation.stdout if tool.last_validation else None,
        'stderr' : tool.last_validation.stderr if tool.last_validation else None,
        'errcode' : tool.last_validation.errcode if tool.last_validation else None,
        'validation_created_at' : datetime_to_str(tool.last_validation.created_at) if tool.last_validation else None,
        'tool_pk': tool.pk, # Used in comments
        'tool_thread': qa_create_thread(tool.comment, obc_user), # Tool comment thread. This is a list
        'tool_score': tool.upvotes - tool.downvotes,
        'tool_voted': tool_voted,
        'tool_comment_id': tool.comment.pk, # Used to create a permalink to the comments
        'tool_comment_title': tool.comment.title,
        'tool_comment_created_at': datetime_to_str(tool.comment.created_at),
        'tool_comment_username': tool.comment.obc_user.user.username,

        'draft': tool.draft,


    }

    #print ('LOGGG DEPENDENCIES + VARIABLES')
    #print (simplejson.dumps(tool_variables_jstree, indent=4))

    return success(ret)

@has_data
def tool_get_dependencies(request, **kwargs):
    '''
    Get the dependencies of this tool
    Called when a stop event (from dnd) happens from search JSTREE to the dependencies JSTREE
    OR from a stop event from search jstree to cytoscape graph

    what_to_do == 1: drag and drop FROM SEARCH TREE TO DEPENDENCY TREE
    what_to_do == 2: drag and drop FROM SEARCH TREE TO CYTOSCAPE CYWORKFLOW DIV
    '''

    tool_name = kwargs.get('tool_name', '')
    tool_version = kwargs.get('tool_version', '')
    tool_edit = int(kwargs.get('tool_edit', -1))
    what_to_do = kwargs.get('what_to_do', None)

    if not what_to_do:
        return fail('Error 9122')

    try:
        what_to_do = int(what_to_do)
    except ValueError as e:
        return fail('Error 9123')

    tool = Tool.objects.get(name=tool_name, version=tool_version, edit=tool_edit)

    #Get the dependencies of this tool
    tool_dependencies = tool_get_dependencies_internal(tool, include_as_root=True)
    tool_dependencies_jstree = tool_build_dependencies_jstree(tool_dependencies, add_installation_commands=what_to_do==2)

    #Get the dependencies + variables of this tool
    tool_variables_jstree = tool_build_dependencies_jstree(tool_dependencies, add_variables=True)

    #print ('LOGGG DEPENDENCIES')
    #print (simplejson.dumps(tool_dependencies_jstree, indent=4))

    #print ('LOGGG DEPENDENCIES + VARIABLES')
    #print (simplejson.dumps(tool_variables_jstree, indent=4))

    # There is $scope.tools_dep_jstree_model and $scope.tools_var_jstree_model
    ret = {
        'dependencies_jstree': tool_dependencies_jstree,
        'variables_jstree': tool_variables_jstree,
    }

    return success(ret)

def validate_toast_button():
    '''
    This button should be similar with the one generated from angular
    '''
    return '<button class="waves-effect waves-light btn red lighten-3 black-text" onclick="window.OBCUI.send_validation_mail()">Validate</button>'

def validate_visibility(ro_visibilty):
    '''
    Get the visibility value from the frontend and validate.
    Return the corresponding visibility code from the model
    '''

    if not ro_visibilty in VisibilityOptions.VISIBILITY_OPTIONS_NAME_dic:
        return 'Error 8751 invalid visibility value'
    return VisibilityOptions.VISIBILITY_OPTIONS_NAME_dic[ro_visibilty]

@has_data
def tools_add(request, **kwargs):
    '''
    Add a new tool
    tool add tool save tool . Create tool tools add
    tool edit tool

    * names and version is searched case insensitive
    '''

    if request.user.is_anonymous: # Server should always check..
        return fail('Please login to create new tools')

    if not user_is_validated(request):
        return fail('Please validate your email to create new tools ' + validate_toast_button())

    obc_user = OBC_user.objects.get(user=request.user)

    tool_website = kwargs.get('tool_website', '')
    #if not tool_website:
    #    return fail('Website cannot be empty') # Website CAN be empty

    if tool_website:
        if not valid_url(tool_website):
            return fail('Website is not a valid URL')

    tool_description = kwargs.get('tool_description', '')
    if not tool_description:
        return fail('Description cannot be empty')

    tool_description_html = markdown(tool_description)

    tools_search_name = kwargs.get('tools_search_name', '')
    if not tools_search_name:
        return fail('Invalid name')

    tools_search_version = kwargs.get('tools_search_version', '')
    if not tools_search_version:
        return fail('Invalid version')

    tool_edit_state = kwargs.get('tool_edit_state', '')
    if tool_edit_state in {'False', 'false'}:
        tool_edit_state = False
    elif tool_edit_state in {'True', 'true'}:
        tool_edit_state = True
    if not type(tool_edit_state) is bool:
        return fail('Error 8715. Tool edit state has not been set')

    tool_visibility = kwargs.get('tool_visibility', '')
    visibility_code = validate_visibility(tool_visibility)
    if type(visibility_code) is str:
        return fail(visibility_code)

    #Dependencies
    if not 'tool_dependencies' in kwargs:
        return fail('Error 8777. Could not find tool dependencies.')
    tool_dependencies = kwargs['tool_dependencies']

    #Check that dependencies are will formed 
    tool_dependencies_objects = []
    for t in tool_dependencies:
        if not 'name' in t:
            return fail('Dependency does not contain name field')
        if not 'version' in t:
            return fail('Dependency does not contain version field')
        if not 'edit' in t:
            return fail('Dependency does not contain edit field')

        # FIXME! What if a dependency is deleted???
        tool_dependencies_objects.append(Tool.objects.get(name=t['name'], version=t['version'], edit=int(t['edit'])))


    #If this is a public tool check that all tool dependencies are public as well
    if visibility_code == VisibilityOptions.PUBLIC_CODE:
        for tool_dependencies_object in tool_dependencies_objects:
            if tool_dependencies_object.visibility != str(VisibilityOptions.PUBLIC_CODE):
                return fail(f'This tool depends from the private tool: {tool_dependencies_object}. Cannot create a public tool with private dependencies.')
                ### TEST 217_create_public_tool_with_private_dependency PYT: test_217_create_public_tool_with_private_dependency()

    upvoted = False
    downvoted = False
    tool_forked_from = None
    tool_changes = None
    if tool_edit_state:
        # We are editing this tool!

        # Get the edit of the tool
        tools_search_edit = kwargs.get('tools_search_edit', '')
        if not tools_search_edit:
            return fail('Invalid tool edit number. Error 8712')
        try:
            tools_search_edit = int(tools_search_edit)
        except ValueError as e:
            return fail('Invalid tool edit number. Error 8713')
        except Exception as e:
            return fail('Invalid tool edit number. Error 8714')


        # Get the previous object
        try:
            tool = Tool.objects.get(name=tools_search_name, version=tools_search_version, edit=tools_search_edit)
        except ObjectDoesNotExist as e:
            return fail('Error 8716')

        #Are we converting from public to private?
        if tool.visibility == str(VisibilityOptions.PUBLIC_CODE) and tool_visibility == VisibilityOptions.PRIVATE_NAME:
            # We are about to make this public tool, private
            # Make sure that there isn't any public tool that depends from this tool
            first = tool.dependencies_related.filter(visibility=str(VisibilityOptions.PUBLIC_CODE)).first()
            if first:
                return fail(f'Cannot make this tool private. Tool {tool} depends from this tool and is public.')
                ### TEST  217_convert_from_public_to_private_tool_that_is_a_dependency_to_public_tool PYT: test_217_convert_from_public_to_private_tool_that_is_a_dependency_to_public_tool

            # Make sure that there isn't any public workflow that contains this tool
            first = Workflow.objects.filter(tools__in = [tool], visibility=str(VisibilityOptions.PUBLIC_CODE)).first()
            if first:
                return fail(f'Cannot make this tool private. Workflow {first} contains this Tool and is public.')
                ### TEST 217_convert_from_public_to_private_tool_that_exists_in_public_wf PYT: test_217_convert_from_public_to_private_tool_that_exists_in_public_wf

        #Are we converting from private to public?
        if tool.visibility == str(VisibilityOptions.PRIVATE_CODE) and tool_visibility == VisibilityOptions.PUBLIC_NAME:
            # We are about to make this private tool, public
            # Does it contain any private dependency?
            first = tool.dependencies.filter(visibility=str(VisibilityOptions.PRIVATE_CODE)).first()
            if first:
                return fail(f'Cannot make this tool public. It depends from the private tool: {first}')
                # Actually we never end up here. Check:
                ### TEST 217_convert_from_private_to_public_tool_has_a_private_dependency PYT: test_217_convert_from_private_to_public_tool_has_a_private_dependency

        # Check that the user who created this tool is the one who deletes it!
        if tool.obc_user != obc_user:
            return fail('Error 8717') # This is strange.. The user who edits this tool is not the one who created it???

        # Store a reference to the comment
        comment = tool.comment

        # Store upvotes/downvotes
        upvotes = tool.upvotes
        downvotes = tool.downvotes

        # Store vote objects
        votes = UpDownToolVote.objects.filter(tool=tool)
        # Disassociate from this tool (this is allowed because null=true)
        for vote in votes:
            if vote.obc_user == obc_user:
                upvoted = vote.upvote
                downvoted = not upvoted

            vote.tool = None
            vote.save()

        # Get the tools that are forks of this tool
        tool_forks = Tool.objects.filter(forked_from=tool)
        # Temporary set that these tools are not forked from any tool
        for tool_fork in tool_forks:
            tool_fork.forked_from = None
            tool_fork.save()

        # Get the tool that this tool is forked from
        tool_forked_from = tool.forked_from

        # Get the tools that depend from this tool
        tools_depending_from_me = tool.dependencies_related.all()
        tools_depending_from_me_list = list(tools_depending_from_me) # We need to add a reference to these object. Otherwise it will be cleared after we delete tool

        # Get the created at. It needs to be sorted according to this, otherwise the jstree becomes messy
        tool_created_at = tool.created_at

        # Get the workflows that use this tool
        workflows_using_this_tool = Workflow.objects.filter(tools__in = [tool])

        # Remove this tool from these workflows
        for workflow_using_this_tool in workflows_using_this_tool:
            workflow_using_this_tool.tools.remove(tool)
            workflow_using_this_tool.save()

        # Delete it!
        tool.delete()

    else:
        upvotes = 0
        downvotes = 0

    #os_type Update
    tool_os_choices = kwargs.get('tool_os_choices',[])
    if not tool_os_choices:
        return fail('Please select at least one operating system')

    #print ('Operating Systems:')
    #print (tool_os_choices)

    # If we are editing this tool, set the same edit number
    # Otherwise get the maximum edit
    if tool_edit_state:
        next_edit = tools_search_edit
    else:
        #Get the maximum edit
        tool_all = Tool.objects.filter(name__iexact=tools_search_name, version__iexact=tools_search_version) # https://docs.djangoproject.com/en/dev/ref/models/querysets/#std:fieldlookup-iexact
        if not tool_all.exists():
            next_edit = 1
        else:
            max_edit = tool_all.aggregate(Max('edit'))
            next_edit = max_edit['edit__max'] + 1

    # Get forked from and edit summary
    tool_forked_from_info = kwargs.get('tool_forked_from', None)
    if tool_forked_from_info:

        tool_forked_from = Tool.objects.get(name=tool_forked_from_info['name'], version=tool_forked_from_info['version'], edit=int(tool_forked_from_info['edit']))
        tool_changes = kwargs.get('tool_changes', '')
        if not tool_changes:
            return fail('Edit summary cannot be empty')

    else:
        pass # Do nothing

    #Installation/Validation commands
    try:
        tool_installation_commands = kwargs['tool_installation_commands']
    except KeyError:
        return fail('Error 8778. Could not find tool_installation_commands field.')

    try:
        tool_validation_commands = kwargs['tool_validation_commands']
    except KeyError:
        return fail('Error 8779. Could not find tool_validation_commands field.')

    #Variables
    try:
        tool_variables = kwargs['tool_variables']
    except KeyError:
        return fail('Error 8780. Could not find tool_variables field')
    tool_variables = [x for x in tool_variables if x['name'] and x['value'] and x['description']] # Filter out empty fields

    # Check that variables do not have the same name
    for variable_name, variable_name_counter in Counter([x['name'] for x in tool_variables]).items():
        if variable_name_counter>1:
            return fail('Two variables cannot have the same name!')


    #Create new tool
    new_tool = Tool(
        obc_user= obc_user,
        name = tools_search_name,
        version=tools_search_version,
        edit=next_edit,
        website = tool_website,
        description = tool_description,
        description_html = tool_description_html,
        forked_from = tool_forked_from,
        changes = tool_changes,
        installation_commands=tool_installation_commands,
        validation_commands=tool_validation_commands,
        upvotes = upvotes,
        downvotes = downvotes,
        draft = True, # By defaut all new tools are draft
        visibility = visibility_code,
        last_validation=None,
    )

    #Save it
    new_tool.save()

    if tool_edit_state:
        # Preserve the created at date. We have to do that AFTER the save! https://stackoverflow.com/questions/7499767/temporarily-disable-auto-now-auto-now-add
        # If we do not preserve the created at, then the jstree becomes messy.
        new_tool.created_at = tool_created_at
        new_tool.save()

    #Add dependencies
    if tool_dependencies_objects:
        new_tool.dependencies.add(*tool_dependencies_objects)
        new_tool.save()

    #Add Variables
    if tool_variables:
        variable_objects = []
        for variable in tool_variables:
            variable_object = Variables(name=variable['name'], value=variable['value'], description=variable['description'], tool=new_tool)
            variable_object.save()
            variable_objects.append(variable_object)

        new_tool.variables.add(*variable_objects)
        new_tool.save()

    #Add os type
    for tool_os_choice in tool_os_choices:
        OS_types_obj, created = OS_types.objects.get_or_create(os_choices=tool_os_choice['value'])
        new_tool.os_choices.add(OS_types_obj)
    new_tool.save()

    #Add keywords
    try:
        keywords = [Keyword.objects.get_or_create(keyword=keyword)[0] for keyword in kwargs['tool_keywords']]
    except KeyError:
        return fail('Error 8781. Could not find tool_keywords field.')
    new_tool.keywords.add(*keywords)
    new_tool.save()

    if tool_edit_state:
        # Add the votes from the previous edit
        for vote in votes:
            vote.tool = new_tool
            vote.save()

        # Add the tools that were forked from this tool (that was deleted before) to the new tool
        for tool_fork in tool_forks:
            tool_fork.forked_from = new_tool
            tool_fork.save()

        # To the tools depending from me, add this tool to dependencies!
        for tool_depending_from_me in tools_depending_from_me_list:
            tool_depending_from_me.dependencies.add(new_tool)
            #print ('Add {} as a dependency to {}'.format(new_tool, tool_depending_from_me))
            tool_depending_from_me.save()

        # Add to the workflows that were using this tool, the new tool
        for workflow_using_this_tool in workflows_using_this_tool:
            workflow_using_this_tool.tools.add(new_tool)
            workflow_using_this_tool.save()

        # Update the json graph of the workflows using this tool
        WJ = WorkflowJSON()
        WJ.update_tool(new_tool)

    else:
        #Add an empty comment. This will be the root comment for the QA thread
        comment = Comment(
            obc_user = OBC_user.objects.get(user=request.user),
            comment = '',
            comment_html = '',
            title = markdown('Discussion on Tool: t/{}/{}/{}'.format(tools_search_name, tools_search_version, next_edit)),
            parent = None,
            upvotes = 0,
            downvotes = 0,
        )
        comment.save()

    new_tool.comment = comment
    new_tool.save()

    ret = {
        'description_html': tool_description_html,
        'edit': next_edit,
        'created_at': datetime_to_str(new_tool.created_at),

        'tool_pk': new_tool.pk, # Used in comments
        'tool_thread': qa_create_thread(new_tool.comment, obc_user), # Tool comment thread
        'score': upvotes-downvotes,
        'voted': {'up': upvoted, 'down': downvoted},
    }

    return success(ret)


class WorkflowJSON:
    '''
    Basically a function collection for dealing with the workflows json object
    '''

    def update_workflow(self, workflow):
        '''
        workflow is a database Workflow opbject
        '''
        self.workflow = workflow
        self.key = workflow_id_cytoscape(self.workflow, None, None)
        self.graph = simplejson.loads(self.workflow.workflow)
        self.all_ids = {node['data']['id'] for node in self.graph['elements']['nodes']} # All node ids
        self.workflows_using_me = Workflow.objects.filter(workflows__in = [self.workflow])
        self.belongto, self.workflow_nodes = self.__build_workflow_belongto(self.graph)
        self.__update_workflow()

    def update_tool(self, tool):
        '''
        tool is a database Tool object
        '''
        self.tool = tool
        self.graph = self.__create_cytoscape_graph_from_tool_dependencies(self.tool)
        self.all_ids = {node['data']['id'] for node in self.graph['elements']['nodes']} # All node ids
        self.workflows_using_me = Workflow.objects.filter(tools__in = [self.tool])
        self.key = tool_id_cytoscape(self.tool)
        self.__update_tool()

    def __iter_workflows(self, graph):
        '''
        '''
        for element in graph['elements']['nodes']:
            if element['data']['type'] == 'workflow':
                yield element



    def __build_workflow_belongto(self, graph):
        '''
        Create dictionaries:
        self.belongto
        Keys: workflow tuple (name, edit)
        Value: The workflow element where this workflow belongs to

        self.workflow_nodes
        Keys: workflow tuple
        Value: The workflow element
        '''


        all_workflows = list(self.__iter_workflows(graph))

        workflow_nodes = {workflow_element['data']['id'] : workflow_element for workflow_element in all_workflows}

        belongto = {}
        for workflow_element in all_workflows:
            workflow_key = workflow_element['data']['id']
            if workflow_element['data']['belongto']:
                belongto[workflow_key] = workflow_nodes[workflow_id_cytoscape(workflow_element['data']['belongto'], None, None)]
            else:
                belongto[workflow_key] = None

        return belongto, workflow_nodes

    def __build_edges_dict(self, graph):
        '''
        Create a dictionary 's': source, 't': target
        Keys are node ids
        Values are a set containing all the nodes that there is an edge
        '''

        ret = {
            's' : defaultdict(set),
            't' : defaultdict(set),
        }
        for edge in graph['elements']['edges']:
            ret['s'][edge['data']['source']].add(edge['data']['target'])
            ret['t'][edge['data']['target']].add(edge['data']['source'])

        return ret

    def __tool_dependencies(self, tool_node, all_nodes, edges):
        '''
        Edge A --> B: Tool A has dependency B . Or else, A depends from B. Or else first install B then A
        Return a set of all tool ids that belong to the dependencies of a tool (tool_node)

        tool_node: The tool node in a workflow cy
        all_nodes: A list of all nodes of a workflow cy
        edges: The object returned from self.__build_edges_dict
        '''

        ret = set()
        #print ('tool_node:', tool_node)
        #print ('Edge set:', edges)

        def recurse(rec_tool_node):
            tool_id = rec_tool_node['data']['id']

            for target_id in edges['s'][tool_id]:
                target_node = all_nodes[target_id]

                if not target_node['data']['type'] == 'tool':
                    continue

                # This is a tool. There exist an edge rec_tool_node --> target_node. This means that rec_tool_node dependes from target_node
                if not target_id in ret:
                    ret.add(target_id)
                    recurse(target_node)

        #print ('set 2:', ret)

        recurse(tool_node)
        ret.add(tool_node['data']['id'])

        return ret

    def __create_cytoscape_graph_from_tool_dependencies(self, tool):
        '''
        tool is a database object.
        Return a workflow cytoscape worflow. It does not contain the workflow node!

        tool_depending_from_me=None
        '''

        all_ids = set()
        workflow = {
            'elements': {
                'nodes': [],
                'edges': [],
            }
        }

        this_tool_cytoscape_node = tool_node_cytoscape(tool)
        workflow['elements']['nodes'].append(this_tool_cytoscape_node)

        # FIXME !!! DUPLICATE CODE
        root_tool_all_dependencies = tool_get_dependencies_internal(tool, include_as_root=False)
        for root_tool_all_dependency in root_tool_all_dependencies:
            # For each dependency create a cytoscape node
            cytoscape_node = tool_node_cytoscape(root_tool_all_dependency['dependency'], tool_depending_from_me=root_tool_all_dependency['dependant'])
            if not cytoscape_node['data']['id'] in all_ids: # An id should exist only once in the graph... FIXME!! all_ids is always empty!
                workflow['elements']['nodes'].append(cytoscape_node)

                # Connect this tool with its dependent tool node
                if root_tool_all_dependency['dependant']:
                    workflow['elements']['edges'].append(edge_cytoscape(tool_node_cytoscape(root_tool_all_dependency['dependant']), cytoscape_node))
                else:
                    # This tool does not have a dependant!
                    # This is a dependency of the root tool!
                    workflow['elements']['edges'].append(edge_cytoscape(this_tool_cytoscape_node, cytoscape_node))

        return workflow


    def __node_belongs_to_a_workflow(self, node, workflow, workflow_nodes):
        '''
        Recursive
        '''

        if not node: # We are running this for ALL workflow nodes. Including the root workflow that its belongto to is None
            return False

        # We reached the root
        if not node['data']['belongto']:
            return False

        workflow_key = workflow['data']['id']
        node_belongto_key = workflow_id_cytoscape(node['data']['belongto'], None, None)
        #print ('Checking: {} == {}'.format(workflow_key, node_belongto_key))
        if workflow_key == node_belongto_key:
            return True

        # This node does not belong to this workflow. Perhaps the node-->belongto workflow belongs to this workflow
        return self.__node_belongs_to_a_workflow(workflow_nodes[node_belongto_key], workflow, workflow_nodes)


    def __nodes_belonging_to_a_workflow(self, graph, workflow_node, workflow_nodes):
        '''
        Returns a set
        '''

        ret = {element['data']['id'] for element in graph['elements']['nodes']
            if self.__node_belongs_to_a_workflow(element, workflow_node, workflow_nodes)}
        ret.add(workflow_node['data']['id']) # Add the workflow node as well

        return ret

    def __remove_nodes_edges(self, graph, node_ids_to_remove, node_ids_to_add):
        '''
        CRITICAL: A mistake here could produce a corrupted graph..
        '''

        # Determine which edges should be removed
        edge_ids_to_remove = set()
        for edge in graph['elements']['edges']:
            source_id = edge['data']['source']
            target_id = edge['data']['target']
            edge_id = edge['data']['id']
            source_id_in = source_id in node_ids_to_remove
            target_id_in = target_id in node_ids_to_remove

            # This is an edge from inside to inside. Remove it
            if source_id_in and target_id_in:
                edge_ids_to_remove.add(edge_id)
                continue

            # This is an edge from inside to outside
            # Also, on the new workflow, the inside node does not exist!
            # Se we are removing the edge. This might render the workflow useless, but not corrupted!
            if source_id_in and not target_id_in:
                if not source_id in node_ids_to_add:
                    edge_ids_to_remove.add(edge_id)
                continue

            # Same as before but the edge is from outside to inside
            if not source_id_in and target_id_in:
                if not target_id in node_ids_to_add:
                    edge_ids_to_remove.add(edge_id)

        # Remove edges
        graph['elements']['edges'] = [edge for edge in graph['elements']['edges'] if not edge['data']['id'] in edge_ids_to_remove]

        # Remove nodes
        graph['elements']['nodes'] = [node for node in graph['elements']['nodes'] if not node['data']['id'] in node_ids_to_remove]

    def __consistency_check_graph_model(self, graph, workflow):
        '''
        Whenever we update the graph of a workflow, we have to make sure that all tools/workflows that this graph has, do exist in the model
        We also need to check the opposite: All tools/workflows that exist in the model also exist in the graph
        '''

        workflow_using_me_tools = workflow.tools.all()
        tools_found = {str(t): [False, t] for t in workflow_using_me_tools}

        workflow_using_me_workflow = workflow.workflows.all()
        workflows_found = {str(w): [False, w] for w in workflow_using_me_workflow}

        for node in graph['elements']['nodes']:
            if node['data']['type'] == 'tool':
                if node['data']['disconnected']:
                    continue

                # This is a tool does it exist in the model?
                this_tool = Tool.objects.get(name=node['data']['name'], version=node['data']['version'], edit=node['data']['edit'])
                if not workflow_using_me_tools.filter(pk=this_tool.pk).exists():
                    # This tools does not exist in the model but exists on the graph. Add it!
                    workflow.tools.add(this_tool)
                else:
                    tools_found[str(this_tool)][0] = True

            if node['data']['type'] == 'workflow':
                if node['data']['disconnected']:
                    continue

                if not node['data']['belongto']:
                    continue # Do not connect the root workflow

                this_workflow = Workflow.objects.get(name=node['data']['name'], edit=node['data']['edit'])
                if not workflow_using_me_workflow.filter(pk=this_workflow.pk).exists():
                    # This workflow does not exist in the model but exists on the graph. Add it!
                    workflow.workflows.add(this_workflow)
                else:
                    workflows_found[str(this_workflow)][0] = True

        workflow.save()

        # Is there any tool that exist on the model, but it does not exist on the graph?
        for tool_id, (exists, this_tool) in tools_found.items():
            if not exists:
                # This tool exists on the model but not in the graph. REMOVE IT!
                workflow.tools.remove(this_tool)

        # Is there any workflow that exists on the model, but it does not exist on the graph?
        for workflow_id, (exists, this_workflow) in workflows_found.items():
            if not exists:
                # Remove this workflow from the model
                workflow.workflows.remove(this_workflow)

        workflow.save()


    def __update_workflow_node(self, workflow_node, workflow_object):
        '''
        Update a workflow node according to the data from the workflow_object
        '''
        workflow_node['data']['draft'] = workflow_object.draft

    def __update_workflow(self,):
        '''
        update this workflow
        '''

        self.__update_workflow_node(self.workflow_nodes[self.key], self.workflow)
        self.workflow.workflow = simplejson.dumps(self.graph)
        self.workflow.save()


        # Update also the workflows that are using me
        for workflow_using_me in self.workflows_using_me:

            #print ('workflow using me:', workflow_using_me)

            graph = simplejson.loads(workflow_using_me.workflow)
            belongto, workflow_nodes = self.__build_workflow_belongto(graph)

            # Get the workflow that the workflow that we want to update belongs to
            belongto_root = belongto[self.key]
            #print ('   belongto_root: ', belongto_root)

            # Get the workflow node that we want to update
            workflow_node_root = workflow_nodes[self.key]
            #print ('   Workflow node root:', workflow_node_root)

            # This is a set of all the nodes that this sub-workflow has
            workflow_nodes_set = self.__nodes_belonging_to_a_workflow(graph, workflow_node_root, workflow_nodes)
            #print ('  workflow nodes set:', workflow_nodes_set)

            # Remove these nodes (and edges connected to them) from the graph
            self.__remove_nodes_edges(graph, workflow_nodes_set, self.all_ids)

            #print ('The graph after removing of nodes edges:')
            #print (simplejson.dumps(graph, indent=4))

            # Add the edges of this graph
            graph['elements']['edges'].extend(self.graph['elements']['edges'])

            # Add the nodes of this graph
            # Make sure that any main step becomes sub_main
            nodes_to_add = self.graph['elements']['nodes']
            for node in nodes_to_add:
                if node['data']['type'] == 'step':
                    if node['data']['main']:
                        node['data']['main'] = False
                        node['data']['sub_main'] = True

            graph['elements']['nodes'].extend(nodes_to_add)

            # Update the belongto info on the root workflow node. We cannot use the belongto and workflow_nodes any more
            workflow_node_root = [node for node in graph['elements']['nodes'] if node['data']['id'] == self.key][0]
            workflow_node_root['data']['belongto'] = {'name': belongto_root['data']['name'] , 'edit': belongto_root['data']['edit']}

            # Update the root workflow node
            self.__update_workflow_node(workflow_node_root, self.workflow)

            # Save the graph
            workflow_using_me.workflow = simplejson.dumps(graph)
            workflow_using_me.save()

            # Check graph <--> model consistency
            self.__consistency_check_graph_model(graph, workflow_using_me)

    def __update_tool(self,):
        '''
        '''

        # Update all the workflows who are using this tool
        for workflow_using_me in self.workflows_using_me:

            #print ('The graph of this tool:')
            #print (simplejson.dumps(self.graph, indent=4))

            #print ('Workflow using me:', workflow_using_me.name, workflow_using_me.edit)

            graph = simplejson.loads(workflow_using_me.workflow)

            #print ('   The workflow graph:')
            #print (simplejson.dumps(graph, indent=4))

            all_nodes = {node['data']['id']:node for node in graph['elements']['nodes']}
            belongto = {node['data']['id']: node['data']['belongto'] for node in graph['elements']['nodes']}
            edges = self.__build_edges_dict(graph)

            #print ('   All nodes:')
            #print (simplejson.dumps(all_nodes, indent=4))

            #print ('   Belongto:')
            #print (simplejson.dumps(belongto, indent=4))

            #print ('   self.key:', self.key)

            tool_node = all_nodes[self.key]
            tool_node_belongto = belongto[self.key]

            # Use download_tool() does the same task. The problem is that it works directly with the UI.
            # We want to construct a cytoscape graph from the database object

            # Get a set of the node ids that depend from this tool
            tool_dependencies = self.__tool_dependencies(tool_node, all_nodes, edges)

            #print ('   Nodes to delete:')
            #print (tool_dependencies)

            # Remove these nodes (and edges connected to them) from the graph
            self.__remove_nodes_edges(graph, tool_dependencies, self.all_ids)

            #print ('   Graph After Deletion of nodes and edges:')
            #print (simplejson.dumps(graph, indent=4))

            # Add the edges of the graph
            #print ('   Edges to add:')
            #print (simplejson.dumps(self.graph['elements']['edges'], indent=4))
            graph['elements']['edges'].extend(self.graph['elements']['edges'])

            # Add the nodes of this graph
            # Make sure that they have the right belongto info
            nodes_to_add = self.graph['elements']['nodes']
            for node_to_add in nodes_to_add:
                node_to_add['data']['belongto'] = tool_node_belongto

            #print ('   Nodes to add:')
            #print (simplejson.dumps(nodes_to_add, indent=4))

            graph['elements']['nodes'].extend(nodes_to_add)

            #print ('  Graph after adding new tool dependencies')
            #print (simplejson.dumps(graph, indent=4))

            # Save the graph
            workflow_using_me.workflow = simplejson.dumps(graph)
            workflow_using_me.save()

            # Check graph <--> model consistency
            self.__consistency_check_graph_model(graph, workflow_using_me)


@has_data
def ro_finalize_delete(request, **kwargs):
    '''
    Called from ro_finalize_delete/
    if action is FINALIZE:
        finalize a tool/workflow (from draft to no draft!)
    if action is DELETE
        DELETE a tool/workflow
    ro: tool or workflow
    '''

    ro = kwargs.get('ro', '')
    if not ro:
        return fail('Error 5476')
    if not ro in ['tool', 'workflow']:
        return fail('Error 5477')

    action = kwargs.get('action', '')
    if not action in ['FINALIZE', 'DELETE']:
        return fail('Error 5475')


    # Get the user
    try:
        obc_user = OBC_user.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        return fail('Error 5472')


    if ro == 'tool':

        tools_info_name = kwargs.get('tools_info_name', '')
        if not tools_info_name:
            return fail('Error 5467')

        tools_info_version = kwargs.get('tools_info_version', '')
        if not tools_info_version:
            return fail('Error 5468')

        tools_info_edit = kwargs.get('tools_info_edit', '')
        if not tools_info_edit:
            return fail('Error 5469')

        try:
            tools_info_edit = int(tools_info_edit)
        except ValueError as e:
            return fail('Error 5470')

        # Get the tool
        try:
            tool = Tool.objects.get(name=tools_info_name, version=tools_info_version, edit=tools_info_edit)
        except ObjectDoesNotExist as e:
            return fail('Error 5471')

        # Is the user who created the tool, the same as the user who wants to edit/delete it?
        if not tool.obc_user == obc_user:
            return fail('Error 5473')

        if not tool.draft:
            return fail('Error 5474')

        if action == 'FINALIZE':
            # Does it depend on any tool that is draft?
            draft_dependencies = [t for t in tool_get_dependencies_internal(tool, include_as_root=False) if t['dependency'].draft]
            if draft_dependencies:
                return fail('This tool cannot be finalized. It depends from {} draft tool(s). For example: {}'.format(len(draft_dependencies), str(draft_dependencies[0]['dependency'])))

            tool.draft = False
            tool.save()

            WJ = WorkflowJSON()
            WJ.update_tool(tool)

        elif action == 'DELETE':
            # Is there any other tool that depends from this tool?
            dependendants = Tool.objects.filter(dependencies__in=[tool])
            if dependendants.count():
                return fail('This tool cannot be deleted. There are {} tool(s) that depend on this tool. For example: {}'.format(dependendants.count(), dependendants.first()))

            # Is there any workflow that contains this tool?
            w = Workflow.objects.filter(tools__in=[tool])
            if w.count():
                return fail('This tool cannot be deleted. It is used in {} workflow(s). For example: {}'.format(w.count(), str(w.first())))

            # Get the tools that are forks of this tool
            tool_forks = Tool.objects.filter(forked_from=tool)

            # Get the tool that this tool is forked from
            tool_forked_from = tool.forked_from

            # All the tools that are forked from this tool are now forked from the tool that this tool was forked from!
            for tool_fork in tool_forks:
                tool_fork.forked_from = tool_forked_from
                tool_fork.save()

            # Delete the comment
            tool.comment.delete()

            # Delete the tool
            tool.delete()

        return success()

    elif ro == 'workflow':
        workflow_info_name = kwargs.get('workflow_info_name', '')
        if not workflow_info_name:
            return fail('Error 5478')

        workflow_info_edit = kwargs.get('workflow_info_edit', '')
        if not workflow_info_edit:
            return fail('Error 5479')

        try:
            workflow_info_edit = int(workflow_info_edit)
        except ValueError as e:
            return fail('Error 5480')

        # Get the workflow
        try:
            workflow = Workflow.objects.get(name=workflow_info_name, edit=workflow_info_edit)
        except ObjectDoesNotExist as e:
            return fail('Error 5481')

        #Is the user who created the workflow the same as the one who wants to edit/delete it?
        if obc_user != workflow.obc_user:
            return fail('Error 5482')

        # Basic sanity check..
        if not workflow.draft:
            return fail('Error 5483')

        if action == 'FINALIZE':
            # Does it contain any tool that it is draft?
            t = workflow.tools.filter(draft=True)
            if t.count():
                return fail('This workflow cannot be finalized. It contains {} draft tool(s). For example: {}'.format(t.count(), str(t.first())))

            # Does it contain any draft workflow?
            w = workflow.workflows.filter(draft=True)
            if w.count():
                return fail('This workflow cannot be finalized. It contains {} draft workflow(s). For example: {}'.format(w.count(), str(w.first())))

            workflow.draft = False
            workflow.save()
            #workflow_has_changed(workflow) # Update other workflows that are using this
            WJ = WorkflowJSON()
            WJ.update_workflow(workflow) # TODO limit action to finalize!

        elif action == 'DELETE':
            # Is there any workflow that contains this workflow?
            w = Workflow.objects.filter(workflows__in = [workflow])
            if w.count():
                return fail('This workflow cannot be deleted. It is used in {} workflow(s). For example: {}'.format(w.count(), str(w.first())))

            # Get the workflows that are forks of this workflow
            workflow_forks = Workflow.objects.filter(forked_from=workflow)

            # Get the workflow that this workflow is forked from
            workflow_forked_from = workflow.forked_from

            # All the workflows that are forked from this workflow are now forked from the workflow that this workflow was forked from!
            for workflow_fork in workflow_forks:
                workflow_fork.forked_from = workflow_forked_from
                workflow_fork.save()

            # Delete the comments
            workflow.comment.delete()

            # Delete the workflow
            workflow.delete()

        return success()


def create_workflow_edge_id(source_id, target_id):
    '''
    ATTENTION!!!!

    This should be in accordance with the javascript code: File: ui.js


        /*
        * Create a "unique" id for an edge
        */
        function create_workflow_edge_id(source_id, target_id) {
            return source_id + '..' + target_id;
        }

    '''
    return source_id + '..' + target_id

def create_workflow_id(workflow):
    '''
    ATTENTION!!
    This should be in accordnace with the javascript code: File: ui.js
        /*
        * Creates a "unique" id from a workflow
        */
        function create_workflow_id(workflow) {
            return workflow.name + '__' + workflow.edit; //It is ok if this is wf1__null
        }
    '''

    if isinstance(workflow, Workflow):
        return create_workflow_id({'name': workflow.name, 'edit': workflow.edit})

    return workflow['name'] + '__' + str(workflow['edit'])


def set_edit_to_cytoscape_json(cy, edit, workflow_info_name, *,
        workflow_description,
        workflow_website,
        workflow_keywords,
        workflow_visibility,
    ):
    '''
    Perform the following tasks:
    * Set the edit number of the workflow to all nodes/edges
    * Change the id of the root workflow from "root" to workflow_info_name
    * Set workflow description
    '''

    # Get the root workflow node
    new_worfklow_node = [x for x in cy['elements']['nodes'] if x['data']['type']=='workflow' and not x['data']['edit']]
    assert len(new_worfklow_node) == 1
    assert new_worfklow_node[0]['data']['name'] == 'root'

    # Set the edit value
    new_worfklow_node[0]['data']['edit'] = edit

    # Set the label value
    new_worfklow_node[0]['data']['label'] = workflow_label_cytoscape(workflow=None, name=workflow_info_name, edit=edit)

    # Set workflow description
    new_worfklow_node[0]['data']['description'] = workflow_description

    # Set workflow website
    new_worfklow_node[0]['data']['website'] = workflow_website

    # Set workflow keywords
    new_worfklow_node[0]['data']['keywords'] = workflow_keywords

    # Set workflow visibility
    new_worfklow_node[0]['data']['visibility'] = workflow_visibility

    belongto = {
        'name': workflow_info_name,
        'edit': edit,
    }
    belongto_id = create_workflow_id(belongto)

    for node in cy['elements']['nodes']:
        # Set the edit in belongto
        if not node['data']['belongto'] is None:
            if not node['data']['belongto']['edit']:
                node['data']['belongto'] = belongto

        # Set the name in root 
        if 'name' in node['data']:
            if node['data']['name'] == 'root':
                node['data']['name'] = workflow_info_name

        if '__null'  in node['data']['id']:
            node['data']['id'] = node['data']['id'].replace('__null', '__' + str(edit))

        if 'root__' in node['data']['id']:
            node['data']['id'] = node['data']['id'].replace('root__', workflow_info_name + '__')

        #Change the bash
        if 'bash' in node['data']:
            node['data']['bash'] = node['data']['bash'].replace('__null', '__' + str(edit))
            node['data']['bash'] = node['data']['bash'].replace('root__', workflow_info_name + '__')

        # Set to step-->Step
        if 'steps' in node['data']:
            for step_i, _ in enumerate(node['data']['steps']):
                if '__null' in node['data']['steps'][step_i]:
                    node['data']['steps'][step_i] = node['data']['steps'][step_i].replace('__null', '__' + str(edit))
                if 'root__' in node['data']['steps'][step_i]:
                    node['data']['steps'][step_i] = node['data']['steps'][step_i].replace('root__', workflow_info_name + '__')

        # Set to step-->inputs
        if 'inputs' in node['data']:
            for input_i, _ in enumerate(node['data']['inputs']):
                if '__null' in node['data']['inputs'][input_i]:
                    node['data']['inputs'][input_i] = node['data']['inputs'][input_i].replace('__null', '__' + str(edit))
                if 'root__' in node['data']['inputs'][input_i]:
                    node['data']['inputs'][input_i] = node['data']['inputs'][input_i].replace('root__', workflow_info_name + '__')

        # Set to step->outputs
        if 'outputs' in node['data']:
            for output_i, _ in enumerate(node['data']['outputs']):
                if '__null' in node['data']['outputs'][output_i]:
                    node['data']['outputs'][output_i] = node['data']['outputs'][output_i].replace('__null', '__' + str(edit))
                if 'root__' in node['data']['outputs'][output_i]:
                    node['data']['outputs'][output_i] = node['data']['outputs'][output_i].replace('root__', workflow_info_name + '__')


    if 'edges' in cy['elements']:
        for edge in cy['elements']['edges']:
            if '__null' in edge['data']['source']:
                edge['data']['source'] = edge['data']['source'].replace('__null', '__' + str(edit))
            if 'root__' in edge['data']['source']:
                edge['data']['source'] = edge['data']['source'].replace('root__', workflow_info_name + '__')
            if '__null' in edge['data']['target']:
                edge['data']['target'] = edge['data']['target'].replace('__null', '__' + str(edit))
            if 'root__' in edge['data']['target']:
                edge['data']['target'] = edge['data']['target'].replace('root__', workflow_info_name + '__')
            if '__null' in edge['data']['id']:
                edge['data']['id'] = create_workflow_edge_id(edge['data']['source'], edge['data']['target'])

def check_workflow_step_main(cy, root_workflow):
    '''
    It should be one and only one main step on the main workflow
    '''

    main_counter = 0
    for node in cy['elements']['nodes']:
        if node['data']['type'] == 'step':
            if node['data']['belongto'] == root_workflow:
                if node['data']['main']:
                    main_counter += 1

    return main_counter

@has_data
def workflows_add(request, **kwargs):
    '''
    add workflow, workflow add, save workflow, workflow save, save wf
    edit workflow edit update workflow
    '''

    workflow_forked_from = None
    workflow_changes = None
    upvoted = False
    downvoted = False


    if request.user.is_anonymous: # Server should always check..
        return fail('Please login to create new workflow')

    if not user_is_validated(request):
        return fail('Please validate your email to create new workflows ' + validate_toast_button());

    obc_user = OBC_user.objects.get(user=request.user)

    workflow_info_name = kwargs.get('workflow_info_name', '')
    if not workflow_info_name.strip():
        return fail('Invalid workflow name')

    try:
        workflow_info_forked_from = kwargs['workflow_info_forked_from']
    except KeyError:
        return fail('Error 4876. Invalid workflow_info_forked_from field')

    workflow_edit_state = kwargs.get('workflow_edit_state', '')
    if not type(workflow_edit_state) is bool:
        return fail('Error 4877. Invalid workflow_edit_state')

    # Check visibility
    workflow_visibility = kwargs.get('workflow_visibility')
    visibility_code = validate_visibility(workflow_visibility)
    if type(visibility_code) is str:
        return fail(visibility_code)

    workflow = kwargs.get('workflow_json', '')

    if g['TEST']:
        print ('Workflow from angular:')
        print (simplejson.dumps(workflow, indent=4))

    if not workflow:
        return fail ('workflows json object is empty') # This should never happen!

    if not workflow['elements']:
        return fail('workflow graph cannot be empty')

    # Get all tools that are used in this workflow except the ones that are disconnected
    tool_nodes = [x for x in workflow['elements']['nodes'] if (x['data']['type'] == 'tool') and (not x['data']['disconnected'])]
    tools = [Tool.objects.get(name=x['data']['name'], version=x['data']['version'], edit=x['data']['edit']) for x in tool_nodes]
    # If this is a public workflow make sure that it does not include any private tool
    if visibility_code == VisibilityOptions.PUBLIC_CODE:
        for tool in tools:
            if tool.visibility != str(VisibilityOptions.PUBLIC_CODE):
                return fail(f'This public workflow contains the private tool: {tool}. Public workflows cannot include private tools.')
                ### TEST 217_create_public_wf_containing_private_tool  PYT: test_217_create_public_wf_containing_private_tool

    # Compute next_edit
    if workflow_edit_state:
        try:
            # workflow_info_edit comes from client.
            workflow_info_edit = int(kwargs.get('workflow_info_edit', ''))
        except ValueError:
            return fail('Error 4878')

        next_edit = workflow_info_edit
    else:
        #Get the maximum version. FIXME DUPLICATE CODE
        workflow_all = Workflow.objects.filter(name__iexact=workflow_info_name)
        if not workflow_all.exists():
            next_edit = 1
        else:
            max_edit = workflow_all.aggregate(Max('edit'))
            next_edit = max_edit['edit__max'] + 1

    # Check workflow website
    workflow_website = kwargs.get('workflow_website', '')
    if workflow_website:
        if not valid_url(workflow_website):
            return fail('website is not a valid URL')

    # Check workflow description
    workflow_description = kwargs.get('workflow_description', '')
    if not workflow_description.strip():
        return fail('Description cannot be empty')

    workflow_description_html = markdown(workflow_description)

    # Get keywords
    try:
        keywords = [Keyword.objects.get_or_create(keyword=keyword)[0] for keyword in kwargs['workflow_keywords']]
    except KeyError:
        return fail('Error 4882. Could not find keywords')


    #Change the edit value in the cytoscape json object
    set_edit_to_cytoscape_json(workflow, next_edit, workflow_info_name,
        workflow_description = workflow_description,
        workflow_website = workflow_website,
        workflow_keywords = kwargs['workflow_keywords'],
        workflow_visibility = workflow_visibility,
    )

    # Get all workflows that are used in this workflow
    workflow_nodes = [x for x in workflow['elements']['nodes'] if x['data']['type'] == 'workflow']

    # Remove self workflow and workflows that are disconnected
    workflow_nodes = [
        {'name': x['data']['name'], 'edit': x['data']['edit']}
        for x in workflow_nodes if
            (not (x['data']['name'] == workflow_info_name and x['data']['edit'] == next_edit)) and (not x['data']['disconnected'])
        ]
    # Get workflow database objects
    workflows = [Workflow.objects.get(**x) for x in workflow_nodes]

    # If this is a public workflow make sure that it does not include any private workflow
    if visibility_code == VisibilityOptions.PUBLIC_CODE:
        for w in workflows:
            if w.visibility != str(VisibilityOptions.PUBLIC_CODE):
                return fail(f'This public workflow contains the private workflow: {w}. Public workflows cannot include private workflows.')
                ### TEST SEL: 217_create_public_wf_containing_private_wf . PYT: test_217_create_public_wf_containing_private_wf

    # Check main_step
    main_counter = check_workflow_step_main(workflow, {'name':workflow_info_name, 'edit': next_edit })
    if main_counter == 0:
        return fail('Could not find main step. One step needs to be declared as "main"')
    if main_counter > 1:
        return fail('Error 49188') # This should never happen

    workflow_changes = kwargs.get('workflow_changes', None)
    if workflow_info_forked_from:
        if not workflow_changes:
            return fail('Edit Summary cannot be empty')
        workflow_forked_from = Workflow.objects.get(name=workflow_info_forked_from['name'], edit=workflow_info_forked_from['edit'])
    else:
        pass # Do nothing


    if workflow_edit_state:
        # We are editing this workflow

        # Does this workflow exist?
        try:
            w = Workflow.objects.get(name=workflow_info_name, edit=workflow_info_edit)
        except ObjectDoesNotExist as e:
            return fail('Error 4879')

        # Are we converting from private to public?
        if w.visibility == str(VisibilityOptions.PRIVATE_CODE) and workflow_visibility == VisibilityOptions.PUBLIC_NAME:
            # Does this workflow contain any private tool?
            first = w.tools.filter(visibility=str(VisibilityOptions.PRIVATE_CODE)).first()
            if first:
                return fail(f'Cannot convert this Workflow to public. It contains the private tool {first}')
                ### TEST 217_convert_from_private_to_public_workflow_containing_private_tool PYT: test_217_convert_from_private_to_public_workflow_containing_private_tool

            # Does this workflow contain an private workflow?
            first = w.workflows.filter(visibility=str(VisibilityOptions.PRIVATE_CODE)).first()
            if first:
                return fail(f'Cannot convert this Workflow to public. It contains the private workflow {first}')
                ### TEST 217_convert_from_private_to_public_workflow_containing_private_wf PYT: test_217_convert_from_private_to_public_workflow_containing_private_tool

        # Are we converting from public to private?
        if w.visibility == str(VisibilityOptions.PUBLIC_CODE) and workflow_visibility == VisibilityOptions.PRIVATE_NAME:
            # Is there any public workflow that uses this workflow?
            first = w.workflows_using_me.filter(visibility=str(VisibilityOptions.PUBLIC_CODE)).first()
            if first:
                return fail(f'Cannot convert this Workflow to private. It is contained in the public workflow {first}')
                ### TEST 217_convert_wf_from_public_to_private_that_is_contained_in_public_wf PYT: test_217_convert_wf_from_public_to_private_that_is_contained_in_public_wf


        # Basic sanity check. We shouldn't be able to edit a workflow which is not a draft..
        if not w.draft:
            return fail('Error 4880')

        # Is the creator of the workflow the same as the user who edits it?
        if obc_user != w.obc_user:
            return fail('Error 4881')

        # Store a reference to the comments
        comment = w.comment

        # Store upvotes/downvotes
        upvotes = w.upvotes
        downvotes = w.downvotes

        # Store votes
        votes = UpDownWorkflowVote.objects.filter(workflow=w)
        # Disassociate from this tool and get upvoted/downvoted status
        for vote in votes:
            if vote.obc_user == obc_user:
                upvoted = vote.upvote
                downvoted = not upvoted

            vote.workflow = None
            vote.save()

        # Get the workflows that are forks of this workflow
        workflow_forks = Workflow.objects.filter(forked_from=w)
        # Temporary set that these workflows are not forked from any workflow
        for workflow_fork in workflow_forks:
            workflow_fork.forked_from = None
            workflow_fork.save()

        # Get the workflow that this workflow is forked from
        workflow_forked_from = w.forked_from

        # Get the created at. It needs to be sorted according to this, otherwise the jstree becomes messy
        workflow_created_at = w.created_at

        # Get the workflows that use this workflow
        workflows_using_this_workflow = Workflow.objects.filter(workflows__in = [w])

        # Remove this workflow from these workflows
        for workflow_using_this_workflow in workflows_using_this_workflow:
            workflow_using_this_workflow.workflows.remove(w)
            workflow_using_this_workflow.save()

        # Delete it!
        w.delete()

    else:
        # This is a new workflow
        upvotes = 0
        downvotes = 0


    new_workflow = Workflow(
        obc_user=obc_user,
        name = workflow_info_name,
        edit = next_edit,
        website = workflow_website,
        description = workflow_description,
        description_html = workflow_description_html,

        # FIXME !! SERIOUS!
        # This is redundand. We do json.loads and then json.dumps.
        # On the other hand, how else can we check if elements are not empty? (perhaps on the backend..)
        workflow = simplejson.dumps(workflow),
        forked_from = workflow_forked_from,
        changes = workflow_changes,
        upvotes = upvotes,
        downvotes = downvotes,
        visibility = visibility_code,
        draft = True, # We always save new workflows as draft.
    )

    #Save it
    new_workflow.save()

    if workflow_edit_state:
        # Preserve the created at date. We have to do that AFTER the save! https://stackoverflow.com/questions/7499767/temporarily-disable-auto-now-auto-now-add
        new_workflow.created_at = workflow_created_at
        new_workflow.save()

    # Add tools
    if tools:
        new_workflow.tools.add(*tools)
        new_workflow.save()

    # Add workflows
    if workflows:
        new_workflow.workflows.add(*workflows)
        new_workflow.save()

    # Add keywords
    new_workflow.keywords.add(*keywords)
    new_workflow.save();

    obc_user = OBC_user.objects.get(user=request.user)

    if workflow_edit_state:
        # Add the votes from the previous edit
        for vote in votes:
            vote.workflow = new_workflow
            vote.save()

        # Add the workflows that were forked from this workflow (that was deleted before) to the new workflow
        for workflow_fork in workflow_forks:
            workflow_fork.forked_from = new_workflow
            workflow_fork.save()

        # Add to the workflows that were using this workflow, the new workflow
        for workflow_using_this_workflow in workflows_using_this_workflow:

            #print ('Workflow using this workflow:', str(workflow_using_this_workflow))

            workflow_using_this_workflow.workflows.add(new_workflow)
            workflow_using_this_workflow.save()

        # Update the json graph to the workflows that are using me
        WJ = WorkflowJSON()
        WJ.update_workflow(new_workflow)

    else:
        # Add an empty comment. This will be the root comment for the QA thread
        comment = Comment(
            obc_user = obc_user,
            comment = '',
            comment_html = '',
            title = markdown('Discussion on Workflow: w/{}/{}'.format(workflow_info_name, next_edit)),
            parent = None,
            upvotes = 0,
            downvotes = 0,
        )
        comment.save()

    new_workflow.comment = comment
    new_workflow.save()

    #print ('AFTER SAVE:')
    #print (simplejson.dumps(simplejson.loads(new_workflow.workflow), indent=4))


    ret = {
        'description_html': workflow_description_html,
        'edit': next_edit,
        'created_at': datetime_to_str(new_workflow.created_at),
        'score': upvotes-downvotes,
        'voted': {'up': upvoted, 'down': downvoted},

        'workflow_pk': new_workflow.pk, # Used in comments
        'workflow_thread': qa_create_thread(new_workflow.comment, obc_user), # Tool comment thread
    }

    return success(ret)

def tool_exists_in_db(tool):
    '''
    Check if tool represented in cytoscape exists 
    '''
    return Tool.objects.filter(
        name = tool['name'],
        version = tool['version'],
        edit = int(tool['edit']),
    ).exists()

def workflow_exists_in_db(workflow):
    '''
    Check if a workflow represented in cytoscape exists
    '''
    return Workflow.objects.filter(
        name = workflow['name'],
        edit = int(workflow['edit']),
    ).exists()



#@has_data
def upload(request, **kwargs):
    '''
    Upload a workflow
    '''

    size = 0
    complete = b''
    for chunk in request.FILES['file']:
        size += len(chunk)
        complete += chunk
        if size > g['maximum_workflow_file_upload'] * 1_048_576:
            return fail(f'Maximum file size: {g["maximum_workflow_file_upload"]} MB reached.')

    try:
        complete_str = complete.decode("utf-8") 
    except UnicodeDecodeError:
        return fail('Failed to convert file\'s content to Unicode UTF-8')

    try:
        workflow = Workflow_executor(workflow_string=complete_str, askinput='NO',)
    except OBC_Executor_Exception as e:
        return fail(str(e))
    except Exception as e:
        return fail(f'Error 5488. Could not parse Workflow: {str(e)}')

    error_message = 'Could not import workflow. '

    if False: # We do not check if ROs exist!
        for tool in workflow.get_tool_installation_order():
            if tool_exists_in_db(tool):
                return fail(error_message + f' Contained tool: {tool_label_cytoscape(tool)} already exists.')

        for w in workflow.get_workflow_order():
            if workflow_exists_in_db(w):
                return fail(error_message + f' Contained workflow: {workflow_label_cytoscape(w)} already exists.')


    rf = RequestFactory()

    # All quality controls seem to be fine. Start importing!
   

    # First, add tools
    tools_added = [] # Keep records of which tools we have added 
    def tool_edit_getter(tool_request):
        '''
        This function takes an "artificial" tool_add request and submits it
        '''
        fake_request = rf.post('/tools_add/', tool_request, content_type='application/json')
        fake_request.user = request.user
        response = tools_add(fake_request)
        response_decoded = decode_response(response)

        if not response_decoded['success']:
            return response_decoded['error_message']

        #tools_added.append('/'.join([
        #    tool_request['tools_search_name'], tool_request['tools_search_version'], str(response_decoded['edit']),
        #]))

        tools_added.append(Tool.objects.get(
            name=tool_request['tools_search_name'],
            version=tool_request['tools_search_version'],
            edit=int(response_decoded['edit']),
        ))
        return response_decoded['edit']

    workflows_added = []
    def workflow_edit_getter(workflow_request):

        fake_request = rf.post('/workflows_add/', workflow_request, content_type='application/json')
        fake_request.user = request.user
        response = workflows_add(fake_request)
        response_decoded = decode_response(response)

        if not response_decoded['success']:
            return response_decoded['error_message']

        #workflows_added.append('/'.join([
        #    workflow_request['workflow_info_name'], str(response_decoded['edit']),
        #]))

        workflows_added.append(Workflow.objects.get(
            name =  workflow_request['workflow_info_name'],
            edit= int(response_decoded['edit']),
        ))
        return response_decoded['edit']


    try:
        error_message = workflow.upload(
            tool_edit_getter = tool_edit_getter,
            #tool_edit_getter = None,
            workflow_edit_getter = workflow_edit_getter,
            #workflow_edit_getter = None,
        )
    except OBC_Executor_Exception as e:
        #raise e 
        error_message = str(e)
    except Exception as e:
        #raise e
        error_message = str(e)

    if error_message:

        # Roll back
        for w in reversed(workflows_added):
            w.comment.delete()
            w.delete()
        for t in reversed(tools_added):
            t.comment.delete()
            t.delete()

        return fail(f'Could not upload Workflow. Reason: {error_message}')

    success_message = 'Workflow uploaded correctly. '
    if tools_added:
        success_message += f'Created {len(tools_added)} tools: {", ".join(map(str, tools_added))}. '
    if workflows_added:
        success_message += f'Created {len(workflows_added)} workflows: {", ".join(map(str, workflows_added))}.'

    ret = {
        'message': success_message,
    }

    return success(ret)

@has_data
def workflows_search_3(request, **kwargs):
    '''
    This is triggered when a user drags a workflow from the jstree and drops it in a current workflow
    '''

    workflow_name = kwargs['workflow_name']
    workflow_edit = kwargs['workflow_edit']

    workflow = Workflow.objects.get(name__iexact = workflow_name, edit=workflow_edit)

    # Get current obc_user
    if request.user.is_anonymous:
        obc_user = None
    else:
        obc_user = OBC_user.objects.get(user=request.user)

    #Is this user allowed to get access to this workflow?
    if not is_visibility_allowed(obc_user=obc_user, ro=workflow):
        return fail('This workflow is private.')

    #Is it voted?
    if obc_user:
        try:
            v = UpDownWorkflowVote.objects.get(obc_user=obc_user, workflow=workflow)
        except ObjectDoesNotExist as e:
            # It is not voted
            workflow_voted = {'up': False, 'down': False}
        else:
            # It is noted
            workflow_voted = {'up': v.upvote, 'down': not v.upvote}

    else:
        workflow_voted = {'up': False, 'down': False}


    ret = {
        'username': workflow.obc_user.user.username,
        'website': workflow.website,
        'description': workflow.description,
        'description_html': workflow.description_html,
        'created_at': datetime_to_str(workflow.created_at),
        'forked_from': workflow_to_json(workflow.forked_from),
        'keywords': [keyword.keyword for keyword in workflow.keywords.all()],
        'workflow' : simplejson.loads(workflow.workflow),
        'changes': workflow.changes,
        'visibility': VisibilityOptions.VISIBILITY_OPTIONS_CODE_dic[workflow.visibility],
        'workflow_pk': workflow.pk, # Used in comments (QAs)
        'workflow_thread': qa_create_thread(workflow.comment, obc_user), # Workflow comment thread
        'workflow_score': workflow.upvotes - workflow.downvotes,
        'workflow_voted': workflow_voted,
        'workflow_comment_id': workflow.comment.pk, # Used to create a permalink to the comments
        'workflow_comment_title': workflow.comment.title,
        'workflow_comment_created_at': datetime_to_str(workflow.comment.created_at),
        'workflow_comment_username': workflow.comment.obc_user.user.username,
        'draft': workflow.draft, # Is this a draft workflow?

    }

    return success(ret)

def workflow_node_cytoscape(workflow, name='root', edit=0):
    '''
    DEPRECATED. Only called from download_tool which is deprecated

    Create a cytoscape workflow node
    Normally it should take a database workflow object and create a cytoscape node
    Now it just creates a root workflow cytoscape node
    '''

    assert not workflow # Not yet implemented

    return {
        'data': {
            'belongto': None,
            'edit': edit,
            'id': workflow_id_cytoscape(workflow, name, edit),
            'label': workflow_label_cytoscape(workflow, name=name, edit=edit),
            'name': name,
            'type': 'workflow',
            'draft': False, # For consistency. It does not realy makes any difference
            'disconnected': False, # For consistency as well.
        }
    }


def tool_node_cytoscape(tool, tool_depending_from_me=None):
    '''

    Create a cytoscape tool node
    tool: A database object tool node
    tool_depending_from_me: If i was added as a dependency, this should be the tool that depends from me. FIXME: REMOVE THIS
    '''

    if isinstance(tool, Tool):

        return {
            'data': {
                'belongto': {'name': 'root', 'edit': 0},
                'dep_id' : tool_id_cytoscape(tool_depending_from_me) if tool_depending_from_me else '#', # Not used in executor
                'edit': tool.edit,
                'id': tool_id_cytoscape(tool),
                'label': tool_label_cytoscape(tool),
                'name': tool.name,
                'description': tool.description,
                'website': tool.website,
                'keywords': [k.keyword for k in tool.keywords.all()],
                'root': 'yes' if tool_depending_from_me else 'no', # Not used in executor. 'yes/no' should be True/False for Christ sake! FIXME
                'text': tool_label_cytoscape(tool),
                'type': 'tool',
                'variables': [{'description': variable.description, 'name': variable.name, 'type': 'variable', 'value': variable.value} for variable in tool.variables.all()],
                'installation_commands': tool.installation_commands,
                'validation_commands': tool.validation_commands,
                'os_choices': [choice.os_choices for choice in tool.os_choices.all()],
                'dependencies': [str(t) for t in tool.dependencies.all()],
                'version': tool.version,
                'draft': tool.draft,
                'disconnected': False,
            }
        }
    elif type(tool) is dict:
        return {
            'data': {
                'belongto': {'name': 'root', 'edit': 0},
                'dep_id' : tool_id_cytoscape(tool_depending_from_me) if tool_depending_from_me else '#', # See comment above. Not used in executor
                'edit': tool['edit'],
                'id': tool_id_cytoscape(tool),
                'label': tool_label_cytoscape(tool),
                'name': tool['name'],
                'description': tool['description'],
                'website': tool['website'],
                'keywords': tool['keywords'],
                'root' : 'yes' if tool_depending_from_me else 'no', # Not used in executor,
                'text': tool_label_cytoscape(tool),
                'type': 'tool',
                'variables': [{'description': variable['description'], 'name': variable['name'], 'type': 'variable', 'value': variable['value']} for variable in tool['variables']],
                'version': tool['version'],
                'draft': tool['draft'],
                'installation_commands': tool['installation_commands'],
                'validation_commands': tool['validation_commands'],
                'os_choices': tool['os_choices'],
                'dependencies': tool['dependencies'],
                'disconnected': False,
            }
        }


def step_node_cytoscape(name='main'):
    '''
    Create a cytoscape step node
    '''

    return {
        'data': {
            'bash': '',
            'belongto': {'name': 'root', 'edit': 0},
            'id': step_id_cytoscape('main', None, 'root', None),
            'label': step_id_label('main'),
            'inputs': [],
            'outputs': [],
            'steps': [],
            'tools': [],
            'main': True,
            'name': step_id_label('main'),
            'sub_main': False,
            'type': 'step',
        }
    }

def edge_cytoscape(source, target):
    '''
    Create a cytscape edge object
    '''

    return {
        'data': {
            'source': source['data']['id'],
            'target': target['data']['id'],
            'id': create_workflow_edge_id(source['data']['id'], target['data']['id']),
        },
        'position': {
            'x': 0,
            'y': 0,
        },
        'group': 'edges',
        'removed': False,
        'selected': False,
        'selectable': True,
        'locked': False,
        'grabbable': True,
        'classes': '',
    }

@has_data
def download_tool(request, **kwargs):
    '''
    DEPRECATED . Not actually used. Tools get downloaded only in the context of a workflow

    Create a cytoscape workflow that installs a given tool.
    Kind of a "fake" workflow that the only thing that it does is install a tool (and its dependencies)
    It is called by download_workflow when the user selects to "download" a tool instead of a workflow
    '''
    workflow = {
        'elements': {
            'nodes': [],
            'edges': [],
        }
    }

    # Add root workflow
    workflow_node = workflow_node_cytoscape(None)
    workflow['elements']['nodes'].append(workflow_node)

    # this does not contain recursively all the dependencies. Only the first level
    root_tool_dependencies = kwargs['tool_dependencies']
    root_tool_objects = [Tool.objects.get(name=t['name'], version=t['version'], edit=t['edit']) for t in root_tool_dependencies]
    all_dependencies_str = list(map(str, root_tool_objects))

    # Add this tool
    tool = {
        'name': str(kwargs['tools_search_name']) if str(kwargs['tools_search_name']) else 'T',
        'version': str(kwargs['tools_search_version']) if str(kwargs['tools_search_version']) else '0',
        'edit': kwargs['tools_search_edit'] if kwargs['tools_search_edit'] else 0, # If this is editable, then the edit is 0
        'variables': [variable for variable in kwargs['tool_variables'] if variable['name'] and variable['value'] and variable['description']],
        'draft': kwargs['tool_draft'],
        'installation_commands': kwargs['tool_installation_commands'],
        'validation_commands': kwargs['tool_validation_commands'],
        'os_choices': kwargs['tool_os_choices'],
        'dependencies': all_dependencies_str,
    }

    this_tool_cytoscape_node = tool_node_cytoscape(tool)
    #print (this_tool_cytoscape_node)

    workflow['elements']['nodes'].append(this_tool_cytoscape_node)

    # Add an edge between the root workflow and this tool
    workflow['elements']['edges'].append(edge_cytoscape(workflow_node, this_tool_cytoscape_node))

    # build all tool nodes for dependency tools
    all_ids = set()
    all_dependencies_str = []

    for root_tool_obj in root_tool_objects:
        # This is a first level dependency
        root_tool_node = tool_node_cytoscape(root_tool_obj)
        # Get all dependencies recursively for this tool
        root_tool_all_dependencies = tool_get_dependencies_internal(root_tool_obj, include_as_root=True)
        for root_tool_all_dependency in root_tool_all_dependencies:
            # For each dependency create a cytoscape node
            cytoscape_node = tool_node_cytoscape(root_tool_all_dependency['dependency'])
            if not cytoscape_node['data']['id'] in all_ids: # An id should exist only once in the graph.... FIXME all_ids is always empty!
                workflow['elements']['nodes'].append(cytoscape_node)

                # Connect this tool with its dependent tool node
                if root_tool_all_dependency['dependant']:
                    workflow['elements']['edges'].append(edge_cytoscape(cytoscape_node, tool_node_cytoscape(root_tool_all_dependency['dependant'])))
                else:
                    # This is a dependency of the root tool!
                    workflow['elements']['edges'].append(edge_cytoscape(cytoscape_node, this_tool_cytoscape_node))

    # Create a step node
    step_node = step_node_cytoscape('main')
    workflow['elements']['nodes'].append(step_node)
    # Connect it with the root workflow
    workflow['elements']['edges'].append(edge_cytoscape(workflow_node, step_node))


    return download_workflow(request, **{
        'workflow_options': {},
        'workflow': None,
        'download_type': kwargs.get('download_type', 'BASH'),
        'workflow_cy': workflow,
        'workflow_info_editable': False,
        })

@has_data
def download_workflow(request, **kwargs):
    '''
    Defined in urls.py:
    path('download_workflow/', views.download_workflow), # Acceps a workflow_options and workflow object. Runs a workflow

    https://docs.djangoproject.com/en/2.2/ref/request-response/#telling-the-browser-to-treat-the-response-as-a-file-attachment

    kwargs['workflow'] = {'name': <workflow_name>, 'edit': <workflow_edit>}

    kwargs['workflow_cy'] is the cytoscape workflow

    Note 1: Everyone can download a workflow!
    '''

    workflow_arg = kwargs['workflow'] # For example: {'name': 'test', 'edit': 1}

    # These are the options fetched from the UI. Check ui.js : window.OBCUI.get_workflow_options
    #    OR
    # The options fetched from the REST API . See rest_views.py : input_parameters
    workflow_options_arg = kwargs['workflow_options']

    download_type = kwargs['download_type'] # For a full list of types see below . if download_type == ...
    workflow_info_editable = kwargs['workflow_info_editable'] # IS this workflow saved or not ? . TRUE: NOT SAVED
    workflow_id = kwargs.get('workflow_id')
    workflow_obc_client = kwargs.get('obc_client', False)
    do_url_quote = kwargs.get('do_url_quote', True) # See rest_views.py
    return_bytes = kwargs.get('return_bytes', False) # See rest_views.py
    coming_from_UI = kwargs.get('UI', False) # WHO CALLED ME??
    coming_from_API = kwargs.get('API', False) # WHO CALLED ME??

    # for break_down_on_tools see executor.py
    # If we are coming from UI then always break down on tools
    break_down_on_tools = kwargs.get('break_down_on_tools', False) or coming_from_UI

    #print ('Name:', workflow_arg['name'])
    #print ('Edit:', workflow_arg['edit'])
    #print ('editable:', workflow_info_editable)

    if workflow_arg:
        # This is a workflow saved
        workflow = Workflow.objects.get(**workflow_arg)
        workflow_cy = simplejson.loads(workflow.workflow)
    else:
        # This is a tool
        workflow = None
        workflow_cy = kwargs['workflow_cy']
    #print (workflow_cy)

    # Create a new Report object
    if (not user_is_validated(request)) or (not workflow) or (workflow.draft):
        '''
        If :
            user is anonymous or
            with non-validated email or
            not saved workflow or
            this is a tool run (workflow is None) or
            workflow is draft
        then:
            we do not create a report!
        '''
        run_report = None
        nice_id = None
        token = None
        report_created = False # Do we create a report upon execution of this workflow?
    else:
        run_report = Report(
            obc_user = OBC_user.objects.get(user=request.user),
            workflow = workflow,
        )
        # Attach a new report_id to it
        run_report.save()
        nice_id = str(run_report.nice_id)
        report_token = ReportToken(status=ReportToken.UNUSED, active=True)
        report_token.save()
        #print ('Report ID:')
        #print (report_id)
        run_report.tokens.add(report_token)
        run_report.save()
        token = str(report_token.token)
        report_created = True

    output_object = {
        'arguments': workflow_options_arg,
        'workflow': workflow_cy,
        'token': token,
        'nice_id': nice_id,
    }
    #output_object = simplejson.dumps(output_object) # .replace('#', 'aa')

    #output_object = escape(simplejson.dumps(output_object))

    #print ('output_object')
    #print (output_object)

    #response = HttpResponse(the_script, content_type='application/x-sh')
    #response['Content-Disposition'] = 'attachment; filename="script.sh"'

    ret = {}

    server_url = get_server_url(request)

    try:
        if download_type == 'JSONGRAPH':
            output_object = simplejson.dumps(output_object)
        elif download_type == 'JSONDAG':
            output_object = create_bash_script(output_object, server_url, 'jsondag',
                workflow_id=workflow_id,
                obc_client=workflow_obc_client,
                break_down_on_tools=break_down_on_tools,
            )

#            ddd = simplejson.loads(output_object)
#            print (simplejson.dumps(ddd, indent=4))
#            print ('====')
#            print (ddd['DOT'])

        elif download_type == 'BASH':
            output_object = create_bash_script(output_object, server_url, 'sh')
        elif download_type == 'CWLTARGZ':
            output_object = create_bash_script(output_object, server_url, 'cwltargz', workflow_id=workflow_id)
        elif download_type == 'CWLZIP':
            output_object = create_bash_script(output_object, server_url, 'cwlzip', workflow_id=workflow_id)
        elif download_type == 'AIRFLOW':
            output_object = create_bash_script(output_object, server_url, 'airflow', workflow_id=workflow_id, obc_client=workflow_obc_client)
        elif download_type == 'ARGO':
            output_object = create_bash_script(output_object, server_url, 'argo', workflow_id=workflow_id, obc_client=workflow_obc_client)
        elif download_type == 'NEXTFLOW':
            output_object = create_bash_script(output_object, server_url, 'nextflow', workflow_id=workflow_id, obc_client=workflow_obc_client)
        elif download_type == 'SNAKEMAKE':
            output_object = create_bash_script(output_object, server_url, 'snakemake', workflow_id=workflow_id, obc_client=workflow_obc_client)

        else:
            output_object = 'UNKNOWN TYPE' # THIS SHOULD NEVER HAPPEN

        if do_url_quote:
            output_object = urllib.parse.quote(output_object)

        ret['output_object'] = output_object

    except OBC_Executor_Exception as e:
        return fail(str(e))

    if return_bytes:
        return ret['output_object']

    ret['report_created'] = report_created
    ret['nice_id'] = nice_id

    return success(ret)

def callback_url(request):
    '''
    Buld callback url
    '''
    return f'{request.scheme}://{request.META["HTTP_HOST"]}/platform/'

@has_data
def run_workflow(request, **kwargs):
    '''
    path('run_workflow/', view.run_workflow)

    curl -H "Content-Type: application/json" --request POST --data '{"type":"workflow","name":"test", "edit": "2"}' "http://139.91.81.103:5000/3ee5ccfb744983968fb3e9735e4bb85d/run_workflow"

    source: Where the request came from. If it from rest then source='frontend'
    '''

    if request.user.is_anonymous: # Server should always check..
        return fail('Error 3291. User is anonymous')

    if not user_is_validated(request):
        return fail('Error 3292. User is not validated ' + validate_toast_button());

    obc_user = OBC_user.objects.get(user=request.user)

    profile_name = kwargs.get('profile_name', '')
    if not str(profile_name):
        return fail('Error 3288. Invalid profile name')

    workflow_options = kwargs.get('workflow_options', {}) # Get the workflow input options (arguments)

    name = kwargs.get('name', '')
    if not str(name):
        return fail('Error 3289. Invalid workflow name')

    edit = kwargs.get('edit', '')
    try:
        edit = int(edit)
    except ValueError as e:
        return fail('Error 3290. Invalid workflow edit')

    # Get the client
    try:
        client = obc_user.clients.get(name=profile_name)
    except ObjectDoesNotExist as e:
        return fail('Error 3293. Could not get execution client.')

    # Parse parameters
    try:
        parameters_parsed = simplejson.loads(client.parameters)
    except simplejson.errors.JSONDecodeError:
        return fail('Error 1591. Could not parse json parameters from DB')

    if not 'type' in parameters_parsed:
        return fail('Error 1592. client parameters does not have a type field.')

    # Get the workflow
    try:
        workflow = Workflow.objects.get(name=name, edit=edit)
    except ObjectDoesNotExist as e:
        return fail('Error 3294. Could not get Workflow object.')

    nice_id = create_nice_id()

    print (simplejson.dumps(parameters_parsed, indent=4))
    print (nice_id)

    # Create report
    run_report = Report(
        obc_user=obc_user,
        workflow=workflow,
        nice_id=nice_id,
        client=client
    )
    run_report.save()
    report_token = ReportToken(status=ReportToken.UNUSED, active=True)
    report_token.save()
    run_report.tokens.add(report_token)
    run_report.save()
    token = str(report_token.token)

    output_object = {
        'arguments': workflow_options,
        'workflow': simplejson.loads(workflow.workflow),
        'token': token,
        'nice_id': nice_id,
    }
    server_url = get_server_url(request) # http://0.0.0.0:8200/platform 
    server_url = 'http://192.168.1.7:8200/platform'


    # Run locally...
    if parameters_parsed['type'] == 'karvdash':

        # Create and run workflow
        import couler.argo as couler
        from couler.argo_submitter import ArgoSubmitter

        executor_parameters = {
            'workflow_name': 'openbio-' + nice_id,
            'image_registry': parameters_parsed['ARGO_IMAGE_REGISTRY'],
            'image_cache_path': parameters_parsed['ARGO_IMAGE_CACHE_PATH'],
            'work_path': os.path.join(parameters_parsed['ARGO_WORK_PATH'], nice_id)
        }
        namespace = parameters_parsed['ARGO_NAMESPACE_PREFIX'] + 'admin' # self.request.user.username
        _ = create_bash_script(output_object, server_url, 'argo', workflow_id=None, obc_client=False, executor_parameters=executor_parameters)
        submitter = ArgoSubmitter(namespace=namespace)
        result = couler.run(submitter=submitter)

        run_report.visualization_url = urllib.parse.urlparse(parameters_parsed['ARGO_BASE_URL'])._replace(path='/workflows/%s/%s' % (namespace, result['metadata']['name'])).geturl()
        run_report.monitor_url = 'http://asdf.com'
        run_report.client_status='SUBMITTED'
        run_report.save()

        # Let's not create a report_token for now.
        ret = {
            'nice_id': nice_id,
        }

        return success(ret)

    # ...or continue with "experimental" code.
    run_url = urllib.parse.urljoin(url + '/', 'run') # https://stackoverflow.com/questions/8223939/how-to-join-absolute-and-relative-urls

    data_to_submit = {
        'type': 'workflow',
        'name': name,
        'edit': edit,
        'callback': callback_url(request),
        'workflow_id': nice_id,
        'input_parameters' : workflow_options,
    }

    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

    #print ('run_url:', run_url)
    #print ('callback:', data_to_submit['callback'])

    '''


    '''

    '''
curl --header "Content-Type: application/json" \
  --request GET \
  http://139.91.190.239:5000/cfa52d9df5a24345d9f740395e4e69e4/check/id/test



[{"dag_id": "mitsos", "dag_run_url": "/admin/airflow/graph?dag_id=mitsos&execution_date=2020-02-28+13%3A16%3A42%2B00%3A00", "execution_date": "2020-02-28T13:16:42+00:00", "id": 2, "run_id": "manual__2020-02-28T13:16:42+00:00", "start_date": "2020-02-28T13:16:42.710933+00:00", "state": "success"}, {"dag_id": "mitsos", "dag_run_url": "/admin/airflow/graph?dag_id=mitsos&execution_date=2020-02-28+13%3A20%3A44%2B00%3A00", "execution_date": "2020-02-28T13:20:44+00:00", "id": 3, "run_id": "manual__2020-02-28T13:20:44+00:00", "start_date": "2020-02-28T13:20:44.423814+00:00", "state": "success"}, {"dag_id": "mitsos", "dag_run_url": "/admin/airflow/graph?dag_id=mitsos&execution_date=2020-02-28+13%3A24%3A02%2B00%3A00", "execution_date": "2020-02-28T13:24:02+00:00", "id": 4, "run_id": "manual__2020-02-28T13:24:02+00:00", "start_date": "2020-02-28T13:24:02.486982+00:00", "state": "success"}]

    '''

    # !!!HIGLY EXPERIMENTAL!!!
    try:
        print('RUNNING WITH CLIENT AT URL:', run_url, 'HEADERS:', headers, 'DATA:', data_to_submit)
        r = requests.post(run_url, headers=headers, data=simplejson.dumps(data_to_submit))
    except requests.exceptions.ConnectionError as e:
        return fail('Could not establish a connection with client')

    if not r.ok:
        #r.raise_for_status()
        return fail('Could not send to URL: {} . Error code: {}'.format(run_url, r.status_code))
    try:
        data_from_client = r.json()
    except Exception as e: # Ideally we should do here: except json.decoder.JSONDecodeError as e: but we would have to import json with simp[lejson..]
        return fail('Could not parse JSON data from Execution Client.')

    #print ('RUN_URL:')
    #print (data_from_client)

    # Check data_from_client. We expect to find an externally triggered True in data_from_client['status']['message']
    if not 'status' in data_from_client:
        return fail('Client does not contains status info')

    if not 'message' in data_from_client['status']:
        return fail("Client's status does not contain any message")

    if not 'externally triggered: True' in data_from_client['status']['message']:
        return fail("Client failed to trigger DAG: {}".format(data_from_client['status']['message']))

    if not 'executor_url' in data_from_client:
        return fail("Could not get workflow monitoring URL..")
    visualization_url = g['create_client_airflow_url'](data_from_client['executor_url'], nice_id)

    if not 'monitor_url' in data_from_client:
        return fail('Could not get monitoring URL..')
    monitor_url = data_from_client['monitor_url']


    # All seem to be ok. Create a report
    report = Report(
        obc_user=obc_user,
        workflow = workflow,
        nice_id = nice_id,
        client=client,
        visualization_url=visualization_url,
        monitor_url = monitor_url,
        client_status='SUBMITTED')
    report.save()

    # Let's not create a report token for now.
    ret = {
        'nice_id': nice_id,
    }

    return success(ret)


@csrf_exempt
@has_data
def report(request, **kwargs):
    '''
    called from the workflows themeslves in order to update the current execution progress.

    curl -X POST "http://0.0.0.0:8200/platform/report/" -H 'Content-Type: application/json' -d '{"token":"a2a71f56-2817-4e45-8f9e-72b1341cdfdc"}' 
    curl -X POST "http://0.0.0.0:8200/platform/report/" -H 'Content-Type: application/json' -d '{"token":"a2a71f56-2817-4e45-8f9e-72b1341cdfdc", "status": "workflow started test4/1"}' 
    '''

    print (kwargs)

    print ('hellloooooooo')

    token = kwargs.get('token', None)
    print ('token:', token)
    if not token:
        return fail('Could not find token field')
    #print ('token: {}'.format(token))

    if not uuid_is_valid(token):
        return fail('bad token format')

    status_received = kwargs.get('status', None)
    if not status_received:
        return fail('Could not find status field')

    status_fields = ReportToken.parse_response_status(status_received)
    #if not status_received in ReportToken.STATUS_CHOICES:
    if status_fields is None:
        return fail('Unknown status: {}'.format(status_received))

    #Get the ReportToken
    try:
        old_report_token = ReportToken.objects.get(token=token)
    except ObjectDoesNotExist as e:
        return fail('Could not find entry to this token')

    if not old_report_token.active:
        return fail('This token has expired')

    # Deactivate it
    old_report_token.active = False
    old_report_token.save()

    # Get the report
    report_obj = old_report_token.report_related.first()

    # Save the new status and return a new token
    new_report_token = ReportToken(status=status_received, active=True) # Duplicate code
    new_report_token.save()
    report_obj.tokens.add(new_report_token)
    report_obj.save()

    #print ('OLD STATUS:', old_report_token.status)
    #print ('NEW STATUS:', new_report_token.status)

    return success({'token': str(new_report_token.token)})

### END OF WORKFLOWS ###
### START OF VALIDATION CALLBACK ###

@has_data
def tool_validation_status(request, **kwargs):
    '''
    Called from the refresh button on Tool validation
    '''
    tool_argument = kwargs['tool']

    tool = Tool.objects.get(**tool_argument)
    # toolvalidations = ToolValidations.get()
    #print ('TOOL VALIDATION STATUS:')

    ret = {
        'validation_status': tool.last_validation.validation_status if tool.last_validation else 'Unvalidated',
        'validation_created_at': datetime_to_str(tool.last_validation.created_at) if tool.last_validation else None,
        'stderr':tool.last_validation.stderr if tool.last_validation else None,
        'stdout':tool.last_validation.stdout if tool.last_validation else None,
        'errcode':tool.last_validation.errcode if tool.last_validation else None,
    }

    #print (ret)

    return success(ret)

@has_data
def tool_info_validation_queued(request, **kwargs):
    '''
    This is called from angular in order to connect the controller id with the database tool
    '''
    if not 'payload' in kwargs:
        return fail('payload was not found on callback')

    payload = kwargs['payload']

    assert payload['status'] == 'Queued'
    tool = Tool.objects.get(**payload['tool'])
    this_id = payload['id']

    tv = ToolValidations(tool=tool, task_id=this_id, validation_status='Queued')
    tv.save()

    #print (f'Saved ToolValidation Queued with task_id: {this_id}')

    tool.last_validation = tv
    tool.save()


    return success({'last_validation': datetime_to_str(tv.created_at)})

@csrf_exempt
@has_data
def callback(request, **kwargs):
    '''
    Funtion called by conntroller.py
    '''
    #print("--------------- REQUEST FROM CONTROLLER ------------------")
    #print(kwargs)
    remote_address = request.META['REMOTE_ADDR']
    #print (f'Callback from: {remote_address}')

    if not remote_address in ['139.91.190.79']:
        return fail(f'Received callback from unknown remote address: {remote_address}')

    if not 'payload' in kwargs:
        return fail('payload was not found on callback')
    payload = kwargs['payload']

    if not 'status' in payload:
        return fail('status was not found on payload')
    status = payload['status']

    if not status in ['Running', 'Validated', 'Failed']:
        return fail(f'Unknown status: {status}')

    if not 'id' in payload:
        return fail('id was not found on payload')
    this_id = payload['id']
    # Get the stdout stdderr and errorcode

    stdout = payload.get('stdout', None)
    stderr = payload.get('stderr', None)
    errcode = payload.get('errcode', None)

    #print(stdout)
    # Get the tool referring to this task_id
    tool = ToolValidations.get_tool_from_task_id(this_id)
    if tool is None:
        return fail(f'Could not find tool with task_id={this_id}')

    # Create new ToolValidations
    # If stdout is emty , stderr and errcode are empty
    # If status is Queued or Running set this three None
    tv = ToolValidations(tool=tool, task_id=this_id, validation_status=status, stdout= stdout, stderr= stderr, errcode= errcode)
    tv.save()
    #print (f'CALLBACK: Tool: {tool.name}/{tool.version}/{tool.edit}  id: {this_id} status: {status}')
    # Assign tv to tool
    tool.last_validation = tv
    tool.save()

    #print (f'CALLBACK: Tool: {tool.name}/{tool.version}/{tool.edit}  id: {this_id} status: {status}')

    return success()

def tools_show_stdout(request, tools_info_name, tools_info_version, tools_info_edit):
    '''
    URL :
    path(r'tool_stdout/[\\w]+/[\\w\\.]+/[\\d]+/', views.tools_show_stdout), # Show stdout of tool
    '''
    #print (tools_info_name, tools_info_version, tools_info_edit)
    tool_repr = Tool.get_repr(tools_info_name, tools_info_version, tools_info_edit)

    try:
        tool = Tool.objects.get(name=tools_info_name, version=tools_info_version, edit=int(tools_info_edit))
    except ObjectDoesNotExist as e:
        return fail(f'Could not find tool: {tool_repr}')

    if not tool.last_validation:
        return fail(f'Could not find any validation effort for tool: {tool_repr}')

    if not tool.last_validation.stdout:
        return fail(f'Coud not find stdout on the lst validation efoort of tool: {tool_repr}')

    context = {
        'html': convert_ansi_to_html(tool.last_validation.stdout)
    }

    return render(request, 'app/tool_stdout.html', context)

### END OF CALL BACK ###

### REPORTS

def reports_search_2(main_search, request):
    '''
    Collect all reports from main search.
    In contrary to other *_search_2 , we only allow to show reports that belong to the login user!
    '''

    # Return empty results if user is anonymous or not validated
    if request.user.is_anonymous or (not user_is_validated(request)):
        return {
            'main_search_reports_number': 0,
            'reports_search_jstree': [],
        }

    obc_user = OBC_user.objects.get(user=request.user)

    nice_id_Q = Q(nice_id__contains=main_search)
    username_Q = Q(obc_user__user__username__icontains=main_search)
    workflow_Q = Q(workflow__name__icontains=main_search)
    not_unused = Q(tokens__status = ReportToken.UNUSED)
    count_1 = Q(num_tokens = 1)
    user_Q = Q(obc_user = obc_user)

    # We do not want reports that have only one tokens which is "unused"
    results = Report.objects.annotate(num_tokens=Count('tokens')).filter(
        user_Q & 
        (nice_id_Q | workflow_Q | username_Q) & 
        (~(not_unused&count_1))
    )

    # BUILD TREE
    reports_search_jstree = []
    workflows_in_tree = set()
    for report in results:

        # Add the workflow
        workflow = report.workflow
        if not workflow in workflows_in_tree:

            workflows_in_tree.add(workflow)

            to_add = {
                'data': {'name': workflow.name, 'edit': workflow.edit, 'type': 'workflow'},
                'text': workflow_text_jstree(workflow) + jstree_icon_html('workflows'),
                'id': workflow_id_jstree(workflow, g['SEARCH_REPORT_TREE_ID']),
                'parent': workflow_id_jstree(workflow.forked_from, g['SEARCH_REPORT_TREE_ID']) if workflow.forked_from else '#',
                'state': { 'opened': True},
            }
            reports_search_jstree.append(to_add)

        # Add the report
        to_add = {
            'data': {'run': report.nice_id, 'type': 'report'},
            'text': report.nice_id + jstree_icon_html('reports'),
            'id': report_id_jstree(report, g['SEARCH_REPORT_TREE_ID']),
            'parent': workflow_id_jstree(workflow, g['SEARCH_REPORT_TREE_ID']),
            'state': { 'opened': True},
        }
        reports_search_jstree.append(to_add)


    ret = {
        'main_search_reports_number': results.count(),
        'reports_search_jstree': reports_search_jstree,
    }

    return ret

@has_data
def reports_search_3(request, **kwargs):
    '''
    Search for an individual report
    '''

    if request.user.is_anonymous or (not user_is_validated(request)):
        return fail('You are either anonymous or your email is not validated. You do not have access to reports.')

    obc_user = OBC_user.objects.get(user=request.user)

    run = kwargs['run']

    try:
        report = Report.objects.get(nice_id=run, obc_user=obc_user)
    except ObjectDoesNotExist as e:
        return fail('Could not find report, or you do not have access.')
    workflow = report.workflow

    #Get all tokens
    tokens = [{
        'status': token.status,
        'created_at': datetime_to_str(token.created_at),
        'token': str(token.token),
        #'node_anim_id': create_node_anim_id(token.status), # the parameter passed to nodeAnimation
        'node_anim_params': ReportToken.parse_response_status(token.status), # the parameter passed to nodeAnimation_public
    } for token in report.tokens.all().order_by('created_at') if token.status != ReportToken.UNUSED]

    # Check if ReportToken.parse_response_status successfully parsed tokens
    # This is a sanity check
    for token in tokens:
        if token['node_anim_params'] is None:
            return fail('Error 8915: could not parse token: {}'.format(token['status']))

    ret = {
        'report_workflow_name': workflow.name,
        'report_workflow_edit': workflow.edit,
        'report_username': report.obc_user.user.username,
        'report_created_at': datetime_to_str(report.created_at),
        'report_tokens': tokens,
        'report_client': bool(report.client),
        'report_url': report.url, # The url with the results
        'report_log_url': report.log_url, # The url with the logs
        'report_visualization_url': report.visualization_url, # The url for monitoring of the execution progress (i.e. from airflow)
        'report_monitor_url': report.monitor_url,
        'report_client_status': report.client_status,
        'workflow' : simplejson.loads(workflow.workflow),
    }

    return success(ret)

@has_data
def reports_refresh(request, **kwargs):
    '''
    path: report_refresh/
    Get an update for a report
    report_workflow_action : 1 = refresh , 2 = pause , 3 = resume

    * Reports --> Refresh --> button click
    * In cases when a workflow is executed from the OBC client. Update the status
    * action: 
    * 1 --> refresh
    * 2 --> pause
    * 3 --> resume
    * 4 --> Delete
    */

    '''

    report_workflow_name = kwargs['report_workflow_name']
    report_workflow_edit = int(kwargs['report_workflow_edit'])
    nice_id = kwargs['report_workflow_run']
    report_workflow_action = kwargs['report_workflow_action']

    # Get the report
    report = Report.objects.get(nice_id=nice_id)
    previous_status = report.client_status

    if request.user.is_anonymous:
        return fail('Please log in to update the status of a Report')

    # Get this user
    obc_user = OBC_user.objects.get(user=request.user)
    if obc_user != report.obc_user:
        return fail('Cannot edit a report of another user.')

    if not report.client:
        if report_workflow_action == 4:
            # Deleting a report that has not been associated with any client.
            # Just delete it..
            report.delete()
            return success()

    if report_workflow_action == 4:
        # Delete it..
        report.delete()
        return success()     

    # Get the url of the client
    client_url = report.client.client

    if report_workflow_action == 1:
        # Refresh
        # Get the url to check status
        url = g['create_client_check_status_url'](client_url, nice_id)
        #print ('CHECK STATUS URL:')
        #print (url)
    elif report_workflow_action == 2:
        # Pause
        url = g['create_client_pause_url'](client_url, nice_id)
        #print ('PAUSE URL:')
        #print (url)
    elif report_workflow_action == 3:
        # Resume
        url = g['create_client_resume_url'](client_url, nice_id)
        #print ('RESUME URL:')
        #print (url)
    elif report_workflow_action == 4:
        # Delete
        url = g['create_client_abort_url'](client_url, nice_id)
        #print ('ABORT URL:')
        #print (url)
    else:
        return fail('Error 5821: {}'.format(str(report_workflow_action)))

    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        return fail('Could not establish a connection with client')

    if not r.ok:
        return fail('Could not send to URL: {} . Error code: {}'.format(client_url, r.status_code))

    data_from_client = r.json()
    #print ('Data from client:')
    #print (data_from_client)
    # {"error": "Dag id mitsos not found"}

    if report_workflow_action == 1: # refresh
        if type(data_from_client) is dict:
            if 'error' in data_from_client:
                if 'not found' in data_from_client['error']:
                    status = 'NOT FOUND'
                else:
                    return fail('Error: 1111')
            else:
                return fail('Error: 1112')
        if not type(data_from_client) is list:
            return fail('Error: 1113')

        if len(data_from_client) != 1:
            return fail('Error: 1114')

        if not type(data_from_client[0]) is dict:
            return fail('Error: 1115')

        if not 'state' in data_from_client[0]:
            return fail('Error: 1116')

        if data_from_client[0]['state'] == 'running':
            status = 'RUNNING'

        elif data_from_client[0]['state'] == 'failed':
            status = 'FAILED'

        elif data_from_client[0]['state'] == 'success':
            status = 'SUCCESS'

        elif data_from_client[0]['state'] == 'paused':
            status = 'PAUSED'

        else:
            return fail('Unknown status:', data_from_client[0]['state'])
    elif report_workflow_action in [2, 3]: # 2 = pause , 3 = resume
        if not type(data_from_client) is dict:
            return fail('Error: 1119')

        if not 'response' in data_from_client:
            return fail('Error: 1120')

        if data_from_client['response'] != 'ok':
            return fail('Error 1121')

        if report_workflow_action == 2:
            status = 'PAUSE_SUBMITTED'
        elif report_workflow_action == 3:
            status = 'RESUME_SUBMITTED'
        else:
            return fail('Error 1122')
    elif report_workflow_action == 4:
        if not type(data_from_client) is dict:
            return fail('Error: 1123')
        if not 'status' in data_from_client:
            return fail('Error 1124')
        if data_from_client['status'] != 'success':
            return fail('Client responded with an error message: {}'.format(data_from_client['status']))

        # Delete it..
        report.delete()
        return success()

    # Update report object
    report.client_status = status
    report.save()

    # If we finished, then create the URL that contains the report
    report_url = None
    log_url = None

    if status == 'SUCCESS':
        report_url = g['create_client_download_report_url'](client_url, nice_id)
    if status in ['SUCCESS', 'FAILED']:
        log_url = g['create_client_download_log_url'](client_url, nice_id)

    report.url = report_url
    report.log_url = log_url

    report.save()

    ret = {
        'report_url': report_url,
        'report_log_url': log_url,
        'report_client_status': status,
    }

    return success(ret)

### END OF REPORTS

### REFERENCES


def bibtex_to_html(content):
    '''
    Convert bibtex to html
    Adapted from: http://pybtex-docutils.readthedocs.io/en/latest/quickstart.html#overview
    '''

    # Ideally we could have these variables set only once,
    # But it is not allowed to have multiuple entries.
    pybtex_style = pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')()
    pybtex_html_backend = pybtex.plugin.find_plugin('pybtex.backends', 'html')()
    pybtex_parser = pybtex.database.input.bibtex.Parser()

    try:
        data = pybtex_parser.parse_stream(six.StringIO(content))
    except pybtex.scanner.TokenRequired as e:
        return False, 'Error during parsing BIBTEX: ' + str(e), None

    if len(data.entries) == 0:
        return False, 'Could not find any BIBTEX entry', None

    if len(data.entries) > 1:
        return False, 'Detected more than one entries in BIBTEX. Only one is allowed', None

    fields = {}
    for entry_key, entry_value in data.entries.items():
        fields[entry_key] = {}
        for field_key, field_value in entry_value.fields.items():
            fields[entry_key][field_key] = field_value

    data_formatted = pybtex_style.format_entries(six.itervalues(data.entries))

    output = io.StringIO()
    try:
        pybtex_html_backend.write_to_stream(data_formatted, output)
    except pybtex.style.template.FieldIsMissing as e:
        return False, str(e), None # This DOI for example: 10.1038/nature09298 . Error: missing author in 2010.
    html = output.getvalue()

    html_s = html.split('\n')
    html_s = html_s[9:-2]
    new_html = '\n'.join(html_s).replace('<dd>', '').replace('</dd>', '')

    return True, new_html, fields

def get_fields_from_bibtex_fields(fields, str_response):
    '''
    Reads fields from a bibtex formated in html

    TEST 1
    @article{Barrangou_2007,
    doi = {10.1126/science.1138140},
    url = {https://doi.org/10.1126%2Fscience.1138140},
    year = 2007,
    month = {mar},
    publisher = {American Association for the Advancement of Science ({AAAS})},
    volume = {315},
    number = {5819},
    pages = {1709--1712},
    author = {R. Barrangou and C. Fremaux and H. Deveau and M. Richards and P. Boyaval and S. Moineau and D. A. Romero and P. Horvath},
    title = {{CRISPR} Provides Acquired Resistance Against Viruses in Prokaryotes},
    journal = {Science}
}
    '''

    name = list(fields.keys())[0] # first key
    title = fields[name].get('title', '')
    # check if it is enclised in brackets {title}
    # Remove '{' and '}' from tite
    #m = re.match(r'{(.*)}', title)
    #if m:
    #    title = m.group(1)
    title = title.replace('{', '').replace('}', '')

    doi = fields[name].get('doi', '')
    if not doi:
        doi = fields[name].get('DOI', '')

    url = fields[name].get('url', '')
    if not url:
        url = fields[name].get('URL', '')

    ret = {
        'references_name': name,
        'references_formatted': str_response,
        'references_title': title,
        'references_doi': doi,
        'references_url': url,
    }

    return ret


@has_data
def references_generate(request, **kwargs):
    '''
    Generate HTML reference from bibtex
    '''

    references_BIBTEX = kwargs['references_BIBTEX']
    suc, str_response, fields = bibtex_to_html(references_BIBTEX)

    if not suc:
        return fail(str_response)

    ret = get_fields_from_bibtex_fields(fields, str_response)
    return success(ret)

@has_data
def references_process_doi(request, **kwargs):
    '''
    Generate a BIBTEX from DOI
    '''

    references_doi = kwargs.get('references_doi', '')
    if not references_doi:
        return fail('DOI is empty')

    doi_url =  "http://dx.doi.org/" + references_doi
    if not valid_url(doi_url):
        return fail('Invalid DOI. Example of valid DOI: 10.1126/science.1138140')

    bibtex = resolve_doi(references_doi)
    #print ('bibtex:')
    #print (bibtex)
    if not bibtex:
        return fail('Could not get bibliographic information for this DOI')

    suc, str_response, fields = bibtex_to_html(bibtex)
    if not suc:
        return fail('The BIBTEX returned from this doi was invalid: ' + str_response) # This should never happen..

    ret = get_fields_from_bibtex_fields(fields, str_response)
    ret['references_BIBTEX']  = bibtex

    return success(ret)


@has_data
def references_add(request, **kwargs):
    '''
    Add a new reference
    '''

    # Check user
    if request.user.is_anonymous:
        return fail('Please login to create References')

    # Check if user is validated
    if not user_is_validated(request):
        return fail('Please validate your email to create new references ' + validate_toast_button());

    references_name = kwargs.get('references_name', '')
    if not references_name:
        return fail('References Name is required')
    if not re.match(r'\w+', references_name):
        return fail('Invalid Reference Name. It should contain only letters and numbers')

    references_title = kwargs.get('references_title', '')
    if not references_title:
        return fail('References Title is required')

    references_url = kwargs.get('references_url', '')
    if not references_url:
        return fail('References URL is required')
    #Is there a reference with the same url?
    url_ref = Reference.objects.filter(url=references_url)
    if url_ref.exists():
        return fail('A Reference with this URL already exists: {}'.format(url_ref.first().name))

    # References are case insensitive!
    references_name = references_name.lower()

    #Are there any references with this name?
    if Reference.objects.filter(name=references_name).exists():
        return fail('A Reference with this name already exists')

    # Is there a reference with the same SOI?
    references_doi = kwargs.get('references_doi', None)
    if references_doi:
        doi_ref = Reference.objects.filter(doi=references_doi)
        if doi_ref.exists():
            return fail('A Reference with this DOI already exists: {}'.format(doi_ref.first().name))


    # Check bibtex
    references_BIBTEX = kwargs.get('references_BIBTEX', '')
    reference_fields = []
    html = None
    if references_BIBTEX:
        suc, str_response, fields = bibtex_to_html(references_BIBTEX)
        if not suc:
            return fail(str_response)

        # It succeeded to parse BIBTEX. Get the html
        html = str_response
        name = list(fields.keys())[0] # first key

        #Create (or get) ReferenceFields
        reference_fields = [ReferenceField.objects.get_or_create(
            key=reference_key,
            value=reference_value,
            )[0] for reference_key, reference_value in fields[name].items()]

    # Create Reference object
    reference = Reference(
        obc_user = OBC_user.objects.get(user=request.user),
        name = references_name,
        url = references_url,
        title = references_title,
        doi = references_doi,
        bibtex = references_BIBTEX if references_BIBTEX else None,
        html = html,
        notes = kwargs.get('references_notes', None),
    )
    reference.save()

    # Add fields from BIBTEX
    reference.fields.add(*reference_fields)
    reference.save()

    ret = {
        'references_formatted': html,
        'references_created_at': datetime_to_str(reference.created_at),
        'references_username': request.user.username,
    }

    return success(ret)

def references_search_2(
    main_search,
    ):
    '''
    Collect all references from main search
    '''

    name_Q = Q(name__icontains=main_search)
    html_Q = Q(html__icontains=main_search)
    username_Q = Q(obc_user__user__username__icontains=main_search)

    results = Reference.objects.filter(name_Q | html_Q | username_Q)
    references_search_jstree = []

    for result in results:
        to_add = {
            'data': {'name': result.name},
            'text': result.name + jstree_icon_html('references'),
            'id': result.name,
            'parent': '#',
            'state': { 'opened': True},
        }
        references_search_jstree.append(to_add)

    ret = {
        'main_search_references_number': results.count(),
        'references_search_jstree': references_search_jstree,
    }

    return ret

def qa_get_root_comment(comment):
    '''
    Take a comment in a nested thread and get the root comment
    '''

    if not comment.parent:
        return comment

    return qa_get_root_comment(comment.parent)

def qa_search_2(main_search, *, request):
    '''
    Collect all Q&A from main search
    '''
    obc_user = get_obc_user(request)
    title_Q = Q(title__icontains=main_search)
    comment_Q = Q(comment__icontains=main_search)
    username_Q = Q(obc_user__user__username__icontains=main_search)

    results = Comment.objects.filter(title_Q | comment_Q | username_Q)

    qa_search_tree = []
    entries_in_tree = set()
    for result in results:
        # Get the root message
        result_parent = qa_get_root_comment(result)

        #Exclude comments on private ROs
        to_continue = False
        for comment_attr in ['tool_comment', 'workflow_comment']: # Reverse relationships from Tools/WF --> Comment
            target_m2m_ROs = getattr(result_parent, comment_attr)
            if target_m2m_ROs.exists():
                RO = target_m2m_ROs.first()
                if (
                    RO.visibility != str(VisibilityOptions.PUBLIC_CODE) and
                    RO.obc_user != obc_user
                ):
                    to_continue = True
                    break
        if to_continue:
            continue

        #Is this on the tree?
        if result_parent.pk in entries_in_tree:
            # It is already in the tree
            continue
        else:
            entries_in_tree.add(result_parent.pk)

        # Remove <a></a> hyperlinks from question answers
        # See issue #106
        if re.search(r'<a.*a>', result_parent.title):
            to_substitute = re.search(r'<a.*a>', result_parent.title).group(0)
            substitute_with = re.search(r'>(.*)</a>', re.search(r'<a.*a>', result_parent.title).group(0)).group(1)
            result_parent.title = result_parent.title.replace(to_substitute, substitute_with)

        to_add = {
            'data': {'id': result_parent.pk},
            'text': result_parent.title + jstree_icon_html('qas'),
            'id': str(result_parent.pk),
            'parent': '#',
            'state': { 'opened': True},
        }
        qa_search_tree.append(to_add)

    ret = {
        'main_search_qa_number': len(qa_search_tree),
        'qa_search_jstree': qa_search_tree,
    }

    return ret


@has_data
def references_search_3(request, **kwargs):
    '''
    Fetch the data for a unique reference
    '''

    name = kwargs.get('name', '')
    try:
        reference = Reference.objects.get(name__iexact=name)
    except ObjectDoesNotExist as e:
        return fail('Could not find Reference') # This should never happen..

    # Has this reference been claimed by the user ?
    obc_user = get_obc_user(request)
    claimed = bool(
            obc_user and
            reference.doi and
            obc_user.references.filter(pk=reference.pk).exists()
    )

    # List of all usernames that claimed this reference
    references_claim_list = list(
        reference
        .users_authored_me
        .all()
        .values_list('user__username', flat=True)
    )

    ret = {
        'references_name': reference.name,
        'references_title': reference.title,
        'references_url': reference.url,
        'references_doi': reference.doi,
        'references_notes': reference.notes,
        'references_BIBTEX': reference.bibtex,
        'references_html': reference.html,
        'references_created_at': datetime_to_str(reference.created_at),
        'references_username': reference.obc_user.user.username,
        'references_claimed': claimed,
        'references_claim_list': references_claim_list,
    }

    return success(ret)

### END OF REFERENCES

### SEARCH

@has_data
def all_search_2(request, **kwargs):
    '''
    Called when there is a key change in main search
    '''
    main_search = kwargs.get('main_search', '')

    main_search_slash_count = main_search.count('/')

    # Check for slashes
    if main_search_slash_count == 0:

        tools_search_name = main_search
        tools_search_version = ''
        tools_search_edit = ''

        workflows_search_name = main_search
        workflows_search_edit = ''

    elif main_search_slash_count == 1:

        tools_search_name, tools_search_version = main_search.split('/')
        tools_search_name = tools_search_name.strip()
        tools_search_version = tools_search_version.strip()
        tools_search_edit = 0 # Do not apply search

        workflows_search_name, workflows_search_edit = main_search.split('/')
        workflows_search_name = workflows_search_name.strip()
        workflows_search_edit = workflows_search_edit.strip()
        try:
            workflows_search_edit = int(workflows_search_edit)
        except ValueError:
            workflows_search_edit = 0 # do not apply search on workflow edit
    elif main_search_slash_count == 2:
        # Practically apply only tool search
        tools_search_name, tools_search_version, tools_search_edit = main_search.split('/')
        tools_search_name = tools_search_name.strip()
        tools_search_version = tools_search_version.strip()
        try:
            tools_search_edit = int(tools_search_edit)
        except ValueError:
            tools_search_edit = 0 # Do not apply search no tool edit

        workflows_search_name = ''
        workflows_search_edit = -1
    else:
        tools_search_name = ''
        tools_search_version = ''
        tools_search_edit = -1

        workflows_search_name = ''
        workflows_search_edit = -1

    ret = {}

    #Get tools
    for key, value in tools_search_2(tools_search_name, tools_search_version, tools_search_edit, request=request).items():
        ret[key] = value

    #Get workflows
    for key, value in workflows_search_2(workflows_search_name, workflows_search_edit, request=request).items():
        ret[key] = value

    #Get reports
    for key, value in reports_search_2(main_search, request).items():
        ret[key] = value

    #Get references
    for key, value in references_search_2(main_search).items():
        ret[key] = value

    #Get users
    for key, value in users_search_2(main_search).items():
        ret[key] = value

    # Get QAs
    for key, value in qa_search_2(main_search, request=request).items():
        ret[key] = value

    return success(ret)


### END OF SEARCH

### Q&A

@has_data
def qa_add_1(request, **kwargs):
    '''
    Called from qa_add_1/
    '''
    qa_title = kwargs.get('qa_title', '')
    if not qa_title:
        return fail('Title should not be empty')

    qa_comment = kwargs.get('qa_comment', '')
    if not qa_comment:
        return fail('Comment should not be empty')
    qa_comment_html = markdown(qa_comment)

    if request.user.is_anonymous:
        return fail('Please login to post a new question')
    user = request.user

    # We cannot have the same comment title more than once
    if Comment.objects.filter(title__iexact=qa_title).exists():
        return fail('A comment with this title already exists!')

    #Create a new comment
    comment = Comment(
        obc_user=OBC_user.objects.get(user=user),
        comment=qa_comment,
        comment_html = qa_comment_html,
        title=qa_title,
        parent=None,
        upvotes=0,
        downvotes=0,
    )
    comment.save()

    ret = {
        'id': comment.pk,
        'comment_html': qa_comment_html,
        'qa_created_at': datetime_to_str(comment.created_at), # Issue 223
    }

    return success(ret)

def qa_create_thread(comment, obc_user = None):
    '''
    Recursive
    Create the children thread of a comment
    '''
    ret = []
    for child in comment.children.all():
        to_add = {
            'comment': child.comment,
            'comment_html': child.comment_html,
            'opinion': child.opinion,
            'score': child.upvotes - child.downvotes,
            'id': child.pk,
            'replying': False,
            'voted' : is_comment_updownvoted(obc_user, child),
            'children': qa_create_thread(child, obc_user),
            'username': child.obc_user.user.username,
            'created_at': datetime_to_str(child.created_at),
        }
        ret.append(to_add)
    return ret


@has_data
def qa_search_3(request, **kwargs):
    '''
    path: qa_search_3/
    From angular: Fetch the data from a single Q&A and update the UI
    Get a unique Q&A thread
    '''

    id_ = kwargs.get('qa_id', None)
    if not id_:
        return fail('Could not find Q&A id')

    try:
        comment = Comment.objects.get(pk=id_)
    except ObjectDoesNotExist as e:
        return fail('Could not find comment database object')

    # Get obc_user
    if request.user.is_anonymous:
        obc_user = None
    else:
        obc_user = OBC_user.objects.get(user=request.user)


    ret = {
        'qa_title': comment.title,
        'qa_comment': comment.comment,
        'qa_comment_html': comment.comment_html,
        'qa_score': comment.upvotes - comment.downvotes,
        'qa_id': comment.pk,
        'qa_thread': qa_create_thread(comment, obc_user),
        'qa_voted': is_comment_updownvoted(obc_user, comment),
        'qa_username': comment.obc_user.user.username,
        'qa_created_at': datetime_to_str(comment.created_at),
    }

    #print (simplejson.dumps(ret, indent=4))

    return success(ret)


@has_data
def get_pk_from_root_comment(request, **kwargs):
    '''
    path: get_pk_from_root_comment/
    '''

    comment_id = int(kwargs['comment_id'])
    pk_type = kwargs['type']

    try:
        if pk_type == 'tool':
            tool = Tool.objects.filter(comment_id=comment_id).first()
            pk = tool.id
        elif pk_type == 'workflow':
            workflow = Workflow.objects.filter(comment_id=comment_id).first()
            pk = workflow.id
        else:
            return fail('ERROR: 2919 . Unknown pk_type: {}'.format(pk_type))
    except ObjectDoesNotExist as e:
        return fail('Could not find tool or workflow database object')

    ret = {
        'pk': pk,
    }
    return success(ret)

@has_data
def gen_qa_search_3(request, **kwargs):
    '''
    PATH: gen_qa_search_3/
    Generic version of qa_search_3
    Get a unique Q&A thread
    '''

    # Get arguments
    object_pk = kwargs['object_pk'] # This is the primary key of the tool/workflow
    qa_type = kwargs['qa_type']

    if qa_type == 'tool':
        commentable = Tool.objects.get(pk=object_pk)
    elif qa_type == 'workflow':
        commentable = Workflow.objects.get(pk=object_pk)
    else:
        return fail('ERROR: 2918 . Unknown qa_type: {}'.format(qa_type))

    # Get obc_user
    if request.user.is_anonymous:
        obc_user = None
    else:
        obc_user = OBC_user.objects.get(user=request.user)

    # Get the thread of this comment
    ret = {
        'qa_id': commentable.comment.pk,
        'qa_thread': qa_create_thread(commentable.comment, obc_user),
        'qa_voted': is_comment_updownvoted(obc_user, commentable.comment),
        'qa_score': commentable.comment.upvotes - commentable.comment.downvotes,
        'qa_username': commentable.comment.obc_user.user.username,
        'qa_created_at': datetime_to_str(commentable.comment.created_at),
    }

    return success(ret)


@has_data
def qa_add_comment(request, **kwargs):
    '''
    Add a comment at a Q&A question
    '''
    if request.user.is_anonymous:
        return fail('Please login to add a new comment')

    if not user_is_validated(request):
        return fail('Please validate your email to add a new comment' + validate_toast_button());

    id_ = kwargs.get('qa_id', None)
    if id_ is None:
        return fail('Could not find Q&A id')

    current_comment = kwargs.get('qa_comment', None)
    if current_comment is None:
        return fail('Could not find Q&A new comment')
    elif not current_comment.strip():
        return fail('Comment cannot be empty')

    current_comment_html = markdown(current_comment)

    opinion = kwargs.get('qa_opinion', None)
    if not opinion in ['solution', 'note', 'agree', 'disagree']:
        return fail('Error 9177. opinion value unknown')

    try:
        parent_comment = Comment.objects.get(pk=id_)
    except ObjectDoesNotExist as e:
        return fail('ERROR: 8991. Could not find comment database object')

    new_comment = Comment(
        obc_user = OBC_user.objects.get(user=request.user),
        comment = current_comment,
        comment_html = current_comment_html,
        opinion = opinion,
        parent = parent_comment,
        upvotes = 0,
        downvotes = 0,
    )
    new_comment.save()
    parent_comment.children.add(new_comment)
    parent_comment.save()

    ret = {
        'comment_html': current_comment_html,
    }

    return success(ret)

@has_data
def gen_qa_add_comment(request, **kwargs):
    '''
    PATH: gen_qa_add_comment/
    Generic version of the qa_add_comment
    Add a comment at a Q&A question
    '''
    if request.user.is_anonymous:
        return fail('Please login to add a new comment')

    if not user_is_validated(request):
        return fail('Please validate your email to add a new comment ' + validate_toast_button());

    comment_pk = kwargs['comment_pk']
    object_pk = kwargs['object_pk']
    qa_comment = kwargs['qa_comment']
    qa_opinion = kwargs['qa_opinion']
    qa_type = kwargs['qa_type']

    current_comment_html = markdown(qa_comment)

    # Get the tool
    if qa_type == 'tool':
        commentable = Tool.objects.get(pk=object_pk)
    elif qa_type == 'workflow':
        commentable = Workflow.objects.get(pk=object_pk)
    else:
        return fail('ERROR: 2918 . Unknown qa_type: {}'.format(qa_type))

    # Get the root comment
    if comment_pk is None:
        root_comment = commentable.comment
    else:
        root_comment = Comment.objects.get(pk=comment_pk)

    new_comment = Comment(
        obc_user=OBC_user.objects.get(user=request.user),
        comment = qa_comment,
        opinion = qa_opinion,
        comment_html = current_comment_html,
        parent = root_comment,
        upvotes = 0,
        downvotes = 0,
    )
    new_comment.save()
    root_comment.children.add(new_comment)
    root_comment.save()

    ret = {
        'comment_html': current_comment_html,
    }

    return success(ret)

def is_comment_updownvoted(obc_user, comment):
    '''
    Has this user upvoted or downvoted this comment?
    '''

    if obc_user is None:
        return {'up': False, 'down': False}

    try:
        vote = UpDownCommentVote.objects.get(obc_user=obc_user, comment=comment)
    except ObjectDoesNotExist as e:
        return {'up': False, 'down': False}

    return {'up': vote.upvote, 'down': not vote.upvote}

@has_data
def updownvote_comment(request, **kwargs):
    '''
    url: updownvote_comment/
    '''

    if request.user.is_anonymous:
        return fail('Please login to upvote/downvote comments')

    if not user_is_validated(request):
        return fail('Please validate your email to upvote/downvote' + validate_toast_button());

    comment_id = int(kwargs['comment_id'])
    upvote = kwargs['upvote']
    assert upvote in [True, False]

    # Get the comment
    comment = Comment.objects.get(pk=comment_id)

    # Get the user
    obc_user = OBC_user.objects.get(user=request.user)

    # Check if this is already a vote
    try:
        vote = UpDownCommentVote.objects.get(obc_user=obc_user, comment=comment)
    except ObjectDoesNotExist as e:
        #Create the UpDownCommentVote object
        vote = UpDownCommentVote(
            obc_user = obc_user,
            comment = comment,
            upvote = upvote,
        )
        vote.save()
        voted = {'up': upvote, 'down': not upvote}
    else:
        # No exception happened. A vote for this comment already exists
        if vote.upvote and upvote:
            # You cannot upvote twice!
            return fail('Already upvoted')
        if (not vote.upvote) and (not upvote): # DeMorgan anyone?
            # You cannot downvote twice!
            return fail('Already downvoted')

        # This post was upvoted and now downvoted from the same user (or vice-versa)!
        # Just delete the vote
        vote.delete()
        voted = {'up': False, 'down': False} # Neither upvoted nor downvoted

    #Add the score
    if upvote:
        comment.upvotes += 1
    else:
        comment.downvotes += 1
    comment.save()

    ret = {
        'score': comment.upvotes - comment.downvotes,
        'voted': voted
    }

    return success(ret)

@has_data
def updownvote_tool_workflow(request, **kwargs):
    '''
    Called from $scope.updownvote_tool_workflow
    Called when a user hit the buttons for upvote or downvote or a tool or for a workflow
    '''

    if request.user.is_anonymous:
        return fail('Please login to upvote/downvote Research Objects')

    if not user_is_validated(request):
        return fail('Please validate your email to upvote/downvote' + validate_toast_button());

    # Get the user
    obc_user = OBC_user.objects.get(user=request.user)

    ro = kwargs.get('ro', '')
    if not ro:
        return fail('Error 1023')
    if not ro in ['tool', 'workflow']:
        return fail('Error 1026')

    ro_obj = kwargs.get('ro_obj', '')
    if not ro_obj:
        return fail('Error 1024')
    upvote = kwargs.get('upvote', '')
    if upvote == '':
        return fail('Error 1025')

    if not upvote in [True, False]:
        return fail('Error 1027')

    # Get the tool/workflow database object
    ro_table = {
        'tool': Tool,
        'workflow': Workflow,
    }[ro]

    ro_ud_table = {
        'tool': UpDownToolVote,
        'workflow': UpDownWorkflowVote,
    }[ro]

    try:
        ro_table_obj = ro_table.objects.get(**ro_obj)
    except ObjectDoesNotExist as e:
        return fail('Error 1027')

    # Check if this user has already upvoted or downvoted this RO
    try:
        ro_ud_table_obj = ro_ud_table.objects.get(**{
            'obc_user': obc_user,
            ro: ro_table_obj,
        })
    except ObjectDoesNotExist as e:
        # This user has **not** upvoted or downvoted this RO
        pass
    else:
        # This user has upvoted or downvoted this RO in the past
        if ro_ud_table_obj.upvote and upvote:
            return fail('You cannot upvote twice')
        elif (not ro_ud_table_obj.upvote) and (not upvote):
            return fail('You cannot downvote twice')
        elif ro_ud_table_obj.upvote and (not upvote):
            # Delete upvote vote!
            ro_ud_table_obj.delete()

            # Update votes
            ro_table_obj.upvotes -= 1
            ro_table_obj.save()
            return success({
                'score': ro_table_obj.upvotes-ro_table_obj.downvotes,
                'voted': {'up': False, 'down': False},
                })

        elif (not ro_ud_table_obj.upvote) and upvote:
            # Delete downvote vote
            ro_ud_table_obj.delete()

            ro_table_obj.downvotes -= 1
            ro_table_obj.save()
            return success({
                'score': ro_table_obj.upvotes-ro_table_obj.downvotes,
                'voted': {'up': False, 'down': False},
                })

    #This user has not upvoted or downvoted before this RO
    #Create a new vote database object
    new_vote_obj = ro_ud_table(**{
        'obc_user': obc_user,
        ro: ro_table_obj,
        'upvote': upvote,
        })
    new_vote_obj.save()

    # Change the upvote / downvote counter of this research object
    if upvote:
        ro_table_obj.upvotes += 1
    else:
        ro_table_obj.downvotes += 1
    ro_table_obj.save()

    ret = {
        'score': ro_table_obj.upvotes-ro_table_obj.downvotes,
        'voted': {'up': upvote, 'down': not upvote},
    }

    return success(ret)

@has_data
def markdown_preview(request, **kwargs):
    text = kwargs.get('text', '')

    if not type(text) is str:
        return fail('Error 2871')

    ret = {
        'html': markdown(text),
    }

    return success(ret)

@has_data
def edit_comment(request, **kwargs):
    '''
    url: edit_comment/
    '''

    if request.user.is_anonymous:
        return fail('Please login to upvote/downvote comments')

    if not user_is_validated(request):
        return fail('Please validate your email to edit the comment.' + validate_toast_button());

    comment_id = int(kwargs['comment_id'])
    new_html = kwargs['new_html']
    is_root = kwargs['is_root']
    comment_type = kwargs.get('comment_type')

    # Get the comment
    comment = Comment.objects.get(pk=comment_id)

    # Get the user
    obc_user = OBC_user.objects.get(user=request.user)

    if comment.obc_user.id != obc_user.id:
        return fail("You don't have the permission to edit this comment!")

    if not is_root:
        comment.comment = markdown(new_html)
        comment.comment_html = new_html
        if comment_type in ['solution', 'note', 'agree', 'disagree']:
            comment.opinion = comment_type
    else:
        comment.title = new_html
    comment.save()

    ret = {
        'message': 'The comment has been updated!'
    }

    return success(ret)

### END OF Q&A
### VIEWS END ######
