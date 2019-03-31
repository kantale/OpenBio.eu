
### Install aiohttp 
```
conda install aiohttp
```

### Install requests
```
conda install requests
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

