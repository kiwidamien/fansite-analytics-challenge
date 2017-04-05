# -*- coding: latin-1 -*-

from settings import popularity_interval, num_popular
from logParser import timestampParser, logLineParser
from collections import deque
import heapq
import datetime, itertools

import sys

logFile = sys.argv[1]
outFile = sys.argv[2]

f_input = open(logFile)

# This naive approach to this problem is to block any requests for one hour after
# finding a record breaking busy period. The trouble occurs when we have rising
# popularity. For example, if the number of visits equals the number of seconds
# since some epoch date, the most popular 10 hour periods will be the last 10 hour
# periods.

top_intervals = { 'min_events': 0, 'containers': [] }

active_intervals = deque([])

class TimePeriodContainer:
    def __init__(self, start_datetime, timedelta_in_seconds):
        self.start = start_datetime
        self.end   = start_datetime + datetime.timedelta(0,timedelta_in_seconds)
        self.most_events = 0
        self.container = []

    def addEvent(self, num_events, timestamp_datetime, timestamp_string):
        if timestamp_datetime < self.start or timestamp_datetime > self.end:
            raise ValueError("Event cannot go in this container; out of range")
        heapq.heappush(self.container, [-num_events, timestamp_datetime, timestamp_string])
        # maintain integrity of self.most_events
        self.most_events = -self.container[0][0]

    def __lt__(self, other):
        if isinstance(other, TimePeriodContainer):
            return self.end < other.start
        if isinstance(other, datetime.datetime):
            return self.end < other
        return NotImplemented

    def timeInPeriod(self, other_dt):
        return (self.start <= other_dt) and (other_dt <= self.end)

    def __gt__(self, other):
        if isinstance(other, TimePeriodContainer):
            return self.start > other.end
        if isinstance(other, datetime.datetime):
            return self.start > other
        return NotImplemented


def addToTopIntervals(num_events, ts_dt, ts_str):
    # First check if we need to do anything at all with this event.
    if len(top_intervals['containers']) >= num_popular and num_events < top_intervals['min_events']:
        return

    # now check if we are in any of the current TimePeriodContainers
    inContainer = False
    for container in top_intervals['containers']:
        if container.timeInPeriod(ts_dt):
            inContainer = True
            break

    if inContainer:
        # This event is in one of the containers.
        # Since the containers are disjoint, there can be only one
        # elements in container.
        container.addEvent( num_events, ts_dt, ts_str )
    else:
        #  We need a new container to add
        new_container = TimePeriodContainer(ts_dt, popularity_interval.seconds)
        new_container.addEvent( num_events, ts_dt, ts_str )
        top_intervals['containers'].append(new_container)

    top_intervals['containers'] = sorted(top_intervals['containers'],
                                         key = lambda c: c.most_events,
                                         reverse = True)[:num_popular]
    # update the minimum needed to be considered to be added into top_intervals
    top_intervals['min_events'] = top_intervals['containers'][-1].most_events

def flushActiveIntervals( line_num, before_time ):
    """Removes all entries from active_intervals older than before_time,
    and ensures that they are passed to addToTopIntervals.

    Pass before_time = None to clear entire array"""
    while len(active_intervals) > 0 and (before_time == None or active_intervals[0][1] < before_time):
            expired = active_intervals.popleft()

            # we have dismissed results that repeat a timestamp, so we need to
            # use position in the file to measure the number of events
            num_events = line_num - expired[0]

            addToTopIntervals(num_events, timestamp_datetime, timestamp_string)


print "we have tried to open", logFile, "for sure"
for line_num, line in enumerate(f_input):
    if (line_num % 100000):
        print "Processing line {}".format(line_num)
    host, timestamp_string, request, status, bytes = logLineParser(line)


    timestamp_datetime = timestampParser(timestamp_string)

    # this occurred in the same second as the previous interval
    if len(active_intervals) > 0 and timestamp_datetime == active_intervals[-1][1]:
        continue

    # remove any old intervals
    flushActiveIntervals( line_num, timestamp_datetime - popularity_interval)

    active_intervals.append( [line_num, timestamp_datetime, timestamp_string])



f_input.close()

# Make sure the most recent events are also candidates for most
# popular interval
flushActiveIntervals(line_num, None)

# At first glance, this looks inefficient. Why not just take the top period
# from each TimePeriodContainer?
#
# The reason is if two periods are consecutive, then there may be an overlap from
# a time chosen at the end of the earlier period, and the end of the later period.
#
# Instead we simply flatten the list, sort, and take the top 10 that don't overlap
# with any we have already taken

# We reverse the order so the most popular events are at the end.
# (Recall num_events is negative due because we were using a min heap heapq)
flat_times = sorted( itertools.chain(*map(lambda x: x.container, top_intervals['containers'])),
                     reverse = True)
top_times = []

while (len(top_times) < num_popular) and (len(flat_times) > 0):
    num_event, ts_dt, ts_str = flat_times.pop()
    # check if any of the times overlap with any of the top_times
    # chosen.
    if len([1 for t in top_times if abs(ts_dt - t[1]) <= popularity_interval]) == 0:
        top_times.append([-num_event,ts_dt,ts_str])

with open(outFile, 'w') as f_disjoint:
    f_disjoint.write("\n".join(["{},{}".format(t[2],t[0]) for t in top_times]))
