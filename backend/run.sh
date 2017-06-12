#!/bin/sh

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks/backend
daemon --name=beachranks -- python /home/admin/beachranks/backend/run_web_server.py -P 9999