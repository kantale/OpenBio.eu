'''
https://docs.aiohttp.org/en/stable/web_quickstart.html#run-a-simple-web-server

### Test to see if alive:
curl -X POST http://0.0.0.0:8080/post

### Send POST data
curl -d "param1=value1&param2=value2" -X POST http://0.0.0.0:8080/post


### Send JSON data iin file: test_1.json via POST :
curl --header "Content-Type: application/json" --request POST -d @test_1.json http://0.0.0.0:8080/post 

'''

from aiohttp import web


async def hello(request):
    '''
    A request handler must be a coroutine that accepts a Request instance as its only parameter and returns a Response instance:
    '''
    return web.Response(text="Hello, world")

async def post_handler(request):
    '''
    Post handler
    '''

    # Receive arbitrary post data
    #data = await request.post()

    # Receive JSON data 
    data = await request.json()


    # Create JSON response 
    # https://docs.aiohttp.org/en/stable/web_quickstart.html#json-response
    responce_data = {'some': 'data'}
    return web.json_response(responce_data)

    # Create TEXT response:
    #return web.Response(text="Hello from post")

'''
Next, create an Application instance and register the request handler on a particular HTTP method and path:
'''
app = web.Application()
app.add_routes([
    web.get('/', hello),
    web.post('/post', post_handler),
])

'''
After that, run the application by run_app() call:
'''
web.run_app(app)



