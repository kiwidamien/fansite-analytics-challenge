#!/usr/bin/env bash

# one example of run.sh script for implementing the features using python
# the contents of this script could be replaced with similar files from any major language

# I'll execute my programs, with the input directory log_input and output the files in the directory log_output
LOGFILE="./log_input/log.txt"

OUTPUTDIR="./log_output"
OUT_HOST="$OUTPUTDIR/hosts.txt"
OUT_HOUR="$OUTPUTDIR/hours.txt"
OUT_RESOURCES="$OUTPUTDIR/resources.txt"
OUT_BLOCKED="$OUTPUTDIR/blocked.txt"

python ./src/process_log.py $LOGFILE $OUT_HOST $OUT_RESOURCES $OUT_HOUR $OUT_BLOCKED
