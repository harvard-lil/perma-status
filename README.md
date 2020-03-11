perma-status
============

This is a Flask application and associated code for generating the site [status.perma.cc](https://status.perma.cc/).

For development, start a virtualenv and install requirements:

    python3 -m venv env
    . env/bin/activate
    pip install -r requirements.txt

After editing `requirements.in`, run

    pip-compile
    pip install -r requirements.txt

Generate the index template with

    python index.py > templates/index.html

Run the Flask application:

    env FLASK_APP=monitor.py flask run
