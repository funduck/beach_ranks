#!/bin/sh

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks/backend
python /home/admin/beachranks/backend/run_web_server.py