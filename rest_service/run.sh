#!/bin/sh

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks/
daemon --name=beachranks -- python /home/admin/beachranks/rest_service/run.py -P 9999