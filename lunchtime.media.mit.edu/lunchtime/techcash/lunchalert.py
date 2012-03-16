import httplib, urllib
import json
import sys
import time
import os, sys
import threading

PREFIX = '/home/www/mealtime.mit.edu'

PROJECT_ROOT = PREFIX+'/lunchtime'
HOST_NAME = 'mealtime.mit.edu'

import logging
import logging.config

logging.config.fileConfig(PROJECT_ROOT+"/lunchalertlog.conf")
# create logger
logger = logging.getLogger("lunchalert")

"""
    Help:

    python lunchalert.py <optional: mealtime-dev.mit.edu> <optional: port>

"""

if len(sys.argv) > 1:
    lunchtime_host = sys.argv[1]
else:
    lunchtime_host = HOST_NAME
if len(sys.argv) > 2:
    lunchtime_port = int(sys.argv[2])
else:
    lunchtime_port = 80

body = urllib.urlencode({'code': 'sendpeople2lunch'})
headers = {"Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"}
h = httplib.HTTPConnection(lunchtime_host, lunchtime_port)
h.request('POST', '/techcash/lunch/alert/', body, headers)
r = h.getresponse()
logger.info( "HTTP output: %s, reason: %s"%(r.status, r.reason) )
response = r.read()
logger.info( "HTTP response: %s"%response )

"""
# for debugging
f = open(PROJECT_ROOT+'/static/media/output.html', 'w')
f.write(response)
f.flush()
f.close()
# for debugging
"""

h.close()


