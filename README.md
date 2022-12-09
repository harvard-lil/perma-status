perma-status
============

This is a Flask application and associated code for generating the
site [status.perma.cc](https://status.perma.cc/).

For development, use [Poetry](https://python-poetry.org/). After any
changes to `poetry.lock`, export requirements for use in deployment:

    poetry export -o requirements.txt

In deployment, set up a virtual environment, install requirements, and
generate the index template with

    python index.py > templates/index.html

Run the Flask application:

    env FLASK_APP=monitor.py flask run
