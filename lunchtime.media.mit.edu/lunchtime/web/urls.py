from django.conf.urls.defaults import *

urlpatterns = patterns('web.views',
    (r'^/?$', 'index'),
    (r'^home/$', 'home'),
    (r'^profile/$', 'profile'),

    (r'^transactions/(?P<sort>\w+)/(?P<page>\d{0,4})/$', 'transactions'),
    (r'^transactions/$', 'transactions', {'sort':"date_desc", 'page':1}),
    (r'^transactions/(?P<page>\d{0,4})/$', 'transactions', {'sort':"date_desc"}),

    (r'^friends/transactions/(?P<friend_id>\d+)/$', 'friends_transactions'),
                       
    (r'^mobile/$', 'mobile'),
    (r'^about/$', 'about'),
    (r'^faq/$', 'faq'),
    
    (r'^winners/$', 'winners'),
    (r'^consent/techcash/$', 'techcash_consent'),
    (r'^consent/otn/$', 'otn_consent'),
    (r'^update/description/$', 'update_description'),
    (r'^update/rating/$', 'update_rating'),
    (r'^update/sharing/$', 'update_sharing'),
    (r'^survey/(?P<survey_id>\d+)/$', 'survey'),
    (r'^gift/$', 'gift'),
    (r'^map/$', 'map'),
)
