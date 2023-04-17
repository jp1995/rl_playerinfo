from flask import Flask, render_template, jsonify
from web.MMR import modMMRjson
import json
import os


data = None
matchData = None
playlistData = None


def run_webserver(mmrq, matchq, playlistq):
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

        if not mmrq.empty():
            data = mmrq.get()
            data = json.loads(data)
            if 'Playlist' not in data.keys():
                if 'MMR' not in data.keys():
                    data = {'MMR': data}
        render_mmr = render_template('MMR.html', mmrData=modMMRjson(data))
        return jsonify({'html': render_mmr})

    @app.route('/update_playlist')
    def update_playlist():
        global playlistData

        if not playlistq.empty():
            data = playlistq.get()
            playlistData = data

        render_content = render_template('playlist.html', playlistData=playlistData)
        return jsonify({'html': render_content})

    @app.route('/update_match')
    def update_match():
        global matchData

        if not matchq.empty():
            data = matchq.get()
            if data[0] == 'Match':
                matchData = data

        render_match = render_template('match.html', matchData=matchData)
        return jsonify({'html': render_match})

    app.run()
