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

test edit
'''

if __name__ != '__main__':
    raise Exception('Do not import this file')

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
#from threading import Thread

# https://stackoverflow.com/questions/47163807/concurrency-with-aiohttp-server?rq=1
logging.getLogger('aiohttp').setLevel(logging.DEBUG)
logging.getLogger('aiohttp').addHandler(logging.StreamHandler(sys.stderr))

lodger = {}



# Execution function return the errorcode and the output



def execute_shell(command):
    '''
    Executes a command in shell
    '''
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        shell= True)

    (stdout,stderr) = process.communicate()
    #print(stdout.decode())
    print(f'[{cmd!r} exited with {process.returncode}]')
    return {
        'stdout' : stdout,
        'stderr' : stderr,
        'errcode' : process.returncode,
    }


def docker_build_cmd(this_id):
    '''
    '''
    return f'docker build --no-cache -t openbioc/{this_id} .'

def docker_remove_failed_builds_cmd():
    '''
    '''
    return f'docker rmi -f $(docker images -f "dangling=true" -q)'


def bash_script_filename(this_id):
    '''
    '''
    return f'bashscript_{this_id}.sh'

def execute_docker_build(this_id, bash):
    # I make a file and add the bashscript on it
    with open("bashscript.sh", "w+") as bashscript:
        bashscript.write(bash)




def execution(this_id,bash,flag):
    # SHOW UNTAGGED IMAGES (DANGLING) docker images --filter "dangling=true"
    '''
        this_id : take the id which we create from request and use it to save the image with this id
        bash : the bash commands from request 
        flag : is boolean if True will make the build else will remove the failed images from docker
    '''
    if flag:
        cmd = f'docker build --no-cache -t openbioc/{this_id} .'
    else:
        cmd = f'docker rmi -f $(docker images -f "dangling=true" -q)'
	#I use the id to give a name in the image
	#print(f'the {this_id} start the build ......') 


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
        #print(bash)
        new_id = get_uuid()
        message = {
            'action': 'validate',
            'status': 'pending',
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

        if not this_id in lodger:
            return fail(f'id: "{this_id}" was not found')

        return success(lodger[this_id])

    else:
        return fail(f'Unknown action: {action}')

    
    #web.web_logger.debug('Hello')

    # Create JSON response 
    # https://docs.aiohttp.org/en/stable/web_quickstart.html#json-response
    responce_data = {
        'some': 'data',
        'success': success,
        'error': error,
    }
    return web.json_response(responce_data)

    # Create TEXT response:
    #return web.Response(text="Hello from post")



def init_web_app(message_queue, ):

    '''
    create an Application instance and register the request handler on a particular HTTP method and path:
    '''
    #asyncio.set_event_loop(asyncio.new_event_loop())

    app = web.Application()

    # Web Applications can have context 
    # https://stackoverflow.com/questions/40616145/shared-state-with-aiohttp-web-server 
    app['message_queue'] = message_queue

    app.add_routes([
        web.get('/', hello),
        web.post('/post', post_handler),
    ])
    
    #After that, run the application by run_app() call:
    web.run_app(app)

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

            this_id = task['id']
            print (f'WORKER: {w_id}. RECEIVED: {this_id}')
            # the executions start and the images are called such as unique id from post
            errcode = execution(this_id,task['bash'],True)
            lodger[this_id]['status'] = 'submitted'
            time.sleep(random.randint(1,5))
            # errcode = 0 means success
            # errcode =! something goes wrong
            if errcode == 0 :
                lodger[this_id]['status'] = 'done'
            else :
                lodger[this_id]['status'] = 'failed'
                execution(this_id,'mpah',False)

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

if __name__ == '__main__':
    message_queue = Thread_queue()
#    worker_thread = threading.Thread(target=worker, args=(message_queue, 55),)
#    worker_thread.start()
    setup_worker_threads(message_queue, 10)


    init_web_app(message_queue)



