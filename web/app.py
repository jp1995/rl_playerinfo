from flask import Flask, render_template
from livereload import Server
from MMR import modMMRjson
import logging
import json

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
            render_table = render_template('MMR_base.html')
            return render_table

    render_table = render_template('MMR.html', data=modMMRjson(data))

    return render_table


if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('.')
    server.serve(root='.')
