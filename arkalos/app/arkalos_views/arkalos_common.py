
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import redirect

from django.core.validators import URLValidator # https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not 
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.db.models import Max, Count

from app.models import Reference, Tools, Reports, Tasks, TasksStats


import io
import re
import six
import uuid
import hashlib
import simplejson

#https://pybtex.org/
from pybtex.database import parse_string as parse_reference_string

import pybtex.database.input.bibtex
import pybtex.plugin

# Globals
pybtex_style = pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')()
pybtex_html_backend = pybtex.plugin.find_plugin('pybtex.backends', 'html')()
pybtex_parser = pybtex.database.input.bibtex.Parser()

sep = '||'
sep2 = '@@'
format_time_string = '%a, %d %b %Y %H:%M:%S' # RFC 2822 Internet email standard. https://docs.python.org/2/library/time.html#time.strftime   # '%Y-%m-%d, %H:%M:%S'
url_validator = URLValidator() # https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not 

class ArkalosException(Exception):
    pass

def get_guid():
    '''
    Create a new guid
    '''
    return str(uuid.uuid4())

def get_user_id(request):
    '''
    Get id of user
    '''
    is_authenticated = request.user.is_authenticated()
    if is_authenticated:
        return request.user.id

    return None

def get_user(request):
    '''
    Get user object
    '''
    is_authenticated = request.user.is_authenticated()
    if is_authenticated:
        return request.user

    return None

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

def has_field(field_names, errors):
    '''
    Check if field names are present
    field_name: The field to check

    '''
    def decorator(f):
        def wrapper(*args, **kwargs):

            for field_index, field_name in enumerate(field_names):
                if not field_name in kwargs:
                    if callable(errors):
                        kwargs['error'] = errors(field_name)
                    elif type(errors) is list:
                        kwargs['error'] = errors[field_index]
                    elif type(errors) is dict:
                        kwargs['error'] = errors[field_name]
                    elif type(errors) is str:
                        kwargs['error'] = errors
                    else:
                        # This should never happen
                        raise ArkalosException('Unknown error type: {}'.format(type(error).__name__))
                    return f(*args, **kwargs)

            return f(*args, **kwargs)

        return wrapper
    return decorator

def has_error(f):
    '''
    Check if error in kwargs
    '''
    def wrapper(*args, **kwargs):
        if 'error' in kwargs:
            return fail(kwargs['error'])

        return f(*args, **kwargs)
    return wrapper

def username_exists(username):
    '''
    Checks if a username exists
    '''
    return User.objects.filter(username=username).exists()

def URL_validate(url):
    '''
    https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    '''

    try:
        url_validator(url)
    except ValidationError as e:
        return False 

    return True

def format_time(t):
    '''
    Universal method to string format time vars
    '''
    return t.strftime(format_time_string)

###########################################################################
##################DATABASE FUNCTIONS#######################################
###########################################################################

def bootstrap_table_format_field(entry, value):
    '''
    Formats the field of a bootstrap table. Values are taken from bidings
    '''
    if type(value) is str:
        if type(entry) is dict:
            return entry[value]
        else:
            return getattr(entry, value)
    elif callable(value):
        return value(entry)

def serve_boostrap_table2(model, query_f, filters, bindings, **kwargs):
    '''
    count_f = Tools.objects.values('name', 'url').annotate(Count('name')).count()
    query_f = Tools.objects.values('name', 'url').annotate(Count('name'))

    IT DOES NOT USE count_f !
    '''

    #count = count_f()

    order = kwargs['order'] 
    offset = kwargs['offset']
    limit = kwargs['limit']

    from_offset = int(offset)
    to_offset = from_offset + int(limit)

    if 'filter' in kwargs:
        # "read" the filter
        filter_ = kwargs['filter']
        filter_ = simplejson.loads(filter_)
        print ("Filter:")
        print (filter_)
        applied_filters = {filters[f][0](): filters[f][1](f_value)  for f, f_value in filter_.items() if f in filters}
        print ("Applied filters:")
        print (applied_filters)

    else:
        applied_filters = {}
    
    querySet = query_f(applied_filters)
    count = querySet.count()
    querySet = querySet[from_offset:to_offset]

    ret = {'total': count}
    ret['rows'] = [ {k: bootstrap_table_format_field(entry, v) for k, v in bindings.items()} for entry in querySet]

    json = simplejson.dumps(ret)
    return HttpResponse(json, content_type='application/json')

def serve_boostrap_table(model, bindings, order_by, **kwargs):
    '''
    http://bootstrap-table.wenzhixin.net.cn/ 
    '''
    count = model.objects.count()

    order = kwargs['order'] 
    offset = kwargs['offset']
    limit = kwargs['limit']

    from_offset = int(offset)
    to_offset = from_offset + int(limit)

    if 'filter' in kwargs:
        filter_ = kwargs['filter']
        filter_ = simplejson.loads(filter_)
        filter_ = { bindings[k] + '__icontains':v for k,v in filter_.items()}

        querySet = model.objects.filter(**filter_)
        count = querySet.count()
        querySet = querySet[from_offset:to_offset]
    else:
        querySet = model.objects.order_by(order_by)[from_offset:to_offset]

    ret = {'total': count}
    ret['rows'] = [ {k: bootstrap_table_format_field(entry, v) for k, v in bindings.items()} for entry in querySet]

    json = simplejson.dumps(ret)
    return HttpResponse(json, content_type='application/json')


def db_exists(model, filters):
    '''
    Does this entry exist?
    '''
    return model.objects.filter(**filters).exists()

def get_maximum_current_version(model, name):
    '''
    Return the next available current_version
    '''


    max_entry = model.objects.filter(name=name).aggregate(Max('current_version'))

    if max_entry['current_version__max'] is None:
        return 1

    assert type(max_entry) is dict
    assert len(max_entry) == 1

    return max_entry['current_version__max'] + 1

def build_jstree_tool_dependencies(tool, prefix='', include_original=False):
    '''
    Build the dependency jstree of this tool
    include_original are we including the original tool in the jstree?
    '''

    def node(t):

        ret = {
            'id': prefix + sep + t.name + sep + str(t.current_version), #Through this id we get info from jstree jandlers 
            'text': t.name + ' ' + str(t.current_version),
            'children': [build_jstree_tool_dependencies(x, prefix, include_original=True) for x in t.dependencies.all()] + \
                [{'text': x[0], 'type': 'exposed', 'value': x[1], 'description': x[2], 'id': prefix+sep+x[0]+sep+t.name+sep2+str(t.current_version)} for x in simplejson.loads(t.exposed)],
            'current_version': t.current_version,
            'name': t.name,
            'type': 'tool',
        }

        return ret

    if include_original:
        return node(tool)
    else:
        return [node(dependent_tool) for dependent_tool in tool.dependencies.all()]

def build_jstree(model, name, prefix=''):
    '''
    Take an entry that has a previous_version and current_version
    Build a jstree compatible structure 
    '''

    index = {}

    if prefix:
        prefix_to_add = prefix + sep
    else:
        prefix_to_add = ''

    def node(o):
        current_version = o.current_version
        ret = {
            'id': prefix_to_add + o.name + sep + str(o.current_version), 
            'text': o.name + ' ' + str(o.current_version), 
            'children': [],
            'current_version': o.current_version,
            'name': o.name
            }

        index[current_version] = ret
        return ret

    ret = []
    all_objects = model.objects.filter(name=name).order_by("current_version")

    #ret.append(node(all_objects[0]))

    for o in all_objects:
        previous_version = o.previous_version
        if previous_version is None:
            ret.append(node(o))
        else:
            this_node = node(o)
            index[previous_version]['children'].append(this_node)

    #print (simplejson.dumps(ret))

    return ret


###########################################################################
##################END OF DATABASE#######################################
###########################################################################

###########################################################################
################## REGISTER ###############################################
###########################################################################


@has_data
@has_field(['username', 'password', 'password_confirm', 'email'], lambda x :'{} is required'.format(x))
@has_error
def register(request, **kwargs):
    '''
    Register
    '''

    #print (kwargs)

    username = kwargs['username']
    password = kwargs['password']
    password_confirm = kwargs['password_confirm']
    email = kwargs['email']

    #Check if this user exists
    if username_exists(username):
        return fail('Username {} exists'.format(username))

    #Check if password match
    if kwargs['password'] != kwargs['password_confirm']:
        return fail('Passwords do not match')

    #Create user
    user = User.objects.create_user(username, email, password)

    return success({})

@has_data
@has_field(['username', 'password'], lambda x :'{} is required'.format(x))
@has_error
def loginlocal(request, **kwargs):
    '''
    Function called from login
    '''

    username = kwargs['username']
    password = kwargs['password']

    user = authenticate(username=username, password=password)

    if user is None:
        return fail('Invalid username or password')

    #if user.is_active: ... # https://docs.djangoproject.com/en/1.9/topics/auth/default/ 

    login(request, user)

    ret = {'username': username}
    return success(ret)

def logoutlocal(request):
    '''
    logout
    '''
    logout(request)
    return redirect('/')

###########################################################################
################## END OF REGISTER ########################################
###########################################################################


###############################
####REFERENCES#################
###############################

def reference_get_fields(content):
    '''
    Get the code of the bibtex entry
    '''
    p = parse_reference_string(content, 'bibtex')
    p_len = len(p.entries)
    if p_len == 0:
        return False, 'Could not find BIBTEX entry'
    if p_len > 1:
        return False, 'More than one BIBTEX entries found'

    code = p.entries.keys()[0]
    if not 'title' in p.entries[code].fields:
        return False, 'Could not find title information'
    
    title = p.entries[code].fields['title']

    if not hasattr(p.entries[code], 'persons'):
        return False, 'Could not find author information'

    if not 'author' in p.entries[code].persons:
        return False, 'Could not find author information'

    if len(p.entries[code].persons['author']) == 0:
        return False, 'Could not find author information'

    authors = sep.join([str(x) for x in p.entries[code].persons['author']])


    return True, {'code': code, 'title': title, 'authors': authors}

def bibtex_to_html(content):
    '''
    Convert bibtex to html
    Adapted from: http://pybtex-docutils.readthedocs.io/en/latest/quickstart.html#overview 
    '''
    data = pybtex_parser.parse_stream(six.StringIO(content))
    data_formatted = pybtex_style.format_entries(six.itervalues(data.entries))

    output = io.StringIO()
    pybtex_html_backend.write_to_stream(data_formatted, output)
    html = output.getvalue()

    html_s = html.split('\n')
    html_s = html_s[9:-2]
    new_html = '\n'.join(html_s).replace('<dd>', '').replace('</dd>', '')
    return new_html

@has_data
@has_field(['content'], 'BIBTEX content is required')
@has_error
def add_reference(request, **kwargs):
    '''
    Add reference 
    '''

    content = kwargs['content']

    s, fields = reference_get_fields(content)
    if not s:
        return fail(fiels)

    if db_exists(Reference, {'code': fields['code']}):
        return fail('BIBTEX entry with code {} already exists'.format(code))

    html = bibtex_to_html(content)

    r = Reference(
        user=get_user(request),
        code=fields['code'],
        title=fields['title'],
        authors=fields['authors'],
        content=content,
        reference_type='BIBTEX',
        html = html,
        )
    r.save()

    return success()

@has_data
def get_references(request, **kwargs):
    '''
    Serve GET Request for References bootstrap table 
    '''
    bindings = {
        'id': 'code',
        'content': 'html',
    }
    return serve_boostrap_table(Reference, bindings, 'id', **kwargs)

@has_data
@has_error
def get_reference(request, **kwargs):
    '''
    Get reference
    '''
    codes = kwargs['codes']

    ret = {'data': {}, 'html': []}

    c = 0
    for code in codes:
        try:
            ref = Reference.objects.get(code=code)
            c += 1
            ret['data'][code] = {'counter': c}
            ret['html'].append({'html': ref.html})

        except ObjectDoesNotExist:
            pass

    ret['total'] = c


    return success(ret)

@has_data
def reference_suggestions(request, **kwargs):
    '''
    Get called from tagas input
    '''
    query = kwargs['query']

    querySet = Reference.objects.filter(content__icontains = query)[:10]
    ret = [ {'value' : entry.code, 'html': entry.html} for entry in querySet] # We have a html representation for each Reference

    json = simplejson.dumps(ret)
    return HttpResponse(json, content_type='application/json')

def get_references_from_text(text):
    '''
    Get all reference objects from a text.
    This is useful for the report
    '''

    ret = []
    all_brackets = re.findall(r'\[[\w]+\]', text)
    for bracket in all_brackets:

        #Remove brackets
        code = bracket[1:-1]

        #Check if this a real reference
        try:
            ref = Reference.objects.get(code=code)
        except ObjectDoesNotExist:
            pass
        else:
            ret += [ref]

    return ret

###############################
######END OF REFERENCES########
###############################

#################################
#### REPORTS ####################
#################################

@has_data
def get_reports(request, **kwargs):
    '''
    Serve bootstrap table for reports 
    '''
    bindings = {
        'name': 'name',
        #'total_edits': lambda entry: entry['name__count'],
        'content': lambda entry : ''
    }

    #return serve_boostrap_table(Reports, bindings, 'id', **kwargs)

    return serve_boostrap_table2(
        model = Reports,
        #count_f = lambda : Reports.objects.values('name').annotate(Count('name')).count(),
        query_f = lambda x : Reports.objects.filter(**x).values('name').distinct(),
        bindings = bindings,
        filters = {
            'name': (lambda : 'name__icontains', lambda x : x) # name_contains = x
        },
        **kwargs
        )

@has_data
@has_error
def get_reports_ui(request, **kwargs):

    name = kwargs['name']
    current_version = kwargs['current_version']

    report = Reports.objects.get(name=name, current_version=current_version)

    username = report.user.username

    ret = {
        'name': name,
        'current_version': current_version,
        'username': username,
        'created_at': format_time(report.created_at),
        'markdown': report.markdown,
        'summary': report.summary,
    }

    return success(ret)

@has_data
@has_error
def add_report(request, **kwargs):

    name = kwargs['name']
    previous_version = kwargs['previous_version']
    markdown = kwargs['markdown']
    references = kwargs['references']
    user = get_user(request)

    #print (name)
    #print (previous_version)
    #print (markdown)
    #print (references)

    current_version = get_maximum_current_version(Reports, name)
    previous_version = kwargs["previous_version"]
    if previous_version == 'N/A':
        previous_version = None
    if current_version == 1:
        previous_version = None

    report = Reports(
        name=name,
        user=user,
        current_version=current_version,
        previous_version=previous_version,
        markdown=markdown,
    )

    report.save()

    fetched_references = [Reference.objects.get(name=x) for x in references]
    report.references.add(*fetched_references)
    report.save()

    ret = {
        'created_at' : format_time(report.created_at),
        'current_version': current_version,
        'jstree': build_jstree(Reports, report.name)
    }

    #print (ret)

    return success(ret)

#################################
#### END OF REPORTS #############
#################################


#################################
####TOOLS / DATA#################
#################################

@has_data
def get_tools(request, **kwargs):
    '''
    Serve GET Request for Tools bootstrap table


    def serve_boostrap_table2(model, count_f, query_f, bindings, **kwargs):
    
    count_f = Tools.objects.values('name', 'url').annotate(Count('name')).count()
    query_f = Tools.objects.values('name', 'url').annotate(Count('name')
    '''

    bindings = {
        'name' : 'name',
        'url': lambda entry : '<a href="{}" target="_blank">{}</a>'.format(entry['url'], entry['url']),
        #'total_edits': lambda entry: entry['name__count'],
        'description': lambda entry: ''

        #'current_version': lambda entry: '{} -- {}'.format(entry.current_version, entry.previous_version),
        #'current_version': 'current_version',
        #'description': 'description',
        #'description': lambda entry: '{} {} -- {}'.format(entry.description, entry.current_version, entry.previous_version),
    }

    #return serve_boostrap_table(Tools, bindings, 'name', **kwargs)
    return serve_boostrap_table2(
        model = Tools,
        #count_f = lambda : Tools.objects.values('name', 'url').annotate(Count('name')).count(),
        query_f = lambda x : Tools.objects.values('name', 'url').annotate(Count('name')),
        filters = {

        },
        bindings = bindings,
        **kwargs
        )

@has_data
@has_error
def get_tools_ui(request, **kwargs):
    '''
    Called when we want an explicit tool from the UI
    '''
    name = kwargs['name']
    current_version = kwargs['current_version']

    tool = Tools.objects.get(name=name, current_version=current_version)

    #print ('System: {}'.format(tool.system))

    exposed = simplejson.loads(tool.exposed)
    if not len(exposed):
        exposed = [['', '', '']]

    jstree = build_jstree(Tools, tool.name)
    dependencies = build_jstree_tool_dependencies(tool, prefix='3', include_original=False)

    #print ('DEPENDENCIES:')
    #print (dependencies)

    ret = {
        'name': tool.name,
        'current_version': current_version,
        'version' : tool.version, 
        'system' : simplejson.loads(tool.system),
        'username': tool.user.username,
        'created_at': format_time(tool.created_at),
        'url': tool.url,
        'description': tool.description,
        'installation': tool.installation,
        'validate_installation': tool.validate_installation,
        'exposed': exposed,
        'jstree': jstree,
        'references': [x.code for x in tool.references.all()],
        'summary': tool.summary,
        'dependencies': dependencies
    }

    return success(ret)


@has_data
@has_field(
    ['name', 'version', 'url', 'description', 'installation'], 
    ['Name cannot be empty', 'Version cannot be empty', 'Link cannot be empty', 'Description cannot be empty', 'Installation cannot be empty'])
@has_error
def add_tool(request, **kwargs):
    '''
    Attempt to add a new Tool
    '''

    system = kwargs['system']
    system_p = simplejson.loads(system)
    if not len(system_p):
        return fail('Please select one or more systems')

    url = kwargs['url']
    if not URL_validate(url):
        return fail('URL: {} does not seem to be valid'.format(url))

    references = kwargs['references']
    references = simplejson.loads(references)
    references = [Reference.objects.get(code=r) for r in references]

    name = kwargs['name']
    current_version = get_maximum_current_version(Tools, name)
    previous_version = kwargs["previous_version"]
    if previous_version == 'N/A':
        previous_version = None

#    else:
#        print ('Previous version: {}'.format(previous_version))
#        print ('Current version: {}'.format(current_version))
#        a=1/0 # Throw exception deliberately
    print ('Current version: {}'.format(current_version))

    user = get_user(request)
    version = kwargs['version']
    description = kwargs['description']
    installation=kwargs['installation']
    validate_installation = kwargs['validate_installation']
    exposed = kwargs['exposed']
    #print ('Exposed: {} {}'.format(exposed, type(exposed).__name__)) # This is a list
    exposed = [e for e in exposed if any(e)] # Remove empty
    exposed = simplejson.dumps(exposed) # Serialize

    summary = kwargs['summary']

    new_tool = Tools(
        user=user,
        name=name,
        version=version,
        system=system,
        current_version=current_version,
        previous_version=previous_version,
        url = url,
        description = description,
        installation = installation,
        validate_installation = validate_installation,
        exposed = exposed,
        summary = summary,
        );

    new_tool.save()

    #Add references
    new_tool.references.add(*references)
    new_tool.save()
    jstree = build_jstree(Tools, new_tool.name)

    #Add dependencies
    dependencies = kwargs['dependencies']
    dependencies_objects = [Tools.objects.get(name=dependency['name'], current_version=dependency['current_version']) for dependency in dependencies]
    new_tool.dependencies.add(*dependencies_objects)
    new_tool.save()

    #Get created at
    created_at = format_time(new_tool.created_at)
    #print ('Created at: {}'.format(created_at))

    ret = {
        'created_at': created_at,
        'current_version': current_version,
        'jstree': jstree
    }

    return success(ret)

@has_data
@has_error
def jstree_tool(request, **kwargs):
    '''
    AJAX backend to get the version jstree for a tool
    '''

    name = kwargs['name']
    prefix = kwargs['prefix']
    ret = {
        'jstree' : build_jstree(Tools, name, prefix=prefix),
    }

    return success(ret)

@has_data
@has_error
def jstree_report(request, **kwargs):
    '''
    AJAX backend to get the version jstree for a tool
    '''

    name = kwargs['name']
    prefix = kwargs['prefix']
    ret = {
        'jstree' : build_jstree(Reports, name, prefix=prefix),
    }

    return success(ret)


@has_data
@has_error
def jstree_wf(request, **kwargs):
    '''
    AJAX backend to get the version jstree for a tool
    '''

    name = kwargs['name']
    prefix = kwargs['prefix']
    ret = {
        'jstree' : build_jstree(Tasks, name, prefix=prefix),
    }

    return success(ret)


@has_data
@has_error
def jstree_tool_dependencies(request, **kwargs):
    '''
    AJAX backend to get the dependency jstree for a tool 
    '''

    name = kwargs['name']
    current_version = int(kwargs['current_version'])
    if 'prefix' in kwargs:
        prefix=kwargs['prefix']
    else:
        prefix = '3'

    tool = Tools.objects.get(name=name, current_version=current_version)

    ret = {
        'jstree': build_jstree_tool_dependencies(tool, prefix=prefix, include_original=True)
    }

    #print(ret)

    return success(ret)

@has_data
@has_error
def get_tool_dependencies(request, **kwargs):
    '''
    Return ONE LEVEL dependencies of this tool
    '''

    name = kwargs['name']
    current_version = int(kwargs['current_version'])

    tool = Tools.objects.get(name=name, current_version=current_version)
    ret = {
        'dependencies': [{'name': x.name, 'current_version': x.current_version} for x in tool.dependencies.all()]
    }

    return success(ret)

@has_data
@has_error
def get_tool_variables(request, **kwargs):
    '''
    Return the variables of this tool
    '''

    name = kwargs['name']
    current_version = int(kwargs['current_version'])

    tool = Tools.objects.get(name=name, current_version=current_version)
    ret = {
        'variables': simplejson.loads(tool.exposed)
    }

    return success(ret)


########################################
####END OF TOOLS / DATA#################
########################################

########################################
######### WORKFLOWS ####################
########################################

def jason_or_django(f):
    '''
    getattr and iterate methods for JSON or DJANGO objects
    '''
    def dec(*args, **kwargs):

        if type(args[0]) is dict:
            attr = lambda x,y : x[y]
            iterate = lambda x,y : (k for k in x[y])
        elif type(args[0]) is Tasks:
            attr = lambda x,y : getattr(x,y)
            iterate = lambda x,y : (k for k in getattr(x,y).all())
        else:
            raise ArkalosException('This should never happen: {}'.format(type(task)))

        kwargs['attr'] = attr
        kwargs['iterate'] = iterate

        return f(*args, **kwargs)

    return dec

@jason_or_django
def task_hash(task, **kwargs):
    '''
    Creates a unique hash for this task
    attr: Get attribute
    iterate: Iterator 
    '''

    attr = kwargs['attr']
    iterate = kwargs['iterate']
    
# Dictionary version
#    to_hash = [
#        task['name'],
#        task['bash'],
#        task['documentation'],
#        '@@'.join(['&&'.join((x['name'], str(x['current_version']))) for x in task['dependencies'] if x['type'] == 'tool']),
#        '!!'.join(['**'.join((x['name'], str(x['current_version']) if x['is_workflow'] else 'None')) for x in task['calls']]),
#        '##'.join(task['inputs']),
#        '$$'.join(task['outputs'])
#    ]

    # This works with both dictionary and django database objects
    to_hash = [
        attr(task, 'name'),
        attr(task, 'bash'),
        attr(task, 'documentation'),
        '@@'.join(['&&'.join((attr(x, 'name'), str(attr(x, 'current_version')))) for x in iterate(task, 'dependencies')]),
        '!!'.join(['**'.join((attr(x, 'name'), str(attr(x, 'current_version')) if attr(x, 'current_version') else 'None')) for x in iterate(task, 'calls')]),
        '##'.join(attr(task, 'inputs')),
        '$$'.join(attr(task, 'outputs')),
    ]

    to_hash = '^^'.join(to_hash)
    to_hash_b = bytearray(to_hash, encoding="utf-8")

    return hashlib.sha256(to_hash_b).hexdigest()


def save_task_or_workflow(request, workflow_or_task):
    '''
    Saves a workflow or task
    '''

    if workflow_or_task['is_workflow']:
        # This is worflow
        is_workflow = True

        if workflow_or_task['current_version'] is None:
            # This workflow is not saved

            # Get the previous_version
            previous_version = workflow_or_task['previous_version']
            # Get the current number 
            current_version = get_maximum_current_version(Tasks, workflow_or_task['name'])
        else:
            # This workflow is saved. Find it and return it
            worklfow = Tasks.objects.get(name=workflow_or_task['name'], current_version=workflow_or_task['current_version'])
            return worklfow
    else:
        # This is a task
        is_workflow = False
        current_version = None
        previous_version = None
        

        #Check if it exists in the database
        try:
            task = Tasks.objects.get(hash_field=workflow_or_task['hash_value'])
        except ObjectDoesNotExist:
            pass
        else:
            return task

    # It does not exist. Create it!
    task = Tasks(
        user=get_user(request),
        name=workflow_or_task['name'],
        current_version=current_version,
        previous_version=previous_version,
        bash=workflow_or_task['bash'],
        documentation=workflow_or_task['documentation'],
        hash_field=workflow_or_task['hash_value'],
        is_workflow=is_workflow,
        inputs=simplejson.dumps(workflow_or_task['inputs']),
        outputs=simplejson.dumps(workflow_or_task['outputs']),
    )
    task.save()

    # Add dependencies
    tools = []
    for dependency in workflow_or_task['dependencies']:
        if dependency['type'] != 'tool':
            continue

        tools += [Tools.objects.get(name=dependency['name'], current_version=dependency['current_version'])]
    task.dependencies.add(*tools)
    task.save()

    # Add references
    refs = get_references_from_text(workflow_or_task['documentation'])
    task.references.add(*refs)
    task.save()

    return task

def update_TasksStats(task):
    '''
    Update the stats of this task
    '''

    name = task.name

    try:
        taskStat = TasksStats.objects.get(name=name)
    except ObjectDoesNotExist:
        taskStat = TasksStats(
            name=name,
            edits=1,
            users=1,
            last_edit=task,
        )
    else:
        taskStat.edits += 1
        taskStat.users = Tasks.objects.filter(name=name).values('user').count()
        taskStat.last_edit=task
    finally:
        taskStat.save()



@has_data
@has_error
def add_workflow(request, **kwargs):
    '''
    Add a new workflow
    '''

    graph = kwargs['graph']
    main_guid = kwargs['main_guid']

    #Fix is_workflow
    for node in graph:
        node['is_workflow'] = node['type'] == 'workflow'

    #Take main node
    main_node = None
    for node in graph:
        if node['guid'] == main_guid:
            main_node = node
            break

    assert not (main_node is None)
    assert main_node['is_workflow']

    # Check if there is another workflow with the same name
    if main_node['previous_version'] is None: # It is a new workflow! 
        if db_exists(Tasks, {'name': main_node['name']}):
            return fail('Another workflow with this name exists. Please choose another name')

    # Check if this workflow calls another workflow which is unsaved (this is not allowed)
    for node in graph:

        if not node['is_workflow']: # It is not a workflow
            continue

        if node['guid'] == main_guid: # It is not the main workflow
            continue

        if node['current_version'] is None: # It is not saved 
            return fail('Could not save. Workflow: {} calls an UNSAVED workflow: {}'.format(main_node['name'],  node['name']))

    #Fix the "calls"
    guids_to_graph = {node['guid']:node for node in graph}
    for node in graph:
        node['calls'] = [{'name': guids_to_graph[callee_guid]['name'], 'current_version': guids_to_graph[callee_guid]['current_version']} for callee_guid in node['serial_calls']]

    #Do the following three things:
    #1. Add hash_value information 
    #2. Take the hash of the main workflow
    #3. Create a mapping from GUIDs to hash_values
    from_guid_to_hash = {}
    main_hash = None
    guids_to_hashes = {}
    for node in graph:
        #print ('======')
        #print(node)
        node['hash_value'] = task_hash(node)

        if node['guid'] == main_guid:
            main_hash = node['hash_value']

        guids_to_hashes[node['guid']] = node['hash_value']


    assert not (main_hash is None)

    # Save the graph and create a new dictionary with the saved objects
    hash_objects_dict = {
        node['hash_value']: save_task_or_workflow(request, node) 
        for node in graph
    }

    #Add the who calls whom information
    for node in graph:
        this_node_called =[hash_objects_dict[guids_to_hashes[callee_guid]] for callee_guid in node['serial_calls']]
        if this_node_called:
            hash_objects_dict[node['hash_value']].calls.add(*this_node_called)
            hash_objects_dict[node['hash_value']].save()
 
    #Update TaskStats. Perhaps can be done better with signals
    update_TasksStats(hash_objects_dict[main_hash])

    ret = {
        'current_version': hash_objects_dict[main_hash].current_version,
        'created_at': format_time(hash_objects_dict[main_hash].created_at),
    }

    return success(ret)

def workflow_graph(workflow_or_task):
    '''
    Create a  caller--callee graph identical to the one sent from angular for a workflow
    '''

    ret = []
    all_hashes = []

    def create_node(node):
        ret = {
            'bash': node.bash,
            'current_version': node.current_version,
            'previous_version': node.previous_version,
            'documentation': node.documentation,
            'tools_jstree_data':  [build_jstree_tool_dependencies(tool, prefix='5', include_original=True) for x in node.dependencies.all()],
            'inputs': simplejson.loads(node.inputs),
            'outputs': simplejson.loads(node.outputs),
            'type': 'workflow' if node.is_workflow else 'task',
            'hash_value': node.hash_field,
            'children': []
        }

        if node.is_workflow:
            ret['name'] = node.name + '_' + str(node.current_version)
            ret['workflow_name'] = node.name
            ret['created_at'] = format_time(node.created_at)
            ret['username'] = node.user.username

        else:
            ret['name'] = node.name

        return ret

    def workflow_graph_rec(node):

        if node.hash_field in all_hashes:
            return

        all_hashes.append(node.hash_field)
        ret_json = create_node(node)
        ret_json['serial_calls'] = []
        for callee in node.calls.all():
            ret_json['serial_calls'].append(callee.hash_field)
            workflow_graph_rec(callee)

        ret.append(ret_json)

    workflow_graph_rec(workflow_or_task)
    return ret




@has_data
def get_workflow(request, **kwargs):
    '''
    Creates a json object EXACTTLY the same as the one saved 

            return {
                "name": node.type == 'workflow' ? node.workflow_name : node.name,
                "bash": node.bash,
                "current_version": node.current_version, // This is always null
                "previous_version": node.previous_version,
                "documentation": node.documentation,
                "dependencies": node.tools_jstree_data,
                "serial_calls" : node.serial_calls,
                "inputs": node.inputs,
                "outputs": node.outputs,
                "type": node.type,
                "guid": node.guid
            };


    '''

    name = kwargs['name']
    current_version = kwargs['current_version']

    wf = Tasks.objects.get(name=name, current_version=current_version)
    graph = workflow_graph(wf)
#    print ('ret:')
#    print (ret)

    ret = {
        'graph': graph,
        'main_hash': wf.hash_field
    }

    return success(ret)


@has_data
def get_workflows(request, **kwargs):
    '''
    Serve bootstrap table for workflows
    '''

    def description(entry):
        ret = '<p>Edits: <strong>%i</strong> Users: <strong>%i</strong> Last Edit: <strong>%s</strong><br />Last documentation: %s</p>' % (entry.edits, entry.users, format_time(entry.last_edit.created_at), entry.last_edit.documentation)
        return ret

    bindings = {
        'name' : 'name',
        'description': description,
    }

    #return serve_boostrap_table(Tools, bindings, 'name', **kwargs)
    return serve_boostrap_table2(
        model = TasksStats,
        #count_f = lambda : Tasks.objects.values('name').count(), # COUNT ALL
        query_f = lambda x : TasksStats.objects.filter(**x), # Query function
        filters = {
            'name': (lambda : 'name__icontains', lambda x : x) # name_contains = x
        },
        bindings = bindings,
        **kwargs
        )

########################################
####### END OF WORKFLOWS ###############
########################################

