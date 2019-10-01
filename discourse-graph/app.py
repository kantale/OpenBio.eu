import json
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__, static_folder='static')


@app.route('/discourse/render/<id>', methods=['GET'])
def render_discource(id):
	return render_template('discourse.html', id=id)

@app.route('/discourse/comments/<id>', methods=['GET'])
def fetch_discourse_comments(id):
	print(id)
	return jsonify({
		'comments': [
			{
				'id': 'n0',
				'title': 'Dear all, how can I convert NCBI Transcribed RefSeq records (with NM_ or NR_ accession prefix) into gene names / sybols or gene IDs?',
				'obc_user': 'B',
				'comment_html': """Dear all, how can I convert NCBI Transcribed RefSeq records (with NM_ or NR_ accession prefix) into gene names / sybols or gene IDs?
                    Transcribed RefSeq IDs have the following format:
                    <br>NM_001007095.3
                    <br>NM_001014465.3
                    <br>NM_001014478.2
                    <br>NM_001014496.3""",
				'created_at': '12344'
			},
			{
				'id': 'n1',
				'obc_user': 'A',
				'comment_html': 'If you are an R user, check out biomart. Very easy to use. Here is the biomaRt package from Bioconductor: https://bit.ly/2Bq4vOt',
				'created_at': '12344',
				'parent': 'n0'
			},
			{
				'id': 'n2',
				'obc_user': 'B',
				'comment_html': 'R is too complicated, a tool that is more straightforward would be more appropriate',
				'created_at': '12344',
				'parent': 'n1'
			},
			{
				'id': 'n3',
				'obc_user': 'C',
				'comment_html': """There is a python library. Biopython is pretty good for moving between IDs and names. Here's an example of something similar: https://bit.ly/2PIVgkX""",
				'created_at': '12344',
				'parent': 'n0'
			},
			{
				'id': 'n4',
				'obc_user': 'B',
				'comment_html': """Although the python solution is simpler, it would be nice if there was something that did not require the knowledge of a programming language""",
				'created_at': '12344',
				'parent': 'n3'
			},
		]
	})

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