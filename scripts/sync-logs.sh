#!/bin/bash
DATA="$(hostname): $(date +"%Y-%m-%d")"
LOG_FILE="/home/pavel/logs-sync/sync.log"
if grep -Fq "$DATA" $LOG_FILE; then
    echo "Already synced today";
else
    export RSYNC_EXCLUDE_PATTERN="sync.log"
    export CREATE_DIRS=yes
    osync.sh --initiator=/home/pavel/logs-sync --target=ssh://pavel@45.76.36.229//home/pavel/logs-sync || exit 1
    echo "$(hostname): $(date +"%Y-%m-%d %H:%m")" >> $LOG_FILE
    notify-send "Syncronization" "Logs submitted to the server"
fi
