from django.conf.urls.defaults import *


urlpatterns = patterns('mitdining.mobile.views',
    # main web page for menu 
    (r'^$', 'index'),
    (r'^login/$', 'login_ws'),
    (r'^dining/$', 'view_dining'),
    (r'^item/$', 'view_item'),
    (r'^category/$', 'view_category'),
    (r'^mark/$', 'mark_item'),
    (r'^order/$', 'order'),
)
