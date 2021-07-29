'''
Migration from 0.1.1 --> 0.1.2
Change the Cytoscape IDS of steps, inputs, outputs
'''


import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'OpenBio.settings'
import django
django.setup()

from django.contrib.auth.models import User

from app.models import Workflow
import json

def do_1():


	def create_new_id(old_node_id, node_type):
		if node_type in ['input', 'output', 'step']:
			if not old_node_id.startswith(node_type):
				#raise Exception('THIS SHOULD NOT HAPPEN!')
				return node_type + '__' + old_node_id
			else:
				return old_node_id
		else:
			return old_node_id

	for w in Workflow.objects.all():
		print ('Workflow:', w.name)
		graph = json.loads(w.workflow)

		#print (json.dumps(graph, indent=4))
		elements = graph['elements']
		nodes = elements['nodes']
		edges = elements['edges']

		node_type_d = {}
		# Create a node type
		for node in nodes:
			node_data = node['data']
			node_id = node_data['id']
			node_type = node_data['type']
			print ('--> {}'.format(node_id))
			node_type = node_data['type']
			if node_id in node_type_d:
				raise Exception ('This should not happen..')
			node_type_d[node_id] = node_type
			if node_type in ['step', 'output', 'input']:
				node_type_d[create_new_id(node_id, node_type)] = node_type

		print ('===================================')
		print(json.dumps(node_type_d, indent=4))
		print ('===================================')

		for node in nodes:
			node_data = node['data']
			node_id = node_data['id']
			node_type = node_data['type']
			if node_type in ['input', 'output', 'step']:
				# Change node id
				new_node_id = create_new_id(node_id, node_type)
				print ('    {}-->{}-->{}'.format(node_type, node_id, new_node_id))

				# Change edge id
				for edge in edges:
					edge_data = edge['data']
					edge_id = edge_data['id']
					source_id, target_id = edge_id.split('..')
					if source_id == node_id:
						new_source_id = new_node_id
					else:
						new_source_id = source_id

					if target_id == node_id:
						new_target_id = new_node_id
					else:
						new_target_id = target_id
					new_edge_id = '{}..{}'.format(new_source_id, new_target_id)
					print ('        EDGE: {} --> {}'.format(edge_id, new_edge_id))

					edge['data']['source'] = new_source_id
					edge['data']['target'] = new_target_id
					edge['data']['id'] = new_edge_id

				node['data']['id'] = new_node_id

			if node_type == 'step':
				node_steps = node_data['steps']
				new_node_steps = []
				for step in node_steps:
					new_node_steps.append(create_new_id(step, node_type_d[step]))

				node_inputs = node_data['inputs']
				new_node_inputs = []
				for inp in node_inputs:
					new_node_inputs.append(create_new_id(inp, node_type_d[inp]))

				node_outputs = node_data['outputs']
				new_node_outputs = []
				for out in node_outputs:
					new_node_outputs.append(create_new_id(out, node_type_d[out]))

				node['data']['steps'] = new_node_steps
				node['data']['inputs'] = new_node_inputs
				node['data']['outputs'] = new_node_outputs

		w.workflow = json.dumps(graph)
		w.save()
		print ('       --> SAVED')


		#a=1/0

if __name__ == '__main__':
	do_1()
