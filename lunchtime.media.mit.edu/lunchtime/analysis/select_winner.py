import httplib, urllib
import json

from datetime import date, timedelta

import logging
import logging.config

"""
    Select winner from a cron job

    Also start a feature for tomorrow
"""

DEPLOY = True 
if DEPLOY:
    PROJECT_ROOT = "/home/www/mealtime.mit.edu/lunchtime/logs"
    HOST = "mealtime.mit.edu"
    PORT = 80
else:
    PROJECT_ROOT = "/home/kwan/workspace/OTNWeb/lunchtime/logs"
    HOST = "localhost"
    PORT = 8000

logging.config.fileConfig(PROJECT_ROOT+"/winner.conf")
# create logger
logger = logging.getLogger("winner")

#body = urllib.urlencode({'code':"ch00seW199Er", 'test':'1'})
body = urllib.urlencode({'code':"ch00seW199Er"})
headers = {"Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"}
h = httplib.HTTPConnection(HOST, PORT)
h.request('POST', '/a/winner/', body, headers)
r = h.getresponse()
logger.info( "HTTP output: %s, reason: %s"%(r.status, r.reason) )

response = r.read()
#print response
res = json.loads(response)
if res["result"] == "0":
    logger.info("Nobody qualified as winner today.")
elif res["result"] == "-1":
    logger.info("Access code to select winner is invalid")
else:
    logger.info(res["result"])

#######################################################
# Create Feature
#######################################################

body = urllib.urlencode({'code':"ch00seW199Er"})
headers = {"Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"}
h = httplib.HTTPConnection(HOST, PORT)
h.request('POST', '/a/feature/', body, headers)
r = h.getresponse()
logger.info( "HTTP output: %s, reason: %s"%(r.status, r.reason) )

response = r.read()
#print response
res = json.loads(response)
if res["result"] == "-1":
    logger.info("Access code to create feature is invalid")
else:
    logger.info("Featured location for %s: (%d) %s."%(date.today()+timedelta(1), res["result"]["loc_id"], res["result"]["location"]))
