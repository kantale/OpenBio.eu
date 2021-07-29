import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'OpenBio.settings'
import django
django.setup()

from django.contrib.auth.models import User

from app.models import OBC_user


print (User.objects.all().delete())
print ('Deleted all User')

print (OBC_user.objects.all().delete())
print ('Deleted all OBC_user')


