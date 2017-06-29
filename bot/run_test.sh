#!/bin/sh

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks_test/
daemon --name=beachranks_test_bot -- python /home/admin/beachranks_test/bot/run_via_get_updates.py --mode=test
