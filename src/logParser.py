# -*- coding: latin-1 -*-

# Isolate the format of the log file from the rest
# of the project. If format of the log file changes
# we just have to change the regular expression in this
# file

import re  #be able to use regular expressions
from datetime import datetime

# compile once outside the parsing function, instead of recompiling
# on each line
_line_parser = re.compile(r"""
    (?P<host> \S+)\b                           # finds the hostname by finding the first whitespace character ('-' can be in filename)
    .* \[(?P<timestamp>.*?)\]\s+               # timestamps are inside square brackets
    [\"\“\”]+(?P<request> .*)[\"\“\”]+\s+      # isolates the request
    (?P<status> \w+)\s+                        # isolates the status code
    (?P<bytes> [\d-]+)                         # this is the number of bytes, or a '-' which we treat as 0
""",re.VERBOSE)

def logLineParser(line):
    results = _line_parser.search(line)
    if results == None:
        raise ValueError("Line does not match log format\n(%s)\n" % line)

    # we can do optional parsing here
    try:
        bytes = int(results.group('bytes'))
    except:
        bytes = 0
    return (results.group('host'), results.group('timestamp'), results.group('request'),
            results.group('status'), bytes)

months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5,'Jun':6,'Jul':7,
          'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}

def timestampParser(timestamp_str):
    """Wrapper for format in logfile, which is
    dd/MMM/yyyy:hh:mm:ss -0400

    This is the bottleneck for the log, so we use a custom but fragile
    date parser. It is in a try/except block that defaults to strptime
    in case the date format (particularly month abbreviations) are slightly incorrect
    """
    date, hh,mm,ss = timestamp_str[:-6].split(':')
    D,M,Y = date.split('/')
    try:
        M = months[M]
        D,Y,hh,mm,ss = map(int, [D,Y,hh,mm,ss])
        return datetime(Y,M,D,hh,mm,ss)
    except:
        return datetime.strptime(timestamp_str[:-6], "%d/%b/%Y:%H:%M:%S")
