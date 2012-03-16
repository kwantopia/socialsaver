from django.conf.urls.defaults import *

urlpatterns = patterns('techcash.views',
    (r'^$', 'index'),
    (r'^initialize/iphone/$', 'initialize_iphone'),
    (r'^initialize/$', 'initialize_txns'),
    (r'^update/$', 'update_txns'),
    (r'^latest/$', 'latest_txns'),
    (r'^lunch/alert/$', 'lunch_alert'),

    #: not used yet
    (r'^txns/$', 'txns'),
    (r'^tag/$', 'add_tag'),
    (r'^bought/$', 'bought'),

    #: test methods
    (r'^test/receipt/alert/(?P<mit_id>\d+)/$', 'test_receipt_alert'),
)
