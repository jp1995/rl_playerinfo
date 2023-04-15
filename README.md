## Clean Template Autoreloads

In the main branch, the whole site is reloaded when an individual include in index.html is updated.
Here every subtemplate has a separate flask route and the content of the associated file(s) is pushed to that route. In index.html a GET request is made for that route, and that data is placed into relevant element by class.

This doesn't seem to work with livereload, so either the basic flask server or a different wsgi server (that is not a colossal headache to install - so not gunicorn, uWSGI - perhaps cheroot, waitress or flask_socketio) has to be used. This means that auto refreshing functionality needs to be added in the javascript as well. Not sure how to proceed with that atm.

Additionally, instead of writing to files to pass data from main.py to webserver, using Multiprocessing Queue would be much cleaner. This can't currently be used on the main branch, because livereload cannot watch variables, only files.

The code I have written here so far could potentially also be some unga bunga grug caveman solution. wcyd
