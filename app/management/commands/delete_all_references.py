from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Reference


class Command(BaseCommand):
    help = 'Delete all references.'

    def handle(self, *args, **options):
        print (Reference.objects.all().delete())
        print ('Deleted all References')
