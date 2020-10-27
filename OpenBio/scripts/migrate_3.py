import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'OpenBioC.settings'
import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist

from app.models import Tool, Workflow

import json

'''
Add tools and workflows to workflows
'''

def do_1():

	for w in Workflow.objects.all():

		print ('Worfklow:', w.name, w.edit)

		w_j = w.workflow
		w_d = json.loads(w_j)
		tools = [{'name': x['data']['name'], 'version': x['data']['version'], 'edit': x['data']['edit']} for x in w_d['elements']['nodes'] if x['data']['type'] == 'tool']

		for t in tools:
			try:
				t_o = Tool.objects.get(**t)
			except ObjectDoesNotExist as e:
				print ('Tool does not exist!', t)
				continue

			print ('   Adding tool:', t_o)
			w.tools.add(t_o)
			w.save()

		workflows = [{'name': x['data']['name'], 'edit': x['data']['edit']} for x in w_d['elements']['nodes'] if x['data']['type'] == 'workflow']
		for w2 in workflows:
			if w.name == w2['name'] and w.edit == w2['edit']:
				print ('   Skipping self workflow:', w2)
				continue

			w_o = Workflow.objects.get(**w2)
			print ('   Adding workflow:', w_o)
			w.workflows.add(w_o)
			w.save()

if __name__ == '__main__':
	do_1()