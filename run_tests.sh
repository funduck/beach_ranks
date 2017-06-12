#!/bin/bash

. /home/admin/anaconda3/bin/activate beachranks
export PYTHONPATH=/home/admin/beachranks/backend
py.test /home/admin/beachranks
