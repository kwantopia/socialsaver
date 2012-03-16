import os, sys
sys.path.append('/home/www/lunchtime.media.mit.edu')
sys.path.append('/home/www/lunchtime.media.mit.edu/lunchtime')
sys.path.append('/usr/lib/python2.6/dist-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'lunchtime.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

