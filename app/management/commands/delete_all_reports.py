from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Report


class Command(BaseCommand):
    help = 'Delete all reports.'

    def handle(self, *args, **options):
        print (Report.objects.all().delete())
        print ('Deleted all Reports')
