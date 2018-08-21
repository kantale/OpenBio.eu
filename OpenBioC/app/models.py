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

