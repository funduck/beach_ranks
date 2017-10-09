#!/bin/sh

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks/
daemon --name=beachranks_console -- python /home/admin/beachranks/beachranks_console/console_bot.py
