import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'OpenBioC.settings'
import django
django.setup()

from django.contrib.auth.models import User

from app.models import OBC_user

for obc_user in OBC_user.objects.all():
	obc_user.email_validated = False
	obc_user.save()

	print ('Invalidated user:', obc_user.user.username)

