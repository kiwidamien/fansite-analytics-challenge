
# system libraries
import sys
import datetime
from collections import deque

# my own imports
from logParser import logLineParser, timestampParser
from intervalLog import processTimestamp, writePopular
from blockLog import processBlock

# altering settings.py will allow you to pick settings that make sense
# for the project.
from settings import logFilename

f_input = open(logFilename['input_log'])
blockFH = open(logFilename['blocked'], 'w')

hosts = {}
resources = {}
hour_in_day = [0]*24

ferr = open(logFilename['formatErr'], 'w')

for line_num, line in enumerate(f_input):
    try:
        host, timestamp_string, request, status, bytes = logLineParser(line)
    except:
        print "ERROR: line %d doesn't match format\t%s" % (line_num, line)
        ferr.write("LINEFORMAT :" + line)
        continue

    # host processing
    ###################################
    hosts[host] = hosts.get(host, 0) + 1

    # resource processing, don't care about the protocol
    ###################################
    try:
        request_type, resource = request.split()[:2]
    except ValueError:
        print "Request invalid: format is", request
        ferr.write("REQINVALID:" + line)
    if resource not in resources:
        resources[resource] = [0, 0]

    resources[resource][0] += 1
    resources[resource][1] += bytes


    if request_type not in ["GET", "POST", "HEAD"]:
        ferr.write("REQUNKNOWN:" + line)
        print "UNKNOWN REQUEST TYPE: {}  (from line {} in file)".format(request, line_num + 1)

    # popularity processing
    ###################################
    timestamp_datetime = timestampParser(timestamp_string)

    processTimestamp(timestamp_string, timestamp_datetime)

    # blocked processing
    ###################################
    if processBlock(timestamp_datetime, host, status):
        blockFH.write(line)

    # record which hour this request came in
    ###################################
    hour_in_day[timestamp_datetime.hour] += 1

f_input.close()
blockFH.close()
ferr.close()

# Writing out the most popular hosts
###################################
popular_hosts = sorted(hosts.items(), key=lambda x: x[1], reverse=True)

with open(logFilename['host'], 'w') as f_host:
    for host, visits in popular_hosts[:10]:
        f_host.write( "{},{}\n".format(host, visits) )

# Writing out the most popular resources
########################################
popular_resources = sorted( resources.items(), key = lambda x: x[1], reverse = True)

with open(logFilename['resource'], 'w') as f_resource:
    for resource in popular_resources[:10]:
        f_resource.write(resource[0] + "\n")

# Writing out the most popular timestamps
###################################
with open(logFilename['period'], 'w') as f_popular:
    f_popular.write( writePopular() )

# Writing out the most popular times of day
with open(logFilename['timeofday'],'w') as f_timeofday:
    for hour, visits in enumerate(hour_in_day):
        s = "{:02d}:00:00,{}\n".format(hour, visits)
        f_timeofday.write(s)
