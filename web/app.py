from flask import Flask, render_template
from flask_socketio import SocketIO
from logging_setup import log
from web.MMR import modMMRjson
import socket
import json
import os

data = None
matchData = []
playlistData = None


def run_webserver(mmrq, matchq, playlistq):
    os.chdir('./web/')
    app = Flask(__name__, template_folder='.', static_folder='assets')
    app.jinja_env.auto_reload = True
    socketio = SocketIO(app, cors_allowed_origins='*')

    log.info("Webserver started")
    log.info("* Running on http://127.0.0.1:5000\n"
             f"* Running on http://{get_local_ip()}:5000\n")

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
        socketio.sleep(0.1)
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

    @socketio.on('request_playlist')
    def update_playlist():
        socketio.sleep(0.1)
        global playlistData

        if not playlistq.empty():
            data = playlistq.get()
            playlistData = data

            with app.app_context():
                render_playlist = render_template('playlist.html', playlistData=playlistData)
            socketio.emit('reply_playlist_update', {'html': render_playlist})
        socketio.start_background_task(update_playlist)

    @socketio.on('request_match')
    def update_match():
        socketio.sleep(0.1)
        global matchData

        if not matchq.empty():
            data = matchq.get()
            if type(data[0]) == dict:
                matchID = data[0]['Match']
                for item in matchData:
                    if item[0]['Match'] == matchID and matchID != '':
                        matchData.pop(matchData.index(item))

                matchData.insert(0, data)
                matchData = matchData[:10]
            with app.app_context():
                render_match = render_template('match.html', matchData=matchData)
            socketio.emit('reply_match_update', {'html': render_match})
        socketio.start_background_task(update_match)

    socketio.run(app, host='0.0.0.0', port=5000)


def get_local_ip():
    ts = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ts.settimeout(0)
    try:
        ts.connect(("1.1.1.1", 1))
    except (socket.gaierror, OSError):
        pass
    finally:
        localIP = ts.getsockname()[0]
        ts.close()
    return localIP
