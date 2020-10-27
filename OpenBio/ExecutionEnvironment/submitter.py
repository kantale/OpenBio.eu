
import json
import time
import requests
import subprocess
import asyncio

URL = 'http://0.0.0.0:8080/'
headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

def json_1():
	return {
		"action": "validate",
		"ostype": "ubuntu:latest",
		"bash": """
#!/bin/bash
set -e

wget http://zzz.bwh.harvard.edu/plink/dist/plink-1.07-x86_64.zip 
unzip plink-1.07-x86_64.zip

cd plink-1.07-x86_64
./plink --noweb --file test
#./plink --noweb
		"""
	}

def json_2(this_id):
	return {
		"action": "query",
		"id": this_id
	}

# def r_1():
# 	r = requests.post(URL,  data=json.dumps(json_1()), headers=headers)

# 	if not r.ok:
# 		r.raise_for_status()
# 	data = r.json()
# 	print (data)
# 	return data['id']

def r_query(this_id):
	r = requests.post(URL,  data=json.dumps(json_2(this_id)), headers=headers)

	if not r.ok:
		r.raise_for_status()

	data =  r.json()
	return data

def check_response(r):
	if not r.ok:
		r.raise_for_status()

	data =  r.json()
	return data


def r_json_submit(js):
	r = requests.post(URL,  data=json.dumps(js), headers=headers)
	return check_response(r)

# def test_1():
# 	# Send 50 validate
# 	ids = [r_1() for x in range(2)]

# 	resp = [r_query(id_) for id_ in ids]

# 	print ('Waiting 10 secs')
# 	time.sleep(4)
# 	resp = [r_query(id_) for id_ in ids]

def test_2():
    print ('Submitting..')
    data = r_json_submit(json_1())
    print (data)

    time.sleep(4)
    print ('Quering...')
    data = r_query(data['id'])
    print ('DATA RECEIVED:')
    print (data)
    while True :
        if (data['status'] == 'done' or data['status'] == 'failed'):
            break
        time.sleep(10)
        data = r_query(data['id'])
        print (data)



if __name__ == '__main__':
#	try:
#		test_1()
#	except KeyboardInterrupt:
#		pass

	test_2()	
