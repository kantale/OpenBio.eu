from django.db import models
from django.contrib.auth.models import User

import uuid
import random

'''
After making changes here run:
python manage.py makemigrations
python manage.py migrate;

Important: 
   * When adding new fields, declare a default value (null=True ?)
   * Do not use underscore in class names
'''

class OBC_user(models.Model):
    '''
    Note: the email is stored in user.email
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Basically we will never delete users ??
    email_validated = models.BooleanField() # Is this user's email validated?
    email_validation_token = models.CharField(max_length=32) # This is a uuid4 . TODO: https://docs.djangoproject.com/en/2.1/ref/models/fields/#uuidfield
    password_reset_token = models.CharField(max_length=32, null=True) # A token to reset the password . TODO: https://docs.djangoproject.com/en/2.1/ref/models/fields/#uuidfield 
    password_reset_timestamp = models.DateTimeField(null=True) # When the request to update the password was done 

    # Profile info
    first_name = models.CharField(max_length=256, null=True)
    last_name = models.CharField(max_length=256, null=True)
    website = models.URLField(max_length=256, null=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#urlfield
    affiliation = models.TextField(null=True)
    public_info = models.TextField(null=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#textfield

class Keyword(models.Model):
    '''
    Tool and Workflow Keywords 
    '''

    keyword = models.CharField(max_length=100)

class Variables(models.Model):
    '''
    Model to hold Tool variables
    '''

    name = models.CharField(max_length=256, null=False)
    value = models.CharField(max_length=256, null=False)
    description = models.CharField(max_length=256, null=False)
    tool = models.ForeignKey(to='Tool', on_delete=models.CASCADE, null=False, related_name='variables_related')

class OS_types(models.Model):
    '''
    Hold OS types
    Another option: https://pypi.org/project/django-multiselectfield/
    '''
    ubuntu_14_04 = 'ubuntu:14.04'
    ubuntu_16_04 = 'ubuntu:16.04'
    debian_jessie = 'debian:8'
    debian_stretch = 'debian:9'
    denian_buster = 'debian:10'


    OS_CHOICES = (
        (ubuntu_14_04,'Ubuntu:14.04'),
        (ubuntu_16_04,'Ubuntu:16.04'), 
        (debian_jessie,'Debian 8 (Jessie)'),
        (debian_stretch,'Debian 9 (Stretch)'),
        (denian_buster,'Debian 10 (Buster)'),
     )

    groups = {
        'Ubuntu': [ubuntu_14_04, ubuntu_16_04],
        'Debian': [debian_jessie, debian_stretch, denian_buster],

    }

    @staticmethod
    def get_angular_model():
        '''
        Return a list of..
        {group:'Ubuntu',name:'Ubuntu:14.04',value:'ubuntu:14.04'},
        '''

        return [{
            'group': [group_name for group_name, group_values in OS_types.groups.items() if os_value in group_values][0],
            'name': os_name,
            'value': os_value
        } for os_value, os_name in OS_types.OS_CHOICES]

    os_choices = models.CharField(choices=OS_CHOICES, max_length=100)



class Tool(models.Model):
    '''
    This table describes Tools and Data

    Basically it has a composite key (name, version, edit)
    Django does not support composite keys (for now):
    https://code.djangoproject.com/wiki/MultipleColumnPrimaryKeys

    https://docs.djangoproject.com/en/2.1/ref/models/options/#unique-together
    '''


    class Meta:
        '''
        https://docs.djangoproject.com/en/2.1/ref/models/options/#unique-together
        '''
        unique_together = (('name', 'version', 'edit'),)

    @staticmethod
    def get_repr(name, version, edit):
        '''
        A string reporesentation of the Tool
        '''
        return f'{name}/{version}/{edit}'

    def __str__(self,):
        '''
        A string representation of the tool
        '''
        return Tool.get_repr(self.name, self.version, self.edit)

    '''
    Os_selection ChoicesField
    https://docs.djangoproject.com/en/2.2/ref/models/fields/#field-options
    '''
    # OS_CHOICES = (
    #     ('Ubuntu',(
    #         ('ubuntu:14.04','Ubuntu:14.04'),
    #         ('ubuntu:16.04','Ubuntu:16.04'),
    #     )),
    #     ('Debian',(
    #         ('jessie','Debian 8 (Jessie)'),
    #         ('stretch','Debian 9 (Stretch)'),
    #         ('buster','Debian 10 (Buster)')
    #     )), 
    # )


    name = models.CharField(max_length=256)
    version = models.CharField(max_length=256)
    edit = models.IntegerField()

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE) # Never delete users..

    website = models.URLField(max_length=256, null=True)
    description = models.TextField(null=True)
    description_html = models.TextField(null=True)
    keywords = models.ManyToManyField(Keyword)
    forked_from = models.ForeignKey(to="Tool", null=True, on_delete=models.CASCADE, related_name='forked_from_related') #Is this forked from another tool? Also Never delete tools
    changes = models.TextField(null=True) # What changes have been made from forked tool?
    created_at = models.DateTimeField(auto_now_add=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#datefield 

    dependencies = models.ManyToManyField(to='Tool', related_name='dependencies_related') # the dependencies of this tool
    os_choices = models.ManyToManyField(to='OS_types') # The OSs that this tool runs 
    installation_commands = models.TextField() # The BASH commands to install this tool
    validation_commands = models.TextField() # The BASH commands to validate this tool

    variables = models.ManyToManyField(to='Variables', related_name='tools_related') # The exposed variables of this tool
    #validation_status = models.CharField(max_length=256) # unvalidated, submitted, ...
    last_validation = models.ForeignKey(to="ToolValidations", null=True, on_delete=models.CASCADE, related_name='last_validation_related')

class ToolValidations(models.Model):
    '''
    This is like a log entry.
    '''

    @staticmethod
    def get_tool_from_task_id(task_id):
        '''
        Gets the tool from a task_id field in the ToolValidations Table
        '''
        query = ToolValidations.objects.filter(task_id=task_id).order_by('created_at')
        if not query.exists():
            return None

        # Get the tool of the last record with that id
        return query.last().tool

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE) # The tool that we are validating

    # The task id in controller. This is a uuid . 
    # We are not using UUIDField because this is not JSON serializable?? 
    task_id = models.CharField(max_length=256) 

    validation_status = models.CharField(max_length=256) 
    errcode = models.IntegerField(null=True)
    stdout = models.TextField(null=True)
    stderr = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#datefield 


class Workflow(models.Model):
    '''
    Describe a single Workflow
    '''

    class Meta:
        '''
        https://docs.djangoproject.com/en/2.1/ref/models/options/#unique-together
        '''
        unique_together = (('name', 'edit'),)


    name = models.CharField(max_length=256)
    edit = models.IntegerField()

    website = models.URLField(max_length=256, null=True)
    description = models.TextField(null=False) # Unlike tools description cannot be empty
    description_html = models.TextField(null=False)
    keywords = models.ManyToManyField(Keyword)

    # JSON serialized,  The workflow cytoscape graph , cy.json. 
    # TODO: When deploying in Postgresql change this to JSONField
    # https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/fields/#jsonfield 
    workflow = models.TextField(null=False)

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    forked_from = models.ForeignKey(to="Workflow", null=True, on_delete=models.CASCADE, related_name='forked_from_related') #Is this forked from another tool?
    changes = models.TextField(null=True) # What changes have been made from forked tool?

    # Links to the tools used (for stats)
    tools = models.ManyToManyField(Tool)

    created_at = models.DateTimeField(auto_now_add=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#datefield 

class ReportToken(models.Model):
    '''
    Each report has multiple Tokens 
    Each Token represent represent a state of the workflow
    '''

    WORKFLOW_STARTED = 'workflow started'
    WORKFLOW_FINISHED = 'workflow finished'
    UNUSED = 'unused'

    STATUS_CHOICES = (WORKFLOW_STARTED, WORKFLOW_FINISHED)

    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # https://books.agiliq.com/projects/django-orm-cookbook/en/latest/uuid.html
    status = models.CharField(max_length=255) # The status of this token
    active = models.BooleanField() # Each token can be used only once. Once used it is set to non active
    created_at = models.DateTimeField(auto_now_add=True)


def create_nice_id(length=5):
    '''
    Create a nice ID for Report class
    I tried to add it as a static method in Report class (below) but the following happened:

    ValueError: Cannot serialize: <staticmethod object at 0x10a8b4908>
    There are some values Django cannot serialize into migration files.
    For more, see https://docs.djangoproject.com/en/2.1/topics/migrations/#migration-serializing

    Any ideas how to fix this?

    '''

    possible_letters = list(range(ord('a'), ord('z')+1)) + list(range(ord('A'), ord('Z')+1)) + list(range(ord('0'), ord('9')+1))
    return ''.join([chr(random.choice(possible_letters)) for _ in range(length)])


class Report(models.Model):
    '''
    Describe a Report
    A Report is an executed workflow
    '''


    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE) # The workflow that it run
    nice_id = models.CharField(max_length=10, unique=True, default=create_nice_id, editable=False)
    tokens = models.ManyToManyField(ReportToken, related_name='report_related')
    created_at = models.DateTimeField(auto_now_add=True)

class ReferenceField(models.Model):
    '''
    This is a tuple of keys/values that come from parsing the BIBTEX entry
    For example: 
    'journal': 'The American journal of human genetics'
    '''

    key = models.CharField(max_length=255,)
    value = models.CharField(max_length=1000,)

class Reference(models.Model):
    '''
    Describe a reference
    '''

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, unique=True, editable=False)
    title = models.CharField(max_length=1000,)
    url = models.URLField(max_length=256, null=False)
    doi = models.URLField(max_length=256, null=True)
    bibtex = models.TextField(null=True)
    html = models.TextField(null=True)
    notes= models.TextField(null=True)
    fields = models.ManyToManyField(ReferenceField, related_name='reference_related')
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    '''
    Q & As
    '''

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    comment = models.TextField()
    comment_html = models.TextField()
    title = models.CharField(max_length=1000,)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(to='Comment', null=True, on_delete=models.CASCADE, related_name='comment_parent')
    children =  models.ManyToManyField(to='Comment', related_name='comment_children')



