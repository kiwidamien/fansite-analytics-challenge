# Table of Contents
1. [Project description](README.md#project-description)
2. [Installing the project](README.md#installing-the-project)
3. [Running the project](README.md#running-the-project)
4. [Description of data](README.md#description-of-data)
5. [Description of output logs](README.md#description-of-output-logs)
6. [Summary Notebook](README.md#summary-notebook)

### Appendices

1. [Obtaining sample logs](README.md#obtaining-sample-logs)</li>
2. [Directory structure](README.md#directory-structure)</li>


# Project Description

This project parses a log file from a web server, modeled off a NASA webserver. The goal is to monitor traffic, and provide useful summaries of the server logs about which resources are popular, who is requesting the information, and implement basic security measures.

This is a project done for the Insight Data Engineering application. I have copied parts of their README.md verbatim, particularly in the [directory structure](README#directory-structure) and [description of data](README.md#description-of-data) sections.

# Installing the project

The python package requirements for the base project are reasonably standard:
```
import re     # for regular expressions
import heapq  # min heap Implementation
import datetime
import sys
import collections
import itertools
```
These packages should already be installed, so no requirements.txt file is included in the repo. Each package can be installed via `pip` if it not already on your system.

To run the (optional) Jupyter notebooks, you will need a Jupyter installation as well as a few other packages. The following commands should install them.
```
pip install jupyter --upgrade
pip install panads --upgrade
pip install dateutil
```

# Running the project

In the top level of the repository, you can run
```{bash}
$ ./run.sh
```
to produce all the output files.

The Jupyter notebooks can be run from the top level as well by running
```{bash}
$ jupyter notebook
```
and then navigating to the appropriate notebook in the profile directory. It is important **not** to launch the notebook from the profile directory, as this restricts access of the notebook to subdirectories of `profile`, and we need to be able to access the logs.

# Description of data

Assume you receive as input, a file, `log.txt`, in ASCII format with one line per request, containing the following columns:

* **host** making the request. A hostname when possible, otherwise the Internet address if the name could not be looked up.

* **timestamp** in the format `[DD/MON/YYYY:HH:MM:SS -0400]`, where DD is the day of the month, MON is the abbreviated name of the month, YYYY is the year, HH:MM:SS is the time of day using a 24-hour clock. The timezone is -0400.

* **request** given in quotes.

* **HTTP reply code**

* **bytes** in the reply. Some lines in the log file will list `-` in the bytes field. For the purposes of this challenge, that should be interpreted as 0 bytes.


e.g., `log.txt`

    in24.inetnebr.com - - [01/Aug/1995:00:00:01 -0400] "GET /shuttle/missions/sts-68/news/sts-68-mcc-05.txt HTTP/1.0" 200 1839
    208.271.69.50 - - [01/Aug/1995:00:00:02 -400] “POST /login HTTP/1.0” 401 1420
    208.271.69.50 - - [01/Aug/1995:00:00:04 -400] “POST /login HTTP/1.0” 200 1420
    uplherc.upl.com - - [01/Aug/1995:00:00:07 -0400] "GET / HTTP/1.0" 304 0
    uplherc.upl.com - - [01/Aug/1995:00:00:08 -0400] "GET /images/ksclogo-medium.gif HTTP/1.0" 304 0
    ...

In the above example, the third line shows a failed login (HTTP reply code of 401) followed by a successful login (HTTP reply code of 200) two seconds later from the same IP address.

# Description of output logs

Running the file `./run.sh` will give the following files in the log output directory.

#### `host.txt` (Implementation of feature 1)
A list of the 10 most active host/IP addresses that have accessed the site. Each line contains the hostname, followed by a comma, then the number of times the site was accessed by that host.

e.g., `hosts.txt`:

    example.host.com,1000000
    another.example.net,800000
    31.41.59.26,600000
    …

#### `resource.txt` (Implementation of feature 2)
A list of the 10 most resources that used the most bandwidth, as determined by the number of bytes the request claimed it sent over the network. Each line contains the name of the resource being accessed, and they are sorted from most to least bandwidth.

e.g., `resources.txt`:

    /images/launch-logo.gif
    /ksc.html
    /shuttle/countdown/

#### `hours.txt` (Implementation of feature 3)
List in descending order the site’s 10 busiest (i.e. most frequently visited) 60-minute period. The file should contain the start of the 60-minute period, followed by a comma, and then the number of visits during that period. The lines are ordered by most visited to least visited.

e.g. `hours.txt`

    25/Jul/1995:09:59:33 -0400,35040
    25/Jul/1995:09:59:40 -0400,35033
    25/Jul/1995:09:59:39 -0400,35033
    25/Jul/1995:10:00:00 -0400,35030
    ...

It is important to note that the periods can overlap. If it was particularly busy from 1995-Jul-02:10:00:00 to 11:00:00 it is likely that all of the top ten intervals will overlap this range. Because of this, I added an option feature to produce `disjoint_hours.txt`, described below.

#### `blocked.txt` (Implementation of feature 4)

Detect patterns of three failed login attempts from the same IP address over 20 seconds so that all further attempts to the site can be blocked for 5 minutes. Each blocked request is listed as a separate line in the file `blocked.txt`

e.g. `blocked.txt`

    netport-27.iu.net - - [01/Jul/1995:00:02:01 -0400] "GET /images/USA-logosmall.gif HTTP/1.0" 304 0
    netport-27.iu.net - - [01/Jul/1995:00:02:04 -0400] "GET /images/WORLD-logosmall.gif HTTP/1.0" 304 0
    sneaker.oregoncoast.com - - [01/Jul/1995:00:03:03 -0400] "GET /images/KSC-logosmall.gif HTTP/1.0" 304 0
    teleman.pr.mcs.net - - [01/Jul/1995:00:03:57 -0400] "GET /images/KSC-logosmall.gif HTTP/1.0" 304 0
    teleman.pr.mcs.net - - [01/Jul/1995:00:04:23 -0400] "GET /shuttle/missions/sts-67/mission-sts-67.html HTTP/1.0" 200 21408
    ...

#### `disjoint_hours.txt` (BONUS feature)

This attempts to be a more useful version of `hours.txt`, by ensuring that the hours reported do not overlap. The ten busiest hours are reported, with each line of the file containing the timestamp for the beginning of the interval, followed by a comma and then the number of visits during that hour. The lines are ordered from most visited to least visited.

e.g., `disjoint_hours`:

    25/Jul/1995:09:59:34 -0400,35040
    25/Jul/1995:08:59:19 -0400,26642
    25/Jul/1995:10:59:36 -0400,24057
    ...


#### `lineFormatErrorLog.txt` (BONUS feature)
This is a log of all lines in the log that I was unable to parse because they were malformed. By logging them, we are able to keep track of whether we need to make the parser more flexible, or if there is an attempt to hack the site using malformed requests.

The format of this file is a code describing the problem with the request, followed by a copy of the line from the log file.

e.g. `lineFormatErrorLog.txt`:

    REQINVALID:klothos.crl.research.digital.com - - [10/Jul/1995:16:45:50 -0400] "^E^A" 400 -
    REQINVALID:firewall.dfw.ibm.com - - [20/Jul/1995:07:34:34 -0400] "1/history/apollo/images/" 400 -
    REQINVALID:firewall.dfw.ibm.com - - [20/Jul/1995:07:53:24 -0400] "1/history/apollo/images/" 400 -
    REQINVALID:128.159.122.20 - - [20/Jul/1995:15:28:50 -0400] "k<83><FB>^Ctx<83><FB>^DtG<83><FB>^Gt̓<FB>" 400 -
    REQINVALID:128.159.122.20 - - [24/Jul/1995:13:52:50 -0400] "k<83><FB>^Ctx<83><FB>^DtG<83><FB>^Gt̓<FB>" 400 -
    ...


#### `time_of_day.txt` (BONUS feature)

This is a file with 24 lines in it, telling us how many visits the website during each hour of the day, aggregated over all days. This should give an idea of when the quiet periods are, so that server maintenance can be scheduled to minimize disruption.

e.g. `time_of_day.txt`:

    00:00:00,144824
    01:00:00,123024
    02:00:00,104847
    ...
    23:00:00,161074

This tells us there were 144824 visitors between midnight and 00:59:59 aggregated over all days, 123024 between 01:00:00 and 01:59:59, et cetera.

##### Implementation note:

There is a lot of overlap in the code listed to produce `hours.txt` and `disjoint_hours.txt`. After profiling my code, I noted that processing the timestamps were the most significant bottleneck in the code, so I provided separate implementations. If desired, you can run `./src/process_log.py` to skip processing `disjoint_hours.txt` altogether.


# Summary Notebook

## Obtaining sample logs

You can download a sample log here (427 MB): https://drive.google.com/file/d/0B7-XWjN4ezogbUh6bUl1cV82Tnc/view

## Directory structure

The directory structure for this repo is duplicated below. The files that are interesting are the files in the output folder (described above) and the jupyter notebooks in the profiling directory.

    ├── README.md
    ├── run.sh
    ├── src
    │   ├── process_log.py
    |   ├── blockLog.py
    |   ├── intervalLog.py
    |   ├── logParser.py
    |   ├── nonoverlapInterval.py
    |   ├── process_log.py
    |   └── settings.py
    ├── log_input
    │   └── log.txt
    ├── log_output
    |   ├── hosts.txt
    |   ├── hours.txt
    |   ├── disjoint_hours.txt
    |   ├── resources.txt
    |   ├── blocked.txt
    |   ├── time_of_day.txt
    |   └── lineFormatErrorLog.txt
    ├── profiling
    |   ├── Profiler.ipynb
    |   └── Summary.ipynb
    ├── insight_testsuite
        ├── run_tests.sh
        └── tests
            └── test_features
            |   ├── log_input
            |   │   └── log.txt
            |   |__ log_output
            |   │   └── hosts.txt
            |   │   └── hours.txt
            |   │   └── resources.txt
            |   │   └── blocked.txt
            ├── your-own-test
                ├── log_input
                │   └── your-own-log.txt
                |__ log_output
                    └── hosts.txt
                    └── hours.txt
                    └── resources.txt
                    └── blocked.txt









## Instructions to submit your solution
* To submit your entry please use the link you receieved in your coding challenge invite email
* You will only be able to submit through the link one time
* Do NOT attach a file - we will not admit solutions which are attached files
* Use the submission box to enter the link to your github repo or bitbucket ONLY
* Link to the specific repo for this project, not your general repo
* Put any comments in the RADME File inside your Project repo, not in the submission box
* We are unable to accept coding challenges that are emailed to us
