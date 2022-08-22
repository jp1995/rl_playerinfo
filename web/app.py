from flask import Flask, render_template
from livereload import Server
import logging

app = Flask(__name__, template_folder='.', static_folder='assets')
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
print('Webserver started')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
def index():
    return render_template('table.html')

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.serve()
