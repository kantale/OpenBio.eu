import simplejson

from django.core.management.base import BaseCommand
from django.conf import settings
from collections import Counter

from ...models import Workflow, Tool, Comment
from ...views import markdown


class Command(BaseCommand):
    help = 'Sanity check.'

    def handle(self, *args, **options):
        for w in Workflow.objects.all():
            d = simplejson.loads(w.workflow)
            change_d = False

            id_counters = Counter(node['data']['id'] for node in d['elements']['nodes'])
            problem = False
            for k,v in id_counters.items():
                if v>1:
                    print ('Workflow: {}. Node {} exists {} times!'.format(str(w), k, v))
                    problem = True

            #if True:
            #   continue

            if not w.comment:
                print ('PROBLEM: Workflow: {} does not have comments! FIXING IT'.format(str(w)))

                c = Comment(obc_user = w.obc_user, comment = '', comment_html = '', title=markdown('Discussion on Workflow: w/{}/{}'.format(w.name, w.edit)), parent = None, upvotes = 0, downvotes = 0)
                c.save()

                w.comment=c
                w.save()

            this_id = w.name + '/' + str(w.edit)

            for w_in in d['elements']['nodes']:
                if w_in['data']['type'] == 'workflow':

                    w_in_name = w_in['data']['name']
                    w_in_edit = w_in['data']['edit']

                    w_in_id = w_in_name + '/' + str(w_in_edit)

                    if not 'disconnected' in w_in['data']:
                        print ('PROBLEM: Workflow: {} does not have a disconnected status inside {}. Setting one to False'.format(str(w_in_id), this_id))
                        w_in['data']['disconnected'] = False
                        change_d = True

                    if w_in['data']['disconnected']:
                        continue

                    if this_id == w_in_id:
                        continue

                    w_in_obj = Workflow.objects.get(name=w_in_name, edit=w_in_edit)
                    if not w.workflows.filter(pk=w_in_obj.pk).exists():
                        print ('PROBLEM: Workflow: {} has workflow {} in graph but not in object model! FIXING IT!'.format(str(w), w_in_id))
                        w.workflows.add(w_in_obj)
                        w.save()

                elif w_in['data']['type'] == 'tool':
                    if w_in['data']['disconnected']:
                        continue

                    w_in_name = w_in['data']['name']
                    w_in_version = w_in['data']['version']
                    w_in_edit = w_in['data']['edit']
                    w_in_id =  w_in_name + '/' + w_in_version + '/' + str(w_in_edit)

                    w_in_obj = Tool.objects.get(name=w_in_name, version=w_in_version, edit=w_in_edit)
                    if not w.tools.filter(pk=w_in_obj.pk).exists():
                        print ('PROBLEM: Workflow: {} has tool {} in graph but not in object model! FIXING IT!'.format(str(w), w_in_id))
                        w.tools.add(w_in_obj)
                        w.save()

            if change_d:
                w.workflow = simplejson.dumps(d)
                w.save()
