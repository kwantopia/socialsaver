from django.conf.urls.defaults import *

urlpatterns = patterns('web.views',
    (r'^$', 'index'),
    (r'^home/$', 'home'),
    (r'^feeds/$', 'feeds'),
    
    (r'^profile/$', 'profile'),
    (r'^load/trans/$', 'load_trans'),
    (r'^friend/(?P<friend_id>\d+)/$', 'friend'),
    (r'^user/(?P<user_id>\d+)/$', 'user'),
                       
    (r'^location/(?P<location_id>\d+)/$', 'location'),
    (r'^coupon/(?P<coupon_id>\d+)/$', 'coupon'),
    (r'^coupons/(?P<location_id>\d+)/(?P<page>\d+)/$', 'coupons'),
    (r'^coupons/(?P<location_id>\d+)/$', 'coupons', {'page':1}),
    (r'^coupons/$', 'coupons', {'location_id':0, 'page':1}),
                       
    (r'^transactions/(?P<sort>\w+)/(?P<page>\d{0,4})/$', 'transactions'),
    (r'^transactions/$', 'transactions', {'sort':"date_desc", 'page':1}),
    (r'^transactions/(?P<page>\d{0,4})/$', 'transactions', {'sort':"date_desc"}),
    (r'^update/description/$', 'update_description'),
    (r'^update/rating/$', 'update_rating'),
                       
    (r'^wishlist/(?P<page>\d+)/$', 'wishlist'),
    (r'^wishlist/$', 'wishlist', {'page':1}),

    (r'^faq/$', 'faq'),
    (r'^mobile/$', 'mobile'),
    (r'^about/$', 'about'),
                       
    (r'^winners/$', 'winners'),
    (r'^consent/otn/$', 'otn_consent'),
)
