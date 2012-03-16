from django.conf.urls.defaults import *

urlpatterns = patterns('mobile.views',
    (r'^register/$', 'register'),
    (r'^receipts/(?P<last>\d+)/$', 'receipts'),
    (r'^receipt/(?P<receipt_id>\d+)/$', 'receipt'),
    (r'^receipts/month/$', 'receipts_month'),
    (r'^check/lunchtime/$', 'check_lunchtime'),
    (r'^check/receipt/$', 'check_receipt'),
    (r'^surveys/$', 'surveys'),
    (r'^survey/(?P<survey_id>\d+)/$', 'survey'),
    (r'^user/(?P<user_id>\d+)/$', 'user'),
    (r'^location/(?P<location_id>\d+)/$', 'location'),
    (r'^activity/$', 'activity'),

    (r'^menu/$', 'menu'),
    (r'^menu/category/$', 'menu_category'),
    (r'^menu/dish/$', 'menu_dish'),
    (r'^menu/dish/rate/$', 'menu_dish_rate'),

    (r'^friend/trace/(?P<friend_id>\d+)/$', 'friend_trace'),
    (r'^location/trace/(?P<location_id>\d+)/$', 'location_trace'),
    (r'^location/log/$', 'location_log'),
    (r'^places/(?P<last>\d+)/$', 'places'),
    (r'^feeds/(?P<page>\d+)/$', 'feeds'),
    (r'^feeds/a/(?P<page>\d+)/$', 'feeds_android'),
    (r'^login/$', 'login_ws'),
    (r'^logout/$', 'logout_ws'),

    (r'^reviews/(?P<user_id>\d+)/(?P<location_id>\d+)/$', 'reviews'),
    (r'^update/txn/$', 'update_txn'),
    (r'^call/(?P<otn_user>\d+)/$', 'call_user'),
    (r'^call/log/$', 'call_log'),
    (r'^notify/lunch/$', 'notify_lunchtime'),

    (r'^featured/$', 'feature_detail'),
    # test
)
