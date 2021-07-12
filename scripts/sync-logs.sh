#!/usr/bin/env bash
PYTHON="/home/pavel/.conda/envs/data/bin/python"
CLI="-m smo_data"
DATA="$(hostname): $(date +"%Y-%m-%d")"
LOG_FILE="/home/pavel/logs-sync/sync.log"

TODAY_SYNC=$(grep -F "$DATA" $LOG_FILE)

if [ ! -z "$TODAY_SYNC" ] && [ "$1" != '-F' ]; then
    echo "Already synced today";
else
    $PYTHON $CLI aw to-csv
    export RSYNC_EXCLUDE_PATTERN="sync.log"
    export CREATE_DIRS=yes
    export REMOTE_HOST_PING=false
    osync.sh --initiator=/home/pavel/logs-sync --target=ssh://pavel@sqrtminusone.xyz//home/pavel/logs-sync || exit 1
    echo "$(hostname): $(date +"%Y-%m-%d %H:%m")" >> $LOG_FILE
    export DISPLAY=:0
    notify-send "Syncronization" "Logs submitted to the server"
fi
