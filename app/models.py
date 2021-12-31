from django.db import models
from django.contrib.auth.models import User

import re
import uuid
import random
import string

'''
After making changes here run:
python manage.py makemigrations
python manage.py migrate;

Important:
   * When adding new fields, declare a default value (null=True ?)
   * Do not use underscore in class names
'''

class ExecutionClient(models.Model):

    name = models.CharField(max_length=256, null=False)
    parameters = models.TextField(null=False) # The parameters of the client in json 
    created_at = models.DateTimeField(auto_now_add=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#datefield


class OBC_user(models.Model):
    '''
    Note: the email is stored in user.email

    # Here are the fields that user has:
    https://docs.djangoproject.com/en/2.2/ref/contrib/auth/#django.contrib.auth.models.User
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Basically we will never delete users ??
    email_validated = models.BooleanField() # Is this user's email validated?
    email_validation_token = models.CharField(max_length=32, null=True) # This is a uuid4 . TODO: https://docs.djangoproject.com/en/2.1/ref/models/fields/#uuidfield
    password_reset_token = models.CharField(max_length=32, null=True) # A token to reset the password . TODO: https://docs.djangoproject.com/en/2.1/ref/models/fields/#uuidfield
    password_reset_timestamp = models.DateTimeField(null=True) # When the request to update the password was done

    # Profile info
    first_name = models.CharField(max_length=256, null=True)
    last_name = models.CharField(max_length=256, null=True)
    website = models.URLField(max_length=256, null=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#urlfield
    affiliation = models.TextField(null=True)
    public_info = models.TextField(null=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#textfield

    #A user can have many Execution Clients
    clients = models.ManyToManyField(ExecutionClient)

    # A user can have many References
    references = models.ManyToManyField(to='Reference', related_name='users_authored_me')


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

    posix = 'posix'
    ubuntu_14_04 = 'ubuntu:14.04'
    ubuntu_16_04 = 'ubuntu:16.04'
    debian_jessie = 'debian:8'
    debian_stretch = 'debian:9'
    denian_buster = 'debian:10'
    osx_1 = 'osx:1'


    OS_CHOICES = (
        (posix, 'POSIX system'),
        (ubuntu_14_04,'Ubuntu:14.04'),
        (ubuntu_16_04,'Ubuntu:16.04'),
        (debian_jessie,'Debian 8 (Jessie)'),
        (debian_stretch,'Debian 9 (Stretch)'),
        (denian_buster,'Debian 10 (Buster)'),
        (osx_1, 'Mac OSX Intel'),
     )

    groups = {
        'Generic': [posix],
        'Ubuntu': [ubuntu_14_04, ubuntu_16_04],
        'Debian': [debian_jessie, debian_stretch, denian_buster],
        'OSX': [osx_1],

    }

    @staticmethod
    def get_angular_model(values=None):
        '''
        Return a list of..
        {group:'Ubuntu',name:'Ubuntu:14.04',value:'ubuntu:14.04'},

        if values is not None, then filter on values

        Explanation of the "(not values) | (os_name in values)" part:
        if values is None then the (not values) is True so the second part will not be evaluated
        if values is a non-empty-list then the (not values) is False so the second part will be evaluated
        '''

        return [{
            'group': [group_name for group_name, group_values in OS_types.groups.items() if os_value in group_values][0],
            'name': os_name,
            'value': os_value,
        } for os_value, os_name in OS_types.OS_CHOICES if (not values) or (os_value in values)]

    os_choices = models.CharField(choices=OS_CHOICES, max_length=100, unique=True)

class VisibilityOptions:

    PUBLIC_CODE = 1
    PUBLIC_NAME = 'public'

    PRIVATE_CODE = 2
    PRIVATE_NAME = 'private'

    VISIBILITY_OPTIONS = (
        (PUBLIC_CODE, PUBLIC_NAME),
        (PRIVATE_CODE, PRIVATE_NAME),
    )

    VISIBILITY_OPTIONS_CODE_dic = {str(x):y for x,y in VISIBILITY_OPTIONS}
    VISIBILITY_OPTIONS_NAME_dic = {y:x for x,y in VISIBILITY_OPTIONS}

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

    upvotes = models.IntegerField() # Number of upvotes
    downvotes = models.IntegerField() # Number of downvotes
    draft = models.BooleanField() # Is this a draft Tool?

    comment = models.ForeignKey(to='Comment', null=True, on_delete=models.CASCADE, related_name='tool_comment') # The comments of the tool

    visibility = models.CharField(choices=VisibilityOptions.VISIBILITY_OPTIONS, max_length=100, default=VisibilityOptions.PUBLIC_CODE)


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

    @staticmethod
    def get_repr(name, edit):
        '''
        A string reporesentation of the workflow
        '''
        return f'{name}/{edit}'

    def __str__(self,):
        '''
        A string representation of the workflow
        '''
        return Workflow.get_repr(self.name, self.edit)

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
    forked_from = models.ForeignKey(to='Workflow', null=True, on_delete=models.CASCADE, related_name='forked_from_related') #Is this forked from another tool?

    # All tools used by this workflow
    tools = models.ManyToManyField(to='Tool', related_name='workflows_using_me')

    # All workflows used by this workflow
    # The fact that the related_name with tools is the same is not a bug!
    workflows = models.ManyToManyField(to='Workflow', related_name='workflows_using_me')

    changes = models.TextField(null=True) # What changes have been made from forked tool?

    created_at = models.DateTimeField(auto_now_add=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#datefield

    upvotes = models.IntegerField() # Number of upvotes
    downvotes = models.IntegerField() # Number of downvotes
    draft = models.BooleanField() # Is this a draft Workflow?
    comment = models.ForeignKey(to='Comment', null=True, on_delete=models.CASCADE, related_name='workflow_comment') # The comments of the tool

    visibility = models.CharField(choices=VisibilityOptions.VISIBILITY_OPTIONS, max_length=100, default=VisibilityOptions.PUBLIC_CODE)

class ReportToken(models.Model):
    '''
    Each report has multiple Tokens
    Each Token represent a state of the workflow
    '''

    # IMPORTANT: ADD THESE CODES ALSO IN ui.js :  window.OBCUI
    WORKFLOW_STARTED_CODE = 1
    WORKFLOW_STARTED = r'workflow started (?P<name>[\w\./]+)[\s]*$'

    WORKFLOW_FINISHED_CODE = 2
    WORKFLOW_FINISHED = r'workflow finished (?P<name>[\w\./]+)[\s]*$'

    TOOL_STARTED_CODE = 3
    TOOL_STARTED = r'tool started (?P<name>[\w\./]+)[\s]*$'

    TOOL_FINISHED_CODE = 4
    TOOL_FINISHED = r'tool finished (?P<name>[\w\./]+)[\s]*$'

    STEP_STARTED_CODE = 5
    STEP_STARTED = r'step started (?P<name>[\w]+) (?P<caller>[\w]+)[\s]*$'

    STEP_FINISHED_CODE = 6
    STEP_FINISHED = r'step finished (?P<name>[\w]+)[\s]*$'

    UNUSED = 'unused'

    STATUS_CHOICES = (
        (WORKFLOW_STARTED_CODE, WORKFLOW_STARTED),
        (WORKFLOW_FINISHED_CODE, WORKFLOW_FINISHED),
        (TOOL_STARTED_CODE, TOOL_STARTED),
        (TOOL_FINISHED_CODE, TOOL_FINISHED),
        (STEP_STARTED_CODE, STEP_STARTED),
        (STEP_FINISHED_CODE, STEP_FINISHED),
    )

    @staticmethod
    def parse_response_status(status):
        '''
        Used from views.report to parse the received status
        '''
        for status_code, status_re in ReportToken.STATUS_CHOICES:
            m = re.match(status_re, status)
            if m:
                return {'status_code': status_code, 'status_fields': m.groupdict()}

        # We don't need this here to return None, left for readability
        return None



    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # https://books.agiliq.com/projects/django-orm-cookbook/en/latest/uuid.html
    status = models.CharField(max_length=255) # The status of this token
    active = models.BooleanField() # Each token can be used only once. Once used it is set to non active
    created_at = models.DateTimeField(auto_now_add=True)


def create_nice_id(length=8):
    '''
    Create a nice ID for Report class
    I tried to add it as a static method in Report class (below) but the following happened:

    ValueError: Cannot serialize: <staticmethod object at 0x10a8b4908>
    There are some values Django cannot serialize into migration files.
    For more, see https://docs.djangoproject.com/en/2.1/topics/migrations/#migration-serializing

    Any ideas how to fix this?

    '''

    possible_letters = tuple(string.ascii_lowercase + string.digits)
    return ''.join(random.sample(possible_letters, length))

class Report(models.Model):
    '''
    Describe a Report
    A Report is an executed workflow or a workflow that is being executed now.
    '''

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, null=False, on_delete=models.CASCADE) # The workflow that it run
    nice_id = models.CharField(max_length=10, unique=True, default=create_nice_id, editable=False)
    client = models.ForeignKey(to='ExecutionClient', null=True, on_delete=models.CASCADE) # Which client creates this report?
    url = models.URLField(max_length=256, null=True) # The url of the report (containing the results)
    log_url = models.URLField(max_length=256, null=True) # The url of the log (containing the results)
    visualization_url = models.URLField(max_length=256, null=True) # The url of the visualization environment (i.e. airflow)
    monitor_url = models.URLField(max_length=256, null=True) # The url of the monitoring environment (i.e. netdata)
    refresh_enabled = models.BooleanField(default=False) # Can this report be updated from the client?
    client_status = models.CharField(max_length=25, null=True) # The status of the client
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

    OPINION_NOTE_CODE = 1
    OPINION_NOTE = 'note'
    OPINION_AGREE_CODE = 2
    OPINION_AGREE = 'agree'
    OPINION_DISAGREE_CODE = 3
    OPINION_DISAGREE = 'disagree'
    OPINION_SOLUTION_CODE = 4
    OPINION_SOLUTION = 'solution'
    OPINION_ISSUE_CODE = 5
    OPINION_ISSUE = 'issue'

    OPINION_CHOICES = (
        (OPINION_NOTE_CODE, OPINION_NOTE),
        (OPINION_AGREE_CODE, OPINION_AGREE),
        (OPINION_DISAGREE_CODE, OPINION_DISAGREE),
        (OPINION_SOLUTION_CODE, OPINION_SOLUTION),
        (OPINION_ISSUE_CODE, OPINION_ISSUE),
    )

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    comment = models.TextField()
    comment_html = models.TextField()
    title = models.CharField(max_length=1000,)
    opinion = models.CharField(choices=OPINION_CHOICES, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(to='Comment', null=True, on_delete=models.CASCADE, related_name='comment_parent')
    children =  models.ManyToManyField(to='Comment', related_name='comment_children')
    upvotes = models.IntegerField() # Number of upvotes
    downvotes = models.IntegerField() # Number of downvotes


class UpDownCommentVote(models.Model):
    '''
    Represents one Up/Down vote at a comment
    '''

    class Meta:
        '''
        https://docs.djangoproject.com/en/2.1/ref/models/options/#unique-together
        '''
        unique_together = (('obc_user', 'comment'),)

        indexes = [
                models.Index(
                    fields=['obc_user', 'comment',],
                    name='UpDownCommentVote_idx',
                ),
            ]

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, null=False, on_delete=models.CASCADE)
    upvote = models.BooleanField() # True --> upvote, False --> downvote
    created_at = models.DateTimeField(auto_now_add=True)


class UpDownToolVote(models.Model):
    '''
    Represents one Up/Down vote at a Tool
    '''

    class Meta:
        '''
        https://docs.djangoproject.com/en/2.1/ref/models/options/#unique-together
        '''
        unique_together = (('obc_user', 'tool'),)

        indexes = [
                models.Index(
                    fields=['obc_user', 'tool',],
                    name='UpDownToolVote_idx',
                ),
            ]

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, null=True, on_delete=models.CASCADE) # null=true to make them votes transferable to other tools
    upvote = models.BooleanField() # True --> upvote, False --> downvote
    created_at = models.DateTimeField(auto_now_add=True)

class UpDownWorkflowVote(models.Model):
    '''
    Represents one Up/Down vote at a Workflow
    '''

    class Meta:
        '''
        https://docs.djangoproject.com/en/2.1/ref/models/options/#unique-together
        '''
        unique_together = (('obc_user', 'workflow'),)

        indexes = [
                models.Index(
                    fields=['obc_user', 'workflow',],
                    name='UpDownWorkflowVote_idx',
                ),
            ]

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, null=True, on_delete=models.CASCADE) # null=true to make them votes transferable to other tools
    upvote = models.BooleanField() # True --> upvote, False --> downvote
    created_at = models.DateTimeField(auto_now_add=True)




