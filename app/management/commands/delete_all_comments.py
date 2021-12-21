from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Comment


class Command(BaseCommand):
    help = 'Delete all comments.'

    def handle(self, *args, **options):
        print (Comment.objects.all().delete())
        print ('Deleted all Comments')
