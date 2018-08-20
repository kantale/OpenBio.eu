
# Django imports
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth.models import User

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login # To distinguish from AJAX called login
from django.contrib.auth import logout as django_logout # To distinguish from AJAX called logout

from django.core.exceptions import ObjectDoesNotExist

# Get csrf_token
# https://stackoverflow.com/questions/3289860/how-can-i-embed-django-csrf-token-straight-into-html
from django.middleware.csrf import get_token 

#Import database objects
from app.models import OBC_user

# Email imports
import smtplib
from email.message import EmailMessage

# System imports 
import re
import uuid
import datetime

# Installed packages imports 
import simplejson

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

def create_validation_url(token):
    '''
    https://stackoverflow.com/a/5767509/5626738
    http://www.example.com/?param1=7&param2=seven.
    '''
    ret = 'http://staging.openbio.eu:8200/?validation_token={token}'.format(token=token)
    return ret


def create_password_email_url(token):
    ret = 'http://staging.openbio.eu:8200/?password_reset_token={token}'.format(token=token)
    return ret


def confirm_email_body(token):
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

    return ret.format(validation_url=create_validation_url(token))

def reset_password_email_body(token):
    '''
    The email for resetting a password
    '''
    ret = '''
Dear user,

Someone (hopefully you) has requested to reset the password on the openbio.eu site.
If this is you, please go the following link to complete the process:
{password_reset_url}

Otherwise please ignore this email!

Regards,
The openbio.eu admin team.
'''

    return ret.format(password_reset_url=create_password_email_url(token))

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
            obc_user.save()
            return True, 'Email successfully validated'
    else:
        return False, 'Unknown token'

def now():
    '''
    https://stackoverflow.com/a/415519/5626738
    '''
    return datetime.datetime.now()

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
    if len(signup_password) < 6:
        return fail('Minimum password length is 6')

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
            body=confirm_email_body(uuid_token),
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
        return fail('This email does not belong to any user')

    # reset_password_email_body 

    # Save token
    token = create_uuid_token()
    obc_user.password_reset_token = token
    obc_user.password_reset_timestamp = now()
    obc_user.save()

    ### HERE HERE LOGIC TO RESET PASSWORD EMAIL

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

### VIEWS END ######

