from flask import Flask, render_template
from livereload import Server
from web.MMR import modMMRjson
import json
import os


def run_webserver():
    os.chdir('./web/')
    app = Flask(__name__, template_folder='.', static_folder='assets')
    app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True

    print("Webserver started: http://127.0.0.1:5500")

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

    server = Server(app.wsgi_app)
    server._setup_logging = lambda: None
    server.watch('.')
    server.serve(root='.')
