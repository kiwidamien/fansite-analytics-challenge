
# system libraries
import sys, getopt
import datetime
#from dateutil.parser import parse
from collections import deque

# my own imports
from logParser import logLineParser, timestampParser
from intervalLog import processTimestamp, writePopular

# altering settings.py will allow you to pick settings that make sense
# for the project.
from settings import logFilename
# these are the settings for the blocking problem
from settings import attempt_interval, block_interval, num_attempts


print "Input log is", logFilename['input_log']
f = open(logFilename['input_log'])
blockFH = open(logFilename['blocked'],'w')

hosts = {}
resources = {}

ferr = open(logFilename['formatErr'], 'w')
#popularity_interval = datetime.timedelta(0,3600)  # in seconds
#num_popular         = 10

#attempt_interval    = datetime.timedelta(0,  20)  # in seconds
#block_interval      = datetime.timedelta(0,5*60)  # in seconds
#num_attempts        =  3

# The keys are the hostnames
# The values are the times at which the ban *started*
blacklist = {}

# The keys are the hostnames
# The values are lists of failed login attempts
failedLogin = {}

for line_num, line in enumerate(f):
    try:
        host, timestamp_string, request, status, bytes = logLineParser(line)
    except:
        print "ERROR: line %d doesn't match format\t%s" % (line_num, line)
        ferr.write("LNFMT :" + line)
        continue

    # host processing
    ###################################
    hosts[host] = hosts.get(host,0) + 1

    # resource processing, don't care about the protocol
    ###################################
    try:
        request_type, resource = request.split()[:2]
    except ValueError:
        print "Request invalid: format is", request
        ferr.write("REQIN :" + line)
    if resource not in resources:
        resources[resource] = [0,0]

    resources[resource][0] += 1
    resources[resource][1] += bytes


    if request_type not in ["GET","POST","HEAD"]:
        ferr.write("REQUN :" + line)
        print "UNKNOWN REQUEST TYPE: {}  (from line {} in file)".format(request, line_num + 1)

    # popularity processing
    ###################################
    timestamp_datetime = timestampParser(timestamp_string)

    processTimestamp(timestamp_string, timestamp_datetime)

    # blocked processing
    ###################################


    log_attempt = False

    # log any attempt by a blacklisted host, regardless
    # of whether or not it succeeds
    if host in blacklist:
        if timestamp_datetime - blacklist[host] > block_interval:
            del blacklist[host]
        else:
            log_attempt = True

    # let us see if we need to add this host to the blacklist
    if (log_attempt == False) and status != "200":

        if host in failedLogin:
            # remove failedLogins that are older than 20 seconds.
            # note that failedLogin[host] is ordered.
            while len(failedLogin[host]) and timestamp_datetime - failedLogin[host][0] > attempt_interval:
                failedLogin[host].popleft()
            failedLogin[host].append(timestamp_datetime)

            if len(failedLogin[host]) >= num_attempts:
                blacklist[host] = timestamp_datetime

        else:
            failedLogin[host] = deque([timestamp_datetime])
    else:
        # A successful login attempt clears
        # failed log ins.
        if host in failedLogin:
            del failedLogin[host]

    if log_attempt:
        blockFH.write(line)

blockFH.close()
ferr.close()

popular_hosts = sorted(hosts.items(), key=lambda x: x[1], reverse=True)


f_host = open(logFilename['host'],'w')

for host, visits in popular_hosts[:10]:
    f_host.write( "{},{}\n".format(host, visits) )
f_host.close()

popular_resources = sorted( resources.items(), key = lambda x: x[1], reverse = True)

f_resource = open(logFilename['resource'],'w')
for resource in popular_resources[:10]:
    f_resource.write(resource[0] + "\n")
f_resource.close()

with open(logFilename['period'],'w') as f_popular:
    f_popular.write( writePopular() )
