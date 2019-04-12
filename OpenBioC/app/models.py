from django.db import models
from django.contrib.auth.models import User

'''
After making changes here run:
python manage.py makemigrations
python manage.py migrate;

Important: When adding new fields, declare a default value (null=True ?)
'''

class OBC_user(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Basically we will never delete users ??
    email_validated = models.BooleanField() # Is this user's email validated?
    email_validation_token = models.CharField(max_length=32) # This is a uuid4 . TODO: https://docs.djangoproject.com/en/2.1/ref/models/fields/#uuidfield
    password_reset_token = models.CharField(max_length=32, null=True) # A token to reset the password . TODO: https://docs.djangoproject.com/en/2.1/ref/models/fields/#uuidfield 
    password_reset_timestamp = models.DateTimeField(null=True) # When the request to update the password was done 

    # Profile info
    first_name = models.CharField(max_length=256, null=True)
    last_name = models.CharField(max_length=256, null=True)
    website = models.URLField(max_length=256, null=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#urlfield
    public_info = models.TextField(null=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#textfield


class Variables(models.Model):
    '''
    Model to hold Tool variables
    '''

    name = models.CharField(max_length=256, null=False)
    value = models.CharField(max_length=256, null=False)
    description = models.CharField(max_length=256, null=False)
    tool = models.ForeignKey(to='Tool', on_delete=models.CASCADE, null=False, related_name='variables_related')

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

    name = models.CharField(max_length=256)
    version = models.CharField(max_length=256)
    edit = models.IntegerField()

    obc_user = models.ForeignKey(OBC_user, null=False, on_delete=models.CASCADE) # Never delete users..

    website = models.URLField(max_length=256, null=True)
    description = models.TextField(null=True) 
    forked_from = models.ForeignKey(to="Tool", null=True, on_delete=models.CASCADE, related_name='forked_from_related') #Is this forked from another tool? Also Never delete tools
    changes = models.TextField(null=True) # What changes have been made from forked tool?
    created_at = models.DateTimeField(auto_now_add=True) # https://docs.djangoproject.com/en/2.1/ref/models/fields/#datefield 

    dependencies = models.ManyToManyField(to='Tool', related_name='dependencies_related') # the dependencies of this tool
    os_type = models.TextField(null=True) # The os which user select to install this tool
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




