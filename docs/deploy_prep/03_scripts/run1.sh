#!/bin/bash
# uso: run1.sh logfile timeout args...
log=$1; to=$2; shift 2
cd /tmp/se
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONUNBUFFERED=1 PYTHONPYCACHEPREFIX=/tmp/se/pyc timeout $to /Users/thiagocarvalho/Public/SamuraiEdge/venv/bin/python "$@" > $log 2>&1
echo "exit=$?" >> $log
