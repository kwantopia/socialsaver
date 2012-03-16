from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('legals.mobile.views',
    # Example:
    # (r'^lunchtime/', include('lunchtime.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),

    # main web page for menu 
    (r'^json/menu/$', 'get_menu'),
    (r'^home/(?P<order_id>\d+)/$', 'home'),
    (r'^(?P<lat>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)/(?P<lon>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)/(?P<udid>\w{64})/$', 'index'),
    (r'^login/$', 'login_mobile'),
    (r'^login/real/$', 'login_ws'),
    (r'^categories/(?P<order_id>\d+)/$', 'categories'),
    (r'^category/(?P<cat_id>\d+)/(?P<order_id>\d+)/$', 'view_category'),
    (r'^chef/choices/(?P<order_id>\d+)/$', 'view_chefs_choices'),
    (r'^friend/choices/(?P<order_id>\d+)/$', 'view_friends_choices'),
    (r'^item/(?P<item_id>\d+)/(?P<order_id>\d+)/$', 'view_item'),
    (r'^mark/(?P<item_id>\d+)/(?P<order_id>\d+)/$', 'mark_item'),
    (r'^unmark/(?P<item_id>\d+)/(?P<order_id>\d+)/$', 'unmark_item'),
    (r'^reconsider/(?P<item_id>\d+)/(?P<order_id>\d+)/$', 'item_reconsider'),
    (r'^myorder/(?P<order_id>\d+)/$', 'my_order'),
    (r'^allergies/(?P<order_id>\d+)/$', 'allergies'),

    (r'^register/$', 'register'),
    #(r'^order/$', 'order'),
)
