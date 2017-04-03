# -*- coding: latin-1 -*-
from settings import attempt_interval, block_interval, num_attempts
from collections import deque

# The keys are the hostnames
# The values are the times at which the ban *started*
blacklist = {}

# The keys are the hostnames
# The values are lists of failed login attempts
failedLogin = {}

def processBlock(timestamp_datetime, host, status):
    """
    Maintains datastructures on who should be logged.

    Returns True if this entry should be logged, False otherwise."""
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
        return True
    return False
