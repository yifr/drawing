import os
import json
import certs
import db_utils
import numpy as np
from flask import Flask
from flask import request 
from flask import session
from flask import Response
from flask import jsonify
from flask import render_template
from configs import generate_config
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.secret_key = certs.secret_app_key

EXPERIMENT_ID = 'TIAN_REPLICATION_0'

@app.route('/experiment_types', methods=['GET'])
def exps():
    exps = []
    for root, dirs, files in os.walk("static/configs", topdown=False):
        for name in files:
            fname = os.path.join(root, name)
            config = json.load(open(fname, 'r'))
            meta = config['metadata']
            exps.append(meta)
    
    if request.args.get('old'):
        exps = {'TIAN_REPLICATION_0': "draw, describe, view images - two phases",
                'sample_img': 'one phase - sample drawings only',
                'sampleText': 'one phase - sample text only',
                'sampleAll': 'one phase - sample drawing and description',
                'drawOnly': 'two phases - collect only drawings',
                'describeOnly': 'two phases - collect only descriptions',
                'readDescriptions': 'two phases - read descriptions and draw/describe. Slow right now because descriptions are pulled from massive random word library that comes with linux',
                'bothStims': 'two phases - read descriptions, see images and draw/describe. Slow right now because descriptions are pulled from massive random word library that comes with linux',
                }

    return Response(json.dumps(exps),  mimetype='application/json') 

@app.route('/record_data', methods=['POST'])
def log_data():
    data = request.get_json()
    user_id = data['metadata'].get('user_id')
    if not user_id:
        return json.dumps({'success':False, 'message': 'No prolific_pid found! Data not logged.'}), 200, {'ContentType':'application/json'} 
    else:
        status = db_utils.record(data)
        return json.dumps(status), 200, {'ContentType':'application/json'} 

@app.route('/instructions', methods=['GET'])
def instructions():
    return render_template('instructions/instruction-all.html')

@app.route('/experiment_config', methods=['GET'])
def get_config():
    experiment_id = session.get('experiment_id')
    condition = session.get('condition')
    with open('debug.txt', 'a+') as f:
        f.write("experiment_id: " + str(experiment_id))
        f.write("condition: " + str(condition))

    if experiment_id and condition:
        config_path = os.path.join('static/configs', experiment_id, condition, 'batch_0_shuffle_0.json')
        config = json.load(open(config_path, 'r'))
        
    elif experiment_id:
        exp_path = os.path.join('static/configs', experiment_id)
        experiment_configs = []
        for root, dirs, files in os.walk(exp_path, topdown=False):
            for name in files:
                fname = os.path.join(root, name)
                experiment_configs.append(fname)
             
        config_path = np.random.choice(experiment_configs)
        config = json.load(open(config_path, 'r'))
    
    elif condition:
        exp_path = os.path.join('static/configs')
        experiment_configs = []
        for root, dirs, files in os.walk(exp_path, topdown=False):
            dirs = [d for d in dirs if d == condition]  # TODO: @Yoni this is probably super buggy
            for name in files:
                fname = os.path.join(root, name)
                experiment_configs.append(fname)
             
        config_path = np.random.choice(experiment_configs)
        config = json.load(open(config_path, 'r'))
    
    else:
        experiment_id = 'TIAN_REPLICATION_0'
        config = generate_config(experiment_id)

    config['metadata']['user_id'] = session['user_id']
    config['metadata']['study_id'] = session['study_id']
    config['metadata']['session_id'] = session['session_id']

    return jsonify(config)

@app.route('/experiment', methods=['GET'])
def experiment():
    if request.method == 'GET':
        user_id = request.args.get('PROLIFIC_PID')
        study_id = request.args.get('STUDY_ID')
        session_id = request.args.get('SESSION_ID')
        experiment_id = request.args.get('experiment_id')
        condition = request.args.get('condition') 
        
        app.logger.info("experiment id " + str(experiment_id))
        app.logger.info("condition: " + str(condition))

        session['user_id'] = user_id
        session['study_id'] = study_id
        session['session_id'] = session_id
        session['experiment_id'] = experiment_id
        session['condition'] = condition
        
        return render_template("experiment.html")

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404
