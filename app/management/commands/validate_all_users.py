from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import OBC_user


class Command(BaseCommand):
    help = 'Validate all users.'

    def handle(self, *args, **options):
        for obc_user in OBC_user.objects.all():
            obc_user.email_validated = True
            obc_user.email_validation_token = None
            obc_user.save()

            print ('Validated user:', obc_user.user.username)
