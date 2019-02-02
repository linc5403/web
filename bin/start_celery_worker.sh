#!/bin/bash

NAME="celery-worker"                                   # Name of the application
WORK_DIR=/data/code/web                          # Django project directory
USER=hunch                                        # the user to run as
GROUP=hunch                                       # the group to run as
NUM_WORKERS=20                                     # how many worker processes should Gunicorn spawn

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $WORK_DIR


# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /home/hunch/.pyenv/versions/3.7.1/envs/web/bin/python3.7 /home/hunch/.pyenv/versions/web/bin/celery -A downloader.tasks worker \
  --concurrency=$NUM_WORKERS
# --gid $GROUP \
# --uid $USER
