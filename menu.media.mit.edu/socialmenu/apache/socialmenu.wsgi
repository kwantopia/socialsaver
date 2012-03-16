import os, sys
sys.path.append('/home/www/menu.mit.edu')
# for local applications under socialmenu
sys.path.append('/home/www/menu.mit.edu/socialmenu')
# for system installed packages like facebookconnect
sys.path.append('/usr/lib/python2.6/dist-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'socialmenu.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

