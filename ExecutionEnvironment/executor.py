
import io
import os
import re
import csv
import copy
import json
import yaml
import base64
import random
import string
import logging
import bashlex
import tarfile
import zipfile
from . import cargo
import networkx as nx

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except (ImportError, AttributeError):
    compression = zipfile.ZIP_STORED

import argparse

from collections import defaultdict
from pprint import pprint
from itertools import product

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
''',
'init_report': r'''

if [ -n "${OBC_WORK_PATH}" ] ; then
    export OBC_REPORT_PATH=${OBC_WORK_PATH}/${OBC_NICE_ID}.html
    export OBC_REPORT_DIR=${OBC_WORK_PATH}/${OBC_NICE_ID}
    mkdir -p ${OBC_REPORT_DIR}
    echo "OBC: Report filename: ${OBC_REPORT_PATH}"

cat > ${OBC_REPORT_PATH} << OBCENDOFFILE
<!DOCTYPE html>
<html lang="en">
   <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
   </head>
   <body>
   <p>
   OpenBio Server: <a href="${OBC_SERVER}">${OBC_SERVER}</a> <br>
   Workflow: <a href="${OBC_SERVER}/w/${OBC_WORKFLOW_NAME}/${OBC_WORKFLOW_EDIT}">${OBC_WORKFLOW_NAME}/${OBC_WORKFLOW_EDIT}</a> <br>

   <p>
   <h3>Intermediate Variables:</h3>
   <ul>
      <!-- {{INTERMEDIATE_VARIABLE}} -->
   </ul>

   <p>
   <h3>Output Variables:</h3>
   <ul>
      <!-- {{OUTPUT_VARIABLE}} -->
   </ul>

   </body>
</html>
OBCENDOFFILE
fi

''',
'function_REPORT': r'''

export OBC_REPORT_PATH=${OBC_WORK_PATH}/${OBC_NICE_ID}.html
export OBC_REPORT_DIR=${OBC_WORK_PATH}/${OBC_NICE_ID}

function REPORT() {
    if [ -n "${OBC_WORK_PATH}" ] ; then
        local VAR=$1
        local TIMENOW=$(date)
        local WHOCALLEDME=$(caller 0 | awk '{print $2}')

        if [ -z $3 ] ; then
            local TAG=INTERMEDIATE_VARIABLE
        else
            local TAG=$3
        fi

        if [ ${TAG} == "INTERMEDIATE_VARIABLE" ] ; then
            local EXTRA="${TIMENOW}. Called from: ${WHOCALLEDME}"
        else
            local EXTRA=""
        fi

        local FILEKIND=$(file "${2}")
        # echo "OBC: FILE RESULT ${FILEKIND}"
        if [[ $FILEKIND == *"PNG image data"* ]]; then
           local NEWFILENAME=${OBC_REPORT_DIR}/$(basename ${2})
           local LOCALFILENAME=${OBC_NICE_ID}/$(basename ${2})
           cp ${2} ${NEWFILENAME}
           local HTML="<li>${EXTRA} ${VAR}: <br><img src=\"${LOCALFILENAME}\"></li>\\\\n      <!-- {{${TAG}}} -->\\\\n"
        elif [[ $FILEKIND == *"PDF document"* ]]; then
           local NEWFILENAME=${OBC_REPORT_DIR}/$(basename ${2})
           local LOCALFILENAME=${OBC_NICE_ID}/$(basename ${2})
           cp ${2} ${NEWFILENAME}
           local HTML="<li>${EXTRA} ${VAR}: <br><a href=\"${LOCALFILENAME}\">${LOCALFILENAME}</a></li>\\\\n      <!-- {{${TAG}}} -->\\\\n"
        else
           local VALUE=$(echo "${2}" | sed 's/&/\\\&amp;/g; s/</\\\&lt;/g; s/>/\\\&gt;/g; s/"/\\\&quot;/g; s/'"'"'/\\\&#39;/g')
           local HTML="<li>${EXTRA} ${VAR}=${VALUE}</li>\\\\n      <!-- {{${TAG}}} -->\\\\n"
        fi

        sed -i -e "s|<\!-- {{${TAG}}} -->|${HTML}|" ${OBC_REPORT_PATH}
        sed 's/\\n/\
/g' ${OBC_REPORT_PATH} > ${OBC_REPORT_PATH}.tmp
        mv ${OBC_REPORT_PATH}.tmp ${OBC_REPORT_PATH}
    fi
}

''',
'final_report': r'''

OBC_REPORT_TGZ=${OBC_WORK_PATH}/${OBC_NICE_ID}.tgz

#echo "RUNNING: "
#echo "tar zcf ${OBC_REPORT_TGZ} -C ${OBC_WORK_PATH} ${OBC_NICE_ID}.html ${OBC_NICE_ID}/"

tar zcf ${OBC_REPORT_TGZ} -C ${OBC_WORK_PATH} ${OBC_NICE_ID}.html ${OBC_NICE_ID}/

''',
'function_PARALLEL': r'''
function PARALLEL() {
    local line_counter=0
    local PIDS=() #

    if [[ $2 == *$'\n'* ]] ; then
      while IFS= read -r line; do

          if [[ -z "${line// }" ]] ; then
              continue # Ignore empty lines
          fi
          let "line_counter=line_counter+1"

          if [ $line_counter -eq 1 ] ; then
              IFS=',' read -ra header <<< "$line"
              local header_length=${#header[@]}
              let "header_length_0=header_length-1"
              continue
          fi

          IFS=',' read -ra line_splitted <<< "$line"
          local line_length=${#line_splitted[@]}

          if [ $header_length -ne $line_length ] ; then
              OBC_ERROR="Line:${line_counter} ${line} contains ${line_length} fields whereas the header has ${header_length} fields."
              return
          fi

          # Set parameters
          for i in $(seq 0 ${header_length_0})
          do
              declare "${header[${i}]}=${line_splitted[${i}]}"
          done

          #echo "Calling step: $1"
          eval ${1} &
          P=$!
          PIDS=("${PIDS[@]}" ${P})

      done <<< "$2"
    else
      for var in "$@" ; do
        #echo ${var}
        eval ${var} &
        P=$!
        IDS=("${PIDS[@]}" ${P})
      done
    fi

    wait "${PIDS[@]}"

    OBC_ERROR=""
}
''',
}

r'''
A="
PARAM_1,PARAM_2
1,2
3,4
5,6
7,8
9,10
"

PARALLEL step_example "$A"
# a = re.findall(r'[\w]+=\"[\w\s,\.]+\"[\s]+PARALLEL[\s]+[\w]+[\s]+\"\$[\w]+\"', text)

PARALLEL step_example_1 step_example_2
'''

bash_patterns['get_json_value'] = '{variable}=$(obc_parse_json "${json_variable}" "{json_key}")'

# Global parameters
g = {
    'silent': False,
    'CLIENT_OBC_DATA_PATH': '/usr/local/airflow/REPORTS/DATA',
    'CLIENT_OBC_TOOL_PATH': '/usr/local/airflow/REPORTS/TOOL',
    'CLIENT_OBC_WORK_PATH': '/usr/local/airflow/REPORTS/WORK',
    'possible_letters_nice_id': tuple(string.ascii_lowercase + string.digits),
}

def log_info(message):
    '''
    '''
    if not g['silent']:
        logging.info(message)



def setup_bash_patterns(args):
    '''
    Change some values of the bash patterns according to arg arguments
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

    # Variables that are assumed to be set from the environment
    DEFAULT_INPUT_VARIABLES = [
        'OBC_TOOL_PATH',
        'OBC_DATA_PATH',
        'OBC_WORK_PATH',
    ]


    def __init__(self,
        workflow_filename=None,
        workflow_object=None,
        workflow_string=None,
        askinput='JSON',
        obc_server=None,
        workflow_id=None,
    ):
        '''
        workflow_filename: the JSON filename of the workflow
        workflow_object: The representation of the workflow
        workflow_string: A string representation of the JSON workflow object (used in workflow upload)
        askinput:
            JSON: Ask for input during convertion to BASH
            BASH: Ask for input in BASH
        One of these should not be None

        obc_server the server for which we are generating the script (if any)
        workflow_id: The nice_id of the workflow
        '''

        # One of workflow_filename, workflow_object, workflow_string can be declared
        declared = [x[0] for x in (
                ('workflow_filename', workflow_filename),
                ('workflow_object', workflow_object),
                ('workflow_string', workflow_string),
            )
                if x[1]
        ]
        if len(declared) == 0:
            raise OBC_Executor_Exception('None of workflow_filename, workflow_object, workflow_string have been declared')

        if len(declared) > 1:
            raise OBC_Executor_Exception(
                f'Only one of workflow_filename, workflow_object, workflow_string can be declared. You declared: '
                ', '.join(declared)
            )

        self.workflow_filename = workflow_filename
        self.workflow_object = workflow_object
        self.workflow_string = workflow_string

        self.askinput = askinput
        self.obc_server = obc_server
        self.workflow_id = workflow_id
        self.parse_workflow_filename()

    def __str__(self,):
        '''
        '''
        return json.dumps(self.workflow, indent=4)

    @staticmethod
    def create_nice_id(length=8):
        '''
        Create a nice id
        '''

        return ''.join(random.sample(g['possible_letters_nice_id'], length))

    def tool_bash_script_generator(self,):
        '''
        '''
        tool_installation_order = self.get_tool_installation_order()
        for tool in tool_installation_order:
            yield tool

    def get_tool_dependencies(self, tool):
        '''
        Returns the tools that this tool depends from
        '''

        def rec(tool):

            ret = []

            for tool_slash_id in tool['dependencies']:
                tool_d = self.tool_slash_id_d[tool_slash_id]

                ret.append(Workflow.get_tool_slash_id(tool_d))
                ret.extend(rec(tool_d))

            return ret

        ret = set(rec(tool))
        return [self.tool_slash_id_d[x] for x in ret]

    def get_tool_dependent_variables(self, tool, include_this_tool=False):
        '''
        Get the variables for which this tool is dependent
        include_this_tool: If True, include also the variables of this tool
        '''

        def recursion(tool, the_list):
            for tool_slash_id in tool['dependencies']:
                tool_d = self.tool_slash_id_d[tool_slash_id]
                for variable in tool_d['variables']:
                    the_list.append((variable, tool_d))
                recursion(tool_d, the_list)

        the_list = []
        recursion(tool, the_list)
        if include_this_tool:
            for variable in tool['variables']:
                the_list.append((variable, tool))

        return the_list

    def parse_workflow_filename(self, ):
        '''
        Parse and perform sanity tests
        '''

        if self.workflow_filename:
            try:
                with open(self.workflow_filename) as f:
                    self.workflow = json.load(f)
            except FileNotFoundError:
                raise OBC_Executor_Exception(f'File {self.workflow_filename} does not exist')
            except json.decoder.JSONDecodeError as e:
                raise OBC_Executor_Exception(f'File {self.workflow_filename} does not seem to be in JSON format. Error: {str(e)}')

        elif self.workflow_string:
            try:
                self.workflow = json.loads(self.workflow_string)
            except json.decoder.JSONDecodeError as e:
                raise OBC_Executor_Exception(f'Could not parse workflow_string as JSON. Error: {str(e)}')

        elif self.workflow_object:
            self.workflow = self.workflow_object

        self.input_parameters = self.get_input_parameters()
        self.root_workflow = self.get_root_workflow()
        self.root_workflow_id = self.root_workflow['id']
        self.root_step = self.get_root_step()
        self.root_inputs_outputs = self.get_input_output_from_workflow(self.root_workflow)
        self.output_parameters = self.root_inputs_outputs['outputs']
        self.nice_id = self.workflow['nice_id'] # The nice ID from the server
        self.nice_id_local = Workflow.create_nice_id() # A local nice ID

        if self.nice_id: # The id from the JSON
            self.nice_id_global = self.nice_id
        elif self.workflow_id: # The id from the executor
            self.nice_id_global = self.workflow_id
        else:
            self.nice_id_global = self.nice_id_local # The id created  in this class

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
        self.input_unset_variables = [] # IDs of variables that have not be set by any step
        log_info('Checking for input values.')
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
                self.input_unset_variables.append(root_input_node);
                user_message = Workflow.create_input_parameter_message(root_input_node['id'], root_input_node['description'])
                if self.askinput == 'JSON':
                    local_input_parameter = input(user_message)
                    self.input_parameter_values[root_input_node['id']] = {'value': local_input_parameter, 'description': root_input_node['description']}

                elif self.askinput == 'BASH':
                    pass # Do nothing

                elif self.askinput == 'NO':
                    log_info('Warning: Input Parameter {} ({}) has not been set by any step.'.format(root_input_node['id'], root_input_node['description']))
                    # Set None values
                    self.input_parameter_values[root_input_node['id']] = {'value': None, 'description': root_input_node['description']}

        # Check that all output_parameterss will be eventually set
        for root_output_node in self.root_inputs_outputs['outputs']:
            found_output_filling_step = False
            for step_node in self.node_iterator():
                if not self.is_step(step_node):
                    continue

                if root_output_node['id'] in step_node['outputs']:
                    found_output_filling_step = True
                    continue

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

        # Create a dictionary. Keys are tool slash ids. Values are lists of the slash ids of their dependencies
        self.tool_run_afters = {self.get_tool_dash_id(t, no_dots=True): [self.get_tool_dash_id(self.tool_slash_id_d[x], no_dots=True) for x in t['dependencies']] for t in self.tool_iterator()}

        # Create a dictionary. Keys are tool ids. Values are tuples: (variables from which they depend from, dependent tool)
        # This does not contain the variables of the tool that is the key
        self.tool_dependent_variables = {self.get_tool_dash_id(tool, no_dots=True):self.get_tool_dependent_variables(tool) for tool in self.tool_iterator()}

        # Create a dictionary. Keys are tool ids. Values are tuples: (variables from which they depend from, dependent tool)
        # It also contains the variables of the tool that is the key
        self.tool_variables = {self.get_tool_dash_id(tool, no_dots=True):self.get_tool_dependent_variables(tool, include_this_tool=True) for tool in self.tool_iterator()}

        # Create a dictionary. Keys are tool variable ids . Values are the tools in which they belong.
        self.tool_variables_ids = {self.get_tool_bash_variable(tool, tool_variable['name']):tool for tool in self.tool_iterator() for tool_variable in tool['variables']}

        # Create a dictionary. Keys are step ids. Values are tool objects
        self.step_ids = {step['id']:step for step in self.step_iterator()}

        # Create a dictionary. Keys are input ids. Values are input objects
        self.input_ids = {inp['id']:inp for inp in self.inputs_iterator()}

        # Create a dictionary. Keys a output ids. Values are output objects
        self.output_ids = {outp['id']:outp for outp in self.outputs_iterator()}


        self.set_step_reads_sets()


    def set_step_reads_sets(self,):
        '''
        The 'inputs' and 'outputs' fields for every step does NOT contain which variables are set and read respectively.
        It contains which variables are **referred**
        Here we make an assumption:
            If a step refers to an input variable and they belong to the same workflow, then the step READS the variable
            If a step refers to an output variable and they belong to the same workflow, then the step SETS the variable
        '''

        # keys are input ids. Values are the steps who set these values
        self.input_setters = defaultdict(list)

        # Keys are output ids. Values are the steps who set htese values
        self.output_setters = defaultdict(list)

        for step in self.step_iterator():
            step['inputs_reads'] = []
            step['inputs_sets'] = []
            step['outputs_sets'] = []
            step['outputs_reads'] = []

            for step_input in step['inputs']:
                input_node = self.input_ids[step_input]

                if input_node['belongto'] == step['belongto']:
                    #print ('Step: {} Reads: {}'.format(step['id'], step_input))
                    step['inputs_reads'].append(step_input)
                else:
                    step['inputs_sets'].append(step_input)
                    self.input_setters[step_input].append(step['id'])

            for step_output in step['outputs']:
                output_node = self.output_ids[step_output]

                if output_node['belongto'] == step['belongto']:
                    #print ('Step: {} Sets: {}'.format(step['id'], step_output))
                    step['outputs_sets'].append(step_output)
                    self.output_setters[step_output].append(step['id'])
                else:
                    step['outputs_reads'].append(step_output)



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
        ret += 'OBC_WORKFLOW_NAME="{}"\n'.format(self.root_workflow['name'])
        ret += 'OBC_WORKFLOW_EDIT={}\n'.format(self.root_workflow['edit'])
        ret += 'OBC_NICE_ID="{}"\n'.format(self.nice_id_global)
        ret += 'OBC_SERVER="{}"\n'.format(self.obc_server)
        ret += 'echo "OBC: Workflow name: ${OBC_WORKFLOW_NAME}"\n'
        ret += 'echo "OBC: Workflow edit: ${OBC_WORKFLOW_EDIT}"\n'
        ret += f'echo "OBC: Workflow report: {self.nice_id}"\n'
        ret += f'echo "OBC: Server URL: {self.obc_server}"\n'
        ret += '\n'
        return ret

    def get_input_parameters_read_bash_commands(self, ):
        '''
        Bash commands for reading input/output
        '''

        ret = '\n'
        if self.input_unset_variables:

            # Read unset variables from the command line
            # https://github.com/kantale/OpenBioC/issues/154
            ret += Workflow.read_arguments_from_commandline([x['id'] for x in self.input_unset_variables])

            # Check if the variable has been read from command line. If not halt execution and prompt for a value
            for unset_variable in self.input_unset_variables:
                ret += 'if [ -z ${{{}+x}} ]; then\n'.format(unset_variable['id']) # https://stackoverflow.com/questions/3601515/how-to-check-if-a-variable-is-set-in-bash
                ret += '   echo "{}"\n'.format(Workflow.create_input_parameter_message(unset_variable['id'], unset_variable['description']))
                ret += '   read -p "{}=" {}\n'.format(unset_variable['id'], unset_variable['id'])
                ret += 'fi\n'

        return ret

    @staticmethod
    def create_input_parameter_message(variable_id, variable_description):
        '''
        Message to display when input variable has not been set.
        '''
        return 'OBC: Input parameter: {} ({}) has not been set by any step. Enter value: '.format(variable_id, variable_description)

    @staticmethod
    def read_arguments_from_commandline(arguments):
        '''
        Help from: https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
        '''

        ret = ''
        ret += 'for i in "$@"\n'
        ret += 'do\n'
        ret += 'case $i in\n'
        for variable_id in arguments:
            ret += '  --{VARIABLE_ID}=*)\n'.format(VARIABLE_ID=variable_id)
            ret += '  {VARIABLE_ID}="${{i#*=}}"\n'.format(VARIABLE_ID=variable_id)
            ret += '  shift\n'
            ret += '  ;;\n'
        ret += '  *)\n'
        ret += '  ;;\n'
        ret += 'esac\n'
        ret += 'done\n\n'

        return ret


    def get_tool_bash_commands(self, tool,
        validation=True,
        update_server_status=True,
        read_variables_from_command_line=False,
        variables_json_filename=None,
        variables_sh_filename_read=None,
        variables_sh_filename_write=None,
        ):
        '''
        update_server_status: boolean, should we update the server status?
        variables_json_filename: Create a json file that contains the values of the variables (if None it does not create it)
        read_variables_from_command_line: Assume that this is running from a cammand line file.sh script. Read the arguments from command line
        variables_sh_filename_read: If it is set (list), then read all variables from all files in the list
        variables_sh_filename_write: If it is set (string), then create a bash filename with all variables
        '''

        log_info('Building installation bash commands for: {}'.format(tool['label']))

        tool_id = Workflow.get_tool_dash_id(tool, no_dots=True)

        # Add Bash commands
        ret =  '### BASH INSTALLATION COMMANDS FOR TOOL: {}\n'.format(tool['label'])
        ret += 'echo "OBC: INSTALLING TOOL: {}"\n'.format(tool['label'])
        if update_server_status:
            ret += Workflow.bash_tool_installation_started(tool) + '\n'
        if read_variables_from_command_line:
            arguments = [Workflow.get_tool_bash_variable(dependent_tool, dependent_variable['name'])
                            for dependent_variable, dependent_tool in self.tool_dependent_variables[tool_id]]
            ret += Workflow.read_arguments_from_commandline(arguments)

        if variables_sh_filename_read:
            for filename in variables_sh_filename_read:
                ret += '### READING VARIABLES FROM {}\n'.format(filename)
                ret += '. {}\n\n'.format(filename)

        # We are adding the installation commands in parenthesis.
        # By doing so, we are isolating the raw installation commands with the rest pre- and post- commands
        ret += '(\n:\n' + tool['installation_commands'] + '\n)\n' # Add A bash no-op command (:) to avoid empty installation instructions
        ret += 'echo "OBC: INSTALLATION OF TOOL: {} . COMPLETED"\n'.format(tool['label'])
        ret += '### END OF INSTALLATION COMMANDS FOR TOOL: {}\n\n'.format(tool['label'])

        if validation:
            # Add Bash validation commands
            ret +=  '### BASH VALIDATION COMMANDS FOR TOOL: {}\n'.format(tool['label'])
            ret += 'echo "OBC: VALIDATING THE INSTALLATION OF THE TOOL: {}"\n'.format(tool['label'])
            #ret += tool['validation_commands'] + '\n'
            #validation_script_filename = tool['label'].replace('/', '__') + '__validation.sh'
            #ret += "cat > {} << ENDOFFILE\n".format(validation_script_filename) # Add 'ENDOFFILE' in single quotes to have raw input
            ret += '(\n:\n' + tool['validation_commands'] + '\n)\n' # Run validation commands in a dedicated environment  () . Add A bash no-op command (:) to avoid empty installation instructions
            #ret += 'ENDOFFILE\n\n'
            #ret += 'chmod +x {}\n'.format(validation_script_filename)
            #ret += './{}\n'.format(validation_script_filename)
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
            tool_bash_variable=self.get_tool_bash_variable(tool, tool_variable['name'])
            ret += 'export {}="{}" # {} \n'.format(tool_bash_variable, tool_variable['value'], tool_variable['description'])
            ret += 'echo "OBC: SET {}=\\"${}\\"   <-- {} "\n'.format(tool_bash_variable, tool_bash_variable, tool_variable['description'])
        ret += '### END OF SETTING TOOL VARIABLES FOR: {}\n\n'.format(tool['label'])

        if variables_json_filename:
            ret += '### CREATING JSON FILE WITH TOOL VARIABLES\n'
            ret += "cat > {} << ENDOFFILE\n".format(variables_json_filename) # Add 'ENDOFFILE' for raw input
            ret += Workflow.get_tool_bash_variables_json(tool) + '\n'
            ret += 'ENDOFFILE\n\n'

        if variables_sh_filename_write:
            ret += '### CREATING BASH WITH TOOL VARIABLES\n'
            ret += "cat > {} << ENDOFFILE\n".format(variables_sh_filename_write)
            for tool_variable in tool['variables']:
                tool_bash_variable=self.get_tool_bash_variable(tool, tool_variable['name'])
                ret +='{VAR}="{VALUE}"\n'.format(VAR=tool_bash_variable, VALUE=tool_variable['value'])
            ret += 'ENDOFFILE\n'


        return ret

    @staticmethod
    def get_edge_id(source_id, target_id):
        return f'{source_id}..{target_id}'

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
        ret += 'echo "OBC: Output Variables:"\n'
        for output_parameter in self.output_parameters:
            ret += 'echo "OBC: {} = ${{{}}}"\n'.format(output_parameter['id'], output_parameter['id'])
            ret += 'REPORT {} ${{{}}} OUTPUT_VARIABLE \n'.format(output_parameter['id'], output_parameter['id'])
        ret += '### END OF PRINTING OUTPUT PARAMETERS\n'

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
            ret += 'if [ ${OBC_WHOCALLEDME} == "PARALLEL" ] ; then \n '
            ret += "   OBC_WHOCALLEDME=$(caller 1 | awk '{print $2}') \n"
            ret += "fi\n"
#            ret += "if [ ${OBC_WHOCALLEDME} != \"main\" ] ; then \n"
#            ret += "   OBC_WHOCALLEDME=${OBC_WHOCALLEDME:6}\n" # :6 =  step__step1__callme__1 --> step1__callme__1
#            ret += "fi\n"
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
    def get_tool_cytoscape_id(tool):
        '''
        '''
        return f'{Workflow.get_tool_dash_id(tool, no_dots=True)}__2'

    @staticmethod
    def create_tool_from_cytoscape_id(cytoscape_tool_id):
        '''
        '''
        s = cytoscape_tool_id.split('__')
        return {
            'name': s[0],
            'version': s[1],
            'edit': int(s[2]),
        }

    @staticmethod
    def get_tool_vars_filename(tool):
        '''
        '''
        return Workflow.get_tool_vars_filename_tool_id(Workflow.get_tool_dash_id(tool, no_dots=True))

    @staticmethod
    def get_tool_vars_filename_tool_id(tool_id):
        '''
        '''

        return '{TOOL_ID}_VARS.sh'.format(TOOL_ID=tool_id)


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
    def tool_label_to_object(tool_label):
        '''
        The inverse of get_tool_slash_id
        '''
        name, version, edit = tool_label.split('/')
        return {
            'name': name,
            'version': version,
            'edit': int(edit),
        }

    @staticmethod
    def tool_dash_id_to_object(tool_dash_id):
        name, version, edit = tool_dash_id.split('__')
        return {
            'name': name,
            'version': version,
            'edit': int(edit),
        }



    @staticmethod
    def get_workflow_slash_id(workflow):
        '''
        '''
        return workflow['name'] + '/' + str(workflow['edit'])

    @staticmethod
    def get_workflow_dash_id(workflow):
        '''
        '''
        return workflow['name'] + '__' + str(workflow['edit'])

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

    def get_workflow_workflow_dependency(self, workflow):
        '''
        Return a list of the workflows that are directly (not recursively) included in this workflow
        Or else returns a list of the workflows that are directly part of this workflow
        '''

        ret = []
        for n in self.node_iterator():
            if not self.is_workflow(n):
                continue

            if n['belongto'] is None:
                continue

            if Workflow.get_workflow_dash_id(n['belongto']) == workflow['id']:
                ret.append(n)

        return ret


    def get_workflow_order(self,):
        '''
        '''

        return self.get_node_order(
            node_iterator = self.workflow_iterator,
            id_getter = lambda x: x['id'],
            dependency_getter = lambda x : list(map(Workflow.get_workflow_dash_id, self.get_workflow_workflow_dependency(x))),
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

    def node_iterator_with_style(self, create_copy=False):
        for node in self.workflow['workflow']['elements']['nodes']:
            if create_copy:
                yield copy.deepcopy(node)
            else:
                yield node


    def edge_iterator_with_style(self, create_copy=False):
        '''
        '''
        for edge in self.workflow['workflow']['elements']['edges']:
            if create_copy:
                yield copy.deepcopy(edge)
            else:
                yield edge

    def tool_iterator(self,):
        '''
        '''
        for node in self.node_iterator():
            if self.is_tool(node):
                yield node

    def workflow_iterator(self,):
        '''
        '''
        for node in self.node_iterator():
            if self.is_workflow(node):
                yield node

    def step_iterator(self,):
        '''
        '''
        for node in self.node_iterator():
            if self.is_step(node):
                yield node

    def inputs_iterator(self,):
        '''
        '''
        for node in self.node_iterator():
            if self.is_input(node):
                yield node

    def outputs_iterator(self,):
        '''
        '''
        for node in self.node_iterator():
            if self.is_output(node):
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

    @staticmethod
    def get_root_workflow_cytoscape(workflow_cytoscape):
        '''
        '''
        for node in workflow_cytoscape['elements']['nodes']:
            if node['data']['belongto'] is None and node['data']['type'] == Workflow.WORKFLOW_TYPE:
                return node

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

    def is_input(self, node):
        '''
        '''
        return node['type'] == self.INPUT_TYPE

    def is_output(self, node):
        '''
        '''
        return node['type'] == self.OUTPUT_TYPE

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
        return Workflow.update_server_status('workflow started {}'.format(Workflow.get_workflow_slash_id(workflow)))

    @staticmethod
    def bash_workflow_ends(workflow):
        return Workflow.update_server_status('workflow finished {}'.format(Workflow.get_workflow_slash_id(workflow)))

    @staticmethod
    def bash_tool_installation_started(tool):
        return Workflow.update_server_status('tool started {}'.format(tool['label']))

    @staticmethod
    def bash_tool_installation_finished(tool):
        return Workflow.update_server_status('tool finished {}'.format(tool['label']))

    @staticmethod
    def declare_decorate_bash(bash, save_to):
        '''
        '''

        ret = ''
        ret += 'OBC_START=$(eval "declare")\n'
        ret += bash + '\n'
        ret += 'OBC_CURRENT=$(eval "declare")\n'
        ret += 'comm -3 <(echo "$OBC_START" | grep -v "_=" | sort) <(echo "$OBC_CURRENT" | grep -v OBC_START | grep -v PIPESTATUS | grep -v "_=" | sort) > {}\n'.format(save_to)

        return ret


    def step_tool_variables(self, step):
        '''
        Get all the tools variables that are used in this step
        '''

        def convert_tool_id(tool_id):
            if not tool_id.count('__') == 3:
                return tool_id.replace('.', '_')

            return '__'.join(tool_id.split('__')[0:-1]).replace('.', '_')

        input_variables_to_final = []
        for tool_id in step['tools']:
            new_tool_id = convert_tool_id(tool_id)
            for dependent_variable, dependent_tool in self.tool_variables[new_tool_id]:
                input_name = Workflow.get_tool_bash_variable(dependent_tool, dependent_variable['name'])
                dependent_tool_id = convert_tool_id(dependent_tool['id'])

                input_variables_to_final.append({
                    'input_name': input_name, # The name of the variable
                    'input_source': dependent_tool_id, # The name of the tool
                })


        return input_variables_to_final


    @staticmethod
    def convert_tool_to_request(tool, added_objects):
        '''
        Takes a tool and creates a dictionary with the fields that can be used for a request to tools_add
        added_objects: The tools that have been added alreadt
        '''

        #  "a1/1/1" --> {'name': 'a', 'version': '1', 'edit': 1}
        tool['dependencies'] = [Workflow.tool_label_to_object(x) for x in tool['dependencies']]

        def change_tool_dependencies(dependencies):
            ret = []
            for dependency in dependencies:
                #print ('==232323==')
                #print (dependency)
                dependency_label = Workflow.get_tool_slash_id(dependency)
                #print ('dependency_label:', dependency_label)
                if dependency_label in added_objects:
                    ret.append(added_objects[dependency_label]['new'])
                else:
                    ret.append(dependency)

            return ret


        def change_tool_variables_in_bash(bash, dependencies):

            ret = bash

            for dependency in dependencies:
                dependency_label = Workflow.get_tool_slash_id(dependency)
                if dependency_label in added_objects:
                    this_tool = added_objects[dependency_label]
                    for variable_name in this_tool['variable_names']:
                        old_tool_variable_bash = Workflow.get_tool_bash_variable(dependency,  variable_name)
                        new_tool_variable_bash = Workflow.get_tool_bash_variable(added_objects[dependency_label]['new'], variable_name)

                        ret = ret.replace(old_tool_variable_bash, new_tool_variable_bash)

            return ret

        ret = {
            'tool_description': tool['description'],
            'tools_search_name': tool['name'],
            'tools_search_version': tool['version'],
            'tool_edit_state': False,
            'tool_visibility': tool['visibility'],
            'tool_dependencies': change_tool_dependencies(tool['dependencies']), # "a1/1/1"
            'tool_os_choices': [{'value': x} for x in tool['os_choices']], # [{'value': 'posix'}],
            'tool_installation_commands': change_tool_variables_in_bash(tool['installation_commands'], tool['dependencies']),
            'tool_validation_commands': change_tool_variables_in_bash(tool['validation_commands'], tool['dependencies']),
            'tool_variables': tool['variables'],
            'tool_keywords': tool['keywords'],

        }

        return ret

    def process_tool_requests(self, edit_getter):
        '''
        edit_getter: A function that gets a tool_request and returns the edit of this tool
        '''

        added_objects = {}
        for tool in self.get_tool_installation_order():
            tool_request = Workflow.convert_tool_to_request(tool, added_objects)
            new_edit = edit_getter(tool_request)

            if not type(new_edit) is int:
                return new_edit, None # This is an error

            tool_label = Workflow.get_tool_slash_id(tool)
            added_objects[tool_label] = {
                'type': 'tool',
                'old': {
                    'name': tool['name'],
                    'version': tool['version'],
                    'edit': int(tool['edit']),
                },
                'new': {
                    'name': tool['name'],
                    'version': tool['version'],
                    'edit': int(new_edit) # response_decoded['edit'],
                },
                'variable_names': [x['name'] for x in tool['variables']],
            }

        old_tool_variables = {
            self.get_tool_bash_variable(tool['old'], variable) : self.get_tool_bash_variable(tool['new'], variable)
            for tool in added_objects.values()
               for variable in tool['variable_names']
                  if tool['type'] == 'tool'
        }
        old_tool_ids = {
            self.get_tool_cytoscape_id(tool['old']): self.get_tool_cytoscape_id(tool['new'])
            for tool in added_objects.values()
        }

        return old_tool_variables,  old_tool_ids


    def test_process_tool_requests(self, ):
        c = 1000
        def edit_getter(tool_request):
            nonlocal c
            c += 1
            return c

        return self.process_tool_requests(edit_getter)


    def isolate_workflow(self, workflow_to_isolate, added_workflows_ids):
        '''
        Extract a workflow from within the workflow object
        workflow_to_isolate:
        {'id': 'a__1', 'name': 'a', 'edit': 1, 'description': '1', 'website': '', 'keywords': [], 'visibility': 'public', 'label': 'a/1', 'type': 'workflow', 'draft': True, 'disconnected': False, 'belongto': {'name': 'a2', 'edit': 1}}
        '''

        #print ('workflow to isolate:')
        #print (workflow_to_isolate)

        ret = {
            'elements': {
                'nodes': [],
                'edges': [],
            },
        }
        # Add the rest fields of the cytoscape workflow
        for k,v in self.workflow['workflow'].items():
            if k == 'elements':
                continue

            ret[k] = v

        workflow_to_isolate_id = workflow_to_isolate['id']
        added_workflows_ids.add(workflow_to_isolate_id)

        for node in self.node_iterator_with_style(create_copy=True):
            #print (node)

            # Is this the root workflow of the complete workflow that belongs to the isolated?
            if self.is_root_workflow(node['data']) and node['data']['id'] == workflow_to_isolate_id:
                #print ('added root')
                ret['elements']['nodes'].append(node)
                continue

            # Is this the root workflow of the workflow to be isolated?
            if self.is_workflow(node['data']) and node['data']['id'] == workflow_to_isolate_id:
                #print ('added isolated')
                node['data']['belongto'] = None
                ret['elements']['nodes'].append(node)
                continue

            # Is this the root workflow of the complete workflow that does not belong to the isolated?
            if node['data']['belongto'] is None:
                continue

            # This not the root workflow
            # If the "belongs" field is in added_workflows_ids, add it
            if Workflow.get_workflow_dash_id(node['data']['belongto']) in added_workflows_ids:
                ret['elements']['nodes'].append(node)


        this_workflows_ids = {node['data']['id'] for node in ret['elements']['nodes']}

        # Add edges
        for edge in self.edge_iterator_with_style(create_copy=True):
            if edge['data']['source'] in this_workflows_ids and edge['data']['target'] in this_workflows_ids:
                ret['elements']['edges'].append(edge)

        return ret


    @staticmethod
    def remove_edit_from_workflow_cytoscape(*, workflow_cytoscape, old_variables, old_tool_ids, old_workflow_ids):
        '''
        Takes a cytoscape workflow object and removes the edit information.
        Makes it appropriate for sending it as a request to the add_workflow function

        This does the reverse job of set_edit_to_cytoscape_json in views.py

        workflow_cytoscape: The workflow in cytoscape format to remove edit info
        old_variables: A dictionary. Keys: old bash variables. Values: new bash variables. Example:
            {'a1__1__1__path': 'a1__1__1001__path', 'a2__1__1__path': 'a2__1__1002__path'}
            {'a1__1__1__path': 'a1__1__1001__path', 'a2__1__1__path': 'a2__1__1002__path', 'step__main_step__a__1': 'step__main_step__a__2001'}
        old_tool_ids: A dictionaty. Keys: old tool cytoscape ids, values: new tool cytoscape ids
            Example: {'a1__1__1__2': 'a1__1__1001__2', 'a2__1__1__2': 'a2__1__1002__2'}
        old_workflow_ids. Example:
            {'a__1': 'a__2001'}
        '''


        # Get the root workflow
        root_workflow = Workflow.get_root_workflow_cytoscape(workflow_cytoscape)
        if not root_workflow:
            raise OBC_Executor_Exception('Could not find root workflow')
        root_workflow = root_workflow['data']

        root_id = root_workflow['id']
        root_name = root_workflow['name']
        root_edit = root_workflow['edit']

        for node in workflow_cytoscape['elements']['nodes']:

            # If this the root workflow Change the edit, the name and
            if node['data']['belongto'] is None:

                node['data']['edit'] = None
                node['data']['name'] = 'root'
                node['data']['id'] = 'root__null'

                del node['data']['label']
                del node['data']['description']
                del node['data']['website']
                del node['data']['keywords']
                del node['data']['visibility']

                continue

            belong_to_dash_id = Workflow.get_workflow_dash_id(node['data']['belongto'])

            # Does this belong in root?  Change belong to
            if belong_to_dash_id == root_id:
                node['data']['belongto']['edit'] = None # Remove edit
                node['data']['belongto']['name'] = 'root'

            # Does this belong to another workflow?
            if belong_to_dash_id in old_workflow_ids:
                # Change the edit of belong to
                node['data']['belongto']['edit'] = int(old_workflow_ids[belong_to_dash_id].split('__')[-1])

            #Change bash
            if 'bash' in node['data']:
                # step__ssrr__name_edit --> step__ssrr__root__null
                node['data']['bash'] = re.sub(r'step__(\w+)__' + root_name + r'__' + str(root_edit) , r'step__\1__root__null',  node['data']['bash'])
                node['data']['bash'] = re.sub(r'input__(\w+)__' + root_name + r'__' + str(root_edit) , r'input__\1__root__null',  node['data']['bash'])
                node['data']['bash'] = re.sub(r'output__(\w+)__' + root_name + r'__' + str(root_edit) , r'output__\1__root__null',  node['data']['bash'])

                for k,v in old_variables.items():
                    node['data']['bash'] = node['data']['bash'].replace(k, v)

            #Change steps
            if 'steps' in node['data']:
                new_steps = []
                for step in node['data']['steps']:
                    new_step = re.sub(r'step__(\w+)__' + root_name + r'__' + str(root_edit) , r'step__\1__root__null',  step)
                    if new_step in old_variables:
                        new_step = old_variables[new_step]
                    new_steps.append(new_step)
                node['data']['steps'] = new_steps

            # Change tools
            if 'tools' in node['data']:
                new_tool_ids = []
                for tool_id in node['data']['tools']:
                    new_tool_id = old_tool_ids.get(tool_id, tool_id)
                    new_tool_ids.append(new_tool_id)
                node['data']['tools'] = new_tool_ids


            #Change inputs
            if 'inputs' in node['data']:
                new_inputs = []
                for input_ in node['data']['inputs']:
                    # input__inp__root__null -->  input__inp__root__null
                    new_input = re.sub(r'input__(\w+)__' + root_name + r'__' + str(root_edit) , r'input__\1__root__null',  input_)
                    if new_input in old_variables:
                        new_input = old_variables[new_input]
                    new_inputs.append(new_input)
                node['data']['inputs'] = new_inputs

            # Change outputs
            if 'outputs' in node['data']:
                new_outputs = []
                for output in node['data']['inputs']:
                    # input__inp__root__null -->  input__inp__root__null
                    new_output = re.sub(r'output__(\w+)__' + root_name + r'__' + str(root_edit) , r'output__\1__root__null',  output)
                    if new_output in old_variables:
                        new_output = old_variables[new_output]
                    new_outputs.append(new_output)
                node['data']['outputs'] = new_outputs

            # Change the id . From step__main_step__a__1 --> step__main_step__root__null
            if re.search(fr'{root_id}$', node['data']['id']):
                node['data']['id'] = re.sub(fr'{root_id}$', 'root__null', node['data']['id'])

            # Change workflows
            if node['data']['type'] == 'workflow':
                node['data']['id'] = old_workflow_ids[node['data']['id']]
                node['data']['label'] = '/'.join(node['data']['id'].split('__'))
                node['data']['edit'] = int(node['data']['id'].split('__')[-1])

            # Change tool nodes
            if node['data']['type'] == 'tool':
                # {'a1__1__1__2': 'a1__1__1001__2', 'a2__1__1__2': 'a2__1__1002__2'}

                # Change tools dependencies
                new_dependencies = []
                for dependency in node['data']['dependencies']:
                    dependency_id = Workflow.get_tool_cytoscape_id(dependency)
                    if not dependency_id in old_tool_ids:
                        raise OBC_Executor_Exception('Could not resolve dependencies')
                    new_dependencies.append(Workflow.create_tool_from_cytoscape_id(old_tool_ids[dependency_id]))
                node['data']['dependencies'] = new_dependencies

                # Change tool id
                node['data']['id'] = old_tool_ids[node["data"]["id"]]

                # Change edit
                node['data']['edit'] = int(node['data']['id'].split('__')[2])

                # Change dep_id
                if node['data']['dep_id'] != '#':
                    node['data']['dep_id'] = old_tool_ids[node["data"]["dep_id"]]


                # Change installation commands and validation commands
                # a1__1__1__path . ${a1__1__1__path} --> ${a1__1__1001__path}
                for old_tool_id_cytoscape, new_tool_id_cytoscape in old_tool_ids.items():
                    old_tool_id = '__'.join(old_tool_id_cytoscape.split('__')[:-1]) # a1__1__1__2 --> a1__1__1
                    new_tool_id = '__'.join(new_tool_id_cytoscape.split('__')[:-1])
                    node['data']['installation_commands'] = re.sub(fr'{old_tool_id}', f'{new_tool_id}', node['data']['installation_commands'] )
                    node['data']['validation_commands'] = re.sub(fr'{old_tool_id}', f'{new_tool_id}', node['data']['validation_commands'] )

                # Change label and text
                t1 = Workflow.tool_label_to_object(node['data']['label'])  # text': 'a2/1/1', 'label': 'a2/1/1',
                t2 = Workflow.get_tool_cytoscape_id(t1) # a2__1__1__2
                t3 = old_tool_ids[t2] # a2__1__1002__2
                t4 = '__'.join(t3.split('__')[:-1])  # a2__1__1002
                t5 = Workflow.tool_dash_id_to_object(t4) # {'name': 'a2', 'version': '1', 'edit': 1002}
                t6 = Workflow.get_tool_slash_id(t5) # a2/1/1002
                node['data']['label'] = t6
                node['data']['text'] = t6

            # Change steps
            if node['data']['type'] == 'step':

                if node['data']['id'] in old_variables:
                    node['data']['id'] = old_variables[node['data']['id']]

                if 'inputs_reads' in node['data']:
                    del node['data']['inputs_reads']
                if 'inputs_sets' in node['data']:
                    del node['data']['inputs_sets']
                if 'outputs_reads' in node['data']:
                    del node['data']['outputs_reads']
                if 'outputs_sets' in node['data']:
                    del node['data']['outputs_sets']

                # If it belongs to root and it is sub_main, then make it a main
                if (
                    node['data']['belongto']['name'] == 'root' and
                    node['data']['belongto']['edit'] is None and
                    node['data']['sub_main'] and
                    not node['data']['main']
                ):
                    node['data']['main'] = True
                    node['data']['sub_main'] = False

            # Change input/output nodes
            if node['data']['type'] in ['input', 'output']:
                if node['data']['id'] in old_variables:
                    node['data']['id'] = old_variables[node['data']['id']]

        # Change edges
        new_edges = []
        for edge in workflow_cytoscape['elements']['edges']:


            if edge['data']['source'] in old_tool_ids:
                edge['data']['source'] = old_tool_ids[edge['data']['source']]
            elif edge['data']['source'] in old_variables:
                edge['data']['source'] = old_variables[edge['data']['source']]
            elif edge['data']['source'] in old_workflow_ids:
                edge['data']['source'] = old_workflow_ids[edge['data']['source']]

            if edge['data']['target'] in old_tool_ids:
                edge['data']['target'] = old_tool_ids[edge['data']['target']]
            elif edge['data']['target'] in old_variables:
                edge['data']['target'] = old_variables[edge['data']['target']]
            elif edge['data']['target'] in old_workflow_ids:
                edge['data']['target'] = old_workflow_ids[edge['data']['target']]

            if root_id in edge['data']['source']:
                edge['data']['source'] = edge['data']['source'].replace(root_id, 'root__null')

            if root_id in edge['data']['target']:
                edge['data']['target'] = edge['data']['target'].replace(root_id, 'root__null')

            edge['data']['id'] = Workflow.get_edge_id(edge['data']['source'], edge['data']['target'])




    @staticmethod
    def convert_workflow_to_request(workflow_cytoscape, isolated_workflow_root_node_before):
        '''
        See also: convert_tool_to_request
        isolated_workflow_root_node_before: The root node of the workflow BEFORE removing edit info
        '''

        #Get root node
        root_node = Workflow.get_root_workflow_cytoscape(workflow_cytoscape)
        if not root_node:
            raise OBC_Executor_Exception('Could not find root node')

        return {
            'workflow_info_name': isolated_workflow_root_node_before['data']['name'],
            'workflow_info_forked_from': None,
            'workflow_edit_state': False,
            'workflow_description': isolated_workflow_root_node_before['data']['description'],
            'workflow_website': isolated_workflow_root_node_before['data']['website'],
            'workflow_keywords': isolated_workflow_root_node_before['data']['keywords'],
            'workflow_visibility': isolated_workflow_root_node_before['data']['visibility'],
            'workflow_json': workflow_cytoscape,
        }


    def process_workflow_requests(self, *, edit_getter, old_tool_variables, old_tool_ids):
        '''
        This method:
        Breaks down the workflow in sub-workflows,
        then removes edit information for every sub-workflow,


        old_tool_variables : dictionary. keys: old tool variables, values: new tool variables
        old_tool_ids : dictionaty. Key: old tool ids, values: new tool ids
        '''

        added_workflows_ids = set()
        old_variables = old_tool_variables
        old_workflow_ids = {}

        for sub_workflow_node in self.get_workflow_order():
            #print ('Workflow sub_workflow_node:')
            #pprint (sub_workflow_node)

            workflow_label = self.get_workflow_slash_id(sub_workflow_node) # a/1
            #print ('Workflow label:', workflow_label)

            isolated_workflow = self.isolate_workflow(sub_workflow_node, added_workflows_ids)
            #print ('Isolated workflow:')
            #pprint (isolated_workflow)

            isolated_workflow_root_node = self.get_root_workflow_cytoscape(isolated_workflow)
            #print ('isolated_workflow_root_node:')
            #print (isolated_workflow_root_node)
            #visibility = isolated_workflow_root_node['data']['visibility']

            isolated_workflow_old_variables = {
                node['data']['id']
                for node in isolated_workflow['elements']['nodes']
                if (
                        node['data']['type'] in {
                            Workflow.STEP_TYPE,
                            Workflow.INPUT_TYPE,
                            Workflow.OUTPUT_TYPE,
                        }
                        and
                        self.get_workflow_slash_id(node['data']['belongto']) == workflow_label
                    )
            }

            isolated_workflow_root_node_before = copy.deepcopy(isolated_workflow_root_node)

            Workflow.remove_edit_from_workflow_cytoscape(
                workflow_cytoscape = isolated_workflow,
                old_variables = old_variables,
                old_tool_ids = old_tool_ids,
                old_workflow_ids = old_workflow_ids,
            )

            workflow_request = Workflow.convert_workflow_to_request(
                isolated_workflow,
                isolated_workflow_root_node_before,
            )
            #print ('workflow request:')
            #pprint (workflow_request)

            new_edit = edit_getter(workflow_request)
            #print ('New edit:', new_edit)
            if not type(new_edit) is int: # This is an error
                return new_edit

            # Add old_workflow_ids --> {'a__1': 'a__2001'}
            old_workflow_ids[isolated_workflow_root_node_before['data']['id']] = re.sub(r'\d+$', str(new_edit), isolated_workflow_root_node_before['data']['id'])

            # Now that we have a new edit, update old_variables
            for isolated_workflow_old_variable in isolated_workflow_old_variables:
                old_variables[isolated_workflow_old_variable] = re.sub(r'(\w+__\w+__\w+)__\d+', r'\1__' + str(new_edit), isolated_workflow_old_variable)


    def upload(self, *, tool_edit_getter=None, workflow_edit_getter=None):
        '''
        '''

        c = 1000
        d = 2000

        def test_tool_edit_getter(tool_request):
            nonlocal c
            c += 1
            return c

        def test_workflow_edit_getter(workflow_request):
            nonlocal d
            d += 1
            return d


        old_tool_variables, old_tool_ids = self.process_tool_requests(
            edit_getter = tool_edit_getter if tool_edit_getter else test_tool_edit_getter
        )
        if type(old_tool_variables) is str: # This is an error
            return old_tool_variables

        error_message = self.process_workflow_requests(
            edit_getter = workflow_edit_getter if workflow_edit_getter else test_workflow_edit_getter,
            old_tool_variables=old_tool_variables,
            old_tool_ids=old_tool_ids,
        )

        if error_message:
            return error_message


    def break_down_step_generator(self,
        enable_read_arguments_from_commandline = True,
        enable_save_variables_to_json = True,
        enable_save_variables_to_sh = True,
        enable_parallel = False,
        break_down_on_tools = False,
        ):
        '''
        enable_read_arguments_from_commandline: If true, arguments are read from command line
        enable_save_variables_to_json: If true, variables are saved in json format
        enable_save_variables_to_sh: If True, variables are saved to sh format
        enable_parallel: If True each PARALLEL yields a new step
        break_down_on_tools: If True, each command that invokes a tool (of the workflow), creates yields a new step
        '''

        # First, check for circles in step calls
        c = self.check_step_calls_for_circles()
        if c:
            raise OBC_Executor_Exception('Found circle in step calls:\n{}\n. Cannot break down workflow.'.format(c))

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

                if hasattr(command, 'list'):
                    for l in command.list:
                        ret = recursive(l, current_level+1)
                        if ret:
                            return ret

                return False

            return recursive(command, 1)

        def save_variables(*, bash, read_from, save_to, input_tool_variables, input_workflow_variables):
            '''
            read_from is either None or __VARS_sh (no dot)
            '''

            ret = ''
            if enable_read_arguments_from_commandline and (read_from or input_tool_variables or input_workflow_variables):
                ret += Workflow.read_arguments_from_commandline([read_from] + input_tool_variables + input_workflow_variables)
            if read_from:
                ret += '. ${{{}}}\n'.format(read_from)

            if enable_save_variables_to_sh:
                ret += Workflow.declare_decorate_bash(bash, save_to)
            else:
                ret += bash

            return ret

        def parse_parallel_constant(bash, delimiter=','):
            '''
            STEPS=
            A,B
            1,2
            3,4
            5,6
            7,8
            9,10

            returns:
            {
                'variable': 'STEPS',
                'content': [[]]
            }
            '''

            m = re.match(r'([\w]+)=[\s]*(.+)', bash, flags=re.DOTALL)
            if not m:
                return {}

            ret = {
                'variable': m.group(1),
                'content': [],
            }

            CSV_content = m.group(2)
            CSV_f = io.StringIO(CSV_content)
            try:
                CSV_reader = csv.reader(CSV_f, delimiter=delimiter)
            except csv.Error as e:
                return {}

            first = True
            for line in CSV_reader:
                if not line:
                    continue

                if first:
                    ret['header'] = line
                    first = False
                    continue

                ret['content'].append(line)

            CSV_f.close() # <-- is there any meaning on this?

            return ret

        def parse_parrallel_call_1(bash):
            '''
            PARALLEL step__new_step__test5__1 ${STEPS}

            Returns:
            {
                'step': step__new_step__test5__1,
                'variable': STEPS
            }
            '''
            m=re.match(r'PARALLEL[\s]+(?P<step_name>step__[\w]+__[\w]+__[\d]+)[\s]+((\$(?P<var_name1>[\w]+))|(\${(?P<var_name2>[\w]+)}))', bash)
            if m:
                calling_step = m.group('step_name')
                calling_variable = m.group('var_name1') or m.group('var_name2')
                if calling_variable:

                    return {
                        'step': calling_step,
                        'variable': calling_variable
                    }

            return {}

        def parse_parallel_call_2(bash):
            '''
            PARALLEL step_1 step_2 , ....
            '''

            m = re.match(r'PARALLEL(?P<steps>([\s]+[\w]+)+)', bash)
            if m:
                return m.group('steps').strip().split()
            return []


        def create_json(*, bash, step, step_breaked_id, is_last, output_variables):
            '''
            Create a json file with the output variables at the end of the bash script
            We do not actually have to pass the intermediate VAR_SH name in the json.. We do not read it.. Maybe we will correct this in the future
            We read the VAR_SH from command line
            '''

            if not enable_save_variables_to_json:
                return bash

            filename_with_intermediate = '{}__{}__VARS.sh'.format(step['id'], step_breaked_id)
            output_filename = '{}__{}.json'.format(step['id'], step_breaked_id)

            output_variables_str = ''
            #if is_last: # Always pass output variables
            if True:
                for var in output_variables:
                    output_variables_str += ',\n"{VAR}": "${{{VAR}}}"'.format(VAR=var)

            # The 'ENDOFILE' means do not interpret anything
            content = '''
cat > {OUTPUT_FILENAME} << ENDOFFILE
{{
"{STEP_ID}__{COUNT}__ID": "{STEP_ID}__{COUNT}__ID",
"{FILENAME_WITH_INTERMEDIATE_NODOT}": "{FILENAME_WITH_INTERMEDIATE}"{OUTPUT_VARIABLES}\n
}}
ENDOFFILE
'''.format(
    OUTPUT_FILENAME=output_filename,
    STEP_ID=step['id'],
    COUNT=step_breaked_id,
    FILENAME_WITH_INTERMEDIATE_NODOT=filename_with_intermediate.replace('.', '_'),
    FILENAME_WITH_INTERMEDIATE = filename_with_intermediate,
    OUTPUT_VARIABLES = output_variables_str,
    )

            return bash+content

        step_counter = defaultdict(int) # How many times this steps has been yielded?

        def break_down_step_recursive(step, parallel_variables=None, run_after=None, ):
            '''
            Use bashlex to break down all steps of a bash script
            parallel_variables: Initialize script with these variables. Used for the parallel execution
            run_after: Run this step after "run_after". This is a list
            '''

            bash = step['bash']
            if not bash.strip():
                return

            # Add variables from parallel
            if parallel_variables:
                to_add= '\n'.join([r'{}="{}"'.format(k,v) for k,v in parallel_variables.items()])
                bash = '\n' + to_add + '\n' + bash

            # Join multiline lines
            # issue #232
            bash = re.sub(r'\\\n', '', bash)

            # https://stackoverflow.com/questions/12404661/what-is-the-use-case-of-noop-in-bash
            # bashlex Cannot parse empty strings!
            bash_to_parse = '{\n:\n' + bash + '\n}'
            calling_steps = step['steps']

            # Get the input variables of this step.
            # We need to add them in every breaked step in order to read from the command line
            input_tool_variables = [variable['input_name'] for variable in self.step_tool_variables(step)]


            try:
                p = bashlex.parse(bash_to_parse)
            except bashlex.errors.ParsingError as e:
                message = 'Could not parse bash script (error 2320):\n'
                message += bash_to_parse + '\n'
                message += 'Error: {}'.format(str(e))
                raise OBC_Executor_Exception(message)

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

            # Main commands are the children of the root node
            main_commands = p[0].list[1].parts
            found_call = False
            start = 2 # Remove '{\n'
            read_from = None
            last_assignment = None # Used for PARALLEL

            #run_afters = [] # List of all the steps that are run in this break down
            if run_after is None:
                run_after = []

            for main_command in main_commands:

                this_is_a_parallel_call_1 = False
                this_is_a_parallel_call_2 = False
                this_is_a_tool_invocation = False

                level_tuple = get_level(main_command, calling_steps)
                if level_tuple:
                    level, called_step = level_tuple
                    if level>2:
                        raise OBC_Executor_Exception('Step: {} calls step: {} in a secondary scope (if,while,for,function..). This is not supported.'.format(
                            step['id'], called_step))

                if not main_command.kind == 'command':
                    continue

                if not hasattr(main_command, 'parts'):
                    continue

                # Check if this is a CommandNode(parts=[AssignmentNode(parts=[] pos=(118, 152) word='STEPS=\nA,B\n1,2\n3,4\n5,6\n7,8\n9,10\n')] pos=(118, 152))
                # OR
                # Check if this is a CommandNode(pos=(0, 20), parts=[WordNode(pos=(0, 20), word='VAR1=\nA,B\n1,2\n3,4\n'),])
                # word='VAR1=\nA,B\n1,2\n3,4\n' --> THIS IS A WordNode !
                # word='VAR=\nA,B\n1,2\n3,4\n' --> THIS IS A AssignmentNode
                if len(main_command.parts) == 1:
                    if main_command.parts[0].kind in ['assignment', 'word']:
                        # This is an assignment
                        assignment_word = main_command.parts[0].word
                        last_assignment = parse_parallel_constant(assignment_word)

                # This is a command
                # check for PARALLEL step__new_step__test5__1 ${STEPS}
                if len(main_command.parts) == 3 and all(hasattr(x,'word') for x in main_command.parts): # Make sure that it contains only word nodes #186
                    line_to_match = ' '.join(x.word for x in main_command.parts)
                    parallel_call = parse_parrallel_call_1(line_to_match)
                    if  parallel_call and \
                        last_assignment and \
                        parallel_call['variable'] == last_assignment['variable'] and \
                        parallel_call['step'] in calling_steps:
                            this_is_a_parallel_call_1 = True
                            pos = (main_command.parts[0].pos[0], main_command.parts[2].pos[1])

                # check for PARALLEL step_step_1, step_step_2, ....
                if len(main_command.parts) > 1 and all(hasattr(x,'word') for x in main_command.parts): # Make sure that it contains only word nodes #186
                    line_to_match = ' '.join(x.word for x in main_command.parts)
                    parallel_call_2 = parse_parallel_call_2(line_to_match)
                    if parallel_call_2 and all(x in calling_steps for x in parallel_call_2):
                        this_is_a_parallel_call_2 = True
                        pos = (main_command.parts[0].pos[0], main_command.parts[-1].pos[1])


                # Check if this command is a call to a tool
                if (
                    break_down_on_tools and
                    not step.get("tool_invocation") and # If this step is an artificial step, do not go into infinite recursion
                    hasattr(main_command, 'parts') and
                    len(main_command.parts) > 0 and
                    hasattr(main_command.parts[0], 'parts') and
                    len(main_command.parts[0].parts) > 0 and
                    main_command.parts[0].parts[0].kind == 'parameter' and
                    main_command.parts[0].parts[0].value in self.tool_variables_ids # Belongs in tool variables
                ):

                    this_is_a_tool_invocation = True
                    positions = [part.pos for part in main_command.parts]
                    pos = (positions[0][0], positions[-1][1])
                    this_var = main_command.parts[0].parts[0].value
                    tool_to_call = self.tool_variables_ids[this_var]
                    tool_to_call_id = self.get_tool_dash_id(tool_to_call, no_dots=True)

                    # Create an artificial step to call
                    artificial_tool_step = {
                        "id": step['id'], # "step__RANDOM__w__1",
                        "name": None, # "RANDOM",
                        "label": None, # "RANDOM",
                        "type": "step",
                        "bash": '\n' + bash_to_parse[pos[0]:pos[1]] + '\n',
                        "main": False,
                        "sub_main": False,
                        "tools": [
                            tool_to_call_id,
                        ],
                        "steps": [],
                        "inputs": [],
                        "outputs": [],
                        #"belongto": {
                        #    "name": "w",
                        #    "edit": 1
                        #},
                        "belongto": None,
                        "inputs_reads": [],
                        "inputs_sets": [],
                        "outputs_sets": [],
                        "outputs_reads": [],
                        "tool_invocation": tool_to_call_id,
                    }



                if not (this_is_a_parallel_call_1 or this_is_a_parallel_call_2 or this_is_a_tool_invocation):
                    # We are looking for a command with a single part (function call)
                    if not len(main_command.parts) == 1:
                        continue

                    # It should be a single word
                    if not main_command.parts[0].kind == 'word':
                        continue

                    word = main_command.parts[0].word

                    #It should be a calling step
                    if not word in calling_steps:
                        continue

                    pos = main_command.parts[0].pos

                #This is a calling step OR a tool invocation step!
                found_call = True

                part_before_step_call = bash_to_parse[start: pos[0]]
                step_counter[step['id']] += 1
                step_inter_id = '{}__{}'.format(step['id'], str(step_counter[step['id']]))
                save_to = '{}__{}__VARS.sh'.format(step['id'], step_counter[step['id']])
                save_to_nodot = '{}__{}__VARS_sh'.format(step['id'], step_counter[step['id']])

                input_workflow_variables = [var for var in step['inputs_reads'] + step['outputs_reads'] if var in part_before_step_call]
                output_workflow_variables = [var for var in step['inputs_sets'] + step['outputs_sets'] if var in part_before_step_call]

                yield {
                    'bash': create_json(
                        bash = save_variables(
                            bash = part_before_step_call,
                            read_from = None,
                            save_to = save_to,
                            input_tool_variables = input_tool_variables,
                            input_workflow_variables = input_workflow_variables,
                        ),
                        step = step,
                        step_breaked_id = step_counter[step['id']],
                        is_last = False,
                        output_variables = output_workflow_variables
                        ),
                    'id': step['id'],
                    'count': step_counter[step['id']],
                    'step_inter_id': step_inter_id,
                    'last': False,
                    'input_variables': input_workflow_variables,
                    'output_variables': output_workflow_variables,
                    'run_after': run_after,
                    'tool_invocation': step.get('tool_invocation'),
                }
                #read_from = save_to
                read_from = save_to_nodot

                run_after.append(step_inter_id)
                
                # Are we calling another step? What is the id of this step?
                if this_is_a_parallel_call_1:
                    step_to_call_id = parallel_call['step']
                elif this_is_a_parallel_call_2:
                    step_to_call_id = None
                elif this_is_a_tool_invocation:
                    step_to_call_id = None # We are not calling any step
                else:
                    step_to_call_id = bash_to_parse[pos[0]:pos[1]]

                # What is the step object to call?
                if step_to_call_id:
                    step_to_call = self.step_ids[step_to_call_id]
                elif this_is_a_tool_invocation:
                    step_to_call = artificial_tool_step
                else:
                    step_to_call = None

                if this_is_a_parallel_call_1:
                    # This is a parallel call. Iterate in all variable assignments in CSV
                    # As per the example:
                    # last_assignment['header'] --> ['VAR_1', 'VAR_2', 'VAR_3']
                    # last_assignment['content'] --> [['VALUE_11', 'VALUE_12', 'VALUE_13'], ['VALUE_21', 'VALUE_22', 'VALUE_23'], ['VALUE_31', 'VALUE_32', 'VALUE_33'], ['VALUE_41', 'VALUE_42', 'VALUE_43'], ['VALUE_51', 'VALUE_52', 'VALUE_53']]  
                    header = last_assignment['header']
                    this_parallel_steps = []

                    if ( # Try to match something like this: ['1:10', '2:20'] 
                        len(last_assignment['content'])==1 and 
                        len(last_assignment['content'][0]) > 0 and # avoid all([]) --> True !
                        all(re.fullmatch(r'\d+:\d+', x) for x in last_assignment['content'][0])
                    ):
                        # 1:10,2:20,6:33
                        # this is a range. Create a lazy iterator
                        ranges = [list(map(int, x.split(':'))) for x in last_assignment['content'][0]] # [[1, 10], [2, 20], [6, 33]]
                        ranges = [range(x[0], x[1]+1) for x in ranges] # [range(1, 11), range(2, 21), range(6, 34)] 
                        last_assignment['content'] = product(*ranges)

                    for values in last_assignment['content']:
                        if len(values) != len(header):
                            raise OBC_Executor_Exception('Values in Parallel execution: {} are different than header: {}'.format(str(values), str(header)))
                        parallel_variables = dict(zip(header, values))
                        this_run_after = copy.deepcopy(run_after)

                        for item in break_down_step_recursive(step_to_call, parallel_variables=parallel_variables, run_after=this_run_after):
                            this_parallel_steps.append(item['step_inter_id'])
                            yield item

                    run_after.extend(this_parallel_steps)

                elif this_is_a_parallel_call_2:
                    # This is a parallel call: PARALLEL step__stp2__test1__1 step__stp3__test1__1 ...

                    this_parallel_steps = []
                    for step_to_call in parallel_call_2: # ['step__stp2__test1__1', 'step__stp3__test1__1']
                        this_run_after = copy.deepcopy(run_after)
                        
                        for item in break_down_step_recursive(self. step_ids[step_to_call], run_after=this_run_after, ):# + [step_inter_id]):
                            this_parallel_steps.append(item['step_inter_id'])
                            yield item


                    run_after.extend(this_parallel_steps)

                else:
                    for item in break_down_step_recursive(step_to_call, run_after=run_after):
                        yield item

                start = pos[1]


            # Yield the rest
            part_after_step_call = bash_to_parse[start:][:-2]
            step_counter[step['id']] += 1
            step_inter_id = '{}__{}'.format(step['id'], str(step_counter[step['id']]))
            save_to = '{}__{}__VARS.sh'.format(step['id'], step_counter[step['id']])
            save_to_nodot = '{}__{}__VARS_sh'.format(step['id'], step_counter[step['id']])
            input_workflow_variables = [var for var in step['inputs_reads'] + step['outputs_reads'] if var in part_after_step_call]
            output_workflow_variables = [var for var in step['inputs_sets'] + step['outputs_sets'] if var in part_after_step_call]


            yield {
                'bash' : create_json(
                    bash = save_variables(
                        bash = part_after_step_call,
                        read_from = None,
                        save_to = save_to,
                        input_tool_variables = input_tool_variables,
                        input_workflow_variables = input_workflow_variables,
                    ),
                    step = step,
                    step_breaked_id = step_counter[step['id']],
                    is_last = True,
                    output_variables = output_workflow_variables),
                'id': step['id'],
                'count': step_counter[step['id']],
                'step_inter_id': step_inter_id,
                'last': True,
                'input_variables': input_workflow_variables,
                'output_variables': output_workflow_variables,
                'run_after': run_after,
                'tool_invocation': step.get('tool_invocation'),
            }

            run_after.append(step_inter_id)


        return break_down_step_recursive(self.root_step)

##################### END OF CLASS WORKFLOW #####################################


class BaseExecutor():
    '''
    '''
    load_obc_functions_bash = r'. ${OBC_WORK_PATH}/obc_functions.sh' + '\n'

    INIT_STEP_NAME = 'INIT_STEP'
    FINAL_STEP_NAME = 'FINAL_STEP'

    def __init__(self, workflow, executor_parameters=None):
        if not isinstance(workflow, Workflow):
            raise OBC_Executor_Exception('workflow unknown type: {}'.format(type(workflow).__name__))
        self.workflow = workflow

        # The file that contain the values of the input parameters
        self.file_with_input_parameters = '${{OBC_WORK_PATH}}/{ID}_inputs.sh'.format(ID=self.workflow.nice_id_global)

        if executor_parameters and type(executor_parameters) == dict:
            for key, value in executor_parameters.items():
                setattr(self, key, value)

    def load_file_with_input_parameters(self,):
        '''
        '''
        return '. {}'.format(self.file_with_input_parameters) + '\n'

    def save_input_parameters(self, from_variable=False, from_workflow=False):
        '''
        from_variable: Read the variable from the variable with the same name: A="${A}".
                       Somehow the variable must be already set
        from_workflow: Read the variable from the workflow. The value of the variable
                       must exist in the workflow

        Either from_variable or from_workflow should be True. Not both.
        '''
        bash = 'touch {}\n'.format(self.file_with_input_parameters)
        for name, parameter in self.workflow.input_parameter_values.items():

            assert sum([from_variable, from_workflow]) == 1 # Only one should be true
            if from_variable:
                value = '${{{VALUE}}}'.format(VALUE=name)
            if from_workflow:
                value = parameter['value'] if not parameter['value'] is None else ''


            bash += r'echo "{VAR}=\"{VALUE}\"" >> {file_with_input_parameters}'.format(
                file_with_input_parameters=self.file_with_input_parameters,
                VAR=name,
                VALUE=value,
            ) + '\n'

        return bash



    def get_environment_variables(self, workflow_id=None, obc_client=None):
        '''
        '''

        if obc_client:
            d = {
                'OBC_DATA_PATH': g['CLIENT_OBC_DATA_PATH'],
                'OBC_TOOL_PATH': g['CLIENT_OBC_TOOL_PATH'],
                'OBC_WORK_PATH': g['CLIENT_OBC_WORK_PATH'],
            }
        else:
            d = {env:g[env] for env in ['OBC_DATA_PATH', 'OBC_TOOL_PATH', 'OBC_WORK_PATH'] if env in g}

        d['OBC_WORKFLOW_NAME'] = self.workflow.root_workflow['name']
        d['OBC_WORKFLOW_EDIT'] = str(self.workflow.root_workflow['edit'])
        d['OBC_NICE_ID'] = workflow_id if workflow_id else self.workflow.root_workflow_id # self.workflow.nice_id_global

        if obc_client:
            #d['OBC_REPORT_PATH'] = os.path.join(d['OBC_WORK_PATH'], workflow_id + '.html') # This is set from BASH
            d['OBC_SERVER'] = self.workflow.obc_server

        self.unset_variables = [var for var in ['OBC_TOOL_PATH', 'OBC_DATA_PATH', 'OBC_WORK_PATH'] if not var in d]

        return d


    def create_step_vars_filename(self, step_inter_id):
        '''
        This is the file that contains the variables of an intermediate step
        '''
        return os.path.join('${OBC_WORK_PATH}', step_inter_id + '_VARS.sh')


    @staticmethod
    def build_graph_from_run_afters(run_afters):
        G = nx.DiGraph()
        edges = [(run_before, run_after) for run_after, run_befores in run_afters.items() for run_before in run_befores]
        G.add_edges_from(edges)

        return G


    def transitive_reduction(self, run_afters):
        '''
        This is a dictionary.
        Keys: IDs of broken down steps
        List: List of broken steps that should be run BEFORE the key

        Return an airflow DAG without redundancies
        Applies https://en.wikipedia.org/wiki/Transitive_reduction
        Method: https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.dag.transitive_reduction.html
        '''
        self.G = BaseExecutor.build_graph_from_run_afters(run_afters)
        self.DAG = nx.transitive_reduction(self.G)
        return self.DAG

    def obc_init_step(self,):
        # Create init step for report
        bash = r'''

{{init_report}}

cat > ${OBC_WORK_PATH}/obc_functions.sh << 'OBCENDOFFILE'

{{function_REPORT}}

OBCENDOFFILE

'''

        bash = bash.replace(r'{{init_report}}', bash_patterns['init_report'])
        bash = bash.replace(r'{{function_REPORT}}', bash_patterns['function_REPORT'])

        return bash

    def obc_final_step(self, previous_tools, previous_steps_vars):
        # CREATE FINAL OPERATOR
        # Add all variables from previous tools.
        load_tool_vars = ''
        for tool_filename in previous_tools:
            load_tool_vars += '. {}\n'.format(tool_filename)

        # Load all variables from previous steps
        load_step_vars = ''
        for step_filename in previous_steps_vars:
            load_step_vars += '. {}\n'.format(step_filename)

        bash = load_tool_vars + load_step_vars + self.load_obc_functions_bash

        # Add output varables
        for output_parameter in self.workflow.output_parameters:
            bash += 'REPORT {} ${{{}}} OUTPUT_VARIABLE \n'.format(output_parameter['id'], output_parameter['id'])

        # Archive the report in tar.gz
        bash += bash_patterns['final_report']

        # The final step, prints the output variables in json format
        export_json = '"{' + ', '.join([r'''\"{A}\": \"${{{A}}}\"'''.format(A=x['id']) for x in self.workflow.output_parameters]) + '}"'
        export_json = "echo " + export_json + '\n'
        bash = bash + export_json

        return bash

    def add_init_and_final_in_graph(self, init_step_name, final_step_name, run_afters, previous_tools, step_inter_ids):
        #Add 'OBC_AIRFLOW_INIT' BEFORE ALL TOOLS
        for tool_id in previous_tools:
            if tool_id in run_afters:
                run_afters[tool_id].append(init_step_name)
            else:
                run_afters[tool_id] = [init_step_name]

        #Add 'OBC_AIRFLOW_INIT' BEFORE ALL STEPS
        for step_inter_id in step_inter_ids:
            if step_inter_id in run_afters:
                run_afters[step_inter_id].append(init_step_name)
            else:
                run_afters[step_inter_id] = [init_step_name]

        # Add to the first step, the last tool
        if previous_tools:
            run_afters[step_inter_ids[0]].append(previous_tools[-1])

        #Add 'OBC_AIRFLOW_FINAL' AFTER ALL STEPS
        run_afters[final_step_name] = step_inter_ids + [init_step_name]

    def initial_variabes(self,):
        ret  = 'export OBC_WORKFLOW_NAME={}\n'.format(self.workflow.root_workflow['name'])
        ret += 'export OBC_WORKFLOW_EDIT={}\n'.format(self.workflow.root_workflow['edit'])
        ret += 'export OBC_NICE_ID={}\n'.format(self.workflow.nice_id_global)
        ret += 'export OBC_SERVER={}\n\n'.format(self.workflow.obc_server)

        return ret


    def create_targz(self, output, files):
        '''
        Adapted from: https://stackoverflow.com/questions/740820/python-write-string-directly-to-tarfile
        '''

        if output is None:
            args = []
            fileIO = io.BytesIO()
            kwargs = {'fileobj': fileIO, 'mode': 'w:gz'}
        else:
            # Check for file extension
            if not os.path.splitext(output)[1].lower() in ['.tgz', '.gz']:
                output = output + '.tgz'

            args = [output, "w:gz"]
            kwargs = {}

        with tarfile.open(*args, **kwargs) as tar:
            for filename in files:
                content = files[filename].encode('utf-8')
                file = io.BytesIO(content)
                info = tarfile.TarInfo(name=filename)
                info.size = len(content)
                tar.addfile(tarinfo=info, fileobj=file)
        if output:
            log_info('Created tar gz file: {}'.format(output))

        if output is None:
            fileIO.flush()
            return fileIO.getvalue()

    def create_zip(self, output, files):
        '''
        '''

        if output is None:
            fileIO = io.BytesIO()
            args = [fileIO, 'w']
        else:
            # Check for file extension
            if os.path.splitext(output)[1].lower() != '.zip':
                output = output + '.zip'

            args = [output, 'w']

        with zipfile.ZipFile(*args) as zipf:
            for filename in files:
                content = files[filename].encode('utf-8')
                #file = io.BytesIO(content)
                zipf.writestr(filename, content, compress_type=compression)
        if output:
            log_info('Created zip file: {}'.format(output))

        if output is None:
            fileIO.flush()
            return fileIO.getvalue()

    def create_environments(self,):
        '''
        An empty tool_run_after: {'wget__latest__1': []} 

        An example of what it might return:
    "environments": {
        "0": {
            "plink__1_07_x86_64__1": [
                "wget__latest__1",
                "unzip__latest__1"
            ],
            "unzip__latest__1": [],
            "wget__latest__1": []
        },
        "1": {
            "test_script__1__2": [
                "python__3_8__1"
            ],
            "python__3_8__1": []
        }
    }
        '''

        ret = {}

        environment_counter = 0
        # https://stackoverflow.com/questions/21739569/finding-separate-graphs-within-a-graph-object-in-networkx
        tool_graph = BaseExecutor.build_graph_from_run_afters(self.workflow.tool_run_afters)
        tool_graph_undirected = tool_graph.to_undirected()
        tool_sub_graphs = (tool_graph_undirected.subgraph(c) for c in nx.connected_components(tool_graph_undirected))
        all_nodes = set()
        for i, sg in enumerate(tool_sub_graphs):
            this_environment_nodes = set(sg.nodes())
            all_nodes |= this_environment_nodes
            #print (i, this_environment_nodes)
            #self.decomposed['environments'][environment_counter] = {x: [y for y in self.decomposed['steps'][x]['run_after'] if y in this_environment_nodes] for x in this_environment_nodes}
            ret[environment_counter] = {x: [y for y in self.workflow.tool_run_afters[x] if y in this_environment_nodes] for x in this_environment_nodes}
            environment_counter += 1


        # It might be the case that the tool_run_afters do not contain dependencies. For example one (or more) tool(s) that do not have
        # any dependency or other tools are dependent from them. In that case we do not have a graph (graph=edges=dependencies) so
        # this method fails.   
        for tool, dependencies in self.workflow.tool_run_afters.items():
            if not tool in all_nodes:
                # This tool is not in any environment
                if dependencies:
                    # This should never happen. If it had dependencis then it should belong in a graph!
                    raise OBC_Executor_Exception('Error 3998')
                ret[environment_counter] = {tool: []} # Create an environment of its own with a single tool.
                environment_counter += 1

        #print (json.dumps(ret, indent=2))

        return ret

    @staticmethod
    def dot_graph(dag):
        '''
        Create a dot visualization
        '''

        EDGE = '   {FROM} -> {TO};'

        ret = '''
digraph G {{
{EDGES}
}}
'''

        edges = []
        for k,v in dag.items():
            for node in v:
                edges.append(EDGE.format(FROM=node, TO=k))

        return ret.format(EDGES='\n'.join(edges))



    def decompose(self,
            break_down_on_tools=False,
        ):
        '''
        Decomposes the workflow in steps. Create DAG.

        break_down_on_tools: Should a tool invocation create a new node in DAG?
        '''
        self.decomposed = {
            'environment_variables': {},
            'steps': {},
        }

        # ENVIRONMENT VARIABLES
        environment_variables = self.get_environment_variables()
        for k,v in environment_variables.items():
            self.decomposed['environment_variables'][k] = v
        self.decomposed['environment_variables']['OBC_RANDOM_NICE_ID'] = self.workflow.nice_id_global
        self.decomposed['environment_variables']['OBC_SERVER'] = self.workflow.obc_server

        #print ('ENVIRONMENT VARIABLES:')
        #print (json.dumps(ret['environment_variables'], indent=4))


        # INPUT VARIABLES
        self.decomposed['input_parameters'] = self.workflow.input_parameter_values
        #print ('INPUT VARIABLES:')
        #print (json.dumps(ret['input_parameters'], indent=4))

        # OUTPUT VARIABLES
        self.decomposed['output_parameters'] = {x['id']: {
                'description': x['description'],
                'belongto': x['belongto'],
            } for x in self.workflow.output_parameters
        }



        #print ('OUTPUT VARIABLES:')
        #print (json.dumps(ret['output_parameters'], indent=4))


        # Create isolated environments
        self.decomposed['environments'] = self.create_environments()


        # INIT STEP
        initial_variabes = self.initial_variabes()
        input_parameters = self.save_input_parameters(from_workflow=True) # touch ${OBC_WORK_PATH}/v5FDK_inputs.sh
        init_bash = initial_variabes + self.obc_init_step() + input_parameters

        run_afters = {BaseExecutor.INIT_STEP_NAME: []}
        self.decomposed['steps'][BaseExecutor.INIT_STEP_NAME] = {
            'bash' : init_bash,
            'run_after': [],
            'type': 'initial',
        }

        #print ('INIT BASH:')
        #print (init_bash)

        # INPUT PARAMETERS
        self.decomposed['input_parameters'] = self.workflow.input_parameter_values

        # TOOL STEPS
        tool_ids = []
        previous_tools = []


        for tool_index, tool in enumerate(self.workflow.tool_bash_script_generator()):


            tool_vars_filename = os.path.join('${OBC_WORK_PATH}', Workflow.get_tool_vars_filename(tool))
            tool_id = self.workflow.get_tool_dash_id(tool, no_dots=True)

            # Get the environment in which this tool belongs
            this_tool_environment = [k for k,v in self.decomposed['environments'].items() if tool_id in v]
            if len(this_tool_environment) == 0:
                raise OBC_Executor_Exception(f'Tool {tool_id} does not exist in any environment')
            if len(this_tool_environment) > 1:
                raise OBC_Executor_Exception(f'Tool {tool_id} exists in more than one environments.')
            this_tool_environment = this_tool_environment[0]
            #print (f'tool: {tool_id} Environment: {this_tool_environment}')

            this_tool_previous_tools = [
                os.path.join('${OBC_WORK_PATH}', Workflow.get_tool_vars_filename(t))
                for t in self.workflow.get_tool_dependencies(tool)
            ]


            bash = self.initial_variabes()
            bash += self.workflow.get_tool_bash_commands(
                tool=tool,
                validation=True,
                update_server_status=False,
                read_variables_from_command_line=False,
                variables_json_filename=None,
                variables_sh_filename_read = this_tool_previous_tools,
                variables_sh_filename_write = tool_vars_filename,
            )

            #print (f'TOOL ID: {tool_id}')
            #print (bash)

            run_afters[tool_id] = [BaseExecutor.INIT_STEP_NAME] # All tools run after PROCESSOBCINIT
            if tool_ids:
                run_afters[tool_id] += copy.copy(tool_ids)

            tool_ids.append(tool_id)
            previous_tools.append(tool_vars_filename)

            self.decomposed['steps'][tool_id] = {
                'bash': bash,
                'run_after': run_afters[tool_id],
                'type': 'tool_installation',
            }



        # STEP STEPS!
        previous_steps_vars = []
        step_inter_ids = []
        step_bash_scripts = []
        all_step_inter_ids = []

        for step in self.workflow.break_down_step_generator(
            enable_read_arguments_from_commandline=False,
            enable_save_variables_to_json=False,
            enable_save_variables_to_sh=False,
            break_down_on_tools=break_down_on_tools,
            ):

            step_id = step['id']
            count = step['count']
            bash = step['bash']
            step_inter_id = '{}__{}'.format(step_id, str(count))
            all_step_inter_ids.append(step_inter_id)
            step_inter_ids.append(step_inter_id)
            step_vars_filename = self.create_step_vars_filename(step_inter_id) # os.path.join('${OBC_WORK_PATH}', step_inter_id + '.sh')

            #print (f'step_inter_id: {step_inter_id}  Run afters: {step.get("run_after", [])}')

            # Mark first step
            if not 'first_step' in self.decomposed:
                self.decomposed['first_step'] = step_inter_id

            run_afters[step_inter_id] = [BaseExecutor.INIT_STEP_NAME] + tool_ids
            if step['run_after']:
                run_afters[step_inter_id] += step['run_after']

            #print (f'{step_inter_id} --> {step["run_after"]}')

            # Add declare. This should be first
            bash = self.workflow.declare_decorate_bash(bash, step_vars_filename)

            # Add all variables from previous tools
            load_tool_vars = ''
            for tool_filename in previous_tools:
                load_tool_vars += '. {}\n'.format(tool_filename)

            # Load all variables from previous steps
            load_step_vars = ''
            if step['run_after']:
                for run_after_step in step['run_after']:
                    load_step_vars += '. {}\n'.format(self.create_step_vars_filename(run_after_step))

            bash = self.initial_variabes() + load_tool_vars + self.load_file_with_input_parameters() + load_step_vars + self.load_obc_functions_bash + bash

            previous_steps_vars.append(step_vars_filename)

            #print (f'STEP ID {step_inter_id} ==> {step.get("tool_invocation")}')
            #print (bash)
            tool_invocation = step.get('tool_invocation')
            if tool_invocation:
                step_type = 'tool_invocation'
            else:
                step_type = 'simple'

            self.decomposed['steps'][step_inter_id] = {
                'bash': bash,
                'run_after': run_afters[step_inter_id],
                'type': step_type
            }
            if tool_invocation:
                self.decomposed['steps'][step_inter_id]['tool_to_call'] = tool_invocation



        # FINAL STEP
        bash = self.initial_variabes() + self.obc_final_step(previous_tools, previous_steps_vars)
        #print ('FINAL_STEP:')
        #print (bash)

        run_afters[BaseExecutor.FINAL_STEP_NAME] = [BaseExecutor.INIT_STEP_NAME] + tool_ids + all_step_inter_ids
        self.decomposed['steps'][BaseExecutor.FINAL_STEP_NAME] = {
            'bash': bash,
            'run_after': run_afters[BaseExecutor.FINAL_STEP_NAME],
            'type': 'final',
        }

        #print ('===FINAL====')
        #print (json.dumps(ret, indent=4))


        # Add DAG
        self.transitive_reduction(run_afters)
        self.decomposed['DAG'] = {node: list(self.DAG.predecessors(node)) for node in self.DAG.nodes()}

        # DOT visualization
        self.decomposed['DOT'] = self.dot_graph(self.decomposed['DAG'])

        #print ('DAG:')
        #print (self.decomposed['DOT'])


        #print ('DAG:')
        #print (json.dumps(self.decomposed['DAG'], indent=4))
        #print ('ENVIRONMENTS')
        #print (json.dumps(self.decomposed['environments'], indent=4))
        #print (break_down_on_tools)


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
            f.write((bash_patterns['init_report'] + bash_patterns['function_REPORT'] + bash_patterns['function_PARALLEL'])
                .replace('{{OBC_SERVER}}', str(self.workflow.obc_server))
                .replace('{{OBC_WORKFLOW_NAME}}', self.workflow.root_workflow['name'])
                .replace('{{OBC_WORKFLOW_EDIT}}', str(self.workflow.root_workflow['edit']))
            )

            # Set the OBC_REPORT_PATH parameter


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
    '''

    CWL_VERSION = "v1.0"

    COMMAND_LINE_CWL_PATTERN = r'''
class: CommandLineTool
cwlVersion: {CWL_VERSION}

baseCommand: ["{SHELL}", "{COMMAND_LINE_SH}"]

requirements:
   InitialWorkDirRequirement:
      listing:
         - class: File
           location: "{COMMAND_LINE_SH}"
   InlineJavascriptRequirement: {{}}
   EnvVarRequirement:
       envDef:
{ENVIRONMENT_VARIABLES}

inputs: {INPUTS}

{STDOUT}

outputs: {OUTPUTS}

'''

    WORKFLOW_CWL_PATTERN = r'''#!/usr/bin/env cwl-runner

cwlVersion: {CWL_VERSION}
class: Workflow

inputs: {INPUTS}

outputs: {OUTPUTS}

steps:
{STEPS}

'''

    STEP_PATTERN = r'''   {ID}:
      run: {CWL_FILENAME}
      in: {INPUTS}
      out: {OUTPUTS}

'''

    ENVIRONMENT_VARIABLE_PATTERN = '         {NAME}: "{VALUE}"'
    ENVIRONMENT_VARIABLE_PATTERN_INPUTS = '         {NAME}: $(inputs.{NAME})' # Passing environment variables from inputs

    # Not Using cwl.output.json : It should be declared in output: https://www.commonwl.org/v1.0/CommandLineTool.html#Output_binding
    OUTPUT_VARIABLES_PATTERN = r'''   {ID}:
      type: string
      outputBinding:
         glob: cwl2.output.json
         loadContents: true
         outputEval: $(JSON.parse(self[0].contents).{ID})
'''

    # This is a trick to allow absolute paths in glob
    OUTPUT_REPORT_PATTERN = '''
   OBC_FINAL_REPORT:
      type: File
      outputBinding:
         glob: $(runtime.outdir)/../../../../../../../../$(inputs.OBC_WORK_PATH)/{NICE_ID}.tgz
'''

    OUTPUT_VARIABLES_REPORT_WORKFLOW_PATTERN = r'''
   OBC_FINAL_REPORT:
      type: File
      outputSource: OBC_CWL_FINAL/OBC_FINAL_REPORT
'''

    OUTPUT_VARIABLES_WORKFLOW_PATTERN = r'''
   {ID}:
      type: string
      outputSource: OBC_CWL_FINAL/{ID}
'''

    INPUT_STRING_FROMCOMMANDLINE_PATTERN = r'''
   {ID}:
      type: string
      inputBinding:
         prefix: --{ID}=
         separate: false
'''
    INPUT_STRING_PATTERN = '   {ID}: string'

    def create_init_step_inputs_cwl(self, arguments):
        '''
        '''
        if not arguments:
            return '\n'

        return '\n'.join(self.INPUT_STRING_FROMCOMMANDLINE_PATTERN.format(ID=argument) for argument in arguments)

    def create_argument_input_cwl(self,):
        '''
        '''
        return '\n'.join(self.INPUT_STRING_PATTERN.format(ID=var) for var in self.unset_variables)


    def create_final_step_output_cwl(self, ):
        '''
        '''
        #if not self.workflow.output_parameters:
        #    return '[]'

        return '\n' + '\n'.join(self.OUTPUT_VARIABLES_PATTERN.format(ID=variable['id']) for variable in self.workflow.output_parameters) + '\n'

    def create_init_step_input_on_final_cwl(self, argument):
        '''
        '''
        return '         {ID}: {ID}'.format(ID=argument)

    def create_init_step_inputs_on_final_cwl(self, arguments):
        '''
        '''
        if not arguments:
            return ''

        return '\n' + '\n'.join(self.create_init_step_input_on_final_cwl(argument) for argument in arguments) + '\n'

    def create_final_workflow_output_cwl(self, ):
        '''
        outputs: ...
        '''
        # There is always an output which is the report
        #if not self.workflow.output_parameters:
        #    return '[]'

        return self.OUTPUT_VARIABLES_REPORT_WORKFLOW_PATTERN + '\n'.join(self.OUTPUT_VARIABLES_WORKFLOW_PATTERN.format(ID=variable['id']) for variable in self.workflow.output_parameters) + '\n'

    def create_final_workflow_input_cwl(self, arguments):
        '''
        '''
        if not arguments:
            return '[]'

        return '\n' + '\n'.join('   {ID}: string'.format(ID=argument) for argument in arguments) + '\n'

    def create_intermediate_step_cwl(self, inputs):
        '''
        '''
        return '\n'.join('         {X}: {X}/{X}'.format(X=x) for x in inputs) + '\n'


    def create_main_workflow_step(self, step_inter_id, inputs, input_parameters,):
        '''
        Create the steps in workflow.cwl
        '''

        # Create INPUTS
        if step_inter_id == 'OBC_CWL_INIT':
            INPUTS = self.create_init_step_inputs_on_final_cwl(input_parameters + self.unset_variables)
        else:
            INPUTS = self.create_init_step_inputs_on_final_cwl(self.unset_variables) + self.create_intermediate_step_cwl(inputs)

        # Create OUTPUTS
        if step_inter_id == 'OBC_CWL_FINAL':
                output_list = ['OBC_FINAL_REPORT', ] + [par['id'] for par in self.workflow.output_parameters]
                OUTPUTS = '[' + ', '.join(output_list) + ']'
        else:
            OUTPUTS = '[' + step_inter_id + ']'

        return self.STEP_PATTERN.format(
            ID=step_inter_id,
            CWL_FILENAME = self.create_step_inter_id_cwl_fn(step_inter_id),
            INPUTS=INPUTS,
            OUTPUTS=OUTPUTS,
        )

    def get_environment_variables_string(self, env_variables):
        '''
        '''

        ret = ''
        ret += '\n'.join(self.ENVIRONMENT_VARIABLE_PATTERN_INPUTS.format(NAME=var_name) for var_name in self.unset_variables)
        if ret:
            ret = ret + '\n'

        ret += '\n'.join(self.ENVIRONMENT_VARIABLE_PATTERN.format(NAME=name, VALUE=value) for name, value in env_variables.items())

        return ret


    def create_tool_id_sh_fn(self, tool_id):
        '''
        '''
        return '{}.sh'.format(tool_id)

    def create_tool_id_cwl_fn(self, tool_id):
        '''
        '''
        return '{}.cwl'.format(tool_id)

    def create_step_inter_id_sh_fn(self, step_inter_id):
        '''
        '''
        return '{}.sh'.format(step_inter_id)

    def create_step_inter_id_cwl_fn(self, step_inter_id):
        '''
        '''
        return '{}.cwl'.format(step_inter_id)


    def cwl_input(self, input_id):
        '''
        '''
        return '   {}:\n      type: File'.format(input_id)

    def cwl_inputs(self, input_ids):
        '''
        '''

        if not input_ids:
            return '[]'

        return '\n' + '\n'.join(map(self.cwl_input, input_ids)) + '\n'

    def cwl_output(self, output_id):
        '''
        '''
        return '\n   {}:\n      type: stdout'.format(output_id)


    def build(self, output, shell='bash', output_format='cwltargz', workflow_id=None):
        '''
        '''

        env_variables = self.get_environment_variables(workflow_id=workflow_id)
        env_variables_string = self.get_environment_variables_string(env_variables)
        # Get the essential variables that have not been set
        # We will set these variable from the input yml file

        previous_tools = []
        tool_ids = []
        files = {}
        run_afters = {}


        # Create init step
        # We read the input parameters of the pipelines from the command line
        input_parameters = list(self.workflow.input_parameter_values.keys())


        bash = Workflow.read_arguments_from_commandline(input_parameters)
        #bash += self.save_input_parameters(from_variable=True)
        bash += self.save_input_parameters(from_workflow=True)
        bash += self.obc_init_step()

        files['OBC_CWL_INIT.sh'] = bash

        files['OBC_CWL_INIT.cwl'] = self.COMMAND_LINE_CWL_PATTERN.format(
            CWL_VERSION=self.CWL_VERSION,
            SHELL=shell,
            COMMAND_LINE_SH='OBC_CWL_INIT.sh',
            INPUTS = self.create_init_step_inputs_cwl(input_parameters) + self.create_argument_input_cwl(), # self.cwl_inputs([]),
            OUTPUTS = self.cwl_output('OBC_CWL_INIT'),
            ENVIRONMENT_VARIABLES=env_variables_string,
            STDOUT='',
        )

        # Add tools
        for tool_index, tool in enumerate(self.workflow.tool_bash_script_generator()):

            tool_vars_filename = os.path.join('${OBC_WORK_PATH}', Workflow.get_tool_vars_filename(tool))
            tool_id = self.workflow.get_tool_dash_id(tool, no_dots=True)
            tool_id_sh_fn = self.create_tool_id_sh_fn(tool_id)

            bash = self.workflow.get_tool_bash_commands(
                tool=tool,
                validation=True,
                update_server_status=False,
                read_variables_from_command_line=False,
                variables_json_filename=None,
                variables_sh_filename_read = previous_tools,
                variables_sh_filename_write = tool_vars_filename,
            )
            files[tool_id_sh_fn] = bash

            if tool_ids:
                run_afters[tool_id] = copy.copy(tool_ids)
            tool_ids.append(tool_id)
            previous_tools.append(tool_vars_filename)


        # Add steps
        previous_steps_vars = []
        step_inter_ids = []

        for step in self.workflow.break_down_step_generator(
            enable_read_arguments_from_commandline=False,
            enable_save_variables_to_json=False,
            enable_save_variables_to_sh=False,
            ):

            step_id = step['id']
            count = step['count']
            bash = step['bash']
            step_inter_id = '{}__{}'.format(step_id, str(count))
            step_inter_ids.append(step_inter_id)
            step_vars_filename = self.create_step_vars_filename(step_inter_id) # os.path.join('${OBC_WORK_PATH}', step_inter_id + '.sh')

            if step['run_after']:
                run_afters[step_inter_id] = step['run_after']

            # Add declare. This should be first
            bash = self.workflow.declare_decorate_bash(bash, step_vars_filename)

            # Add all variables from previous tools
            load_tool_vars = ''
            for tool_filename in previous_tools:
                load_tool_vars += '. {}\n'.format(tool_filename)

            # Load all variables from: input_parameters + previous steps
            load_step_vars = ''
            if step['run_after']:
                for run_after_step in step['run_after']:
                    load_step_vars += '. {}\n'.format(self.create_step_vars_filename(run_after_step))

            bash = load_tool_vars + self.load_file_with_input_parameters() + load_step_vars + self.load_obc_functions_bash + bash

            previous_steps_vars.append(step_vars_filename)

            step_inter_id_sh_fn = self.create_step_inter_id_sh_fn(step_inter_id)
            files[step_inter_id_sh_fn] = bash

        # Create final step
        files['OBC_CWL_FINAL.sh'] = self.obc_final_step(previous_tools, previous_steps_vars)

        # Add INIT and FINAL in the graph
        self.add_init_and_final_in_graph('OBC_CWL_INIT', 'OBC_CWL_FINAL', run_afters, tool_ids, step_inter_ids)

        #Create DAG
        DAG = self.transitive_reduction(run_afters)

        steps_cwl = []
        for node in DAG.nodes:
            #print (node + ' --> ', list(DAG.predecessors(node)))
            predecessors = list(DAG.predecessors(node))
            fn = self.create_step_inter_id_cwl_fn(node) # The CWL individual file for each step

            if node == 'OBC_CWL_FINAL':
                INPUTS = self.cwl_inputs(predecessors)
                OUTPUTS = self.OUTPUT_REPORT_PATTERN.format(NICE_ID=env_variables['OBC_NICE_ID']) + self.create_final_step_output_cwl() # OBC_FINAL_OUTPUT = REPORT + WORKFLOW_OUTPUTS
                STDOUT = 'stdout: cwl2.output.json' # Normally this should be cwl.output.json . https://www.commonwl.org/v1.0/CommandLineTool.html#Output_binding
                                                    # It is not very clear how this feature will hold in future..
            else:
                INPUTS = self.cwl_inputs(predecessors)
                OUTPUTS = self.cwl_output(node)
                STDOUT = ''

            INPUTS = INPUTS + self.create_argument_input_cwl()

            cwl = self.COMMAND_LINE_CWL_PATTERN.format(
                CWL_VERSION=self.CWL_VERSION,
                SHELL=shell,
                COMMAND_LINE_SH=self.create_step_inter_id_sh_fn(node),
                INPUTS= INPUTS,
                OUTPUTS=OUTPUTS,
                ENVIRONMENT_VARIABLES=env_variables_string,
                STDOUT= STDOUT,
            )

            # We have already added the INIT
            if node != 'OBC_CWL_INIT':
                files[fn] = cwl

            steps_cwl.append(self.create_main_workflow_step(node, predecessors, input_parameters))

        # Create the filename of the workflow CWL
        if output:
            # Check the extension
            if os.path.splitext(output)[1].lower() == '.cwl':
                output_wf_fn = output
            else:
                output_wf_fn = output + '.cwl'
        else:
            output_wf_fn = 'workflow.cwl'

        files[output_wf_fn] = self.WORKFLOW_CWL_PATTERN.format(
            CWL_VERSION=self.CWL_VERSION,
            INPUTS=self.create_final_workflow_input_cwl(input_parameters + self.unset_variables), #  + self.create_argument_input_cwl(),
            OUTPUTS=self.create_final_workflow_output_cwl(),
            STEPS='\n'.join(steps_cwl),
        )

        # Create a file with input values
        content = ''
        for v in self.unset_variables:
            content += '# {}: "" # Please set this environment variable\n'.format(v)
        for k,v in self.workflow.input_parameter_values.items():
            if v['value'] is None:
                line = '\n# Please set this input parameter! \n'
                line +=  '# {}: "" # {}\n'.format(k, v['description'])
            else:
                line = '{}: "{}" # {}\n'.format(k, v['value'], v['description'])
            content += line
        files['inputs.yml'] = content


        if output_format == 'cwltargz':
            return self.create_targz(output, files)
        elif output_format == 'cwlzip':
            return self.create_zip(output, files)
        elif output_format == 'cwl':
            for filename, content in files.items():
                filename = os.path.join('del', filename)
                with open(filename, 'w') as f:
                    f.write(content)
        else:
            raise OBC_Executor_Exception('Unknown format: {}'.format(str(output_format)))



class AirflowExecutor(BaseExecutor):
    '''
    '''

    # https://airflow.readthedocs.io/en/stable/tutorial.html
    pattern = '''
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {{
    'owner': 'Airflow',
    'start_date': datetime(2015, 6, 1),
}}


dag = DAG(
    '{WORKFLOW_ID}', default_args=default_args, schedule_interval=None)

{BASH_OPERATORS}

{ORDER}

'''

    bash_operator_pattern = '''
{ID} = BashOperator(
    {ENVS}
    task_id='{ID}',
    bash_command=r"""
{BASH}
""",
    dag=dag)
'''

    def raw_jinja2(self, bash):
        '''
        remove jinja template from airflow
        '''
        return '{% raw %}\n' + bash + '\n{% endraw %}\n'


    def create_DAG(self, run_afters):
        '''
        Create an Airflow format of the transitive reduction of the graph
        '''
        #print (DAG.edges)
        DAG = self.transitive_reduction(run_afters)
        return '\n'.join('{} >> {}'.format(edge[0], edge[1]) for edge in DAG.edges)

    def build(self, output, output_format='airflow', workflow_id=None, obc_client=False):
        '''
        output: Name of output file. If None then the function returns a string
        output_format: it is not currently used
        workflow_id : The id to use in DAG. If None it will use "<workflow_name>__<workflow_edit>"
        obc_client : IF True, generate airflow for OBC client. This just sets the proper OBC_* directories
        '''

        d = self.get_environment_variables(obc_client=obc_client, workflow_id=workflow_id)

        if d:
            envs = 'env={},'.format(str(d))
        else:
            envs = ''

        # Create init step
        bash = self.obc_init_step()
        bash += self.save_input_parameters(from_workflow=True)
        bash = self.raw_jinja2(bash)

        airflow_bash = self.bash_operator_pattern.format(
            ID='OBC_AIRFLOW_INIT',
            BASH=bash,
            ENVS=envs,
        )

        init_operators = [airflow_bash]
        run_afters = {}

        # CREATE TOOL OPERATORS
        previous_tools = []
        tool_bash_operators = []
        tool_ids = []
        for tool_index, tool in enumerate(self.workflow.tool_bash_script_generator()):

            tool_vars_filename = os.path.join('${OBC_WORK_PATH}', Workflow.get_tool_vars_filename(tool))
            tool_id = self.workflow.get_tool_dash_id(tool, no_dots=True)

            bash = self.workflow.get_tool_bash_commands(
                tool=tool,
                validation=True,
                update_server_status=False,
                read_variables_from_command_line=False,
                variables_json_filename=None,
                variables_sh_filename_read = previous_tools,
                variables_sh_filename_write = tool_vars_filename,
            )
            bash = self.raw_jinja2(bash)
            airflow_bash = self.bash_operator_pattern.format(
                ID=tool_id,
                BASH=bash,
                ENVS=envs,
            )


            tool_bash_operators.append(airflow_bash)
            if tool_ids:
                run_afters[tool_id] = copy.copy(tool_ids)
            tool_ids.append(tool_id)

            previous_tools.append(tool_vars_filename)

        # CREATE STEP OPERATORS
        previous_steps_vars = []
        step_inter_ids = []
        step_bash_operators = []
        for step in self.workflow.break_down_step_generator(
            enable_read_arguments_from_commandline=False,
            enable_save_variables_to_json=False,
            enable_save_variables_to_sh=False,
            ):

            step_id = step['id']
            count = step['count']
            bash = step['bash']
            step_inter_id = '{}__{}'.format(step_id, str(count))
            step_inter_ids.append(step_inter_id)
            step_vars_filename = self.create_step_vars_filename(step_inter_id) # os.path.join('${OBC_WORK_PATH}', step_inter_id + '.sh')

            if step['run_after']:
                run_afters[step_inter_id] = step['run_after']

            # Add declare. This should be first
            bash = self.workflow.declare_decorate_bash(bash, step_vars_filename)

            # Add all variables from previous tools
            load_tool_vars = ''
            for tool_filename in previous_tools:
                load_tool_vars += '. {}\n'.format(tool_filename)

            # Load all variables from previous steps
            load_step_vars = ''
            if step['run_after']:
                for run_after_step in step['run_after']:
                    load_step_vars += '. {}\n'.format(self.create_step_vars_filename(run_after_step))

            bash = load_tool_vars + self.load_file_with_input_parameters() + load_step_vars + self.load_obc_functions_bash + bash

            previous_steps_vars.append(step_vars_filename)

            bash = self.raw_jinja2(bash)
            airflow_bash = self.bash_operator_pattern.format(
                ID = step_inter_id,
                BASH = bash,
                ENVS=envs,
            )
            step_bash_operators.append(airflow_bash)

        # Create final step
        bash = self.obc_final_step(previous_tools, previous_steps_vars)
        bash = self.raw_jinja2(bash) # Wrap in jinja2 verbatim . https://stackoverflow.com/questions/25359898/escape-jinja2-syntax-in-a-jinja2-template
        airflow_bash = self.bash_operator_pattern.format(
            ID='OBC_AIRFLOW_FINAL',
            BASH=bash,
            ENVS=envs,
        )
        final_operators = [airflow_bash]

        # Add INIT and FINAL in the run_afters graph
        self.add_init_and_final_in_graph('OBC_AIRFLOW_INIT', 'OBC_AIRFLOW_FINAL', run_afters, tool_ids, step_inter_ids)
        # Create dag
        DAG = self.create_DAG(run_afters)

        airflow_python = self.pattern.format(
            WORKFLOW_ID = workflow_id if workflow_id else self.workflow.root_workflow_id,
            BASH_OPERATORS = '\n'.join(init_operators + tool_bash_operators + step_bash_operators + final_operators),
            ORDER = DAG,
        )

        # Save output / Return
        if output:
            # Saving to a file

            # Checking if the output has a .py extension
            extension = os.path.splitext(output)[1]
            if extension.lower() != '.py':
                output += '.py'

            log_info('Saving airflow to {}'.format(output))
            with open(output, 'w') as f:
                f.write(airflow_python)
        else:
            # Return string
            return airflow_python


class ArgoExecutor(BaseExecutor):
    def __init__(self, workflow, executor_parameters=None):
        # Set defaults
        if not executor_parameters:
            executor_parameters = {}
        if 'workflow_name' not in executor_parameters:
            executor_parameters['workflow_name'] = ''
        if 'image_registry' not in executor_parameters:
            executor_parameters['image_registry'] = '127.0.0.1'
        if 'image_cache_path' not in executor_parameters:
            executor_parameters['image_cache_path'] = None
        if 'work_path' not in executor_parameters:
            executor_parameters['work_path'] = '/work'

        super().__init__(workflow, executor_parameters)

    def build(self, output, output_format='argo', workflow_id=None, obc_client=False):
        self.decompose(break_down_on_tools=True,)
        json_wf = json.dumps(self.decomposed)
        ret = cargo.pipeline(json_wf, self.workflow_name, self.image_registry, self.image_cache_path, self.work_path)
        print (ret)
        #a=1/0
        return ret


class JSONDAGExecutor(BaseExecutor):
    def build(self, output,
            output_format='jsondag',
            workflow_id=None,
            obc_client=False,
            break_down_on_tools=False,
        ):


        self.decompose(
            break_down_on_tools=break_down_on_tools,
        )
        return json.dumps(self.decomposed)


class NextflowExecutor(BaseExecutor):
    '''

    '''

    NEXTFLOW_TEMPLATE = '''
{PROCESSES}
'''

    # Source: https://www.nextflow.io/docs/latest/process.html#script
    # When you need to access a system environment variable in your script you have two options.
    # The first choice is as easy as defining your script block by using a single-quote string.
    NEXTFLOW_PROCESS_TEMPLATE = """
process {PROCESS_NAME} {{
{INPUT_CHANNELS}
{OUTPUT_CHANNELS}
    '''
{BASH}
    '''
}}
"""

    NEXTLOW_INPUT_TEMPLATE = '''
    input:
{INPUT_CHANNELS}
'''
    NEXTFLOW_INPUT_CHANNEL = "    val {VALUE} from {CHANNEL}\n"

    NEXTFLOW_OUTPUT_TEMPLATE = '''
    output:
    val '{VALUE}' into {CHANNELS}
'''

    @staticmethod
    def create_input_channels(channels):

        if not channels:
            return ''

        input_channels = ''.join(NextflowExecutor.NEXTFLOW_INPUT_CHANNEL.format(
            VALUE='VAL_{}'.format(channel),
            CHANNEL=channel)
        for channel in channels)

        return NextflowExecutor.NEXTLOW_INPUT_TEMPLATE.format(INPUT_CHANNELS=input_channels)

    @staticmethod
    def create_output_channels(channels):

        if not channels:
            return ''

        return NextflowExecutor.NEXTFLOW_OUTPUT_TEMPLATE.format(
            VALUE='OBC',
            CHANNELS = ', '.join(channels)
        )

    @staticmethod
    def bash_escape(bash):
        '''
        https://github.com/nextflow-io/nextflow/issues/2017
        '''

        return bash.replace('\\', '\\\\')

    @staticmethod
    def create_process(process_name, input_channels, output_channels, bash):
        return NextflowExecutor.NEXTFLOW_PROCESS_TEMPLATE.format(
            PROCESS_NAME= 'PR_' + process_name,
            INPUT_CHANNELS = NextflowExecutor.create_input_channels(input_channels),
            OUTPUT_CHANNELS = NextflowExecutor.create_output_channels(output_channels),
            BASH= NextflowExecutor.bash_escape(bash),
        )


    def initial_variabes(self,):
        ret  = 'export OBC_WORKFLOW_NAME={}\n'.format(self.workflow.root_workflow['name'])
        ret += 'export OBC_WORKFLOW_EDIT={}\n'.format(self.workflow.root_workflow['edit'])
        ret += 'export OBC_NICE_ID={}\n'.format(self.workflow.nice_id_global)
        ret += 'export OBC_SERVER={}\n\n'.format(self.workflow.obc_server)

        return ret


    def build(self, output, output_format='nextflow', workflow_id=None, obc_client=False):
        '''
        In nextflow processes we need to know all the forward and backward steps of every step.
        For this reason we keep everything in a dictionary and we export it after TR
        '''


        #variables = self.get_environment_variables(obc_client=obc_client, workflow_id=workflow_id)

        nextflow_process = {}

        # Create init step
        bash = self.initial_variabes() # Use this ONLY for NEXFLOW
        bash += self.obc_init_step()
        bash += self.save_input_parameters(from_workflow=True)


        nextflow_process['PROCESSOBCINIT'] = {'BASH': bash}

        run_afters = {'PROCESSOBCINIT': []}

        # CREATE TOOL OPERATORS Nextflow
        previous_tools = []
        #tool_bash_scripts = []
        tool_ids = []
        for tool_index, tool in enumerate(self.workflow.tool_bash_script_generator()):

            tool_vars_filename = os.path.join('${OBC_WORK_PATH}', Workflow.get_tool_vars_filename(tool))
            tool_id = self.workflow.get_tool_dash_id(tool, no_dots=True)

            bash = self.initial_variabes()
            bash += self.workflow.get_tool_bash_commands(
                tool=tool,
                validation=True,
                update_server_status=False,
                read_variables_from_command_line=False,
                variables_json_filename=None,
                variables_sh_filename_read = previous_tools,
                variables_sh_filename_write = tool_vars_filename,
            )

            nextflow_process[tool_id] = {'BASH': bash}

            run_afters[tool_id] = ['PROCESSOBCINIT'] # All tools run after PROCESSOBCINIT
            if tool_ids:
                run_afters[tool_id] += copy.copy(tool_ids)

            tool_ids.append(tool_id)

            #argo_dags.append(tool_id)

            previous_tools.append(tool_vars_filename)


        # CREATE STEP OPERATORS Nextflow
        previous_steps_vars = []
        step_inter_ids = []
        step_bash_scripts = []
        all_step_inter_ids = []
        for step in self.workflow.break_down_step_generator(
            enable_read_arguments_from_commandline=False,
            enable_save_variables_to_json=False,
            enable_save_variables_to_sh=False,
            ):

            step_id = step['id']
            count = step['count']
            bash = step['bash']
            step_inter_id = '{}__{}'.format(step_id, str(count))
            all_step_inter_ids.append(step_inter_id)
            step_inter_ids.append(step_inter_id)
            step_vars_filename = self.create_step_vars_filename(step_inter_id) # os.path.join('${OBC_WORK_PATH}', step_inter_id + '.sh')

            run_afters[step_inter_id] = ['PROCESSOBCINIT'] + tool_ids
            if step['run_after']:
                run_afters[step_inter_id] += step['run_after']

            # Add declare. This should be first
            bash = self.workflow.declare_decorate_bash(bash, step_vars_filename)

            # Add all variables from previous tools
            load_tool_vars = ''
            for tool_filename in previous_tools:
                load_tool_vars += '. {}\n'.format(tool_filename)

            # Load all variables from previous steps
            load_step_vars = ''
            if step['run_after']:
                for run_after_step in step['run_after']:
                    load_step_vars += '. {}\n'.format(self.create_step_vars_filename(run_after_step))

            bash = self.initial_variabes() + load_tool_vars + self.load_file_with_input_parameters() + load_step_vars + self.load_obc_functions_bash + bash

            previous_steps_vars.append(step_vars_filename)

            nextflow_process[step_inter_id] = {'BASH': bash}

        # Create final step
        bash = self.initial_variabes() + self.obc_final_step(previous_tools, previous_steps_vars)

        nextflow_process['PROCESSOBCFINAL'] = {'BASH': bash}

        run_afters['PROCESSOBCFINAL'] = ['PROCESSOBCINIT'] + tool_ids + all_step_inter_ids
        #print (run_afters)

        # Create the DAGS part of the YAML
        processes = []
        DAG = self.transitive_reduction(run_afters)
        for node in DAG.nodes():
            predecessors = list(DAG.predecessors(node))
            successors = list(DAG.successors(node))

            def create_channel_mame(node_from, node_to):
                return node_from + '__' + node_to

            input_channels = [create_channel_mame(x, node) for x in predecessors]
            output_channels = [create_channel_mame(node, x) for x in successors]

            # create_process(process_name, input_channels, output_channels, bash):
            processes.append(
                NextflowExecutor.create_process(node, input_channels, output_channels, nextflow_process[node]['BASH'])
            )


        nextflow = self.NEXTFLOW_TEMPLATE.format(
            PROCESSES = '\n\n'.join(processes),
        )

        #print (nextflow)

        return nextflow



class SnakemakeExecutor(BaseExecutor):
    '''
    '''


    RULE_TEMPLATE = '''

rule {RULE_ID}:
{INPUT}
{OUTPUT}
{SHELL}

'''

    @staticmethod
    def create_input_output(input_output, variables):
        if not variables:
            return '    # no {}'.format(input_output)

        ret = '    {}:\n'.format(input_output)
        ret += '        ' + ', '.join([repr(x) for x in variables]) + '\n'

        return ret


    def create_shell(self, shell, node):

        touch = '\ntouch {}\n'.format(self.create_rule_filename(node))

        ret = '    shell:\n'
        #ret += '        ' + repr(shell + touch) + '\n'
        ret +=  '        r"""\n'
        ret += shell.replace('{', '{{').replace('}', '}}')
        ret += touch
        ret +=  '        """\n'

        return ret

    def create_rule_filename(self, rule):
       return os.path.join(self.OBC_DONE_DIR, rule + '.done' )

    def build(self, output, output_format='snakemake', workflow_id=None, obc_client=False):


        #self.RANDOM_ID = 'OBC_DONE_DIR'
        self.RANDOM_ID = Workflow.create_nice_id()
        #self.OBC_DONE_DIR = os.path.join('${OBC_WORK_PATH}', self.RANDOM_ID)
        self.OBC_DONE_DIR =  'OBC_' + self.RANDOM_ID


        snakemake_rules = {}

        # Create init step
        bash = 'mkdir -p {}\n'.format(self.OBC_DONE_DIR)
        bash += self.initial_variabes() # Load OBC_WORKFLOW, OBC
        bash += self.obc_init_step()
        bash += self.save_input_parameters(from_workflow=True)


        snakemake_rules['RULEOBCINIT'] = {'BASH': bash}

        run_afters = {'RULEOBCINIT': []}

        # CREATE TOOL OPERATORS Snakemake
        previous_tools = []
        tool_ids = []
        for tool_index, tool in enumerate(self.workflow.tool_bash_script_generator()):

            tool_vars_filename = os.path.join('${OBC_WORK_PATH}', Workflow.get_tool_vars_filename(tool))
            tool_id = self.workflow.get_tool_dash_id(tool, no_dots=True)

            bash = self.initial_variabes()
            bash += self.workflow.get_tool_bash_commands(
                tool=tool,
                validation=True,
                update_server_status=False,
                read_variables_from_command_line=False,
                variables_json_filename=None,
                variables_sh_filename_read = previous_tools,
                variables_sh_filename_write = tool_vars_filename,
            )

            snakemake_rules[tool_id] = {'BASH': bash}

            run_afters[tool_id] = ['RULEOBCINIT'] # All tools run after PROCESSOBCINIT
            if tool_ids:
                run_afters[tool_id] += copy.copy(tool_ids)

            tool_ids.append(tool_id)

            previous_tools.append(tool_vars_filename)

        # CREATE STEP OPERATORS Snakemake
        previous_steps_vars = []
        step_inter_ids = []
        step_bash_scripts = []
        all_step_inter_ids = []
        for step in self.workflow.break_down_step_generator(
            enable_read_arguments_from_commandline=False,
            enable_save_variables_to_json=False,
            enable_save_variables_to_sh=False,
            ):

            step_id = step['id']
            count = step['count']
            bash = step['bash']
            step_inter_id = '{}__{}'.format(step_id, str(count))
            all_step_inter_ids.append(step_inter_id)
            step_inter_ids.append(step_inter_id)
            step_vars_filename = self.create_step_vars_filename(step_inter_id) # os.path.join('${OBC_WORK_PATH}', step_inter_id + '.sh')

            run_afters[step_inter_id] = ['RULEOBCINIT'] + tool_ids
            if step['run_after']:
                run_afters[step_inter_id] += step['run_after']

            # Add declare. This should be first
            bash = self.workflow.declare_decorate_bash(bash, step_vars_filename)

            # Add all variables from previous tools
            load_tool_vars = ''
            for tool_filename in previous_tools:
                load_tool_vars += '. {}\n'.format(tool_filename)

            # Load all variables from previous steps
            load_step_vars = ''
            if step['run_after']:
                for run_after_step in step['run_after']:
                    load_step_vars += '. {}\n'.format(self.create_step_vars_filename(run_after_step))

            bash = self.initial_variabes() + load_tool_vars + self.load_file_with_input_parameters() + load_step_vars + self.load_obc_functions_bash + bash

            previous_steps_vars.append(step_vars_filename)

            snakemake_rules[step_inter_id] = {'BASH': bash}

        # Create final step snakemake
        bash = self.initial_variabes() + self.obc_final_step(previous_tools, previous_steps_vars)

        snakemake_rules['RULEOBCFINAL'] = {'BASH': bash}

        run_afters['RULEOBCFINAL'] = ['RULEOBCINIT'] + tool_ids + all_step_inter_ids
        #print (run_afters)

        # Create the DAGS part of the YAML
        rules = [SnakemakeExecutor.RULE_TEMPLATE.format(
            RULE_ID = 'all',
            INPUT = SnakemakeExecutor.create_input_output('input', [self.create_rule_filename('RULEOBCFINAL')]),
            OUTPUT = SnakemakeExecutor.create_input_output('output', []),
            SHELL = '',
        )]
        DAG = self.transitive_reduction(run_afters)
        for node in DAG.nodes():
            predecessors = list(DAG.predecessors(node))
            #successors = list(DAG.successors(node))

            rules.append(SnakemakeExecutor.RULE_TEMPLATE.format(
                RULE_ID = node,
                INPUT = SnakemakeExecutor.create_input_output('input',  [self.create_rule_filename(x) for x in predecessors]),
                OUTPUT = SnakemakeExecutor.create_input_output('output',  [self.create_rule_filename(node)]),
                SHELL = self.create_shell(snakemake_rules[node]['BASH'], node),
            ))

        snakemake = '\n\n'.join(rules)
        #print (snakemake)


        return snakemake

def create_bash_script(workflow_object, server, output_format,
        workflow_id=None,
        obc_client=False,
        break_down_on_tools=False,
        executor_parameters=None,
    ):
    '''
    convenient function called by server
    server: the server to report to
    workflow_id: The ID of the workflow. Used in airflow
    obc_client: True/False. Do we have to generate a script for the obc client?
    break_down_on_tools : See decomposer
    executor_parameters: Dictionary with options per implementation of workflow creator.
    '''

    args = type('A', (), {
        'server': server,
        'insecure': False,
    })

    setup_bash_patterns(args)

    # Setup global variables
    g['silent'] = True

    if output_format == 'sh':
        w = Workflow(workflow_object = workflow_object, askinput='BASH', obc_server=server)
        e = LocalExecutor(w)
        return e.build(output=None)
    elif output_format == 'jsondag':
        w = Workflow(workflow_object = workflow_object, askinput='NO', obc_server=server, workflow_id=workflow_id)
        e = JSONDAGExecutor(w)
        return e.build(
            output=None,
            output_format='jsondag',
            workflow_id=workflow_id,
            obc_client=obc_client,
            break_down_on_tools=break_down_on_tools,
        )
    elif output_format in ['cwltargz', 'cwlzip']:
        w = Workflow(workflow_object = workflow_object, askinput='NO', obc_server=server, workflow_id=workflow_id)
        e = CWLExecutor(w)
        return e.build(output=None, output_format=output_format, workflow_id=workflow_id)
    elif output_format in ['airflow']:
        w = Workflow(workflow_object = workflow_object, askinput='NO', obc_server=server, workflow_id=workflow_id)
        e = AirflowExecutor(w)
        return e.build(output=None, output_format='airflow', workflow_id=workflow_id, obc_client=obc_client)
    elif output_format in ['argo']:
        w = Workflow(workflow_object = workflow_object, askinput='NO', obc_server=server, workflow_id=workflow_id)
        e = ArgoExecutor(w, executor_parameters)
        return e.build(output=None, output_format='argo', workflow_id=workflow_id, obc_client=obc_client)
    elif output_format in ['nextflow']:
        w = Workflow(workflow_object = workflow_object, askinput='NO', obc_server=server, workflow_id=workflow_id)
        e = NextflowExecutor(w)
        return e.build(output=None, output_format='nextflow', workflow_id=workflow_id, obc_client=obc_client)
    elif output_format in ['snakemake']:
        w = Workflow(workflow_object = workflow_object, askinput='NO', obc_server=server, workflow_id=workflow_id)
        e = SnakemakeExecutor(w)
        return e.build(output=None, output_format='snakemake', workflow_id=workflow_id, obc_client=obc_client)


    else:
        raise OBC_Executor_Exception('Error: 6912: Unknown output format: {}'.format(str(output_format)))



if __name__ == '__main__':
    '''
    Example:
    python executor.py -W workflow.json
    '''

    runner_options = ['sh', 'cwl', 'cwltargz', 'cwlzip', 'airflow']

    parser = argparse.ArgumentParser(description='OpenBio-C workflow executor')

    parser.add_argument('-W', '--workflow', dest='workflow_filename', help='JSON filename of the workflow to run', required=True)
    parser.add_argument('-S', '--server', dest='server', help='The Server\'s url. It should contain http or https', default='https://www.openbio.eu/platform')
    parser.add_argument('-F', '--format', dest='format', choices=runner_options,
        help='Select the output format of the workflow. Options are:\n  ' \
'sh: Create a shell script (default)\n  ' \
'cwl: Create a set of Common Workflow Language files\n' \
'cwltargz: Same as cwl but create a tar.gz file\n' \
'cwlzip: Same as cwl but create a zip file\n' \
'airflow: Create airflow bashoperator scripts\n' \
'argo: Create ARGO workflow (YAML)\n'
'nextflow: Create NEXTFLOW workflow\n'
'snakemake: Create a Snakemake workflow\n',
        default='sh')
    parser.add_argument('-O', '--output', dest='output', help='The output filename. default is script.sh, workflow.cwl and workflow.tar.gz, depending on the format', default='script')
    parser.add_argument('--insecure', dest='insecure', help="Pass insecure option (-k) to curl", default=False, action="store_true")
    parser.add_argument('--silent', dest='silent', help="Do not print logging info", default=False, action="store_true")
    parser.add_argument('--askinput', dest='askinput',
        help="Where to get input parameters from. Available options are: 'JSON', during convert JSON to BASH, 'BASH' ask for input in bash, 'NO' do not ask for input.",
        default='JSON', choices=['JSON', 'BASH', 'NO'])
    parser.add_argument('--OBC_DATA_PATH', dest='OBC_DATA_PATH', required=False, help="Set the ${OBC_DATA_PATH} environment variable. This is where the data are stored")
    parser.add_argument('--OBC_TOOL_PATH', dest='OBC_TOOL_PATH', required=False, help="Set the ${OBC_TOOL_PATH} environment variable. This is where the tools are installed")
    parser.add_argument('--OBC_WORK_PATH', dest='OBC_WORK_PATH', required=False, help="Set the ${OBC_WORK_PATH} environment variable. This is where the tools are installed")

    args = parser.parse_args()

    if args.OBC_DATA_PATH:
        g['OBC_DATA_PATH'] = args.OBC_DATA_PATH
    if args.OBC_TOOL_PATH:
        g['OBC_TOOL_PATH'] = args.OBC_TOOL_PATH
    if args.OBC_WORK_PATH:
        g['OBC_WORK_PATH'] = args.OBC_WORK_PATH

    setup_bash_patterns(args)

    # Setup global variables
    if args.silent:
        g['silent'] = True

    # Do not ask input values if the format is CWL or airflow
    if args.format in ['cwl', 'cwltargz', 'cwlzip', 'airflow']:
        args.askinput = 'NO'

    w = Workflow(args.workflow_filename, askinput=args.askinput)

    ##################
    # python executor.py -W workflow.json
    ###############


    if args.format == 'sh':
        e = LocalExecutor(w)
        if args.output == 'script':
            args.output = 'script.sh'
        e.build(output = args.output)
    elif args.format in ['cwl', 'cwltargz', 'cwlzip']:
        e = CWLExecutor(w)
        if args.output == 'script':
            args.output = 'workflow.' + {'cwl': 'cwl', 'cwltargz': 'tar.gz', 'cwlzip': 'zip'}[args.format]
        e.build(output = args.output, output_format=args.format)
    elif args.format in ['airflow']:
        e = AirflowExecutor(w)
        e.build(output = args.output)
    elif args.format in ['argo']:
        e = ArgoExecutor(w)
        e.build(output = args.output)
    elif args.format in ['nextflow']:
        e = NextflowExecutor(w)
        e.build(output=args.output)
    elif args.format in ['snakemake']:
        e = SnakemakeExecutor(w)
        e.build(output=args.output)
    else:
        raise OBC_Executor_Exception('Unknown format: {}'.format(args.format))






