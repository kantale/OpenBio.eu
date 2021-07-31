from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Workflow


class Command(BaseCommand):
    help = 'Delete all workflows.'

    def handle(self, *args, **options):
        print (Workflow.objects.all().delete())
        print ('Deleted all Workflow')
