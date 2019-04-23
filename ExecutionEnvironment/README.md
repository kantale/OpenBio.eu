
### Install aiohttp 
Install aiohttp\_cors: https://github.com/aio-libs/aiohttp-cors

```
conda install aiohttp
pip install aiohttp_cors
```

### Install requests
```
conda install requests
```

### Install  ansi2html 
Convert text with ANSI color codes to HTML: https://pypi.org/project/ansi2html/
```
pip install ansi2html 
```

### Run:
```
python server.py
```

### How to test:
This should generate an error:
```
curl --header "Content-Type: application/json" --request POST -d "zsdfasdf" http://0.0.0.0:8080/post
```

Send a JSON file:
```
curl --header "Content-Type: application/json" --request POST -d @test_1.json http://0.0.0.0:8080/post 
```

Test on pappos:
```
curl --header "Content-Type: application/json" --request POST -d @test_1.json http://139.91.190.79:8080/post 
```

Send json data with curl
```
curl --header "Content-Type: application/json" --request POST -d '{"token": "123"}' http://0.0.0.0:8200/report/
```




