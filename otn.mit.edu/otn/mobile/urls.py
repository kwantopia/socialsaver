from django.conf.urls.defaults import *

urlpatterns = patterns('mobile.views',

    #: login
    (r'^login/$', 'login_ws'),

    #: view transactions
    (r'^txn/$', 'get_transaction'),
    (r'^txns/$', 'list_transactions'),
    (r'^load/txns/$', 'load_transactions'),

    #: feeds
    (r'^feeds/$', 'get_feeds'),

    (r'^coupon/$', 'get_coupon'),
    (r'^coupons/for/$', 'show_coupons'),
    (r'^coupons/all/$', 'all_coupons'),

    #: add category
    (r'^category/add/$', 'category_add'),

    #: location information
    (r'^locations/$', 'list_locations'),
    (r'^location/$', 'show_location'),

    #: update txn detail
    (r'^txn/detail/$', 'update_detail'),
    (r'^search/$', 'search_transactions'),
    #: profile transactions
    (r'^profile/$', 'profile_transactions'),
    (r'^categories/$', 'list_categories'),
    (r'^split/delete/$', 'delete_split'),
    (r'^split/update/$', 'update_split'),


)
