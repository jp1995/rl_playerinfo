from flask import Flask, render_template, jsonify
from web.MMR import modMMRjson
import json
import os


data = None


def run_webserver(wq):
    os.chdir('./web/')
    app = Flask(__name__, template_folder='.', static_folder='assets')
    app.jinja_env.auto_reload = True

    print("Webserver started")

    @app.route('/')
    def index():
        render_table = render_template('index.html')
        return render_table

    @app.route('/update_mmr')
    def update_mmr():
        global data
        print(f'Data is now: {data}')

        if not wq.empty():
            data = wq.get()
            data = json.loads(data)
            if 'MMR' not in data.keys():
                data = {'MMR': data}

        render_mmr = render_template('MMR.html', data=modMMRjson(data))
        return jsonify({'html': render_mmr})

    @app.route('/update_playlist')
    def update_playlist():
        render_content = render_template('playlist.html')
        return jsonify({'html': render_content})

    @app.route('/update_match')
    def update_match():
        render_match = render_template('table.html')
        return jsonify({'html': render_match})

    app.run()
