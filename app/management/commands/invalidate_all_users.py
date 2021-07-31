from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import OBC_user


class Command(BaseCommand):
    help = 'Invalidate all users.'

    def handle(self, *args, **options):
        for obc_user in OBC_user.objects.all():
            obc_user.email_validated = False
            obc_user.save()
            print ('Invalidated user:', obc_user.user.username)
