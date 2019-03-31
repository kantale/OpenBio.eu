
import json
import time
import requests

URL = 'http://0.0.0.0:8080/post'
headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

def json_1():
	return {
		"action": "validate",
		"bash": "test"
	}

def json_2(this_id):
	return {
		"action": "query",
		"id": this_id
	}

def r_1():
	r = requests.post(URL,  data=json.dumps(json_1()), headers=headers)

	if not r.ok:
		r.raise_for_status()

	data = r.json()
	print (data)
	return data['id']

def r_2(this_id):
	r = requests.post(URL,  data=json.dumps(json_2(this_id)), headers=headers)

	if not r.ok:
		r.raise_for_status()

	data =  r.json()
	print (data)
	return data

def test_1():
	# Send 50 validate
	ids = [r_1() for x in range(50)]

	resp = [r_2(id_) for id_ in ids]

	print ('Waiting 10 secs')
	time.sleep(10)
	resp = [r_2(id_) for id_ in ids]
	

test_1()
