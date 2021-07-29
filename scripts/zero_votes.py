'''
Set zero all upvotes / downvotes
'''

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'OpenBio.settings'
import django
django.setup()

from django.contrib.auth.models import User

from app.models import Comment, UpDownCommentVote, Tool, Workflow

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

def do_1():
	pass

if __name__ == '__main__':
	do_1()
