
import os
import json
import argparse 

from collections import defaultdict

class OBC_Executor_Exception(Exception):
	'''
	'''
	pass

class Worfklow:
	'''
	'''

	WORKFLOW_TYPE = 'workflow'
	INPUT_TYPE = 'input'
	OUTPUT_TYPE = 'output'
	STEP_TYPE = 'step'
	TOOL_TYPE = 'tool'

	def __init__(self, workflow_filename):
		'''
		'''

		if not os.path.exists(workflow_filename):
			raise OBC_Executor_Exception(f'File {workflow_filename} does not exist')

		self.workflow_filename = workflow_filename
		self.parse_workflow_filename()

	def __str__(self,):
		return json.dumps(self.workflow, indent=4)

	def parse_workflow_filename(self, ):
		'''
		'''

		with open(self.workflow_filename) as f:
			self.workflow = json.load(f)

		self.input_parameters = self.get_input_parameters()
		self.root_workflow = self.get_root_workflow()
		self.root_inputs_outputs = self.get_input_output_from_workflow(self.root_workflow)

		# Apply some integrity checks
		for node in self.node_iterator():
			# Every node has a type
			assert 'type' in node
			# Every node has a id
			assert 'id' in node
			# Every node has a belongto
			assert 'belongto' in node

			# Assert proper fields and types in belongto
			if not node['belongto'] is None:
				assert 'name' in node['belongto']
				assert 'edit' in node['belongto']
				assert type(node['belongto']['name']) is str
				assert type(node['belongto']['edit']) is int

		# Check that all root input output are set
		for root_input_node in self.root_inputs_outputs['inputs']:
			print ('The following input values have been set:')
			for arg_input_name, arg_input_value in self.input_parameters.items():
				if arg_input_name == root_input_node['id']:
					print ('  {}={}'.format(root_input_node['id'], arg_input_value))
					break
			else:
				message = 'Input parameter: {} has not been set!'.format(root_input_node['id'])
				raise OBC_Executor_Exception(message)

	def get_tool_installation_order(self, ):
		'''
		Get a list of tools in dependency order.
		'''

		for a_node in self.node_iterator():
			if not self.is_tool(a_node):
				continue

			print (a_node)



	def get_input_parameters(self, ):
		'''
		'''

		return self.workflow.get('arguments', [])

	def node_iterator(self,):
		for node in self.workflow['workflow']['elements']['nodes']:
			yield node['data']

	def get_root_workflow(self,):
		'''
		'''

		ret = None

		for node in self.node_iterator():
			if node.get('belongto', None) is None:
				if not ret is None:
					raise OBC_Executor_Exception('Integrity Error: Found more than one root workflow')

				ret = node

		if ret is None:
			raise OBC_Executor_Exception('Failed to locate root worfklow')

		return ret

	def node_2_str(self, node):
		'''
		'''
		return json.dumps(node, indent=4)


	def is_input_output(self, node):
		'''
		'''
		return node['type'] in [self.INPUT_TYPE, self.OUTPUT_TYPE]

	def is_step(self, node):
		'''
		'''
		return node['type'] == self.STEP_TYPE

	def is_tool(self, node):
		return node['type'] == self.TOOL_TYPE

	def belongto(self, node):
		'''
		'''
		if node['belongto'] is None:
			return None

		return node['belongto']['name'] + '__' + str(node['belongto']['edit'])



	def get_input_output_from_workflow(self, node):
		'''
		'''

		if not node['type'] == self.WORKFLOW_TYPE:
			message = f'Cannot get input/ouputs from a no-network node \nNode: \n{self.node_2_str(node)}'
			raise OBC_Executor_Exception(message)

		ret = {'inputs': [], 'outputs': []}

		for a_node in self.node_iterator(): 
			if self.is_input_output(a_node) and self.belongto(a_node) == node['id']:
				ret[a_node['type'] + 's'].append(a_node)

		return ret

	def get_steps_from_workflow(self, node):
		'''
		'''
		if not node['type'] == self.WORKFLOW_TYPE:
			message = f'Cannot get steps from a no-network node \nNode: \n{self.node_2_str(node)}'
			raise OBC_Executor_Exception(message)

		ret = []
		for a_node in self.node_iterator():
			if self.is_step(a_node) and self.belongto(a_node) == node['id']:
				ret.append(a_node)

		return ret

if __name__ == '__main__':
	'''

	'''
	parser = argparse.ArgumentParser(description='OpenBio-C worfklow execute-or')

	parser.add_argument('-W', '--workflow', dest='workflow_filename', help='JSON filename of the workflow to run', required=True)

	args = parser.parse_args()

	w = Worfklow(args.workflow_filename)
	#print (w.root_inputs_outputs)
	#print (w)
	w.get_tool_installation_order()

	



