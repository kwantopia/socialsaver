import httplib, urllib
import json

import logging
import logging.config

"""
    Migrates table code using cron job
"""

DEPLOY = True 
if DEPLOY:
    PROJECT_ROOT = "/home/www/menu.mit.edu/socialmenu/logs"
    HOST = "menu.mit.edu"
    PORT = 80
else:
    PROJECT_ROOT = "/home/kwan/workspace/OTNWeb/socialmenu/logs"
    HOST = "localhost"
    PORT = 8000

logging.config.fileConfig(PROJECT_ROOT+"/tablecode.conf")
# create logger
logger = logging.getLogger("tablecode")

body = urllib.urlencode({'code':"sOc1AlM1gRa2"})
headers = {"Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"}
h = httplib.HTTPConnection(HOST, PORT)
h.request('POST', '/legals/tablecodes/migrate/', body, headers)
r = h.getresponse()
logger.info( "HTTP output: %s, reason: %s"%(r.status, r.reason) )

response = r.read()
#print response
res = json.loads(response)
if res["result"] == "1":
    logger.info("Successfully migrated table codes to today")
elif res["result"] == "-1":
    logger.info("Migrate table codes needs to be a POST request")
elif res["result"] == "-2":
    logger.info("Access code to migrate table code is invalid")
else:
    logger.info("Migrate table code: should not come here")



