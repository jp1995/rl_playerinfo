from flask import Flask, render_template

app = Flask(__name__, template_folder='.', static_folder='assets')
app.config['TEMPLATES_AUTO_RELOAD'] = True
print('Webserver started')


@app.route('/')
def index():
    return render_template('table.html')


if __name__ == '__main__':
    app.run(debug=False)