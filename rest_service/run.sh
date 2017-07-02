#!/bin/sh

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks/
export LOG_FILE=/home/admin/logs/rest-service.log
daemon --name=beachranks -- python /home/admin/beachranks/rest_service/run.py
