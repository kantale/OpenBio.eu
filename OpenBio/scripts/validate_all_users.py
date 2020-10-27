import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'OpenBioC.settings'
import django
django.setup()

from django.contrib.auth.models import User

from app.models import OBC_user

for obc_user in OBC_user.objects.all():
	obc_user.email_validated = True
	obc_user.email_validation_token = None
	obc_user.save()

	print ('Validated user:', obc_user.user.username)

