from django.core.management.base import BaseCommand
from django.conf import settings

from django.contrib.auth.models import User
from ...models import OBC_user


class Command(BaseCommand):
    help = 'Delete all users.'

    def handle(self, *args, **options):
        print (User.objects.all().delete())
        print ('Deleted all User')

        print (OBC_user.objects.all().delete())
        print ('Deleted all OBC_user')
