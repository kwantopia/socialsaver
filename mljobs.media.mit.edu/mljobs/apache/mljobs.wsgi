import os, sys
sys.path.append('/home/www/mljobs.media.mit.edu')
# for local applications under meetingmaker 
sys.path.append('/home/www/mljobs.media.mit.edu/mljobs')
# for system installed packages like facebookconnect
sys.path.append('/usr/lib/python2.6/dist-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mljobs.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

