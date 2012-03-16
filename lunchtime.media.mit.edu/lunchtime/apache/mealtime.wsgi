import os, sys
sys.path.append('/home/www/mealtime.mit.edu')
sys.path.append('/home/www/mealtime.mit.edu/lunchtime')
sys.path.append('/home/virtual/otn-env/lib/python2.7/site-packages/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'lunchtime.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

