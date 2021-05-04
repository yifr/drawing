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
from flask import render_template, redirect, url_for
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

@app.route('/experiment_types', methods=['GET'])
def exps():
    exps = []
    for root, dirs, files in os.walk("static/configs", topdown=False):
        for name in files:
            fname = os.path.join(root, name)
            config = json.load(open(fname, 'r'))
            meta = config['metadata']
            exps.append(meta)

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

def get_instruction_pages(config):
    instruction_pages = ['instructions/overview-1.html',
                        'instructions/overview-2.html',
                        'instructions/overview-3.html',
                        'instructions/overview-4.html']
    tasks = []
    elements = set()
    for phase in config.get('phases', []):
        phase_elements = set(config[phase]['ui_components'])
        elements.update(phase_elements)

        if 'draw' not in phase_elements and 'describe' not in phase_elements:
            elements.add('look-only')

        if config[phase].get('sampling'):
            elements.add('sample')

    print(elements)
    if 'images' in elements:
        tasks.append('Look at images')

    if 'look-only' in elements:
        instruction_pages.append('instructions/look-only.html')

    if 'draw' in elements:
        tasks.append('Draw images')
        instruction_pages.append('instructions/drawing-1.html')
        instruction_pages.append('instructions/drawing-2.html')
        instruction_pages.append('instructions/drawing-3.html')

    if 'descriptions' in elements:
        tasks.append('Interpret descriptions of images')
    
    if 'describe' in elements:
        tasks.append('Describe images')
        instruction_pages.append('instructions/describing-1.html')
        instruction_pages.append('instructions/describing-2.html')

    if 'sample' in elements:
        tasks.append('Draw and describe new images like the ones you have seen')
        instruction_pages.append('instructions/sampling-1.html')
        instruction_pages.append('instructions/sampling-2.html')

    instruction_pages.append('instructions/quiz.html')
    return tasks, instruction_pages

@app.route('/instructions', methods=['GET'])
def instructions():
    if request.args.get('experiment_id') or request.args.get('condition') or not session['config']:
        user_id = request.args.get('PROLIFIC_PID')
        study_id = request.args.get('STUDY_ID')
        session_id = request.args.get('SESSION_ID')
        experiment_id = request.args.get('experiment_id')
        condition = request.args.get('condition')
        app.logger.info('Generating config for: ')

        app.logger.info("experiment id " + str(experiment_id))
        app.logger.info("condition: " + str(condition))

        session['user_id'] = user_id
        session['study_id'] = study_id
        session['session_id'] = session_id
        session['experiment_id'] = experiment_id
        session['condition'] = condition

        get_config()

    print(session['config']['metadata']['experiment_id'])
    index = max(0, request.args.get('index', 0, type=int))
    tasks, instruction_pages = get_instruction_pages(session['config'])
    n_phases = len(session['config']['phases'])

    if int(index) >= len(instruction_pages):
        return render_template("experiment.html")
    else:
        return render_template(instruction_pages[int(index)], index=int(index), tasks=tasks, n_phases=n_phases)

@app.route('/experiment_config', methods=['GET'])
def get_config():
    experiment_id = session.get('experiment_id')
    condition = session.get('condition')

    if experiment_id and condition:
        config_path = os.path.join('static/configs', experiment_id, condition, 'batch_0_shuffle_0.json')
        config = json.load(open(config_path, 'r'))
    else:
        exp_path = os.path.join('static/configs')
        experiment_configs = []
        for root, dirs, files in os.walk(exp_path, topdown=False):
            if experiment_id:
                dirs = [d for d in dirs if d == experiment_id]
            elif condition:
                dirs = [d for d in dirs if d == condition]  # TODO: @Yoni this is probably super buggy

            for name in files:
                fname = os.path.join(root, name)
                if experiment_id and experiment_id not in fname:
                    continue
                if condition and condition not in fname:
                    continue
                print(fname)
                experiment_configs.append(fname)

        config_path = np.random.choice(experiment_configs)
        config = json.load(open(config_path, 'r'))

    config['metadata']['user_id'] = session['user_id']
    config['metadata']['study_id'] = session['study_id']
    config['metadata']['session_id'] = session['session_id']

    session['config'] = config
    return jsonify(config)

@app.route('/experiment', methods=['GET'])
def experiment():
    if request.method == 'GET':
        if request.args:
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

@app.route('/consent', methods=['GET'])
def consent():
    if request.args:
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

    return render_template("consent.html")

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET': 
        return render_template("questionnaire.html")
