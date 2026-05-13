#!/bin/sh
set -e

python index.py > templates/_index.html
mv templates/_index.html templates/index.html

exec "$@"
