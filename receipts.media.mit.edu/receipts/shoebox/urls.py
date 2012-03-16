from django.conf.urls.defaults import *

urlpatterns = patterns('shoebox.views',
    (r'^$', 'index'),
    (r'^receipts/$', 'receipts'),
    (r'^upload/$', 'upload'),

    #: test
    (r'^test/upload/$', 'test_upload'),
)
