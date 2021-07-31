from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Tool


class Command(BaseCommand):
    help = 'Delete all tools.'

    def handle(self, *args, **options):
        print (Tool.objects.all().delete())
        print ('Deleted all Tool')
