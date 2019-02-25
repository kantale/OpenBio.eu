import json
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__, static_folder='static')

@app.route('/discourse/<user>', methods=['GET'])
def get_discourse(user):
	return render_template('index.html', author=user)

@app.route('/graph', methods=['GET'])
def get_graph():
	with open('file.json') as f:
		graph = json.load(f)
	return jsonify(graph)
	
@app.route('/graph/<user>', methods=['POST'])
def save_graph(user):
	with open('file.json', 'w') as f:
		json.dump(request.json, f)
	return 'ok'

@app.route("/")
def hello():
    return "Hello World!"
	
if __name__ == '__main__':
    app.run(debug=True)