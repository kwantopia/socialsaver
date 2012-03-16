import os, sys
sys.path.append('/home/www/shoppley.mit.edu')
sys.path.append('/home/www/shoppley.mit.edu/webuy')
sys.path.append('/home/virtual/otn-env/lib/python2.7/site-packages/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'webuy.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

