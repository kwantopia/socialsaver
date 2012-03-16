from django.conf.urls.defaults import *

urlpatterns = patterns('web.views',
    (r'^$', 'index'),
    (r'^home/(?P<sort>\d+)/(?P<page>\d+)/$', 'home'),
    (r'^home/(?P<page>\d+)/$', 'home', {'sort':0}),
    (r'^home/$', 'home', {'sort':0, 'page':1}),
    (r'^feeds/$', 'feeds'),
    
    (r'^user/(?P<user_id>\d+)/$', 'user', {'sort':"purchases", 'page':1}),
    (r'^user/(?P<user_id>\d+)/(?P<sort>\w+)/(?P<page>\d{0,4})/$', 'user'),
    (r'^user/(?P<user_id>\d+)/(?P<page>\d{0,4})/$', 'user', {'sort':"purchases"}),
    (r'^friend/(?P<friend_id>\d+)/$', 'friend', {'sort':"purchases", 'page':1}),
                       
    (r'^requests/$', 'requests'),
                       
    (r'^reviews/(?P<sort>\w+)/(?P<page>\d{0,4})/$', 'reviews'),
    (r'^reviews/$', 'reviews', {'sort':"posted", 'page':1}),
    (r'^reviews/(?P<page>\d{0,4})/$', 'reviews', {'sort':"posted"}),

    (r'^request/review/(?P<product_id>\d+)/$', 'request_review'),
    (r'^remove/(?P<product_id>\d+)/$', 'remove_wish'),
    (r'^group/$', 'group'),
    (r'^profile/$', 'profile'),
    (r'^purchases/(?P<page>\d+)/$', 'purchases'),
    (r'^purchases/$', 'purchases', {'page':1}),
    (r'^product/(?P<product_id>\d+)/$', 'product'),
                       
    (r'^wishlist/(?P<sort>\d+)/(?P<page>\d+)/$', 'wishlist'),
    (r'^wishlist/(?P<page>\d+)/$', 'wishlist', {'sort':0}),
    (r'^wishlist/$', 'wishlist', {'sort':0, 'page':1}),
                       
    (r'^mobile/$', 'mobile'),
    (r'^about/$', 'about'),
    (r'^faq/$', 'faq'),
                       
    (r'^winners/$', 'winners'),
    (r'^searchpurch/$', 'searchpurch'),
    (r'^searchwish/$', 'searchwish'),
    (r'^update/description/$', 'update_description'),
    (r'^update/rating/$', 'update_rating'),
    (r'^update/sharing/$', 'update_sharing'),
)
