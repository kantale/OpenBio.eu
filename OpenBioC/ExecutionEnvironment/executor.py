
import io
import os
import re
import copy
import json
import base64
import logging
import bashlex
import argparse 

from collections import defaultdict

logging.basicConfig(level=logging.DEBUG)

class OBC_Executor_Exception(Exception):
	'''
	'''
	pass

def detect_circles(graph, start, end):
    '''
    https://stackoverflow.com/questions/40833612/find-all-cycles-in-a-graph-implementation
    '''
    fringe = [(start, [])]
    while fringe:
        state, path = fringe.pop()
        if path and state == end:
            yield path
            continue
        for next_state in graph[state]:
            if next_state in path:
                continue
            fringe.append((next_state, path+[next_state]))

bash_patterns = {
    'parse_json' : r'''
function obc_parse_json()
{
    echo $1 | \
    sed -e "s/.*$2\":[ ]*\"\([^\"]*\)\".*/\1/"
}
''' + '\n', # https://stackoverflow.com/a/26655887/5626738 
    'curl_send_json': '''curl -s --header "Content-Type: application/json" --request POST -d '{json}' {url}''',
    'command_to_variable': '''{variable}=$({command})''',
    'string_contains': '''
if [[ ${variable} == *'{string}'* ]]; then
   {contains_yes}
else
   {contains_no}
fi
''',
    'fail': 'echo "{error_message}"\nexit 1\n',
    'update_server_status': r'''
function update_server_status()
{

    if [[ $obc_current_token =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then

        local command="curl {insecure}-s --header \"Content-Type: application/json\" --request POST -d '{\"token\": \"$obc_current_token\", \"status\": \"$1\"}' {server}/report/"

        local c=$(eval "$command")

        if [[ $c == *'"success": true'* ]]; then
            obc_current_token=$(obc_parse_json "$c" "token")
        else
           
            if [[ $c == *'"success": false'* ]]; then
                obc_error_message=$(obc_parse_json "$c" "error_message")
                echo "Server Return Error: $obc_error_message"
                # exit 1
            else
                echo "Server does not respond, or unknown error"
                # exit 1
            fi
        fi
    else
        : 
    fi
}

''',
  'base64_decode': r'''
function obc_base64_decode() {
    echo $1 | base64 --decode
}
''',
'validate': r'''
function obc_validate() {
    local command="$(obc_base64_decode $1)"
    eval $command
}
'''
}

bash_patterns['get_json_value'] = '{variable}=$(obc_parse_json "${json_variable}" "{json_key}")'

# Global parameters
g = {
    'silent': False,
}

def log_info(message):
    '''
    '''
    if not g['silent']:
        logging.info(message)



def setup_bash_patterns(args):
    '''
    Change some values of te bash patterns according to arg arguments
    '''
    bash_patterns['update_server_status'] = bash_patterns['update_server_status'].replace('{server}', args.server) # .format does not work since it contains "{"
    bash_patterns['update_server_status'] = bash_patterns['update_server_status'].replace('{insecure}', '-k ' if args.insecure else '')


## Helper functions
def base64_encode(s):
    '''
    Takes a string and converts it to a base64 string
    '''
    return base64.b64encode(s.encode()).decode('ascii')

class Workflow:
    '''
    '''

    WORKFLOW_TYPE = 'workflow'
    INPUT_TYPE = 'input'
    OUTPUT_TYPE = 'output'
    STEP_TYPE = 'step'
    TOOL_TYPE = 'tool'

    def __init__(self, workflow_filename=None, workflow_object=None, askinput='JSON'):
        '''
        workflow_filename: the JSON filename of the workflow
        workflow_object: The representation of the workflow
        askinput: 
            JSON: Ask for input during convertion to BASH
            BASH: Ask for input in BASH
        One of these should not be None
        '''

        if workflow_filename:
            if not os.path.exists(workflow_filename):
                raise OBC_Executor_Exception(f'File {workflow_filename} does not exist')
        else:
            if not workflow_object:
                raise OBC_Executor_Exception('Both workflow_filename and workflow_string are empty')

        self.workflow_filename = workflow_filename
        self.workflow_object = workflow_object
        self.askinput = askinput
        self.parse_workflow_filename()

    def __str__(self,):
        '''
        '''
        return json.dumps(self.workflow, indent=4)

    def tool_bash_script_generator(self,):
        '''
        '''
        tool_installation_order = self.get_tool_installation_order()
        for tool in tool_installation_order:
            yield tool

    def get_tool_dependent_variables(self, tool,):
        '''
        Get the variables for which this tool is dependent
        '''

        def recursion(tool, the_list):
            for tool_slash_id in tool['dependencies']:
                tool_d = self.tool_slash_id_d[tool_slash_id]
                for variable in tool_d['variables']:
                    the_list.append((variable, tool_d))
                recursion(tool_d, the_list)

        the_list = []
        recursion(tool, the_list)
        return the_list

    def parse_workflow_filename(self, ):
        '''
        Parse and perform sanity tests
        '''

        if self.workflow_filename:
            with open(self.workflow_filename) as f:
                self.workflow = json.load(f)
        elif self.workflow_object:
            self.workflow = self.workflow_object
        else:
            raise OBC_Executor_Exception('Both workflow_filename and workflow_string are empty')

        self.input_parameters = self.get_input_parameters()
        self.root_workflow = self.get_root_workflow()
        self.root_step = self.get_root_step()
        self.root_inputs_outputs = self.get_input_output_from_workflow(self.root_workflow)
        self.output_parameters = self.root_inputs_outputs['outputs']
        self.nice_id = self.workflow['nice_id']
        self.current_token = self.workflow['token']


        log_info('Workflow Name: {}   Edit: {}   Report: {}'.format(
            self.root_workflow['name'], self.root_workflow['edit'], self.nice_id,
            ))

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

        # Check that that there are no circular dependencies
        self.check_tool_dependencies_for_circles();

        # Check that all root input are set
        self.input_parameter_values = {}
        self.input_parameters_read_bash_commands = []
        log_info('Checking for input values:')
        for root_input_node in self.root_inputs_outputs['inputs']:
            var_set = False
            for arg_input_name, arg_input_value in self.input_parameters.items():
                if arg_input_value is None:
                    break
                if arg_input_name == root_input_node['id']:
                    log_info('  {}={}'.format(root_input_node['id'], arg_input_value))
                    self.input_parameter_values[root_input_node['id']] = {'value': arg_input_value, 'description': root_input_node['description']}
                    var_set = True
                    break
            if not var_set:
                #message = 'Input parameter: {} has not been set!'.format(root_input_node['id'])
                #raise OBC_Executor_Exception(message)
                user_message = 'Input parameter: {} ({}) has not been set. Enter value: '.format(root_input_node['id'], root_input_node['description'])
                if self.askinput == 'JSON':
                    local_input_parameter = input(user_message)
                    self.input_parameter_values[root_input_node['id']] = {'value': local_input_parameter, 'description': root_input_node['description']}

                bash_command = 'read -p "{}" {}\n'.format(user_message, root_input_node['id'])
                self.input_parameters_read_bash_commands.append(bash_command)

        # Check that all outpus will be eventually set
        self.output_parameter_step_setters = {}
        for root_output_node in self.root_inputs_outputs['outputs']:
            found_output_filling_step = False
            for step_node in self.node_iterator():
                if not self.is_step(step_node):
                    continue

                if root_output_node['id'] in step_node['outputs']:
                    if not self.output_parameter_step_setters.get(root_output_node['id']) in [None, step_node]:
                        message = 'OBC: Output variable: {} is set by more than one steps:\n'.format(root_output_node['id'])
                        message += '   {}\n'.format(self.output_parameter_step_setters[root_output_node['id']]['id'])
                        message += '   {}\n'.format(step_node['id'])
                        raise OBC_Executor_Exception(message)

                    self.output_parameter_step_setters[root_output_node['id']] = step_node
                    found_output_filling_step = True

            if not found_output_filling_step and (not self.askinput in ['BASH']):
                # If askinput = BASH don't raise exception 
                message = 'Output {} ({}) is not set by any step!'.format(root_output_node['id'], root_output_node['description'])
                raise OBC_Executor_Exception(message)

        # Confirm that all main workflows have exactly one main step
        # Confirm that all sub workflows have exactly one sub main step
        for workflow in self.get_all_workflows():
            # Is this the main workflow?
            if self.is_root_workflow(workflow):
                main_counter = sum(step['main'] for step in self.get_steps_from_workflow(workflow))
                main_str = 'MAIN'
            else:
                main_counter = sum(step['sub_main'] for step in self.get_steps_from_workflow(workflow))
                main_str = 'SUB'
            if main_counter == 0:
                message = '{} Workflow {} has 0 main steps'.format(main_str, workflow['id'])
                raise OBC_Executor_Exception(message)
            if main_counter > 1:
                message = '{} Workflow {} has more than one ({}) main steps'.format(main_str, workflow['id'], main_counter)
                raise OBC_Executor_Exception(message)

        # Create a dictionary. Keys are tool slash id. values are tools
        self.tool_slash_id_d = {self.get_tool_slash_id(tool):tool for tool in self.tool_iterator()}

        # Create a dictionary. Keys are tool ids. Values are tuples: (variables from which they depend from, deoendent tool)
        self.tool_dependent_variables = {self.get_tool_dash_id(tool, no_dots=True):self.get_tool_dependent_variables(tool) for tool in self.tool_iterator()} 

        # Create a dictioray. Keys are step ids. Values are tool objects
        self.step_ids = {step['id']:step for step in self.step_iterator()}

    def check_tool_dependencies_for_circles(self,):
        '''
        '''

        # Get all tools
        all_tools = [node for node in self.node_iterator() if self.is_tool(node)]

        # Contruct the tool graph
        graph = {self.get_tool_slash_id(tool): tool['dependencies'] for tool in all_tools}

        for tool_id in graph.keys():
            circles = detect_circles(graph, tool_id, tool_id)
            try:
                circle = next(circles)
            except StopIteration as e:
                pass # This is supposed to happen
            else:
                message = 'Found circular tool dependency!'
                message += '\n' + ' --> '.join(circle)
                raise OBC_Executor_Exception(message)

    def check_step_calls_for_circles(self,):
        '''
        '''

        #Construct the step graph
        graph = {step['id']: step['steps'] for step in self.step_iterator()}

        for step_id in graph.keys():
            circles = detect_circles(graph, step_id, step_id)
            try:
                circle = next(circles)
            except StopIteration as e:
                pass
            else:
                circle_str = ' --> '.join(circle)
                return circle_str

        return ''


    def get_token_set_bash_commands(self, ):
        '''
        '''
        return 'obc_current_token="{}"'.format(self.current_token)

    def show_basic_info(self,):
        '''
        self.root_workflow['name'], self.root_workflow['edit'], self.nice_id,
        '''

        ret = '\n'
        ret += 'echo "Workflow name: {}"\n'.format(self.root_workflow['name'])
        ret += 'echo "Workflow edit: {}"\n'.format(self.root_workflow['edit'])
        ret += f'echo "Workflow report: {self.nice_id}"\n'
        ret += '\n'
        return ret

    def get_input_parameters_read_bash_commands(self, ):
        '''
        Bash commands for reading input/output
        '''

        ret = '\n'
        if self.input_parameters_read_bash_commands:
            ret += 'echo "The following input commands have not been set by any step. Please define input values:"\n'
            for input_parameters_read_bash_command in self.input_parameters_read_bash_commands:
                ret += input_parameters_read_bash_command
            ret += '\n'

        return ret


    def get_tool_bash_commands(self, tool, 
        validation=True, 
        update_server_status=True,
        read_variables_from_command_line=False,
        variables_json_filename=None,
        ):
        '''
        update_server_status: boolean, should we update the server status?
        variables_json_filename: Create a json file that contains the values of the variables (if None it does not create it)
        read_variables_from_command_line: Assume that this is running from a cammand line file.sh script. Read the arguments from command line 
        '''

        log_info('Building installation bash commands for: {}'.format(tool['label']))

        tool_id = Workflow.get_tool_dash_id(tool, no_dots=True)

        # Add Bash commands
        ret =  '### BASH INSTALLATION COMMANDS FOR TOOL: {}\n'.format(tool['label'])
        ret += 'echo "OBC: INSTALLING TOOL: {}"\n'.format(tool['label'])
        if update_server_status:
            ret += Workflow.bash_tool_installation_started(tool) + '\n'
        if read_variables_from_command_line:
            ret += 'for i in "$@"\n'
            ret += 'do\n'
            ret += 'case $i in\n'
            for dependent_variable, dependent_tool in self.tool_dependent_variables[tool_id]:

                variable_id = Workflow.get_tool_bash_variable(dependent_tool, dependent_variable['name'])

                ret += '  --{VARIABLE_ID}=*)\n'.format(VARIABLE_ID=variable_id)
                ret += '  {VARIABLE_ID}="${{i#*=}}"\n'.format(VARIABLE_ID=variable_id)
                ret += '  shift\n'
                ret += '  ;;\n'
            ret += '  *)\n'
            ret += '  ;;\n'
            ret += 'esac\n'
            ret += 'done\n\n'

        ret += tool['installation_commands'] + '\n'
        ret += 'echo "OBC: INSTALLATION OF TOOL: {} . COMPLETED"\n'.format(tool['label'])
        ret += '### END OF INSTALLATION COMMANDS FOR TOOL: {}\n\n'.format(tool['label'])

        if validation:
            # Add Bash validation commands
            ret +=  '### BASH VALIDATION COMMANDS FOR TOOL: {}\n'.format(tool['label'])
            ret += 'echo "OBC: VALIDATING THE INSTALLATION OF THE TOOL: {}"\n'.format(tool['label'])
            #ret += tool['validation_commands'] + '\n'
            validation_script_filename = tool['label'].replace('/', '__') + '__validation.sh'
            ret += "cat > {} << 'ENDOFFILE'\n".format(validation_script_filename)
            ret += tool['validation_commands'] + '\n'
            ret += 'ENDOFFILE\n\n'
            ret += 'chmod +x {}\n'.format(validation_script_filename)
            ret += './{}\n'.format(validation_script_filename)
            ret += 'if [ $? -eq 0 ] ; then\n'
            ret += '   echo "OBC: VALIDATION FOR TOOL: {} SUCCEEDED"\n'.format(tool['label'])
            ret += 'else\n'
            ret += '   echo "OBC: VALIDATION FOR TOOL: {} FAILED"\n'.format(tool['label'])
            ret += 'fi\n\n'
            ret += '### END OF VALIDATION COMMANDS FOR TOOL: {}\n\n'.format(tool['label'])

        if update_server_status:
            ret += Workflow.bash_tool_installation_finished(tool) + '\n'
        ret += '### SETTING TOOL VARIABLES FOR: {}\n'.format(tool['label'])
        for tool_variable in tool['variables']:
            ret += 'export {}="{}" # {} \n'.format(self.get_tool_bash_variable(tool, tool_variable['name']), tool_variable['value'], tool_variable['description'])
            ret += 'echo "OBC: SET {}=\"{}\"   <-- {} "\n'.format(self.get_tool_bash_variable(tool, tool_variable['name']), tool_variable['name'], tool_variable['value'], tool_variable['description']) 
        ret += '### END OF SETTING TOOL VARIABLES FOR: {}\n\n'.format(tool['label'])

        if variables_json_filename:
            ret += '### CREATING JSON FILE WITH TOOL VARIABLES\n'
            ret += "cat > {} << 'ENDOFFILE'\n".format(variables_json_filename)
            ret += Workflow.get_tool_bash_variables_json(tool) + '\n'
            ret += 'ENDOFFILE\n\n'


        return ret


    def get_input_bash_commands(self,):
        '''
        '''
        ret = '### SET ROOT WORKFLOW INPUT PARAMETERS\n'
        for variable, data in self.input_parameter_values.items():
            ret += '{}="{}" #  {}\n'.format(variable, data['value'], data['description'])
        ret += '### END OF SET ROOT WORKFLOW INPUT PARAMETERS'

        return ret

    def get_output_bash_commands(self,):
        ret = '### PRINT OUTPUT PARAMETERS\n'
        ret += 'echo "Output Variables:"\n'
        for output_parameter in self.output_parameters:
            ret += 'echo "{} = ${{{}}}"\n'.format(output_parameter['id'], output_parameter['id'])
        ret += '### END OF PRINTINT OUTPUT PARAMETERS\n'

        return ret

    def get_step_bash_commands(self, ):
        '''
        TODO: CREATE AN ORDERING ACCORDING TO WORKFLOWS!
        '''
        ret = '### SETTING BASH FUNCTIONS FOR STEPS\n\n'
        for a_node in self.node_iterator():
            if not self.is_step(a_node):
                continue

            ret += '# STEP: {}\n'.format(a_node['id'])
            ret += '{} () {{\n'.format(a_node['id'])
            #ret += ':\n' # No op in case a_node['bash'] is empty 
            ret += "OBC_WHOCALLEDME=$(caller 0 | awk '{print $2}') \n"
            ret += "if [ $OBC_WHOCALLEDME != \"main\" ] ; then \n"
            ret +="   OBC_WHOCALLEDME=${OBC_WHOCALLEDME:6}\n" # :6 =  step__step1__callme__1 --> step1__callme__1
            ret += "fi\n"
            ret += 'echo "OBC: CALLING STEP: {}    CALLER: $OBC_WHOCALLEDME"\n'.format(a_node['id']) # 
            ret += 'update_server_status "step started {} $OBC_WHOCALLEDME"\n'.format(a_node['id'])
            ret += a_node['bash'] + '\n'
            ret += 'update_server_status "step finished {}"\n'.format(a_node['id'])
            ret += '}\n'

        ret += '### END OF SETTING BASH FUNCTIONS FOR STEPS\n'

        return ret

    def get_main_step_bash_commands(self,):
        '''
        '''

        ret = '### CALLING MAIN STEP\n'
        ret += '{}\n'.format(self.root_step['id'])
        ret += '### END OF CALLING MAIN STEP\n'

        return ret

    @staticmethod
    def get_tool_slash_id(tool):
        '''
        '''
        return '/'.join([tool['name'], tool['version'], str(tool['edit'])])

    @staticmethod
    def get_tool_dash_id(tool, no_dots=False):
        '''
        '''
        ret =  '__'.join([tool['name'], tool['version'], str(tool['edit'])])

        if no_dots:
            ret = ret.replace('.', '_')

        return ret

    @staticmethod
    def get_tool_bash_variable(tool, variable_name):
        '''
        '''

        return '{}__{}'.format(Workflow.get_tool_dash_id(tool, no_dots=True), variable_name)


    @staticmethod
    def get_tool_bash_variables_json(tool):
        '''
        '''
        
        d = {Workflow.get_tool_bash_variable(tool, tool_variable['name']): tool_variable['value'] for tool_variable in tool['variables']}
        return json.dumps(d, indent=4)


    @staticmethod
    def get_workflow_dash_id(workflow):
        '''
        '''
        return workflow['name'] + '/' + str(workflow['edit'])

    def get_step_calling_order(self,):
        '''
        '''

        return self.get_node_order(
            node_iterator = self.step_iterator,
            id_getter = lambda x : x['id'],
            dependency_getter = lambda x : x['steps']
        )

    def get_tool_installation_order(self,):
        '''
        '''

        return self.get_node_order(
            node_iterator = self.tool_iterator,
            id_getter = self.get_tool_slash_id,
            dependency_getter = lambda x : x['dependencies'],

        )


    def get_node_order(self, node_iterator, id_getter, dependency_getter):
        '''
        node_iterator: iterator through all nodes of a given type
        id_getter: Function. Takes a node. Returns an id of the node
        dependency_getter: Functions. Takes a node. Returns a list of dependencies
        '''

        def has_dependency(node, list_of_nodes):
            '''
            '''

            all_dependencies = [id_getter(n) for n in list_of_nodes]
            return all(n in all_dependencies for n in dependency_getter(node))

        ret = []

        # Get all nodes that have dependencies 
        dependencies_notok = []


        for node in node_iterator():
            if dependency_getter(node):
                dependencies_notok.append(node)
            else:
                ret.append(node)

        steps = 0
        while True:
            # If all dependencies have been resolved, break
            if not dependencies_notok:
                break

            steps += 1
            current_notok = []
            found_on_this_round = []

            for node in dependencies_notok:
                if has_dependency(node, ret):
                    found_on_this_round.append(node)
                else:
                    current_notok.append(node)

            ret.extend(found_on_this_round)
            dependencies_notok = current_notok

        return ret


    def get_tool_installation_order_DEPERECATED(self, ):
        '''
        Get a list of tools in dependency order.
        '''

        def has_dependency(tool, list_of_tools):
            '''
            Checks if the tool has all its dependencies on the list of tools
            '''

            all_dependencies = [self.get_tool_slash_id(t) for t in list_of_tools]
            return all(t in all_dependencies for t in tool['dependencies'])


        ret = []

        # Get all tools
        all_tools = [a_node for a_node in self.node_iterator() if self.is_tool(a_node)]

        # Get all tools that have dependencies 
        dependencies_notok = []

        for tool in all_tools:
            if tool['dependencies']:
                dependencies_notok.append(tool)
            else:
                ret.append(tool)

        steps = 0
        while True:

            # If all dependencies have been resolved, break
            if not dependencies_notok:
                break

            steps += 1

            current_notok = []
            found_on_this_round = []
            for tool in dependencies_notok:
                if has_dependency(tool, ret):
                    found_on_this_round.append(tool)
                else:
                    current_notok.append(tool)

            ret.extend(found_on_this_round)
            dependencies_notok = current_notok
	
        return ret	


    def get_input_parameters(self, ):
        '''
        '''

        return self.workflow.get('arguments', [])

    def node_iterator(self,):
        '''
        '''
        for node in self.workflow['workflow']['elements']['nodes']:
            yield node['data']

    def tool_iterator(self,):
        '''
        '''
        for node in self.node_iterator():
            if self.is_tool(node):
                yield node

    def step_iterator(self,):
        '''
        '''
        for node in self.node_iterator():
            if self.is_step(node):
                yield node

    def is_root_workflow(self, workflow):
        '''
        '''
        return workflow.get('belongto', None) is None

    def get_root_workflow(self,):
        '''
        '''

        ret = None

        for node in self.node_iterator():
            if self.is_root_workflow(node):
                if not ret is None:
                    raise OBC_Executor_Exception('Integrity Error: Found more than one root workflow')

                ret = node

        if ret is None:
            raise OBC_Executor_Exception('Failed to locate root workflow')

        return ret

    def get_all_workflows(self,):
        '''
        '''
        return [node for node in self.node_iterator() if self.is_workflow(node)]

    def node_2_str(self, node):
        '''
        '''
        return json.dumps(node, indent=4)

    def is_workflow(self, node):
        '''
        '''
        return node['type'] == self.WORKFLOW_TYPE

    def is_input_output(self, node):
        '''
        '''
        return node['type'] in [self.INPUT_TYPE, self.OUTPUT_TYPE]

    def is_step(self, node):
        '''
        '''
        return node['type'] == self.STEP_TYPE

    def is_tool(self, node):
        '''
        '''
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

    def get_root_step(self,):
        '''
        '''
        ret = None
        for step in self.get_steps_from_workflow(self.root_workflow):
            if step['main']:
                if not ret is None:
                    message = 'Found more than one main steps in root workflow!'
                    raise OBC_Executor_Exception(message)

                ret = step

        if ret is None:
            message = 'Could not find main step in root workflow'
            raise OBC_Executor_Exception(message)

        return ret

    @staticmethod
    def update_server_status(new_status):
        '''
        * Update the serve with a new status
        * Checks for error messages 
        * sets the new token
        '''
        ret = 'update_server_status "{}"\n'.format(new_status)
        return ret

    @staticmethod
    def bash_workflow_starts(workflow):
        return Workflow.update_server_status('workflow started {}'.format(Workflow.get_workflow_dash_id(workflow)))

    @staticmethod
    def bash_workflow_ends(workflow):
        return Workflow.update_server_status('workflow finished {}'.format(Workflow.get_workflow_dash_id(workflow)))

    @staticmethod
    def bash_tool_installation_started(tool):
        return Workflow.update_server_status('tool started {}'.format(tool['label']))

    @staticmethod
    def bash_tool_installation_finished(tool):
        return Workflow.update_server_status('tool finished {}'.format(tool['label']))

    def break_down_step_generator(self,):
        '''
        '''

        # First, check for circles in step calls
        c = self.check_step_calls_for_circles()
        if c:
            raise OBC_Executor_Exception('Found circle in step calls:\n{}\n. Cannot generate CWL worfklow.'.format(c))

        def get_level(command, steps):
            '''
            What is the level with which a script is calling a step?
            command does not necessarily has to be a bashlex command class node 
            '''

            def recursive(command, current_level):
                if hasattr(command, 'word'):
                    if command.word in steps:
                        return current_level, command.word

                if hasattr(command, 'parts'):
                    for part in command.parts:
                        ret = recursive(part, current_level+1)
                        if ret:
                            return ret

                if hasattr(command, 'command'):
                    ret = recursive(command.command, current_level+1)
                    if ret:
                        return ret

                return False

            return recursive(command, 1)

        def save_variables(bash, save_to, read_from):
            '''
            '''

            ret = ''
            if read_from:
                ret = '. ./{}\n'.format(read_from)

            ret += 'OBC_START=$(eval "declare")\n'
            ret += bash + '\n'
            ret += 'OBC_CURRENT=$(eval "declare")\n'
            ret += 'comm -3 <(echo "$OBC_START" | grep -v "_=") <(echo "$OBC_CURRENT" | grep -v OBC_START | grep -v PIPESTATUS | grep -v "_=") > {}\n'.format(save_to)
            return ret


        def create_json(bash, step, step_breaked_id, is_last):
            '''
            Create a json file with the output variables
            '''

            filename_with_intermediate = '{}__{}.sh'.format(step['id'], step_breaked_id)
            output_filename = '{}__{}.json'.format(step['id'], step_breaked_id)

            output_variables = ''
            if is_last:
                for var in step['outputs']:
                    output_variables += ',\n"{VAR}": "{VAR}"\n'.format(VAR=var)
                

            content = '''
cat > {OUTPUT_FILENAME} << 'ENDOFFILE'
{{
"{FILENAME_WITH_INTERMEDIATE}": "{FILENAME_WITH_INTERMEDIATE}"{OUTPUT_VARIABLES}
}}
ENDOFFILE
'''.format(
    OUTPUT_FILENAME=output_filename,
    FILENAME_WITH_INTERMEDIATE = filename_with_intermediate,
    OUTPUT_VARIABLES = output_variables,
    )

            return bash+content




        step_counter = defaultdict(int) # How many times this steps has been yielded?

        def break_down_step_recursive(step):
            '''
            '''

            bash = step['bash']
            bash_to_parse = '{\n' + bash + '\n}'
            calling_steps = step['steps']

            try:
                p = bashlex.parse(bash_to_parse)
            except bashlex.errors.ParsingError as e:
                raise OBC_Executor_Exception('Could not parse bash script (error 2308). {}'.format(str(e)))

            if not type(p) is list:
                raise OBC_Executor_Exception('Could not parse bash script. Error 2301')

            if not len(p):
                raise OBC_Executor_Exception('Could not parse bash script. Is it empty? Error 2302')

            if not type(p[0]) is bashlex.ast.node:
                raise OBC_Executor_Exception('Could not parse bash script. Error 2303')

            if not hasattr(p[0], 'list'):
                raise OBC_Executor_Exception('Could not parse bash script. Error 2304')

            if not type(p[0].list[0]) is bashlex.ast.node:
                raise OBC_Executor_Exception('Could not parse bash script. Error 2305')

            if not type(p[0].list[1]) is bashlex.ast.node:
                raise OBC_Executor_Exception('Could not parse bash script. Error 2306')

            if not hasattr(p[0].list[1], 'parts'):
                raise OBC_Executor_Exception('Could not parse bash script. Error 2307')

            if not len(p[0].list[1].parts):
                raise OBC_Executor_Exception('Could not parse bash script. Error 2308')

            main_commands = p[0].list[1].parts
            found_call = False
            start = 0
            read_from = None

            for main_command in main_commands:

                level_tuple = get_level(main_command, calling_steps)
                if level_tuple:
                    level, called_step = level_tuple
                    if level>2:
                        raise OBC_Executor_Exception('Step: {} calls step: {} in a secondary scope (if,while,for,function..). This is not supported.'.format(
                            step['id'], called_step))

                if not main_command.kind == 'command':
                    continue

                # This is a command

                if not hasattr(main_command, 'parts'):
                    continue

                # We are looking for a command with a single part (funtion call)
                if not len(main_command.parts) == 1:
                    continue

                # It should be a single word
                if not main_command.parts[0].kind == 'word':
                    continue

                word = main_command.parts[0].word

                #It should be a calling step
                if not word in calling_steps:
                    continue

                #This is a calling step!
                found_call = True
                pos = main_command.parts[0].pos

                part_before_step_call = bash_to_parse[start: pos[0]][2:]
                step_counter[step['id']] += 1
                save_to = '{}__{}.sh'.format(step['id'], step_counter[step['id']])
                yield {
                    'bash': create_json(save_variables(part_before_step_call, read_from, save_to), step, step_counter[step['id']], False),
                    'id': step['id'],
                    'count': step_counter[step['id']],
                    'last': False,
                }
                read_from = save_to
                

                step_to_call_id = bash_to_parse[pos[0]:pos[1]]
                step_to_call = self.step_ids[step_to_call_id]

                for item in break_down_step_recursive(step_to_call):
                    yield item
                start = pos[1]


            # Yield the rest
            part_after_step_call = bash_to_parse[start:][:-2]
            step_counter[step['id']] += 1
            save_to = '{}__{}.sh'.format(step['id'], step_counter[step['id']])
            yield {
                'bash' : create_json(save_variables(part_after_step_call, read_from, save_to), step, step_counter[step['id']], True),
                'id': step['id'],
                'count': step_counter[step['id']],
                'last': True,
            }


#                print (part_before_step_call)
#                print ('==')
#                print (step_to_call)
#                print ('==')
#                print (part_after_step_call)
#                print ('==')
#                print (word, pos)


 
        return break_down_step_recursive(self.root_step)


class BaseExecutor():
    '''
    '''
    def __init__(self, workflow):
        if not isinstance(workflow, Workflow):
            raise OBC_Executor_Exception('workflow Unknown type: {}'.format(type(workflow).__name__))
        self.workflow = workflow



class LocalExecutor(BaseExecutor):
    '''
    Creates a unique BIG script!
    '''

    def build(self, output):
        '''
        output: if string then consider this a file name
                if None then create a in-memory file and return the string 
        '''

        if type(output) is str:
            opener = open
            opener_args = [output, 'w']
            opener_kwargs = {}
        elif output is None:
            opener = io.StringIO
            opener_args = ['w']
            opener_kwargs = {'newline': '\n'}
        else:
            raise OBC_Executor_Exception('Unknown type of output in build: {}'.format(type(output).__name__))

        ret = None

        with opener(*opener_args, **opener_kwargs) as f:

            # Print basic info of executed workflow
            f.write(self.workflow.show_basic_info())

            # Ask for input parameters
            f.write(self.workflow.get_input_parameters_read_bash_commands())

            # Set current token
            f.write(self.workflow.get_token_set_bash_commands())

            #Insert essential functions
            f.write(bash_patterns['parse_json'])
            f.write(bash_patterns['update_server_status'])
            f.write(bash_patterns['base64_decode'])
            f.write(bash_patterns['validate'])

            f.write(Workflow.bash_workflow_starts(self.workflow.root_workflow))

            # INSTALLATION TOOL BASH
            for tool in self.workflow.tool_bash_script_generator():
                f.write(self.workflow.get_tool_bash_commands(tool))

            # INPUT PARAMETERS BASH
            f.write(self.workflow.get_input_bash_commands())

            # STEP FUNCTIONS BASH
            f.write(self.workflow.get_step_bash_commands())

            # CALL MAIN STEP
            f.write(self.workflow.get_main_step_bash_commands())

            # PRINT OUTPUT PARAMETERS
            f.write(self.workflow.get_output_bash_commands())

            f.write(Workflow.bash_workflow_ends(self.workflow.root_workflow))

            # Get srtring content of file
            if output is None:
                f.flush()
                ret = f.getvalue()

        if type(output) is str:
            log_info(f'Created file: {output}')

        return ret

class CWLExecutor(BaseExecutor):
    '''
    Common Workflow Language Executor
    '''

    RUNNER = '#!/usr/bin/env cwl-runner'
    VERSION = 'v1.0'
    TOOL_BASH_FILENAME_P = '{TOOL_ID}.sh'
    STEP_BASH_FILENAME_P = '{STEP_ID}_{COUNTER}.sh'
    TOOL_CWL_P = '{TOOL_ID}.cwl'
    STEP_CWL_P = '{STEP_ID}_{COUNTER}.cwl'
    TOOL_JSON_P = '{TOOL_ID}.json'
    TOOLS_WORKFLOW_FILENAME = 'tools_workflow.cwl'
    COMMANDLINE_CWL_P = '''{HEADER}
baseCommand: [{SHELL}, {BASH_FILENAME}]
class: CommandLineTool

requirements:
   InitialWorkDirRequirement:
      listing:
         - class: File
           location: {BASH_FILENAME}
   InlineJavascriptRequirement: {{}}

inputs: {CWL_INPUT_VARIABLES}
outputs: {CWL_OUTPUT_VARIABLES}
'''

    def header(self,):
        '''
        CWL HEADER
        '''
        return '''
{RUNNER}

cwlVersion: {VERSION}
'''.format(RUNNER=self.RUNNER, VERSION=self.VERSION)

    def cwl_input_variable(self, variable_id):
        '''
        Assume a single variable that is read from command line
        '''

        return '''
   {VARIABLE_ID}:
      type: string
      inputBinding:
         prefix: --{VARIABLE_ID}=
         separate: false
'''.format(VARIABLE_ID=variable_id)

    def cwl_input_variables(self, variable_ids):
        '''
        variable_ids: a list of strings (ids)
        '''
        if not variable_ids:
            return '[]\n\n'

        return ''.join([self.cwl_input_variable(variable_id) for variable_id in variable_ids])


    def tool_cwl_input_variables(self, tool):
        '''
        '''

        tool_id = Workflow.get_tool_dash_id(tool, no_dots=True)

        variable_ids = [Workflow.get_tool_bash_variable(dependent_tool, dependent_variable['name']) 
            for dependent_variable, dependent_tool 
                in self.workflow.tool_dependent_variables[tool_id]]

        return self.cwl_input_variables(variable_ids)


    def tool_cwl_output_variable(self, variable_id, output_json_filename):
        '''
        Set the value of the output from a json file
        '''

        return '''
   {VARIABLE_ID}:
      type: string
      outputBinding:
         glob: {OUTPUT_JSON_FILENAME}
         loadContents: true
         outputEval: $(JSON.parse(self[0].contents).{VARIABLE_ID})

'''.format(VARIABLE_ID=variable_id, OUTPUT_JSON_FILENAME=output_json_filename)

    def cwl_output_variables(self, variables):
        '''
        variables is a list of tuples. (Variable name, name of the json file that they will be read from)
        '''

        if not variables:
            return '[]\n\n'

        ret = ''
        for variable_id, output_json_filename in variables:
            ret += self.tool_cwl_output_variable(variable_id, output_json_filename)

        return ret

    def tool_cwl_output_variables(self, tool):
        '''
        '''

        if not tool['variables']:
            return '[]\n\n'

        tool_id = Workflow.get_tool_dash_id(tool, no_dots=True)
        output_json_filename = self.TOOL_JSON_P.format(TOOL_ID=tool_id)
        ret = ''
        for variable in tool['variables']:
            variable_id = Workflow.get_tool_bash_variable(tool, variable['name'])
            ret += self.tool_cwl_output_variable(variable_id, output_json_filename)

        return ret

    def tool_cwl(self, tool, shell='sh'):
        '''
        Create a CWL file for the installation of this tool
        '''

        tool_id = Workflow.get_tool_dash_id(tool, no_dots=True)

        content = self.COMMANDLINE_CWL_P.format(
        HEADER=self.header(),
        SHELL=shell,
        BASH_FILENAME=self.TOOL_BASH_FILENAME_P.format(TOOL_ID=tool_id),
        CWL_INPUT_VARIABLES=self.tool_cwl_input_variables(tool),
        CWL_OUTPUT_VARIABLES=self.tool_cwl_output_variables(tool),
    )

        output_filename = self.TOOL_CWL_P.format(TOOL_ID=tool_id)
        log_info('Creating CWL for tool: {}'.format(output_filename))
        with open(output_filename, 'w') as f:
            f.write(content)


    def tool_cwl_bash(self, tool):
        '''

        '''
        tool_id = Workflow.get_tool_dash_id(tool, no_dots=True)
        bash_commands = self.workflow.get_tool_bash_commands(
            tool, 
            update_server_status=False,
            variables_json_filename=self.TOOL_JSON_P.format(TOOL_ID=tool_id),
            read_variables_from_command_line=True,
        )
        output_filename = self.TOOL_BASH_FILENAME_P.format(TOOL_ID=tool_id)

        log_info('Creating CWL BASH for tool: {}'.format(output_filename))
        with open(output_filename, 'w') as f:
            f.write(bash_commands)

    def tool_workflow_step_cwl(self, tool):
        '''
        '''

        ret_p = '''
   {TOOL_ID}:
      run: {TOOL_CWL_FILENAME}
      in: {TOOL_STEP_INPUTS}
      out: {TOOL_STEP_OUTPUTS}
'''

        tool_id = Workflow.get_tool_dash_id(tool, no_dots=True)

        # Create tool_step_inputs
        dependent_variable_tools = self.workflow.tool_dependent_variables[tool_id]
        if dependent_variable_tools:
            tool_step_inputs = '\n'
            for dependent_variable, dependent_tool in dependent_variable_tools:
                dependent_tool_id = Workflow.get_tool_dash_id(dependent_tool, no_dots=True)
                dependent_variable_id = Workflow.get_tool_bash_variable(dependent_tool, dependent_variable['name'])
                tool_step_inputs += ' ' * 9 + dependent_variable_id + ': ' + dependent_tool_id + '/' + dependent_variable_id + '\n'

        else:
            tool_step_inputs = '[]'

        # Create tool_step_outputs
        tool_step_outputs = '[' + \
            ', '.join(
                [Workflow.get_tool_bash_variable(tool, variable['name']) 
                    for variable in tool['variables']]
                ) + \
            ']'

        return ret_p.format(
                    TOOL_ID=tool_id,
                    TOOL_CWL_FILENAME=self.TOOL_CWL_P.format(TOOL_ID=tool_id),
                    TOOL_STEP_INPUTS=tool_step_inputs,
                    TOOL_STEP_OUTPUTS=tool_step_outputs,
                )

    def tool_workflow_cwl(self, ):
        '''
        Create a workflow for the installation of tools of this workflow
        '''

        content_p = '''{HEADER}
class: Workflow

inputs: []

outputs: []

steps:
{STEPS}

'''

        steps = '\n'.join([self.tool_workflow_step_cwl(tool) for tool in self.workflow.tool_iterator()]) + '\n'

        content = content_p.format(
            HEADER = self.header(),
            STEPS = steps,
            )

        log_info('Creating CWL workflow for tools: {}'.format(self.TOOLS_WORKFLOW_FILENAME))
        with open(self.TOOLS_WORKFLOW_FILENAME, 'w') as f:
            f.write(content)

    def step_cwl_bash(self, step_breaked):
        '''
        '''
        bash_filename = self.STEP_BASH_FILENAME_P.format(
            STEP_ID=step_breaked['step_id'],
            COUNTER=step_breaked['counter'],
        )

        log_info('CREATING CWL BASH for step: {}'.format(bash_filename))
        with open(bash_filename, 'w') as f:
            f.write(step_breaked['bash'])

    def step_breaked_cwl(self, step_breaked, shell='sh'):
        '''
        Create a CWL for this breaked step
        step_breaked is an object yielded from break_down_step_generator
        '''

        bash_filename = self.STEP_BASH_FILENAME_P.format(
            STEP_ID=step_breaked['id'],
            COUNTER=step_breaked['count'],
        )

        # The json file with the output variables
        filename_output_json = '{}__{}.json'.format(step_breaked['id'], step_breaked['count'])
        filename_output_sh = '{}__{}.sh'.format(step_breaked['id'], step_breaked['count'])
        filename_output_cwl = '{}__{}.cwl'.format(step_breaked['id'], step_breaked['count'])

        log_info('CREATING STEP INTERMEDIATE CWL SH:{}'.format(filename_output_sh))
        with open(filename_output_sh, 'w') as f:
            f.write(step_breaked['bash'])

        input_variables = []
        # The input variables of this breaked step are:
        #  1. The tools used in the step
        #  2. The input values read from the step
        #  3. The intermediate variables from previous parts of the same step

        # 1. Tools used in this step:
        #print (self.workflow.step_ids[step_breaked['id']])

        #print (self.workflow.tool_dependent_variables)

        def convert_tool_id(tool_id):
            if not tool_id.count('__') == 3:
                return tool_id

            return '__'.join(tool_id.split('__')[0:-1]).replace('.', '_')

        input_variables.extend(
            [Workflow.get_tool_bash_variable(dependent_tool, dependent_variable['name']) 
                for tool_id in self.workflow.step_ids[step_breaked['id'].replace('.', '_')]['tools']
                    for dependent_variable, dependent_tool 
                        in self.workflow.tool_dependent_variables[convert_tool_id(tool_id)]]
        )

        # 2. The input values read from the step
        input_variables.extend(self.workflow.step_ids[step_breaked['id']]['inputs'])

        # 3. The intermediate variables from previous parts of the same step
        if step_breaked['count']>1:
            input_variables.append('{}__{}.sh'.format(step_breaked['id'], step_breaked['count']-1))


        #print (input_variables)

        output_variables = []

        # The output variables of this breaked step are
        # 1. The output variables set in this step
        # 2. The intermediate variables of the previous breaked step

        # 1. The output variables that are set from this step
        if step_breaked['last']:
            #This is a last breaked step
            for var in self.workflow.step_ids[step_breaked['id']]['outputs']:
                output_variables.append( (var, filename_output_json) )
        
        # 2. The intermediate variables of the previous breaked step
        output_variables.append((filename_output_sh, filename_output_json))


        content = self.COMMANDLINE_CWL_P.format(
            HEADER = self.header(),
            SHELL=shell,
            BASH_FILENAME=bash_filename,
            CWL_INPUT_VARIABLES=self.cwl_input_variables(input_variables),
            CWL_OUTPUT_VARIABLES=self.cwl_output_variables(output_variables),
        )

        log_info('CREATING STEP CWL: {}'.format(filename_output_cwl))
        with open(filename_output_cwl, 'w') as f:
            f.write(content)

    def step_workflow_cwl(self,):
        '''
        '''

        for step_breaked in self.workflow.break_down_step_generator():
            self.step_breaked_cwl(step_breaked)


    def build(self, output):
        '''
        Test with:
        cwl-runner FILENAME.cwl
        '''

        for tool in self.workflow.tool_bash_script_generator():

            self.tool_cwl_bash(tool)
            self.tool_cwl(tool)

        self.tool_workflow_cwl()
        self.step_workflow_cwl()

            #tool_id = Workflow.get_tool_dash_id(tool)
            

            #print (self.tool_to_cwl(tool_id))

            #break


class DockerExecutor(BaseExecutor):
    '''
    '''
    pass

class AmazonExecutor(BaseExecutor):
    '''
    '''
    pass

def create_bash_script(workflow_object, server):
    '''
    convenient function called by server
    server: the server to report to
    '''

    args = type('A', (), {
        'server': server,
        'insecure': False,
    })

    setup_bash_patterns(args)

    # Setup global variables
    g['silent'] = True

    w = Workflow(workflow_object = workflow_object, askinput='BASH')
    le = LocalExecutor(w)
    return le.build(output=None)


if __name__ == '__main__':
    '''
    Example:
    python executor.py -W workflow.json 
    '''

    runner_options = ['sh', 'cwl']

    parser = argparse.ArgumentParser(description='OpenBio-C workflow execute-or')

    parser.add_argument('-W', '--workflow', dest='workflow_filename', help='JSON filename of the workflow to run', required=True)
    parser.add_argument('-S', '--server', dest='server', help='The Server\'s url. It should contain http or https', default='https://www.openbio.eu/platform')
    parser.add_argument('-F', '--format', dest='format', choices=runner_options, 
        help='Select the output format of the workflow. Options are:\n  sh: Create a shell script (default)\n  cwl: Create a set of Common Workflow Language files\n', 
        default='sh')
    parser.add_argument('-O', '--output', dest='output', help='The output filename. default is script.sh', default='script.sh')
    parser.add_argument('--insecure', dest='insecure', help="Pass insecure option (-k) to curl", default=False, action="store_true")
    parser.add_argument('--silent', dest='silent', help="Do not print logging info", default=False, action="store_true")
    parser.add_argument('--askinput', dest='askinput', 
        help="Where to get input parameters from. Available options are: 'JSON', during convert JSON to BASH, 'BASH' ask for input in bash", 
        default='JSON', choices=['JSON', 'BASH'])

    args = parser.parse_args()

    setup_bash_patterns(args)

    # Setup global variables
    if args.silent:
        g['silent'] = True

    w = Workflow(args.workflow_filename, askinput=args.askinput)
    #print (w.root_inputs_outputs)
    #print (w)
    #w.get_tool_installation_order()
    #list(w.tool_bash_script_generator())

    if args.format == 'sh':
        e = LocalExecutor(w)
        e.build(output = args.output)
    elif args.format == 'cwl':
        e = CWLExecutor(w)
        e.build(output = 'output.cwl')
    else:
        raise OBC_Executor_Exception('Unknown ')


	



