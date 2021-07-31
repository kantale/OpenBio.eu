from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Comment, UpDownCommentVote, Tool, Workflow


class Command(BaseCommand):
    help = 'Set all upvotes/downvotes to zero.'

    def handle(self, *args, **options):
        UpDownCommentVote.objects.all().delete()
        for c in Comment.objects.all():
            c.upvotes = 0
            c.downvotes = 0
            c.save()
        for c in Tool.objects.all():
            c.upvotes = 0
            c.downvotes = 0
            c.save()
        for c in Workflow.objects.all():
            c.upvotes = 0
            c.downvotes = 0
            c.save()
