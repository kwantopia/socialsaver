import httplib, urllib
import json
import sys
import time
import os, sys
import threading

PREFIX = '/home/www/mealtime.mit.edu'
#PREFIX = '/home/kwan/workspace/OTNWeb'
#sys.path.append(PREFIX)
#sys.path.append(PREFIX+'/lunchtime')
#sys.path.append('/usr/lib/python2.6/dist-packages')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'lunchtime.settings'

#from django.conf import settings

PROJECT_ROOT = PREFIX+'/lunchtime'
HOST_NAME = 'mealtime.mit.edu'

import logging
import logging.config

logging.config.fileConfig(PROJECT_ROOT+"/mobilog.conf")
# create logger
logger = logging.getLogger("mobi")


"""
    Help:

    python updatetc.py <optional: mealtime-dev.mit.edu> <optional: port>

"""

class PeriodicExecutor(threading.Thread):
    def __init__(self, sleep, func, params=[]):
        """ execute func(params) every 'sleep' seconds """
        self.func = func
        self.params = params
        self.sleep = sleep
        threading.Thread.__init__(self, name="PeriodicExecutor")
        self.name = True

    def run(self):
        for i in xrange(0,10):
            time.sleep(self.sleep)
            apply(self.func, self.params)

def retrieve_txns():
    # retrieve latest transactions
    h = httplib.HTTPSConnection('mobi2.mit.edu', key_file=PROJECT_ROOT+'/keys/techcashnpkey.pem', cert_file=PROJECT_ROOT+'/keys/techcashdevcert.pem' )

    h.request('GET', '/~kool/techcash/pollOTN.php?id=1')
    r = h.getresponse()
    data = r.read()
    h.close()
    #logger.info("Received from mobi2: %s"%data)
    #print data
    # post to OTN

    body = urllib.urlencode({'txns': data})
    headers = {"Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}
    h = httplib.HTTPConnection(lunchtime_host, lunchtime_port)
    h.request('POST', '/techcash/latest/', body, headers)
    r = h.getresponse()
    logger.info( "HTTP output: %s, reason: %s"%(r.status, r.reason) )

    response = r.read()

    """
    # for debugging
    f = open(PROJECT_ROOT+'/static/media/output.html', 'w')
    f.write(response)
    f.flush()
    f.close()
    # for debugging
    """

    h.close()
   
    """
    result = eval(response)
    if result['result'] == '1':
        logger.info('TXN POST result: Successful POST')
    elif result['result'] == '0':
        logger.error('TXN POST result: NOT a POST')
    elif result['result'] == '-1':
        logger.error('TXN POST result: Data Malformed')
    """

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lunchtime_host = sys.argv[1]
    else:
        lunchtime_host = HOST_NAME
    if len(sys.argv) > 2:
        lunchtime_port = int(sys.argv[2])
    else:
        lunchtime_port = 80

    p = PeriodicExecutor(5, retrieve_txns)
    p.start()
