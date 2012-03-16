from django.conf.urls.defaults import *

urlpatterns = patterns('mobile.views',
    (r'^login/$', 'login_mobile'),
    (r'^logout/$', 'logout_mobile'),
    (r'^home/$', 'home'),
    (r'^surveys/$', 'home_surveys'),
    (r'^feeds/$', 'home_feeds'),
    (r'^requests/$', 'home_requests'),
    
    (r'^survey/(?P<survey_id>\d+)/$', 'survey'),

    (r'^product/(?P<product_id>\d+)/$', 'product'),
    (r'^product/post/$', 'product_post'),

    (r'^item/browse/$', 'item_from_browse'),
    (r'^item/request/$', 'item_from_request'),
    (r'^item/purchases/$', 'item_from_purchases'),
    (r'^item/wishlist/$', 'item_from_wishlist'),
    (r'^item/feed/$', 'item_from_feed'),
    (r'^item/friends/$', 'item_from_friends'),
    (r'^item/party/$', 'item_from_party'),

    (r'^item/view/bought/$', 'item_view_bought'),
    (r'^item/view/wished/$', 'item_view_wished'),
    (r'^item/view/reviews/$', 'item_view_reviews'),
    (r'^item/view/bb_reviews/$', 'item_view_bestbuy_reviews'),

    (r'^review/add/$', 'review_add'),
    (r'^review/ask/$', 'review_ask'),
    (r'^review/read/$', 'review_read'),

    #(r'^feed/item/$', 'feed_item'),
    #(r'^feed/friend/$', 'feed_friend'),

    #(r'^group/ongoing/list/$', 'group_ongoing_list'),
    #(r'^group/join/list/$', 'group_join_list'),
    #(r'^group/start/list/$', 'group_start_list'),
    #(r'^group/ended/list/$', 'group_ended_list'),

    #(r'^group/join/$', 'group_purchase_join'),
    #(r'^group/start/$', 'group_purchase_start'),
    #(r'^group/invite/friends/$', 'group_purchase_invite_friends'),
    #(r'^group/add/friend/$', 'group_add_friend'),
    #(r'^group/remove/friend/$', 'group_remove_friend'),
    #(r'^group/send/invite/$', 'group_send_invite'),

    (r'^purchases/$', 'view_purchases'),
    (r'^wishlist/$', 'view_wishlist'),
    (r'^wishlist/add/$', 'wishlist_add'),
    (r'^wishlist/item/update/$', 'wish_item_update'),

    (r'^search/$', 'search'),
    (r'^scan/$', 'scan_item'),
    (r'^browse/categories/$', 'browse_categories'),
    (r'^browse/hot/$', 'browse_hot'),
    (r'^browse/category/$', 'browse_category'),

    (r'^find/store/$', 'find_store'),

    (r'^friends/wish/$', 'view_friends_wish'),
    (r'^friends/bought/$', 'view_friends_bought'),

    #(r'^bought/people/$', 'bought_people'),
    #(r'^wish/people/$', 'wish_people'),

    (r'^party/$', 'view_party'),
    # test
)
