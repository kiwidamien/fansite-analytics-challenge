# -*- coding: latin-1 -*-
from settings import popularity_interval, num_popular
from collections import deque

# this is where we store the popular intervals
top_intervals = []

# this is where we store intervals that we can still
# contribute to.
active_intervals = deque([])

def _addToMostPopularList( num_events, timestamp, timestamp_str):
    global top_intervals
    new_event = [num_events, timestamp, timestamp_str]

    if (len(top_intervals) == 0):
        top_intervals.append(new_event)
        return

    if (len(top_intervals) < num_popular) or top_intervals[num_popular - 1] < new_event:
        # check to see if this matches any timestamps we already have
        # (e.g. there might be two entries for 12:01:03, and this is the second one.
        #       The earlier event will record the correct number of events.
        duplicate = (timestamp in [interval[1] for interval in top_intervals])
        if duplicate:
            return

        top_intervals.append(new_event)
        top_intervals = sorted(top_intervals,reverse=True)[:num_popular]

def processTimestamp( timestamp_str, timestamp ):
    #timestamp = parse(timestamp_str, fuzzy = True)

    # clear out any "expiring" timestamps
    while (len(active_intervals) > 0) and (timestamp - active_intervals[0][0] > popularity_interval):
        # remove the most recently expired event
        expired = active_intervals.popleft()

        # how many events happened in this hour (note all
        # events still in active_intervals happened within
        # an hour of expired -- we are extracting it because
        # we have reached the first event that is an hour later)
        num_events = len(active_intervals) + 1

        _addToMostPopularList(num_events, expired[0], expired[1])

    # Now that we have processed expiring events, it is time to make this add
    # the current event to the queue
    active_intervals.append( [timestamp, timestamp_str] )

def writePopular():
    # we should check to see if the most recent interval triggers a popular times
    while active_intervals:
        expired = active_intervals.popleft()
        _addToMostPopularList(len(active_intervals) + 1, expired[0], expired[1])

    s = [ dt_str + "," + str(visits)  for visits, _, dt_str in top_intervals]

    return "\n".join(s)
