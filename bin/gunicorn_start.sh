#!/bin/bash

NAME="download"                                   # Name of the application
DJANGODIR=/data/code/web                          # Django project directory
SOCKFILE=/data/code/web/gunicorn.sock             # we will communicte using this unix socket
USER=hunch                                        # the user to run as
GROUP=hunch                                       # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=download.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=download.wsgi                     # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
# source ../bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
# export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /home/hunch/.pyenv/versions/3.7.1/envs/web/bin/python3.7 /home/hunch/.pyenv/versions/web/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --worker-class=gevent \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --reload
  # --log-level=debug \
  # --log-file=${DJANGODIR}/logs/gunicorn.log

#/home/hunch/.pyenv/versions/3.7.1/envs/web/bin/python3.7 /home/hunch/.pyenv/versions/web/bin/gunicorn download.wsgi:application --name=download --worker-class=gevent --workers=5 --bind=unix:/data/code/web/gunicorn.sock --log-level=info --timeout=300 --limit-request-line=8190 --reload --daemon
