
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

#Import database objects
from app.models import OBC_user, Tool, Workflow, Variables, ToolValidations, \
    OS_types, Keyword, Report, ReportToken, Reference, ReferenceField, Comment

# Email imports
import smtplib
from email.message import EmailMessage

# System imports 
import io
import os
import re
import six
import uuid
import hashlib
#import datetime # Use timezone.now()

import logging # https://docs.djangoproject.com/en/2.1/topics/logging/

from collections import Counter
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


__version__ = '0.0.4rc'

# Get an instance of a logger
logger = logging.getLogger(__name__)

#GLOBAL CONSTANTS
g = {
    'SERVER': 'https://www.openbio.eu',
    'EMAIL': 'info@swww.openbio.eu',
    'ADMIN': 'kantale@ics.forth.gr', # In case the email fail, use this instead

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
    'jstree_icons': {
        'tools': 'settings',
        'workflows': 'device_hub',
        'reports': 'description',
        'references': 'link',
        'users': 'person',
        'qas': 'forum',
    },
    'url_validator': URLValidator(), # Can be customized: URLValidator(schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))
}

### HELPING FUNCTIONS AND DECORATORS #####

def md5(t):
    '''
    Return the md5 hash of this string
    '''
    return hashlib.md5(t.encode("utf-8")).hexdigest()

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
                        kwargs[k] = request.GET[k]
                        #print ("GET: {} == {}".format(k, kwargs[k]))

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


def workflow_text_jstree(workflow):
    '''
    The JS tree workflow text
    '''
    return '/'.join(map(str, [workflow.name, workflow.edit]))

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

def tool_variable_text_jstree(variable):
    '''
    The JSTree variable text
    '''
    return '{}:{}'.format(variable.name, variable.description)

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

def tool_build_dependencies_jstree(tool_dependencies, add_variables=False):
    '''
    Build JS TREE from tool_dependencies
    ATTENTION: THIS IS NOT GENERIC!!! 
    IT uses g['DEPENDENCY_TOOL_TREE_ID']. 
    '''

    tool_dependencies_jstree = []
    for tool_dependency in tool_dependencies:
        tool_dependencies_jstree.append({

            'data': {
#                    'name': tool_dependency['dependency'].name,
#                    'version': tool_dependency['dependency'].version,
#                    'edit': tool_dependency['dependency'].edit,
                    'type': 'tool',
             },
            'text': tool_text_jstree(tool_dependency['dependency']),
            'id': tool_id_jstree(tool_dependency['dependency'], g['DEPENDENCY_TOOL_TREE_ID']),
            'parent': tool_id_jstree(tool_dependency['dependant'], g['DEPENDENCY_TOOL_TREE_ID']) if tool_dependency['dependant'] else '#',
            'type': 'tool', ### This is redundant with ['data']['type'], but we need it because 
                            ### The node[0].data.type is checked in $scope.tools_var_jstree_model. 
                            ### See also issue #93

            'name': tool_dependency['dependency'].name,
            'version': tool_dependency['dependency'].version,
            'edit': tool_dependency['dependency'].edit,



        })

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
                    'text': tool_variable_text_jstree(variable),
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

@has_data
def users_search_3(request, **kwargs):
    '''
    Get profile info for a single user
    '''

    username = kwargs.get('username', '')
    if not username:
        return fail('Could not get username')

    try:
        u = OBC_user.objects.get(user__username__iexact=username)
    except ObjectDoesNotExist as e:
        return fail('Could not find user with this username')

    ret = {
        'profile_firstname': u.first_name,
        'profile_lastname': u.last_name,
        'profile_website': u.website,
        'profile_affiliation': u.affiliation,
        'profile_publicinfo': u.public_info,
        'profile_created_at': datetime_to_str(u.user.date_joined), # https://docs.djangoproject.com/en/2.2/ref/contrib/auth/#django.contrib.auth.models.User.date_joined
    }

    # We fetch mail only for registered user 
    if username == request.user.username:
        ret['profile_email'] = u.user.email
    else:
        ret['profile_email'] = ''

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


### END OF USERS 

def index(request):
    '''
    View url: ''
    '''

    context = {}

    # Is this user already logged in?
    # https://stackoverflow.com/questions/4642596/how-do-i-check-whether-this-user-is-anonymous-or-actually-a-user-on-my-system 
    if request.user.is_anonymous:
        #print ('User is anonumous')
        username = ''
    else:
        username = request.user.username
        #print ('Username: {}'.format(username))

    context['username'] = username
    context['general_alert_message'] = ''
    context['general_success_message'] = ''
    context['password_reset_token'] = ''
    context['reset_signup_username'] = ''
    context['reset_signup_email'] = ''

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

    # Add port information or other insrtance settings on template
    instance_settings = get_instance_settings()
    context['port'] = instance_settings['port']
    context['controller_url'] = instance_settings['controller_url']

    # Get OS choices
    context['os_choices'] = simplejson.dumps(OS_types.get_angular_model());

    # Add version
    context['version'] = __version__

    return render(request, 'app/index.html', context)

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
    obc_user = OBC_user(user=user, email_validated=False, email_validation_token=uuid_token)
    obc_user.save()


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
    }

    return success(ret)

def logout(request):
    '''
    View url: 'logout/'
    This is NOT called by AJAX
    '''

    django_logout(request)
    return redirect('/')

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


def tools_search_2(tools_search_name, tools_search_version, tools_search_edit):
    '''
    This is triggered when there is a key-change on the main-search
    '''

    Qs = []
    if tools_search_name:
        Qs.append(Q(name__icontains=tools_search_name))

    if tools_search_version:
        Qs.append(Q(version__icontains=tools_search_version))

    if tools_search_edit:
        Qs.append(Q(edit = int(tools_search_edit)))

    results = Tool.objects.filter(*Qs) # This applies an AND operator. https://docs.djangoproject.com/en/2.2/topics/db/queries/#complex-lookups-with-q-objects 

    # { id : 'ajson1', parent : '#', text : 'KARAPIPERIM', state: { opened: true} }

    # Build JS TREE structure

    tools_search_jstree = []
    for x in results:
        to_add = {
            'data': {'name': x.name, 'version': x.version, 'edit': x.edit},
            'text': tool_text_jstree(x) + jstree_icon_html('tools'),
            'id': tool_id_jstree(x, g['SEARCH_TOOL_TREE_ID']),
            'parent': tool_id_jstree(x.forked_from, g['SEARCH_TOOL_TREE_ID']) if x.forked_from else '#',
            'state': { 'opened': True},
        }
        tools_search_jstree.append(to_add)

    ret = {
        'tools_search_tools_number' : results.count(),
        #'tools_search_list': [{'name': x.name, 'version': x.version, 'edit': x.edit} for x in results], # We do not need a list, we need a tree!
        'tools_search_jstree' : tools_search_jstree,
    }

    return ret

def workflows_search_2(workflows_search_name, workflows_search_edit):
    '''
    Called by all_search_2
    '''

    Qs = []
    #workflows_search_name = kwargs.get('workflows_search_name', '')
    if workflows_search_name:
        Qs.append(Q(name__icontains=workflows_search_name))

    #workflows_search_edit = kwargs.get('workflows_search_edit', '')
    if workflows_search_edit:
        Qs.append(Q(edit = int(workflows_search_edit)))

    results = Workflow.objects.filter(*Qs)

    # Build JS TREE structure

    
    workflows_search_jstree = []
    for x in results:
        to_add = {
            'data': {'name': x.name, 'edit': x.edit},
            'text': workflow_text_jstree(x) + jstree_icon_html('workflows'),
            'id': workflow_id_jstree(x, g['SEARCH_WORKFLOW_TREE_ID']),
            'parent': workflow_id_jstree(x.forked_from, g['SEARCH_WORKFLOW_TREE_ID']) if x.forked_from else '#',
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
        'variables_js_tree': tool_variables_jstree,

        'variables': tool_variables,
        'tool_os_choices': OS_types.get_angular_model([x.os_choices for x in tool.os_choices.all()]),
        'installation_commands': tool.installation_commands,
        'validation_commands': tool.validation_commands,
        
        'validation_status': tool.last_validation.validation_status if tool.last_validation else 'Unvalidated',
        # Show stdout, stderr and error code when the tool is clicked on the tool-search-jstree
        'stdout' : tool.last_validation.stdout if tool.last_validation else None,
        'stderr' : tool.last_validation.stderr if tool.last_validation else None,
        'errcode' : tool.last_validation.errcode if tool.last_validation else None,
        'validation_created_at' : datetime_to_str(tool.last_validation.created_at) if tool.last_validation else None,
        'tool_pk': tool.pk, # Used in comments
        'tool_thread': qa_create_thread(tool.comment), # Tool comment thread 

    }

    #print ('LOGGG DEPENDENCIES + VARIABLES')
    #print (simplejson.dumps(tool_variables_jstree, indent=4))

    return success(ret)

@has_data
def tool_get_dependencies(request, **kwargs):
    '''
    Get the dependencies of this tool
    Called when a stop event (from dnd) happens from search JSTREE to the dependencies JSTREE
    '''

    tool_name = kwargs.get('tool_name', '')
    tool_version = kwargs.get('tool_version', '')
    tool_edit = int(kwargs.get('tool_edit', -1))

    tool = Tool.objects.get(name=tool_name, version=tool_version, edit=tool_edit)

    #Get the dependencies of this tool
    tool_dependencies = tool_get_dependencies_internal(tool, include_as_root=True)
    tool_dependencies_jstree = tool_build_dependencies_jstree(tool_dependencies)

    #Get the dependencies + variables of this tool
    tool_variables_jstree = tool_build_dependencies_jstree(tool_dependencies, add_variables=True)

    #print ('LOGGG DEPENDENCIES')
    #print (simplejson.dumps(tool_dependencies_jstree, indent=4))

    #print ('LOGGG DEPENDENCIES + VARIABLES')
    #print (simplejson.dumps(tool_variables_jstree, indent=4))

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

@has_data
def tools_add(request, **kwargs):
    '''
    Add a new tool
    tool add tool save tool

    * names and version is searched case insensitive
    '''

    if request.user.is_anonymous: # Server should always check..
        return fail('Please login to create new tools')

    if not user_is_validated(request):
        return fail('Please validate your email to create new tools ' + validate_toast_button());
    
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

    #os_type Update 
    tool_os_choices = kwargs.get('tool_os_choices',[])
    if not tool_os_choices:
        return fail('Please select at least one operating system')

    #print ('Operating Systems:')
    #print (tool_os_choices)

    #Get the maximum version
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
        tool_forked_from = None
        tool_changes = None
    
    
    #Installation/Validation commands 
    tool_installation_commands = kwargs['tool_installation_commands']
    tool_validation_commands = kwargs['tool_validation_commands']

    #Dependencies
    tool_dependencies = kwargs['tool_dependencies']
    #print ('tool_dependencies:')
    #print (tool_dependencies)
    tool_dependencies_objects = [Tool.objects.get(name=t['name'], version=t['version'], edit=int(t['edit'])) for t in tool_dependencies]

    #Variables
    tool_variables = kwargs['tool_variables']
    tool_variables = [x for x in tool_variables if x['name'] and x['value'] and x['description']] # Filter out empty fields

    # Check that variables do not have the same name
    for variable_name, variable_name_counter in Counter([x['name'] for x in tool_variables]).items():
        if variable_name_counter>1:
            return fail('Two variables cannot have the same name!')
    #Create new tool
    new_tool = Tool(
        obc_user= OBC_user.objects.get(user=request.user), 
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
        
        last_validation=None,
    )

    #Save it
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
    keywords = [Keyword.objects.get_or_create(keyword=keyword)[0] for keyword in kwargs['tool_keywords']]
    new_tool.keywords.add(*keywords)
    new_tool.save()

    #Add an empty comment. This will be the root comment for the QA thread
    comment = Comment(
        obc_user = OBC_user.objects.get(user=request.user),
        comment = '',
        comment_html = '',
        title = markdown('Discussion on Tool: t/{}/{}/{}'.format(tools_search_name, tools_search_version, next_edit)),
        parent = None,
    )
    comment.save()
    new_tool.comment = comment
    new_tool.save()

    ret = {
        'description_html': tool_description_html, 
        'edit': next_edit,
        'created_at': datetime_to_str(new_tool.created_at),

        'tool_pk': new_tool.pk, # Used in comments
        'tool_thread': qa_create_thread(new_tool.comment), # Tool comment thread 
    }

    return success(ret)

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


def set_edit_to_cytoscape_json(cy, edit, workflow_info_name):
    '''
    Perform the following tasks:
    * Set the edit number of the workflow to all nodes/edges
    * Change the id of the root workflow from "root" to workflow_info_name
    '''

    # Get the root workflow node
    new_worfklow_node = [x for x in cy['elements']['nodes'] if x['data']['type']=='workflow' and not x['data']['edit']]
    assert len(new_worfklow_node) == 1
    assert new_worfklow_node[0]['data']['name'] == 'root'

    # Set the edit value
    new_worfklow_node[0]['data']['edit'] = edit

    belongto = {
        'name': workflow_info_name,
        'edit': edit,
    }
    belongto_id = create_workflow_id(belongto)

    for node in cy['elements']['nodes']:
        if not node['data']['belongto'] is None:
            if not node['data']['belongto']['edit']:
                node['data']['belongto'] = belongto

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
    add workflow, workflow add, save workflow, workflow save
    '''

    if request.user.is_anonymous: # Server should always check..
        return fail('Please login to create new workflow')

    if not user_is_validated(request):
        return fail('Please validate your email to create new workflows ' + validate_toast_button());

    workflow_info_name = kwargs.get('workflow_info_name', '')
    if not workflow_info_name.strip():
        return fail('Invalid workflow name')

    workflow_info_forked_from = kwargs['workflow_info_forked_from'] # If it does not exist, it should raise an Exception

    workflow_changes = kwargs.get('workflow_changes', None)
    if workflow_info_forked_from:
        if not workflow_changes:
            return fail('Edit Summary cannot be empty')
        workflow_forked_from = Workflow.objects.get(name=workflow_info_forked_from['name'], edit=workflow_info_forked_from['edit'])
    else:
        workflow_forked_from = None
        workflow_changes = None

    workflow_website = kwargs.get('workflow_website', '')
    if workflow_website:
        if not valid_url(workflow_website):
            return fail('website is not a valid URL')

    workflow_description = kwargs.get('workflow_description', '')
    if not workflow_description.strip():
        return fail('Description cannot be empty')

    workflow_description_html = markdown(workflow_description)

    workflow = kwargs.get('workflow_json', '')
    if not workflow:
        return fail ('workflows json object is empty') # This should never happen!

    if not workflow['elements']:
        return fail('workflow graph cannot be empty')

    # Client sents the root workflow node.
    # When we save we make root False so that it is easier to import it later 
    #workflow_root_node = [x for x in workflow['elements']['nodes'] if x['data']['type']=='workflow' and x['data']['root']]
    #if len(workflow_root_node) != 1:
    #    return fail('Error 28342')
    #workflow_root_node[0]['data']['root'] = False

    #Check that one and only one step is main


    #Get the maximum version. FIXME DUPLICATE CODE
    workflow_all = Workflow.objects.filter(name__iexact=workflow_info_name)
    if not workflow_all.exists():
        next_edit = 1
    else:
        max_edit = workflow_all.aggregate(Max('edit'))
        next_edit = max_edit['edit__max'] + 1

#    print ('BEFORE')
#    print (simplejson.dumps(workflow, indent=4))
#    print ('=====')
    #Change the edit value in the cytoscape json object
    set_edit_to_cytoscape_json(workflow, next_edit, workflow_info_name)
#    print ('AFTER')
#    print (simplejson.dumps(workflow, indent=4))

    #print (simplejson.dumps(workflow, indent=4))
    main_counter = check_workflow_step_main(workflow, {'name':workflow_info_name, 'edit': next_edit })
    if main_counter == 0:
        return fail('Could not find main step. One step needs to be declared as "main"')
    if main_counter > 1:
        return fail('Error 49188') # This should never happen

    new_workflow = Workflow(
        obc_user=OBC_user.objects.get(user=request.user), 
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

    )

    #Save it
    new_workflow.save()

    # Get all tools that are used in this workflow
    tool_nodes = [x for x in workflow['elements']['nodes'] if x['data']['type'] == 'tool']
    tools = [Tool.objects.get(name=x['data']['name'], version=x['data']['version'], edit=x['data']['edit']) for x in tool_nodes]
    if tools:
        new_workflow.tools.add(*tools)
        new_workflow.save()

    # Add keywords
    keywords = [Keyword.objects.get_or_create(keyword=keyword)[0] for keyword in kwargs['workflow_keywords']]
    new_workflow.keywords.add(*keywords)
    new_workflow.save();

    # Add an empty comment. This will be the root comment for the QA thread
    comment = Comment(
        obc_user = OBC_user.objects.get(user=request.user),
        comment = '',
        comment_html = '',
        title = markdown('Discussion on Workflow: w/{}/{}'.format(workflow_info_name, next_edit)),
        parent = None,
    )
    comment.save()
    new_workflow.comment = comment
    new_workflow.save()


    ret = {
        'description_html': workflow_description_html, 
        'edit': next_edit,
        'created_at': datetime_to_str(new_workflow.created_at),

        'workflow_pk': new_workflow.pk, # Used in comments
        'workflow_thread': qa_create_thread(new_workflow.comment), # Tool comment thread 
    }

    return success(ret)

@has_data
def workflows_search_3(request, **kwargs):
    '''
    This is triggered when there is a key-change on the workflow-search pane
    See also:  tools_search_3

    OR:

    When a user drags a workflow from the jstree and drops it in a current workflow
    '''

    workflow_name = kwargs['workflow_name']
    workflow_edit = kwargs['workflow_edit']

    workflow = Workflow.objects.get(name__iexact = workflow_name, edit=workflow_edit)

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
        'workflow_pk': workflow.pk, # Used in comments (QAs)
        'workflow_thread': qa_create_thread(workflow.comment), # Tool comment thread 

    }

    return success(ret)

@has_data
def run_workflow(request, **kwargs):
    '''
    Defined in urls.py:
    path('run_workflow/', views.run_workflow), # Acceps a workflow_options and workflow object. Runs a workflow

    https://docs.djangoproject.com/en/2.2/ref/request-response/#telling-the-browser-to-treat-the-response-as-a-file-attachment
    '''

    workflow_arg = kwargs['workflow']
    workflow_options_arg = kwargs['workflow_options']

    workflow = Workflow.objects.get(**workflow_arg)
    workflow_cy = simplejson.loads(workflow.workflow)
    #print (workflow_cy)

    # Get the tools of this workflow
    workflow_tools = [tool for tool in workflow_cy['elements']['nodes'] if tool['data']['type']=='tool']
    # Add bash information that does not exist in cytoscape graph
    for workflow_tool in workflow_tools:
        workflow_tool_obj = Tool.objects.get(
            name=workflow_tool['data']['name'], 
            version=workflow_tool['data']['version'], 
            edit=workflow_tool['data']['edit'])

        workflow_tool['data']['installation_commands'] =  workflow_tool_obj.installation_commands
        workflow_tool['data']['validation_commands'] = workflow_tool_obj.validation_commands
        workflow_tool['data']['os_choices'] = [choice.os_choices for choice in workflow_tool_obj.os_choices.all()]
        workflow_tool['data']['dependencies'] = [str(tool) for tool in workflow_tool_obj.dependencies.all()]

    # Create a new Report object 
    if not user_is_validated(request):
        '''
        If user is anonymous or with non-validated email, we do not create a report!
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
    output_object = urllib.parse.quote(simplejson.dumps(output_object))
    #output_object = escape(simplejson.dumps(output_object))

    #print ('output_object')
    #print (output_object)

    #response = HttpResponse(the_script, content_type='application/x-sh')
    #response['Content-Disposition'] = 'attachment; filename="script.sh"'
    ret = {
        'output_object': output_object,
        'report_created': report_created,
        'nice_id': nice_id,
    }

    return success(ret)


@csrf_exempt
@has_data
def report(request, **kwargs):
    '''
    called from executor
    '''

    #print (kwargs)

    token = kwargs.get('token', None)
    if not token:
        return fail('Could not find token field')
    #print ('token: {}'.format(token))

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

    #Deactivate it
    old_report_token.active = False
    old_report_token.save()

    # Get the report
    report_obj = old_report_token.report_related.first()

    #Save the new status and return a new token 
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
    # print(kwargs)
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

def reports_search_2(
    main_search,
    ):
    '''
    Collect all reports from main search
    '''

    nice_id_Q = Q(nice_id__contains=main_search)
    workflow_Q = Q(workflow__name__icontains=main_search)
    not_unused = Q(tokens__status = ReportToken.UNUSED)
    count_1 = Q(num_tokens = 1)

    # We do not want reports that have only one tokens which is "unused"
    results = Report.objects.annotate(num_tokens=Count('tokens')).filter( (nice_id_Q | workflow_Q) & (~(not_unused&count_1)) )

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

    run = kwargs['run']

    report = Report.objects.get(nice_id=run)
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
        'workflow' : simplejson.loads(workflow.workflow),
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
    pybtex_html_backend.write_to_stream(data_formatted, output)
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

    results = Reference.objects.filter(name_Q | html_Q)
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

def qa_search_2(main_search):
    '''
    Collect all Q&A from main search
    '''
    title_Q = Q(title__icontains=main_search)
    comment_Q = Q(comment__icontains=main_search)

    results = Comment.objects.filter(title_Q | comment_Q)

    qa_search_tree = []
    entries_in_tree = set()
    for result in results:
        # Get the root message
        result_parent = qa_get_root_comment(result)

        #Is this on the tree?
        if result_parent.pk in entries_in_tree:
            # It is already in the tree
            continue
        else:
            entries_in_tree.add(result_parent.pk)

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
    '''

    name = kwargs.get('name', '')
    try:
        reference = Reference.objects.get(name__iexact=name)
    except ObjectDoesNotExist as e:
        return fail('Could not find Reference') # This should never happen..

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
    for key, value in tools_search_2(tools_search_name, tools_search_version, tools_search_edit).items():
        ret[key] = value

    #Get workflowws
    for key, value in workflows_search_2(workflows_search_name, workflows_search_edit).items():
        ret[key] = value

    #Get reports
    for key, value in reports_search_2(main_search).items():
        ret[key] = value

    #Get references
    for key, value in references_search_2(main_search).items():
        ret[key] = value

    #Get users
    for key, value in users_search_2(main_search).items():
        ret[key] = value

    # Get QAs
    for key, value in qa_search_2(main_search).items():
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

    # We csannot have the same comment title more than once
    if Comment.objects.filter(title__iexact=qa_title).exists():
        return fail('A comment with this title already exists!')

    #Create a new comment
    comment = Comment(
        obc_user=OBC_user.objects.get(user=user), 
        comment=qa_comment,
        comment_html = qa_comment_html,
        title=qa_title,
        parent=None,
    )
    comment.save()

    ret = {
        'id': comment.pk,
        'comment_html': qa_comment_html,
    }

    return success(ret)

def qa_create_thread(comment):
    '''
    Recursive
    Create the children thread of a comment
    '''
    ret = []
    for child in comment.children.all():
        to_add = {
            'comment': child.comment,
            'comment_html': child.comment_html,
            'id': child.pk,
            'replying': False,
            'children': qa_create_thread(child),
            'username': child.obc_user.user.username,
            'created_at': datetime_to_str(child.created_at),
        }
        ret.append(to_add)
    return ret


@has_data
def qa_search_3(request, **kwargs):
    '''
    path: qa_search_3/
    Get a unique Q&A thread
    '''

    id_ = kwargs.get('qa_id', None)
    if not id_:
        return fail('Could not find Q&A id')

    try:
        comment = Comment.objects.get(pk=id_)
    except ObjectDoesNotExist as e:
        return fail('Could not find comment database object')

#                $scope.qa_thread = [
#                    {'comment': 'comment 1', 'id': 1, 'replying': false},
#                    {'comment': 'comment 2', 'id': 2, 'replying': false}
#                ];

    ret = {
        'qa_title': comment.title,
        'qa_comment': comment.comment,
        'qa_comment_html': comment.comment_html,
        'qa_id': comment.pk,
        'qa_thread': qa_create_thread(comment),
        'qa_username': comment.obc_user.user.username,
        'qa_created_at': datetime_to_str(comment.created_at),
    }

    #print (simplejson.dumps(ret, indent=4))

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

    # Get the thread of this comment
    ret = {
        'qa_id': commentable.comment.pk,
        'qa_thread': qa_create_thread(commentable.comment),
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
    if not current_comment:
        return fail('Could not find Q&A new comment')

    current_comment_html = markdown(current_comment)

    try:
        parent_comment = Comment.objects.get(pk=id_)
    except ObjectDoesNotExist as e:
        return fail('ERROR: 8991. Could not find comment database object')

    new_comment = Comment(
        obc_user=OBC_user.objects.get(user=request.user),
        comment = current_comment,
        comment_html = current_comment_html,
        parent=parent_comment,
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
        comment_html = current_comment_html,
        parent = root_comment,
    )
    new_comment.save()
    root_comment.children.add(new_comment)
    root_comment.save()

    ret = {
        'comment_html': current_comment_html,
    }

    return success(ret)


### END OF Q&A

### VIEWS END ######

