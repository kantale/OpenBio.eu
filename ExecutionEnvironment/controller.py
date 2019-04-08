'''
https://docs.aiohttp.org/en/stable/web_quickstart.html#run-a-simple-web-server

### Test to see if alive:
curl -X POST http://0.0.0.0:8080/post

### Send POST data
curl -d "param1=value1&param2=value2" -X POST http://0.0.0.0:8080/post


### Send JSON data in file: test_1.json via POST:
curl --header "Content-Type: application/json" --request POST -d @test_1.json http://0.0.0.0:8080/post 

BASIC TERMINOLOGY:
CONTROLLER: aiohttp, or flask, django server listening for actions
WORKER: checks if there is any pending job/request and handles it.
SUBMITTER: client.py . Submits jobs to CONTROLLER and queries the CONTROLLER regarding the progress of these jobs

# RUN docker os non-root 
https://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo
sudo groupadd docker 
sudo usermod -aG docker kantale 
sudo systemctl restart docker 
'''

if __name__ != '__main__':
    raise Exception('Do not import this file')

import os
import sys
import json
import time
import uuid
import random
import asyncio
import logging
import threading
import subprocess

from queue import Queue as Thread_queue #  

from aiohttp import web
import aiohttp_cors
#from threading import Thread

# https://stackoverflow.com/questions/47163807/concurrency-with-aiohttp-server?rq=1
logging.getLogger('aiohttp').setLevel(logging.DEBUG)
logging.getLogger('aiohttp').addHandler(logging.StreamHandler(sys.stderr))

lodger = {}

dockerfile_content_template = '''
#Using ENTRYPOINT

# FROM ubuntu:latest

# RUN  apt-get update \
#  && apt-get install unzip \ 
#  && apt-get install -y wget

# ADD bashscript.sh /root/ 

# RUN chmod +x /root/bashscript.sh  

# ENTRYPOINT ["/root/bashscript.sh"]



#Using CMD

FROM {ostype}

RUN  apt-get update \
  && apt-get install unzip \ 
  && apt-get install -y wget

ADD {bashscript_path} /root/ 


RUN cd /root; chmod +x {bashscript_filename} ; /bin/bash {bashscript_filename}
'''

execution_directory = 'executions'

def execute_shell(command):
    '''
    Executes a command in shell
    dummy: Do nothing. Return a success-like message
    '''

    # if dummy:
    #     return {
    #         'stdout' : 'DUMMY STDOUT',
    #         'stderr' : 'DUMMY STDERR',
    #         'errcode' : 0,
    #     }

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        shell= True)
    # Read every line in stdout and print in controller
    '''
    https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
    '''

    for line in iter(process.stdout.readline, b''):
        print(line)

    
    (stdout,stderr) = process.communicate()

    print(f'[{command!r} exited with {process.returncode}]')
    return {
        'stdout' : stdout,
        'stderr' : stderr,
        'errcode' : process.returncode,
    }



def docker_build_cmd(this_id, Dockerfile_filename):
    '''
    https://docs.docker.com/engine/reference/commandline/build/

    --file , -f         Name of the Dockerfile (Default is ‘PATH/Dockerfile’)
    '''
    return f'docker build --no-cache -t openbioc/{this_id} -f {Dockerfile_filename} .'

def docker_remove_failed_builds_cmd():
    '''
    '''
    return f'docker rmi -f $(docker images -f "dangling=true" -q)'


def create_bash_script_filename(this_id):
    '''
    '''
    return f'bashscript_{this_id}.sh', os.path.join(execution_directory, f'bashscript_{this_id}.sh')


def create_Dockerfile_filename(this_id):
    '''
    '''

    return os.path.join(execution_directory, f'{this_id}.Dockerfile')

def create_Dockerfile_content(ostype, bashscript_path,bashscript_filename):
    return dockerfile_content_template.format(
        ostype= ostype,
        bashscript_path = bashscript_path,
        bashscript_filename=bashscript_filename
        )



def execute_docker_build(this_id, ostype, bash):
    '''
    make a file and add the bashscript on it
    '''

    bash_script_filename,bash_script_path = create_bash_script_filename(this_id)
    Dockerfile_filename = create_Dockerfile_filename(this_id)

    # Save bash_script 
    with open(bash_script_path, 'w') as bash_script_f:
        bash_script_f.write(bash)

    # Save Dockerfile
    with open(Dockerfile_filename, 'w') as Dockerfile_f:
        Dockerfile_f.write(create_Dockerfile_content(ostype, bash_script_path,bash_script_filename))

    print (f'Created bash file: {bash_script_filename}')
    print (f'Created Dockerfile: {Dockerfile_filename}')


    command = docker_build_cmd(this_id, Dockerfile_filename)
    print (f'Executing command: {command}')

    return execute_shell(command)




def get_uuid():
    '''
    Get a unique uuid4 id
    str(uuid.uuid4()).split('-')[-1]
    '''
    return str(uuid.uuid4())

async def hello(request):
    '''
    A request handler must be a coroutine that accepts a Request instance as its only parameter and returns a Response instance:
    '''
    return web.Response(text="Hello, world")

def fail(message):
    responce_data = {
        'success': False,
        'error_message': message
    }

    return web.json_response(responce_data)

def success(d):
    d['success'] : True
    return  web.json_response(d)

async def post_handler(request):
    '''
    Post handler
    https://docs.aiohttp.org/en/stable/web_reference.html
    '''

    # Access the application context:
    # request.app['lodger']

    # Receive arbitrary post data
    #data = await request.post()

    # Receive JSON data 

    try:
        data = await request.json()
    except json.decoder.JSONDecodeError as e:
        return fail('Input not a JSON')

    if not 'action' in data:
        return fail('key: "action" not present')
    print(data)
    message_queue = request.app['message_queue']
    action = data['action']
    if action == 'validate':
        '''
        data = {
            'action': 'validate',
            'bash' : 'mplah'
        }
        '''
        if not 'bash' in data:
            return fail('key: "bash" not present')
        bash = data['bash']
        if not 'ostype' in data:
            return fail('key: "ostype" not present')
        ostype = data['ostype']
        #print(bash)
        new_id = get_uuid()
        message = {
            'action': 'validate',
            'status': 'pending',
            'ostype': ostype,
            'bash': bash,
            'id': new_id,
        }
        lodger[new_id] = message
        message_queue.put(message)
        return success({'id': new_id})

    elif action == 'query':
        if not 'id' in data:
            return fail('key: "id" not present')
        this_id = data['id']
        if not str(this_id) in lodger:
            return fail(f'id: "{this_id}" was not found')

        return success(lodger[this_id])

    else:
        return fail(f'Unknown action: {action}')

    
    #web.web_logger.debug('Hello')

    # Create JSON response 
    # https://docs.aiohttp.org/en/stable/web_quickstart.html#json-response
    response_data = {
        'some': 'data',
        'success': success,
        'error': error,
    }
    return web.json_response(response_data)

    # Create TEXT response:
    #return web.Response(text="Hello from post")



def init_web_app(message_queue, port=8080):

    '''
    create an Application instance and register the request handler on a particular HTTP method and path:
    '''
    #asyncio.set_event_loop(asyncio.new_event_loop())

    app = web.Application()

    # `aiohttp_cors.setup` returns `aiohttp_cors.CorsConfig` instance.
    # The `cors` instance will store CORS configuration for the
    # application.
    cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions( # TODO: CHANGE "*" To server IP
            allow_credentials=True,
            expose_headers=('access-control-allow-origin','content-type','x-csrftoken'),
            allow_headers=('access-control-allow-origin','content-type','x-csrftoken'),
        )
    })

    # Web Applications can have context 
    # https://stackoverflow.com/questions/40616145/shared-state-with-aiohttp-web-server 
    app['message_queue'] = message_queue

    app.add_routes([
        web.get('/', hello),
        web.post('/post', post_handler),
    ])

    for route in list(app.router.routes()):
        cors.add(route)

    #resource = cors.add(app.router.add_resource("/post"))
    #cors.add(route)
#    route = cors.add(
#    resource.add_route("POST", post_handler), {
#        # "http://client.example.org" 
#        "*": aiohttp_cors.ResourceOptions(
#            allow_credentials=True,
#            expose_headers='*',
#            allow_headers='*',
#            #expose_headers=("Access-Control-Allow-Origin",),
#            #allow_headers=("Access-Control-Allow-Origin", "Content-Type: application/json"),
#            max_age=3600,
#        )
#        }
#    )
    
    #After that, run the application by run_app() call:
    web.run_app(app, port=port)

    #runner = web.AppRunner(app)
    #return runner
    #await runner.setup()
    #site = web.TCPSite(runner, '0.0.0.0', 8080)
    #await site.start()


    #OR, create a handler if we are running in a thread
    #handler = app.make_handler() # DeprecationWarning: Application.make_handler(...) is deprecated, use AppRunner API instead 
    #return handler




def worker(message_queue, w_id):
    '''
    w_id: worker id
    '''
    
    print (f'Worker: {w_id} starting..')

    while True:
        if message_queue.empty():
            # do nothing
            pass
        else:
            task = message_queue.get()
            print(task)
            this_id = task['id']
            bash = task['bash']
            ostype = task['ostype']

            print (f'WORKER: {w_id}. RECEIVED: {this_id}')
            # the executions start and the images are called such as unique id from post

            lodger[this_id]['status'] = 'submitted'
            result = execute_docker_build(this_id,ostype, bash)
            print ('RESULT FROM execute_docker_build:')
            print (result)

            
            #time.sleep(random.randint(1,5))
            time.sleep(1)
            
            # errcode = 0 means success
            # errcode =! something goes wrong
            if result['errcode'] == 0:
                lodger[this_id]['status'] = 'done'
            else:
                lodger[this_id]['status'] = 'failed'
                #execution(this_id,'mpah',False)

            lodger[this_id]['stdout'] = result['stdout'].decode()
            lodger[this_id]['stderr'] = result['stderr'].decode()
            lodger[this_id]['errcode'] = result['errcode']


            #print(lodger)
            print (f'WORKER: {w_id}. DONE: {this_id}')


        time.sleep(1)

#init_web_app()
#start_init_web_app_thread()

#message_queue = Thread_queue()

#loop = asyncio.new_event_loop()
#asyncio.set_event_loop(loop)


#t = threading.Thread(target=create_server_for_web_app, args=(init_web_app(message_queue),))
#t = threading.Thread(target=init_web_app, args=(message_queue, ),)
#t = threading.Thread(target=thr, args=(message_queue, ),)
#t.start()

def setup_worker_threads(message_queue, n):
    '''
    n = number of threads

    '''

    threads = [threading.Thread(target=worker, args=(message_queue, i+1),) for i in range(n)]
    for thread in threads:
        thread.start()

import socket, errno

def check_if_port_is_used(port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    used = False

    try:
        s.bind(("0.0.0.0", port))
    except socket.error as e:
        used = True
        if e.errno == errno.EADDRINUSE:
            print(f"Port {port} is already in use")
        else:
            # something else raised the socket.error exception
            print(e)
    finally:
        s.close()

    return used

if __name__ == '__main__':
    message_queue = Thread_queue()
#    worker_thread = threading.Thread(target=worker, args=(message_queue, 55),)
#    worker_thread.start()
    setup_worker_threads(message_queue, 2)

    if check_if_port_is_used(8080):
        print ('Running on port 8081')
        init_web_app(message_queue, port=8081)
    else:
        init_web_app(message_queue, port=8080)



