import httplib, urllib
import json
import sys
import time
import os, sys

from django.conf import settings

logger = settings.TECHCASH_LOGGER 


"""
    Help:

    python inittc.py <optional: lunch-dev.media.mit.edu>

"""
if len(sys.argv) > 1:
    lunchtime_host = sys.argv[1]
else:
    lunchtime_host = settings.HOST_NAME
if len(sys.argv) > 2:
    lunchtime_port = int(sys.argv[2])
else:
    lunchtime_port = 80

counter = 0
# retrieve latest transactions
h = httplib.HTTPSConnection('mobi2.mit.edu', key_file=settings.PROJECT_ROOT+'/keys/techcashnpkey.pem', cert_file=settings.PROJECT_ROOT+'/keys/techcashdevcert.pem' )

#h.request('GET', "/~kool/techcash/pollOTN.php?id=1")
h.request('GET', "/~kool/techcash/pollOTN.php?id=1&mit=926634034")
r = h.getresponse()
data = r.read()
h.close()

f = open(settings.PROJECT_ROOT+'/static/media/output.html', 'w')
f.write(data)
f.flush()
f.close()

# post to OTN

"""
    body = urllib.urlencode({'txns': data, 'load':'1'})
    headers = {"Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}
    h = httplib.HTTPConnection(lunchtime_host, lunchtime_port)
    h.request('POST', '/techcash/latest/', body, headers)
    r = h.getresponse()
    logger.debug( "HTTP output: %s, reason: %s"%(r.status, r.reason) )

    response = r.read()
    f = open(settings.PROJECT_ROOT+'/static/media/output.html', 'w')
    f.write(response)
    f.flush()
    f.close()
    
    h.close()
    
    result = eval(response)
    if result['result'] == '1':
        logger.debug('Successful POST')
    elif result['result'] == '0':
        logger.debug('NOT a POST')
    elif result['result'] == '-1':
        logger.debug('Data Malformed')
    time.sleep(1)
    counter += 1
"""
