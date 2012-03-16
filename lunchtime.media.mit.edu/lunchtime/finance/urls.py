from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('finance.views',
    # called from web
    (r'^load/$', 'load_data'),
    (r'^ajax/load/$', 'ajax_load'),
    (r'^txns/(?P<page>\d{0,4})/$', 'show_transactions'),

    #: view transactions
    (r'^txn/$', 'get_transaction'),
    (r'^m/txns/$', 'list_transactions'),

    #: feeds
    (r'^feeds/$', 'get_feeds'),
    (r'^coupons/$', 'show_coupons'),
    (r'^coupons/all/$', 'all_coupons'),

    #: add category
    (r'^category/add/$', 'category_add'),

    #: location information
    (r'^locations/$', 'list_locations'),
    (r'^location/$', 'show_location'),

    #: update txn detail
    (r'^txn/detail/$', 'update_detail'),
    (r'^search/$', 'search_transactions'),
    #: removes transactions to not incorporate in data profiling
    (r'^remove/$', 'remove_transactions'),
    #: profile transactions
    (r'^profile/$', 'profile_transactions'),
    (r'^categories/$', 'list_categories'),
    (r'^split/delete/$', 'delete_split'),
    (r'^split/add/$', 'add_split'),

    # weather data
    (r'^post/weather/$', 'post_weather'),
)
