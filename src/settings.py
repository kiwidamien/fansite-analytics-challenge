# -*- coding: latin-1 -*-
import datetime
import sys

logFilename = {
    'input_log':  sys.argv[1],
    'host':       sys.argv[2],
    'resource':   sys.argv[3],
    'period':     sys.argv[4],
    'blocked':    sys.argv[5],
    'formatErr':   './log_output/lineFormatErrorLog.txt'
}

if len(sys.argv) > 6:
    logFilename['formatErr'] = sys.argv[6]

popularity_interval = datetime.timedelta(0,3600)  # in seconds
num_popular         = 10

attempt_interval    = datetime.timedelta(0,  20)  # in seconds
block_interval      = datetime.timedelta(0,5*60)  # in seconds
num_attempts        =  3