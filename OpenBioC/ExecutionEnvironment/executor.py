
import io
import os
import json
import base64
import logging
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

    local command="curl -s --header \"Content-Type: application/json\" --request POST -d '{\"token\": \"$obc_current_token\", \"status\": \"$1\"}' {server}/report/"

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

def setup_bash_patterns(args):
    '''
    Change some values of te bash patterns according to arg arguments
    '''
    bash_patterns['update_server_status'] = bash_patterns['update_server_status'].replace('{server}', args.server) # .format does not work since it contains "{"



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

    def __init__(self, workflow_filename=None, workflow_object=None):
        '''
        workflow_filename: the JSON filename of the workflow
        workflow_object: The representation of the workflow
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
            logging.info('Building installation bash commands for: {}'.format(tool['label']))
            yield tool


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


        logging.info('Workflow Name: {}   Edit: {}   Report: {}'.format(
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

        # Check that that there are not circular dependencies
        self.check_tool_dependencies_for_circles();

        # Check that all root input are set
        self.input_parameter_values = {}
        logging.info('Checking for input values:')
        for root_input_node in self.root_inputs_outputs['inputs']:
            var_set = False
            for arg_input_name, arg_input_value in self.input_parameters.items():
                if arg_input_value is None:
                    break
                if arg_input_name == root_input_node['id']:
                    logging.info('  {}={}'.format(root_input_node['id'], arg_input_value))
                    self.input_parameter_values[root_input_node['id']] = {'value': arg_input_value, 'description': root_input_node['description']}
                    var_set = True
                    break
            if not var_set:
                #message = 'Input parameter: {} has not been set!'.format(root_input_node['id'])
                #raise OBC_Executor_Exception(message)
                local_input_parameter = input('Input parameter: {} ({}) has not been set. Enter value: '.format(root_input_node['id'], root_input_node['description']))
                self.input_parameter_values[root_input_node['id']] = {'value': local_input_parameter, 'description': root_input_node['description']}

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

            if not found_output_filling_step:
                message = 'Output {} ({}) is not set by any step!'.format(root_output_node['id'], root_output_node['description'])
                raise OBC_Executor_Exception(message)

        # Confirm that all workflows have exactly one main step
        for workflow in self.get_all_workflows():
            main_counter = sum(step['main'] for step in self.get_steps_from_workflow(workflow))
            if main_counter == 0:
                message = 'Workflow {} has 0 main steps'.format(workflow['id'])
                raise OBC_Executor_Exception(message)
            if main_counter > 1:
                message = 'Workflow {} has more than one ({}) main steps'.format(workflow['id'], main_counter)


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

    def get_token_set_bash_commands(self, ):
        '''
        '''
        return 'obc_current_token="{}"'.format(self.current_token)

    def get_tool_bash_commands(self, tool, validation=True):
        '''
        '''

        # Add Bash commands
        ret =  '### BASH INSTALLATION COMMANDS FOR TOOL: {}\n'.format(tool['label'])
        ret += 'echo "OBC: INSTALLING TOOL: {}"\n'.format(tool['label'])
        ret += Workflow.bash_tool_installation_started(tool) + '\n'
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
            ret += tool['validation_commands']
            ret += 'ENDOFFILE\n\n'
            ret += 'chmod +x {}\n'.format(validation_script_filename)
            #ret +=  "mitsos="+base64_encode(tool['validation_commands']) + '\n'
            ret += './{}\n'.format(validation_script_filename)
            ret += 'if [ $? -eq 0 ] ; then\n'
            ret += '   echo "OBC: VALIDATION FOR TOOL: {} SUCCEEDED"\n'.format(tool['label'])
            ret += 'else\n'
            ret += '   echo "OBC: VALIDATION FOR TOOL: {} FAILED"\n'.format(tool['label'])
            ret += 'fi\n\n'
            ret += '### END OF VALIDATION COMMANDS FOR TOOL: {}\n\n'.format(tool['label'])

        ret += Workflow.bash_tool_installation_finished(tool) + '\n'
        ret += '### SETTING TOOL VARIABLES FOR: {}\n'.format(tool['label'])
        for tool_variable in tool['variables']:
            ret += 'export {}__{}="{}" # {} \n'.format(self.get_tool_dash_id(tool, no_dots=True), tool_variable['name'], tool_variable['value'], tool_variable['description'])
        ret += '### END OF SETTING TOOL VARIABLES FOR: {}\n\n'.format(tool['label'])


        return ret


    def get_input_bash_commands(self,):
        '''
        '''
        ret = '### SET ROOT WORKFLOW INPUT PARAMETERS\n'
        for variable, data in self.input_parameter_values.items():
            ret += 'input__{}="{}" #  {}\n'.format(variable, data['value'], data['description'])
        ret += '### END OF SET ROOT WORKFLOW INPUT PARAMETERS'

        return ret

    def get_output_bash_commands(self,):
        ret = '### PRINT OUTPUT PARAMETERS\n'
        ret += 'echo "Output Variables:"\n'
        for output_parameter in self.output_parameters:
            ret += 'echo "{} = ${{output__{}}}"\n'.format(output_parameter['id'], output_parameter['id'])
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
            ret += 'step__{} () {{\n'.format(a_node['id'])
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
        ret += 'step__{}\n'.format(self.root_step['id'])
        ret += '### END OF CALLING MAIN STEP\n'

        return ret

    def get_tool_slash_id(self, tool):
        '''
        '''
        return '/'.join([tool['name'], tool['version'], str(tool['edit'])])

    def get_tool_dash_id(self, tool, no_dots=False):
        '''
        '''
        ret =  '__'.join([tool['name'], tool['version'], str(tool['edit'])])

        if no_dots:
            ret = ret.replace('.', '_')

        return ret

    @staticmethod
    def get_workflow_dash_id(workflow):
        '''
        '''
        return workflow['name'] + '/' + str(workflow['edit'])

    def get_tool_installation_order(self, ):
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
            logging.info(f'Created file: {output}')

        return ret



class DockerExecutor(BaseExecutor):
    '''
    '''
    pass

class AmazonExecutor(BaseExecutor):
    '''
    '''
    pass

def create_bash_script(workflow_object):
    '''
    convenient function called by server
    '''

    args = type('A', (), {'server':'https://www.openbio.eu/platform'})

    setup_bash_patterns(args)
    w = Workflow(workflow_object = workflow_object)
    le = LocalExecutor(w)
    return le.build(output=None)


if __name__ == '__main__':
    '''
    Example:
    python executor.py -W workflow.json 
    '''
    parser = argparse.ArgumentParser(description='OpenBio-C worfklow execute-or')

    parser.add_argument('-W', '--workflow', dest='workflow_filename', help='JSON filename of the workflow to run', required=True)
    parser.add_argument('-S', '--server', dest='server', help='The Server\'s url. It should contain http or https', default='https://www.openbio.eu/platform')

    args = parser.parse_args()
    setup_bash_patterns(args)

    w = Workflow(args.workflow_filename)
    #print (w.root_inputs_outputs)
    #print (w)
    #w.get_tool_installation_order()
    #list(w.tool_bash_script_generator())

    le = LocalExecutor(w)
    le.build(output = 'script.sh')


	



