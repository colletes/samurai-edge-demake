#!/bin/bash
# uso: start.sh LOG TIMEOUT script args...  (so inicia se nao houver outro processo e2e)
if pgrep -f "/tmp/se/(e2e_|t_)" > /dev/null; then echo "JA HA PROCESSO RODANDO"; exit 1; fi
log=$1; to=$2; shift 2
nohup /tmp/se/run1.sh $log $to "$@" > /dev/null 2>&1 &
echo started
