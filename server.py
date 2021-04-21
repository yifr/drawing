import json
import certs
import db_utils
from flask import Flask
from flask import request 
from flask import session
from flask import Response
from flask import jsonify
from flask import render_template
from configs import generate_config

app = Flask(__name__)
app.secret_key = certs.secret_app_key

EXPERIMENT_ID = 'TIAN_REPLICATION_0'

@app.route('/experiment_types', methods=['GET'])
def exps():
    exps = {'TIAN_REPLICATION_0': "draw, describe, view images - two phases",
            'sample_img': 'one phase - sample drawings only',
            'sampleText': 'one phase - sample text only',
            'sampleAll': 'one phase - sample drawing and description',
            'drawOnly': 'two phases - collect only drawings',
            'describeOnly': 'two phases - collect only descriptions',
            'readDescriptions': 'two phases - read descriptions and draw/describe. Slow right now because descriptions are pulled from massive random word library that comes with linux',
            'bothStims': 'two phases - read descriptions, see images and draw/describe. Slow right now because descriptions are pulled from massive random word library that comes with linux',
            }
    return jsonify(exps)

@app.route('/record_data', methods=['POST'])
def log_data():
    data = request.get_json()
    user_id = data['meta'].get('user_id')
    if not user_id:
        return json.dumps({'success':False, 'message': 'No prolific_pid found! Data not logged.'}), 200, {'ContentType':'application/json'} 
    else:
        status = db_utils.record(data)
        return json.dumps(status), 200, {'ContentType':'application/json'} 


@app.route('/experiment_config', methods=['GET'])
def get_config():
    if session.get('experiment_id'):
        config_type = session.get('experiment_id')
    else:
        config_type = EXPERIMENT_ID
    config = generate_config(config_type)
    config['meta']['user_id'] = session['user_id']
    config['meta']['study_id'] = session['study_id']
    config['meta']['session_id'] = session['session_id']

    return jsonify(config)

@app.route('/drawlang')
def drawlang():
    if request.method == 'GET':
        user_id = request.args.get('PROLIFIC_PID')
        study_id = request.args.get('STUDY_ID')
        session_id = request.args.get('SESSION_ID')
        experiment_id = request.args.get('experiment_id')

        session['user_id'] = user_id
        session['study_id'] = study_id
        session['session_id'] = session_id
        session['experiment_id'] = experiment_id

        return render_template("drawlang.html")

@app.route('/experiment', methods=['GET'])
def experiment():
    if request.method == 'GET':

        user_id = request.args.get('PROLIFIC_PID')
        study_id = request.args.get('STUDY_ID')
        session_id = request.args.get('SESSION_ID')
        experiment_id = request.args.get('experiment_id')

        session['user_id'] = user_id
        session['study_id'] = study_id
        session['session_id'] = session_id
        session['experiment_id'] = experiment_id

        return render_template("experiment.html")

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404
