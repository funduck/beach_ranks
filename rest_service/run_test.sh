#!/bin/sh

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks_test/
daemon --name=beachranks_test -- python /home/admin/beachranks_test/rest_service/run.py --mode=test
