#!/bin/bash
PYTHON="/home/pavel/Programs/miniconda3/bin/python"
CLI="/home/pavel/Code/Data/cli.py"
DATA="$(hostname): $(date +"%Y-%m-%d")"
LOG_FILE="/home/pavel/logs-sync/sync.log"
if grep -Fq "$DATA" $LOG_FILE; then
    echo "Already synced today";
else
    $PYTHON $CLI aw to-csv
    export RSYNC_EXCLUDE_PATTERN="sync.log"
    export CREATE_DIRS=yes
    /usr/local/bin/osync.sh --initiator=/home/pavel/logs-sync --target=ssh://pavel@45.76.36.229//home/pavel/logs-sync || exit 1
    echo "$(hostname): $(date +"%Y-%m-%d %H:%m")" >> $LOG_FILE
    export DISPLAY=:0
    notify-send "Syncronization" "Logs submitted to the server"
fi
