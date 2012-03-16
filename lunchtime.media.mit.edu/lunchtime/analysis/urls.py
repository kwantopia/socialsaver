from django.conf.urls.defaults import *

urlpatterns = patterns('analysis.views',
    (r'^winner/$', 'find_winner'),
    (r'^winner/social/$', 'social_winner'),
    (r'^latest/$', 'latest_joined'),
    (r'^add/otn/$', 'add_to_otn'),
    (r'^friend/stats/$', 'friend_stats'),
    (r'^emails/get/$', 'get_emails'),
    (r'^last/week/winners/$', 'last_week_winners'),
    (r'^past/winners/(?P<days>\d+)/$', 'past_winners'),
    (r'^feature/$', 'add_feature'),
)
