from flask import Flask, render_template
from livereload import Server
from web.MMR import modMMRjson
import logging
import json
import os


def run_webserver():
    os.chdir('./web/')
    app = Flask(__name__, template_folder='.', static_folder='assets')
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.logger.disabled = True

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    print('Webserver started')

    @app.route('/')
    def index():
        with open('mmr.txt') as f:
            try:
                data = json.load(f)
                data = {'MMR': data}
            except json.decoder.JSONDecodeError:
                data = ''

        render_table = render_template('index.html', data=modMMRjson(data))
        return render_table

    server = Server(app)
    server.serve()
    server.watch('.')
    server.serve(root='.')
