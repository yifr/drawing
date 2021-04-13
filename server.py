import json
from flask import Flask
from flask import request 
from flask import Response
from flask import jsonify
from flask import render_template

app = Flask(__name__)

@app.route('/get_stims')
def get_stims(methods=['GET']):
    if request.method == 'GET':
        group_id = request.args.get('group_id', 1)        
        with open('log.txt', 'w') as f:
            f.write('group_id: ' + str(group_id) + '\n')
        with open('stims.json', 'r') as f:
            stim_config = json.load(f)
        stim_type = stim_config['conditions'][group_id]
        stims = [stim_config['stims'][category] for category in stim_type]
        return Response(json.dumps(stims), mimetype='application/json')

@app.route('/index')
def index():
    group_id = 0
    experiment_id = 0
    test_id = 0
     
    resp = {'group_id': group_id,
            'experiment_id': experiment_id,
            'test_id': test_id}

    return resp

@app.route('/draw')
def draw(methods=['GET', 'POST']):
    if request.method == 'GET':
        return render_template("draw.html")

@app.route('/describe')
def describe(methods=['GET', 'POST']):
    if request.method == 'GET':
        return render_template("describe.html")

@app.route('/drawlang')
def drawlang(methods=['GET', 'POST']):
    if request.method == 'GET':
        return render_template("drawlang.html")
