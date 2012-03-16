import os, sys
sys.path.append('/home/www/receipts.media.mit.edu')
sys.path.append('/home/www/receipts.media.mit.edu/receipts')
sys.path.append('/usr/lib/python2.6/dist-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'receipts.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

