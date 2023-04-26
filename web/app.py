from flask import Flask, render_template
from flask_socketio import SocketIO
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

    socketio = SocketIO(app, cors_allowed_origins='*')
    print("Webserver started")

    @app.route('/')
    def index():
        render_table = render_template('index.html')
        return render_table

    @socketio.on('rq_current_mmr')
    def get_mmr():
        global data

        render_mmr = render_template('MMR.html', mmrData=modMMRjson(data))
        socketio.emit('reply_mmr_update', {'html': render_mmr})

    @socketio.on('rq_current_playlist')
    def get_playlist():
        global playlistData

        render_playlist = render_template('playlist.html', playlistData=playlistData)
        socketio.emit('reply_playlist_update', {'html': render_playlist})

    @socketio.on('rq_current_match')
    def get_playlist():
        global matchData

        render_match = render_template('match.html', matchData=matchData)
        socketio.emit('reply_match_update', {'html': render_match})

    @socketio.on('request_mmr')
    def update_mmr():
        global data

        if not mmrq.empty():
            data = mmrq.get()
            data = json.loads(data)
            if 'Playlist' not in data.keys():
                if 'MMR' not in data.keys():
                    data = {'MMR': data}
            with app.app_context():
                render_mmr = render_template('MMR.html', mmrData=modMMRjson(data))
            socketio.emit('reply_mmr_update', {'html': render_mmr})
        socketio.start_background_task(update_mmr)
        socketio.sleep(1)

    @socketio.on('request_playlist')
    def update_playlist():
        global playlistData

        if not playlistq.empty():
            data = playlistq.get()
            playlistData = data

            with app.app_context():
                render_playlist = render_template('playlist.html', playlistData=playlistData)
            socketio.emit('reply_playlist_update', {'html': render_playlist})
        socketio.start_background_task(update_playlist)
        socketio.sleep(1)

    @socketio.on('request_match')
    def update_match():
        global matchData

        if not matchq.empty():
            data = matchq.get()
            if data[0] == 'Match':
                matchData = data
            with app.app_context():
                render_match = render_template('match.html', matchData=matchData)
            socketio.emit('reply_match_update', {'html': render_match})
        socketio.start_background_task(update_match)
        socketio.sleep(1)

    socketio.run(app, host='0.0.0.0', port=5000)
