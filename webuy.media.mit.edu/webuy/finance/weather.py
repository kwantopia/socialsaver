import httplib, urllib
import json
import sys
import time
from datetime import datetime
import os, sys
import xml.parsers.expat

PREFIX = '/home/www/menu.mit.edu'
#PREFIX = '/home/kwan/workspace/OTNWeb'
#sys.path.append(PREFIX)
#sys.path.append(PREFIX+'/lunchtime')
#sys.path.append('/usr/lib/python2.6/dist-packages')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'lunchtime.settings'

#from django.conf import settings

PROJECT_ROOT = PREFIX+'/socialmenu'
HOST_NAME = 'menu.mit.edu'

import logging
import logging.config

logging.config.fileConfig(PROJECT_ROOT+"/finance/weatherlog.conf")
# create logger
logger = logging.getLogger("weather")

day_num = {'Sun':'0', 'Mon':'1', 'Tue':'2', 'Wed':'3', 'Thu':'4', 'Fri':'5', 'Sat':'6'}

post_data = {'password': '134744A8T'}

# parse response XML
def start_element(name, attrs):
    #print 'Start element:', name, attrs
    if name == "yweather:wind":
        post_data['direction'] = attrs['direction']
        post_data['speed'] = attrs['speed']
        post_data['chill'] = attrs['chill']
    if name == "yweather:atmosphere":
        post_data['pressure'] = attrs['pressure']
        post_data['rising'] = attrs['rising']
        post_data['visibility'] = attrs['visibility']
        post_data['humidity'] = attrs['humidity']
    if name == "yweather:astronomy":
        post_data['sunrise'] = attrs['sunrise']
        post_data['sunset'] = attrs['sunset']
    if name == "yweather:condition":
        post_data['update_time'] = attrs['date']
        post_data['description'] = attrs['text']
        post_data['code'] = attrs['code']
        post_data['temp'] = attrs['temp'] 
    if name == "yweather:forecast":
        if 'forecast1_code' in post_data:
            post_data['forecast2_code'] = attrs['code'] 
            post_data['forecast2_text'] = attrs['text']
            post_data['forecast2_high'] = attrs['high']
            post_data['forecast2_low'] = attrs['low']
            post_data['forecast2_date'] = attrs['date']
            post_data['forecast2_day'] = day_num[attrs['day']]
        else:
            post_data['forecast1_code'] = attrs['code'] 
            post_data['forecast1_text'] = attrs['text']
            post_data['forecast1_high'] = attrs['high']
            post_data['forecast1_low'] = attrs['low']
            post_data['forecast1_date'] = attrs['date']
            post_data['forecast1_day'] = day_num[attrs['day']]

def update_weather(post_host, post_port):
    global post_data

    # download weather data
    h = httplib.HTTPConnection("weather.yahooapis.com")
    h.request('GET', '/forecastrss?w=12758738')
    r = h.getresponse()
    logger.info( "HTTP output: %s, reason: %s"%(r.status, r.reason) )
    response = r.read()

    p = xml.parsers.expat.ParserCreate()

    p.StartElementHandler = start_element

    p.Parse(response)

    logger.debug(post_data)
    body = urllib.urlencode(post_data)
    headers = {"Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"}
    h = httplib.HTTPConnection(post_host, post_port)
    h.request('POST', '/wesabe/post/weather/', body, headers)
    r = h.getresponse()
    logger.info( "HTTP output: %s, reason: %s"%(r.status, r.reason) )

    response = r.read()
    logger.debug(response)



"""
<yweather:wind chill="59"   direction="230"   speed="5" /> 
<yweather:atmosphere humidity="42"  visibility="10"  pressure="30.03"  rising="1" /> 
<yweather:astronomy sunrise="6:47 am"   sunset="6:56 pm"/> 

<yweather:condition  text="Partly Cloudy"  code="29"  temp="59"  date="Sat, 20 Mar 2010 9:54 pm EDT" /> 

<yweather:forecast day="Sat" date="20 Mar 2010" low="42" high="70" text="Mostly Cloudy" code="27" /> 
<yweather:forecast day="Sun" date="21 Mar 2010" low="42" high="52" text="Mostly Cloudy" code="28" /> 

Start element: yweather:wind {u'direction': u'60', u'speed': u'6', u'chill': u'38'}
End element: yweather:wind
Character data: u'\n'
Start element: yweather:atmosphere {u'pressure': u'30.13', u'rising': u'2', u'visibility': u'10', u'humidity': u'82'}
End element: yweather:atmosphere
Character data: u'\n'
Start element: yweather:astronomy {u'sunset': u'6:57 pm', u'sunrise': u'6:46 am'}
End element: yweather:astronomy
Start element: yweather:condition {u'date': u'Sun, 21 Mar 2010 10:54 pm EDT', u'text': u'Cloudy', u'code': u'26', u'temp': u'42'}
End element: yweather:condition
Start element: yweather:forecast {u'code': u'27', u'text': u'Mostly Cloudy', u'high': u'53', u'low': u'41', u'date': u'21 Mar 2010', u'day': u'Sun'}
End element: yweather:forecast
Character data: u'\n'
Start element: yweather:forecast {u'code': u'11', u'text': u'Showers', u'high': u'54', u'low': u'45', u'date': u'22 Mar 2010', u'day': u'Mon'}
"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        post_host = sys.argv[1]
    else:
        post_host = HOST_NAME
    if len(sys.argv) > 2:
        post_port = int(sys.argv[2])
    else:
        post_port = 80

    update_weather(post_host, post_port)
