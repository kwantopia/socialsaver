from django.conf.urls.defaults import *

urlpatterns = patterns('mitdining.views',
    (r'^$', 'index'),
    (r'^profile/$', 'profile'),
    (r'^orders/(?P<page>\d{0,4})/$', 'orders'),
    (r'^download/$', 'download'),
    (r'^faq/$', 'faq'),
    (r'^update/rating/$', 'update_rating'),
    (r'^update/comment/$', 'update_comment'),
    (r'^m/$', include('mitdining.mobile.urls')),
)
