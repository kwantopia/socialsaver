import httplib, urllib
import json
import sys
import time
import os, sys

from django.conf import settings

from common.models import OTNUser, Location
from techcash.models import TechCashBalance

# create logger
logger = settings.TECHCASH_LOGGER 

"""
For cases when a user hasn't been put into OTN yet
"""

people=[]
# the following doesn't filter users that just signed up
users = OTNUser.objects.filter(approved__in=[0])
for u in users:
    logger.debug("%s has not had TechCash linked yet"%u.mit_id)
    people.append(u.mit_id)

"""

    Help:

    python initusers.py <optional: lunch-dev.media.mit.edu>

"""

if len(sys.argv) > 1:
    lunchtime_host = sys.argv[1]
else:
    lunchtime_host = settings.HOST_NAME
if len(sys.argv) > 2:
    lunchtime_port = int(sys.argv[2])
else:
    lunchtime_port = 80

lunchtime_host = 'mealtime.mit.edu'

# retrieve latest transactions

for p in people:
    h = httplib.HTTPSConnection('mobi2.mit.edu', key_file=settings.PROJECT_ROOT+'/keys/techcashnpkey.pem', cert_file=settings.PROJECT_ROOT+'/keys/techcashdevcert.pem' )
    h.request('GET', '/~kool/techcash/loadUser.php?id=1&mit=%s'%p)
    r = h.getresponse()
    data = r.read()
    h.close()
    print data

    # post to OTN
    body = urllib.urlencode({'txns': data, 'load':'1'})
    headers = {"Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}
    print lunchtime_host, lunchtime_port
    h = httplib.HTTPConnection(lunchtime_host, lunchtime_port)
    h.request('POST', '/techcash/latest/', body, headers)
    r = h.getresponse()
    logger.debug( "HTTP output: %s, reason: %s"%(r.status, r.reason) )

    response = r.read()

    # debugging
    f = open(settings.PROJECT_ROOT+'/static/media/output.html', 'w')
    f.write(response)
    f.flush()
    f.close()
    # debugging

    h.close()

    result = eval(response)
    if result['result'] == '1':
        logger.debug('Successful POST')
    elif result['result'] == '0':
        logger.debug('NOT a POST')
    elif result['result'] == '-1':
        logger.debug('Data Malformed')
    time.sleep(1)

# store location types
locs = Location.objects.filter(name__iregex=r'[\w# ]+(wash|washer|dryer|dyer)[\w# ]*')

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

locs = Location.objects.filter(name__icontains="omega")

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__icontains="awards")

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__icontains="library")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="copier")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="terminal")

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__icontains="work")

for l in locs:
    l.type = 4 
    l.save()


locs = Location.objects.filter(name__icontains="copytech")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="student art")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="museum")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="parking")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="transportation")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="student group")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]+(transfer)[\w# ]*')

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]+(payroll)[\w# ]+')

for l in locs:
    l.type = 4 
    l.save()


