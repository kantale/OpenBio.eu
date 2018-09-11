
# Django imports
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth.models import User

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login # To distinguish from AJAX called login
from django.contrib.auth import logout as django_logout # To distinguish from AJAX called logout

from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q # https://docs.djangoproject.com/en/2.1/topics/db/queries/#complex-lookups-with-q-objects
from django.db.models import Max # https://docs.djangoproject.com/en/2.1/topics/db/aggregation/

from django.utils import timezone

# Get csrf_token
# https://stackoverflow.com/questions/3289860/how-can-i-embed-django-csrf-token-straight-into-html
from django.middleware.csrf import get_token 

#Import database objects
from app.models import OBC_user, Tool

# Email imports
import smtplib
from email.message import EmailMessage

# System imports 
import re
import uuid
#import datetime # Use timezone.now()

# Installed packages imports 
import simplejson

__version__ = '0.0.3rc'

#GLOBAL CONSTANTS
g = {
    'SEARCH_TOOL_TREE_ID': '1',
    'DEPENDENCY_TOOL_TREE_ID': '2',
    'format_time_string' : '%a, %d %b %Y %H:%M:%S', # RFC 2822 Internet email standard. https://docs.python.org/2/library/time.html#time.strftime   # '%Y-%m-%d, %H:%M:%S'
}

### HELPING FUNCTIONS AND DECORATORS #####

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
                            POST = simplejson.loads(request.body)
                            for k in POST:
                                kwargs[k] = POST[k]
            elif request.method == 'GET':
                    for k in request.GET:
                        kwargs[k] = request.GET[k]
                        print ("GET: {} == {}".format(k, kwargs[k]))

            return f(*args, **kwargs)

    return wrapper

def username_exists(username):
    '''
    Checks if a username exists
    '''

    return User.objects.filter(username=username).exists()

def datetime_to_str(d):
    '''
    String format
    '''
    
    return d.strftime(g['format_time_string'])

def create_uuid_token():
    '''
    Create a uuid token for email validation 
    Length: 32 characters
    '''
    # return str(uuid.uuid4()).split('-')[-1] # Last part: 12 characters
    return str(uuid.uuid4()).replace('-', '') # 32 characters

def send_mail(from_, to, subject, body):
    '''
    Standard email send function with SMTP 

    Adjusted from here:
    https://docs.python.org/3/library/email.examples.html
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
    if port == '80':
        return ''

    return ':' + port # For example ':8080'


def create_validation_url(token, port=''):
    '''
    https://stackoverflow.com/a/5767509/5626738
    http://www.example.com/?param1=7&param2=seven.
    '''
    ret = 'http://staging.openbio.eu{port}/?validation_token={token}'.format(token=token, port=port)
    return ret


def create_password_email_url(token, port=''):
    ret = 'http://staging.openbio.eu{port}/?password_reset_token={token}'.format(token=token, port=port)
    return ret


def confirm_email_body(token, port=''):
    '''
    The mail verification mail body
    '''
    ret = '''
Thank you for signing up to openbio.eu

To complete your registration please click (or copy-paste to your browser) the following link:
{validation_url}

Regards,
The openbio.eu admin team.
'''

    return ret.format(validation_url=create_validation_url(token, port))

def reset_password_email_body(token, port=''):
    '''
    The email for resetting a password
    '''
    ret = '''
Dear user,

Someone (hopefully you) has requested to reset the password at openbio.eu .
If this is you, please go to the following link to complete the process:
{password_reset_url}

Otherwise please ignore this email!

Regards,
The openbio.eu admin team.
'''

    return ret.format(password_reset_url=create_password_email_url(token, port))

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
            return False, 'Password Reset Token expires after 2 Hours'
        else:
            return True, ''
    else:
        return False, "Unknown token"


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

def tool_get_dependencies_internal(tool, include_as_root=False):
    '''
    Get the dependencies of this tool in a flat list
    Recursive
    include_this. Should we add this tool as root?
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


### HELPING FUNCTIONS AND DECORATORS END #######


### VIEWS ############

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

    # PASSWORD RESET
    password_reset_token = GET.get('password_reset_token', '')
    context['password_reset_token'] = '' # It will be set after checks
    if password_reset_token:
        password_reset_check_success, password_reset_check_message = password_reset_check_token(password_reset_token)
        if password_reset_check_success:
            context['password_reset_token'] = password_reset_token
        else:
            context['general_alert_message'] = password_reset_check_message
	
    return render(request, 'app/index.html', context)

@has_data
def register(request, **kwargs):
    '''
    View url: 'register/'
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

    ## Try to send an email
    uuid_token = create_uuid_token()

    try:
        send_mail(
            from_='noreply@staging.openbio.eu', 
            to=signup_email,
            subject='[openbio.eu] Please confirm your email',
            body=confirm_email_body(uuid_token, port=request_port_to_url(request)),
        )
    except smtplib.SMTPRecipientsRefused:
        return fail('Could not sent an email to {}'.format(signup_email))


    #Create user
    user = User.objects.create_user(signup_username, signup_email, signup_password)

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

    #Send email
    try:
        send_mail(
            from_ = 'noreply@staging.openbio.eu',
            to = email,
            subject = '[openbio.eu] Reset your password',
            body = reset_password_email_body(token, port=request_port_to_url(request))
        )
    except smtplib.SMTPRecipientsRefused:
        return fail('Could not send an email to: {}'.format(email))

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

    # Since we logged in the csrf token has changed.
    ret = {
        'username': login_username,
        'csrf_token': get_token(request),
    }

    return success(ret)

def logout(request):
    '''
    View url: 'logout/'
    This is NOT called by AJAX
    '''

    django_logout(request)
    return redirect('/')

def user_data_get(request):
    '''
    View url: user_data_get
    GET THE DATA OF THE LOGGED-IN USER
    It does not have the @has_data decorator because it has.. no data
    '''

    user = request.user
    obc_user = OBC_user.objects.get(user=user)
    ret = {
        'user_first_name': obc_user.first_name,
        'user_last_name': obc_user.last_name,
        'user_email': user.email,
        'user_website': obc_user.website,
        'user_public_info': obc_user.public_info,
    }

    return success(ret)

@has_data
def user_data_set(request, **kwargs):
    user = request.user
    obc_user = OBC_user.objects.get(user=user)

    obc_user.first_name = None_if_empty_or_nonexisting(kwargs, 'user_first_name')
    obc_user.last_name = None_if_empty_or_nonexisting(kwargs, 'user_last_name')
    obc_user.website = None_if_empty_or_nonexisting(kwargs, 'user_website')
    obc_user.public_info = None_if_empty_or_nonexisting(kwargs, 'user_public_info')

    obc_user.save()

    return success()

@has_data
def tools_search_1(request, **kwargs):
    queries = []

    ret = {
        'tools_search_tools_number': Tool.objects.count()
    }

    return success(ret)

def tool_text_jstree(tool):
    '''
    The JS tree text
    '''
    return '/'.join(map(str, [tool.name, tool.version, tool.edit]))


def tool_id_jstree(tool, id_):
    '''
    The JS tree id
    '''
    return tool_text_jstree(tool) + '/' + str(id_) 


@has_data
def tools_search_2(request, **kwargs):

    Qs = []
    tools_search_name = kwargs.get('tools_search_name', '')
    if tools_search_name:
        Qs.append(Q(name__icontains=tools_search_name))

    tools_search_version = kwargs.get('tools_search_version', '')
    if tools_search_version:
        Qs.append(Q(version__icontains=tools_search_version))

    tools_search_edit = kwargs.get('tools_search_edit', '')
    if tools_search_edit:
        Qs.append(Q(edit = int(tools_search_edit)))

    results = Tool.objects.filter(*Qs)

    # { id : 'ajson1', parent : '#', text : 'KARAPIPERIM', state: { opened: true} }

    # Build JS TREE structure

    tools_search_jstree = []
    for x in results:
        to_add = {
            'data': {'name': x.name, 'version': x.version, 'edit': x.edit},
            'text': tool_text_jstree(x),
            'id': tool_id_jstree(x, g['SEARCH_TOOL_TREE_ID']),
            'parent': tool_id_jstree(x.forked_from, g['SEARCH_TOOL_TREE_ID']) if x.forked_from else '#',
            'state': { 'opened': True},
        }
        tools_search_jstree.append(to_add)

    ret = {
        'tools_search_tools_number' : results.count(),
        'tools_search_list': [{'name': x.name, 'version': x.version, 'edit': x.edit} for x in results],
        'tools_search_jstree' : tools_search_jstree,
    }

    return success(ret)

@has_data
def tools_search_3(request, **kwargs):

    tool_name = kwargs.get('tool_name', '')
    tool_version = kwargs.get('tool_version', '')
    tool_edit = int(kwargs.get('tool_edit', -1))

    tool = Tool.objects.get(name=tool_name, version=tool_version, edit=tool_edit)

    ret = {
        'website': tool.website,
        'description': tool.description,
        'username': tool.obc_user.user.username,
        'created_at': datetime_to_str(tool.created_at),
        'forked_from': tool_to_json(tool.forked_from),
        'changes': tool.changes,

        'installation_commands': tool.installation_commands,
        'validation_commands': tool.validation_commands,
    }

    return success(ret)

@has_data
def tool_get_dependencies(request, **kwargs):
    '''
    Get the dependencies of this tool
    '''

    tool_name = kwargs.get('tool_name', '')
    tool_version = kwargs.get('tool_version', '')
    tool_edit = int(kwargs.get('tool_edit', -1))

    tool = Tool.objects.get(name=tool_name, version=tool_version, edit=tool_edit)

    #Get the dependencies of this tool
    tool_dependencies = tool_get_dependencies_internal(tool, include_as_root=True)

    #Build JS TREE
    tool_dependencies_jstree = []
    for tool_dependency in tool_dependencies:
        tool_dependencies_jstree.append({
            'data': {
                    'name': tool_dependency['dependency'].name,
                    'version': tool_dependency['dependency'].version,
                    'edit': tool_dependency['dependency'].edit,
                },
            'text': tool_text_jstree(tool_dependency['dependency']),
            'id': tool_id_jstree(tool_dependency['dependency'], g['DEPENDENCY_TOOL_TREE_ID']),
            'parent': tool_id_jstree(tool_dependency['dependant']) if tool_dependency['dependant'] else '#',
        })

    print ('LOGGG DEPENDENCIES')
    print (tool_dependencies_jstree)

    ret = {
        'dependencies_jstree': tool_dependencies_jstree,
    }

    return success(ret)



@has_data
def tools_add(request, **kwargs):

    if request.user.is_anonymous: # Server should always check..
        return fail('Please login to create new tools')
    
    tool_website = kwargs.get('tool_website', '')
    if not tool_website:
        return fail('Website cannot be empty')

    tool_description = kwargs.get('tool_description', '')
    if not tool_description:
        return fail('Description cannot be empty')

    tools_search_name = kwargs.get('tools_search_name', '') 
    if not tools_search_name:
        return fail('Invalid name')

    tools_search_version = kwargs.get('tools_search_version', '')
    if not tools_search_version:
        return fail('Invalid version')

    #Get the maximum version
    tool_all = Tool.objects.filter(name=tools_search_name, version=tools_search_version)
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

    tool_installation_commands = kwargs['tool_installation_commands']
    tool_validation_commands = kwargs['tool_validation_commands']

    #Create new tool
    new_tool = Tool(
        obc_user=OBC_user.objects.get(user=request.user), 
        name = tools_search_name,
        version=tools_search_version,
        edit=next_edit,
        website = tool_website,
        description = tool_description,
        forked_from = tool_forked_from,
        changes = tool_changes,

        installation_commands=tool_installation_commands,
        validation_commands=tool_validation_commands,
    )

    #Save it
    new_tool.save()

    ret = {
        'edit': next_edit,
        'created_at': datetime_to_str(new_tool.created_at)
    }

    return success(ret)


### VIEWS END ######

