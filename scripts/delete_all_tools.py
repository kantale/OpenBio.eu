import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'OpenBio.settings'
import django
django.setup()

from django.contrib.auth.models import User

from app.models import Tool


print (Tool.objects.all().delete())
print ('Deleted all Tool')


