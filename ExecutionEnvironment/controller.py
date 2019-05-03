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
import requests
import threading
import subprocess
import docker
from queue import Queue as Thread_queue #  
# import stats
from aiohttp import web
import aiohttp_cors
#from threading import Thread

# https://stackoverflow.com/questions/47163807/concurrency-with-aiohttp-server?rq=1
logging.getLogger('aiohttp').setLevel(logging.DEBUG)
logging.getLogger('aiohttp').addHandler(logging.StreamHandler(sys.stderr))


dockerfile_content_template = '''
#Using ENTRYPOINT

FROM {ostype}

RUN  apt-get update \
  && apt-get install unzip \
  && apt-get install -y wget

ADD {bashscript_filename} /root/

RUN chmod +x /root/{bashscript_filename}

ENTRYPOINT ["/root/{bashscript_filename}"]

CMD ["./{bashscript_filename}"]




#Using CMD

# FROM {ostype}

# RUN  apt-get update \
#   && apt-get install unzip \ 
#   && apt-get install -y wget

# ADD {bashscript_path} /root/ 


# RUN cd /root; chmod +x {bashscript_filename} ; /bin/bash {bashscript_filename}
'''

execution_directory = 'executions'
instance_settings = {} # Will be set later 

class OBC_Controller_Exception(Exception):
    '''
    Custom OBC Exception
    '''
    pass

def docker_build_image(Dockerfile_filename,image_name):
    '''
    Executes a command in shell
    dummy: Do nothing. Return a success-like message
    Changed: Build the image using build command from docker_py.
    When the build finished the run to show the results from image start
    '''

    # if dummy:
    #     return {
    #         'stdout' : 'DUMMY STDOUT',
    #         'stderr' : 'DUMMY STDERR',
    #     }

    # process = subprocess.Popen(
    #     command,
    #     stdout=subprocess.PIPE, 
    #     stderr=subprocess.PIPE, 
    #     shell= True)

    docker_client = docker.from_env()
    # build image usind SDK and take execution time

    build_start = time.time()
    print(Dockerfile_filename)
    # (stdout,stderr) = process.communicate()
    print(os.getcwd()+'/executions')
    set_worker_for_stats(image_name)
    # time.sleep(5)
    image_build = docker_client.images.build(path=os.getcwd()+'/executions',
        dockerfile=f'{Dockerfile_filename}' , tag=f'{image_name}')

    build_end = time.time()

    execution_time = build_end - build_start
    print(f'Image : {image_build} created in {execution_time}sec.')
    
    # ret = {
    #     'stdout' : stdout,
    #     'stderr' : stderr,
    #     'errcode' : process.returncode,
    #     'execution_time' : execution_time,
    #     'disk_usage' :disk_usage,
    #     'cpu_usage': stats_usages['cpu_stats'],
    #     'memory_usage': stats_usages['memory_stats'],
    #     'networks': stats_usages['network_stats'],
    # }

    #print ('EXCUTE SHELL ABOUT TO RETURN:')
    #print (ret)
    return docker_run_image(docker_client,image_name,execution_time)

def docker_run_image(docker_client,image_name,execution_time):
    '''
    https://github.com/docker/docker-py/blob/master/docker/errors.py
    Run the builded image
    if run is failed we use try , except and we take the error code and stderr from the error 
    '''
    result={}
    disk_usage = image_disk_usage(docker_client,image_name)
    try:
        result['stderr']= None
        result['errcode']= 0
        result['stdout'] = docker_client.containers.run(image_name,stdout=True, stderr=True).decode()
        return {
            'stdout' : result['stdout'],
            'stderr' : result['stderr'],
            'errcode' : result['errcode'],
            'execution_time' : execution_time,
            'disk_usage' :disk_usage,
            # 'cpu_usage': stats_usages['cpu_stats'],
            # 'memory_usage': stats_usages['memory_stats'],
            # 'networks': stats_usages['network_stats'],
        }
    # if run failed 
    except docker.errors.ContainerError as e:
        print('error')
        result['stdout'] = None
        result['errcode']= e.exit_status
        result['stderr']= e.stderr.decode()
        return {
            'stdout' : result['stdout'],
            'stderr' : result['stderr'],
            'errcode' : result['errcode'],
            'execution_time' : execution_time,
            'disk_usage' : disk_usage,
            # 'cpu_usage': stats_usages['cpu_stats'],
            # 'memory_usage': stats_usages['memory_stats'],
            # 'networks': stats_usages['network_stats'],
        }

        
    
    # stats_usages= check_build_status(True)
    # print(stats_usages)
    # return {
    #     'stdout' : result['stdout'],
    #     'stderr' : None,
    #     'errcode' : result['errcode'],
    #     'execution_time' : execution_time,
    #     'disk_usage' :disk_usage,
    #     # 'cpu_usage': stats_usages['cpu_stats'],
    #     # 'memory_usage': stats_usages['memory_stats'],
    #     # 'networks': stats_usages['network_stats'],
    # }

def image_disk_usage(docker_client,image_name):
    '''
    docker.from_env()
    https://docker-py.readthedocs.io/en/stable/client.html
    Communicate with docker daemon,
    Return client configured from environment variables

    df()
    https://docker-py.readthedocs.io/en/stable/api.html
    Get data usage information
    '''
    

    mem_of_all = docker_client.df()['Images']
    # the sizes in bytes , if you like i can change them!
    image_disk_usage = [
        {
            'shared_size' : mem_of_all[i]['SharedSize']/1024/1024,
            'size' : mem_of_all[i]['Size']/1024/1024,
            'virtual_size' : mem_of_all[i]['VirtualSize']/1024/1024,
        }
        for i in range(len(mem_of_all)) 
        if f'{image_name}:latest' in mem_of_all[i]['RepoTags']
    ]
    if image_disk_usage is None:
        print('Something goes wrong')
        print(image_disk_usage)
        return None

    print(image_disk_usage)
    return image_disk_usage.pop()


def docker_build_cmd(this_id, Dockerfile_filename):
    '''
    https://docs.docker.com/engine/reference/commandline/build/

    --file , -f         Name of the Dockerfile (Default is ‘PATH/Dockerfile’)
    '''
    return f'openbioc/{this_id}'

# def docker_remove_failed_builds_cmd():
#     '''
#     '''
#     return f'docker rmi -f $(docker images -f "dangling=true" -q)'


def create_bash_script_filename(this_id):
    '''d
    '''
    return f'bashscript_{this_id}.sh', os.path.join(execution_directory, f'bashscript_{this_id}.sh')


def create_Dockerfile_filename(this_id):
    '''
    '''

    return f'{this_id}.Dockerfile',os.path.join(execution_directory, f'{this_id}.Dockerfile')

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
    Dockerfile_filename,Dockerfile_path = create_Dockerfile_filename(this_id)

    # Save bash_script 
    with open(bash_script_path, 'w') as bash_script_f:
        bash_script_f.write(bash)

    # Save Dockerfile
    with open(Dockerfile_path, 'w') as Dockerfile_f:
        Dockerfile_f.write(create_Dockerfile_content(ostype, bash_script_path,bash_script_filename))

    print (f'Created bash file: {bash_script_filename}')
    print (f'Created Dockerfile: {Dockerfile_filename}')


    image_name = docker_build_cmd(this_id, Dockerfile_filename)
    print (f'Build starts --> {image_name}')

    return docker_build_image(Dockerfile_filename,image_name)




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
    d['success'] = True
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
        message_queue.put(message)
        return success({'id': new_id, 'status': 'Queued'})

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

def talk_to_server(payload):
    '''
    Call this in order to talk to openbio.eu/callback
    '''
    global instance_settings

    def report_error(payload, data, message):
        print ('payload')
        print (payload)
        print ('Data returned:')
        print (data)
        raise OBC_Controller_Exception(message)


    callback_url = instance_settings['callback_url']
    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

    r = requests.post(callback_url,  data=json.dumps({'payload': payload}), headers=headers)

    if not r.ok:
            r.raise_for_status()

    data =  r.json()

    if not 'success' in data:
        report_error(payload, data, 'Invalid return data from server. key "success" is not present')

    if not data['success']:
        report_error(payload, data, 'Invalid return data from server. "success" is false ')

    #print (data)
    return data


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

            payload = {
                'id': this_id,
                'status': 'Running',
            }
            talk_to_server(payload)
            result = execute_docker_build(this_id,ostype, bash)
            print ('RESULT FROM execute_docker_build:')
            print (result)

            
            #time.sleep(random.randint(1,5))
            #time.sleep(1)
            
            # errcode = 0 means success
            # errcode =! something goes wrong
            payload = {'id': this_id}
            if result['errcode'] == 0:
                payload['status'] = 'Validated'
            else:
                payload['status'] = 'Failed'
                #execution(this_id,'mpah',False)

            payload['stdout'] = result['stdout']
            payload['stderr'] = result['stderr']
            payload['errcode'] = result['errcode']
            talk_to_server(payload)


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

def find_running_container(selected_image):
    '''
    Find the selected images which running as container to take the stats
    '''
    client = docker.from_env()
    res = None
    image=None
    # image_name = image_name+':latest'
    for container in client.containers.list():
        if (container.attrs['Config']['Image'] == selected_image):
            # If the image is inside of running containers take the res and 
            # send to print_stats function
            res = container.stats(stream=False)
            image = container.attrs['Config']['Image']
            # image_name = container.attrs['Config']['Image']
    return res,image

def get_stats(selected_image):
    '''
    get a snapshot of stats when the image build 
    '''

    logs={}
    while True:
        res,image = find_running_container(selected_image)

        if res and image is not None: # Useless if
            # print("Statistical results (JSON) :")
            # print(container.status)
            logs.update({'image_name': image})
            logs.update(res['cpu_stats'])
            if res['memory_stats'] is None:
                print("System don't catch memory usages")
            else:
                logs.update(res['memory_stats'])
            # Drop me keyerror if the system don't find networks (this key does not exist blah blah)
            try:
                logs.update(res['networks'])
            except KeyError:
                pass
            print(logs)
            # return logs



def setup_worker_threads(message_queue, n):
    '''
    n = number of threads

    '''

    threads = [threading.Thread(target=worker, args=(message_queue, i+1),) for i in range(n)]
    for thread in threads:
        thread.start()

import socket, errno

def set_worker_for_stats(image_name):
    '''
    Create new worker inside of build-run worker to take the statistics(Only one thread)
    '''
    stats_thread = threading.Thread(target= worker_for_stats, args=(image_name,))
    stats_thread.start()

def worker_for_stats(image_name):
    '''
    '''
    print('SUBWORKER : docker stats starts....')
    stats_res = get_stats(image_name)
    print(stats_res)

def check_if_port_is_used(port):
    '''
    Not used.
    '''

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

def get_instance_settings():
    '''
    Also see views.py for instance_settings
    TODO: This exists twice in the project!!
    '''

    instance_settings =  {
        'cb62fc6f-f203-4525-bf40-947cbf51bda3': {
            'port': 8200,
            'controller_port': 8080,
            'controller_url': 'http://139.91.190.79:8080/post',
            'callback_url': 'http://139.91.190.79:8200/callback/', # Important: it should always a slash at the end
        },
        '341422c9-36c4-477e-81b7-26a76c77dd9a': {
            'port': 8201,
            'controller_port': 8081,
            'controller_url': 'http://139.91.190.79:8081/post',
            'callback_url': 'http://139.91.190.79:8201/callback/', 
        },
    }

    # Deliberately fail if id.txt does not exist
    with open('id.txt') as f:
        this_id = f.read().strip()

    return instance_settings[this_id]


if __name__ == '__main__':
    message_queue = Thread_queue()
    setup_worker_threads(message_queue, 2)
    instance_settings = get_instance_settings()

    init_web_app(message_queue, port=instance_settings['controller_port'])

    #if check_if_port_is_used(8080):
    #    print ('Running on port 8081')
    #    init_web_app(message_queue, port=8081)
    #else:
    #    init_web_app(message_queue, port=8080)



