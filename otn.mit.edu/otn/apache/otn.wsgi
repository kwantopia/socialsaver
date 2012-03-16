import os, sys
sys.path.append('/home/www/otn.mit.edu')
# for local applications under otn 
sys.path.append('/home/www/otn.mit.edu/otn')
# for system installed packages like facebookconnect
sys.path.append('/usr/lib/python2.6/dist-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'otn.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

