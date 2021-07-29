
import json
import re

'''
/Users/antonakd/anaconda3/bin/python do.py 
https://gist.github.com/kantale/c60ddec0470fbeb0034e2294634d1166
'''

fn = 'questions.txt'
f = open(fn)
d = f.read()
f.close()

s = re.findall(r'!!!\n(.+?)\n!!!', d, re.DOTALL)
#print (len(s))


def f3(s):

	a = re.findall(r'%%.+?%%', s)

	return [x[2:-2] for x in a]

def f1(s):
	ret = {}
	sp = s.split('\n')
	ret['id'] = int(sp[0])
	ret['url'] = sp[1]
	ret['title'] = sp[2].replace('View Full Version :', '').strip()

	yield(ret)


	rest = '\n' + '\n'.join(sp[3:])

	#print (rest)
	#print ('########################################################')

	date_r = r'\n[^\n.]+?\n\d\d-\d\d-\d\d\d\d, \d\d:\d\d [AP]M'

	d1 = re.split(date_r, rest, re.DOTALL)[1:]
	#print (d1)

	d2 = re.findall(date_r, rest, re.DOTALL)

	#print (len(d1), len(d2))

	#print (d1)
	#print ('###############')
	#print (d2)
	#a=1/0


	for x,y in zip(d1, d2):
		to_yield = {}

		y2 = y.strip().split('\n')

		to_yield['user'] = y2[0]
		to_yield['date'] = y2[1]
		to_yield['content'] = x
		to_yield['tools'] = f3(x)
		
		yield to_yield
		


def f2(s):

	all_ret = []

	for x in s:
		g = f1(x)
		ret = next(g)
		ret['question'] = next(g)
		ret['answers'] = [y for y in g]

		#print (ret)
		print (json.dumps(ret, indent=4))
		print ('############################################################################')

		#yield ret

		all_ret.append(ret)
	return all_ret




#print (s[0])
#print ('===')
#f2(s[0])

#print (s)


r = f2(s)
with open('questions.json', 'w') as f:
	json.dump(r, f, indent=4)
print ('Created: questions.json')


