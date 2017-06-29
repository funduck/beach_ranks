#!/bin/sh

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks/
daemon --name=beachranks_bot -- python /home/admin/beachranks/bot/run_via_get_updates.py
