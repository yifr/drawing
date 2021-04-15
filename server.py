import json
from flask import Flask
from flask import request 
from flask import Response
from flask import jsonify
from flask import render_template
from configs import generate_config

app = Flask(__name__)

EXPERIMENT_ID = 'TIAN_REPLICATION_0'

@app.route('/experiment_config')
def get_config(methods=['GET']):
    if request.method == 'GET':
        config = generate_config(EXPERIMENT_ID)
        with open('served_config.json', 'w') as f:
            json.dump(config, f)
        return jsonify(config)

@app.route('/drawlang')
def drawlang(methods=['GET', 'POST']):
    if request.method == 'GET':
        return render_template("drawlang.html")
"""
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404
"""
