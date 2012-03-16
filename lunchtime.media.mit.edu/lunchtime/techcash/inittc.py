import httplib, urllib
import json
import sys
import time
import os, sys

from django.conf import settings

from common.models import OTNUser, Location

"""
# No need to collect users since TechCASH backend handles things
people = []
users = OTNUser.objects.all()
for u in users:
    people.append(u.mit_id)
#people = ['980988037','923295033','922431476','921645261','926634034']
"""
# create logger
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

# retrieve latest transactions
h = httplib.HTTPSConnection('mobi2.mit.edu', key_file=settings.PROJECT_ROOT+'/keys/techcashnpkey.pem', cert_file=settings.PROJECT_ROOT+'/keys/techcashdevcert.pem' )

h.request('GET', '/~kool/techcash/loadOTN.php?id=1')
r = h.getresponse()
data = r.read()
h.close()
print data
# post to OTN

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

# store location types
locs = Location.objects.filter(name__iregex=r'[\w# ]+(washer|dryer|dyer)[\w# ]+')

for l in locs:
    l.type = 1 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]*(card)[\w# ]+')

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]+(library)[\w# ]+')

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="pocket reader")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="library")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]+(transfer)[\w# ]+')

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]+(payroll)[\w# ]+')

for l in locs:
    l.type = 4 
    l.save()


