from django.conf.urls.defaults import *

urlpatterns = patterns('analysis.views',
    (r'^num/participants/$', 'num_participants'),
    (r'^get/emails/$', 'get_emails'),
    (r'^get/emails/iphone/$', 'get_emails_iphone'),
    (r'^phone/distribution/$', 'phone_distribution'),
    (r'^legals/experienced/$', 'legals_experienced'),
    (r'^demographic/distribution/$', 'demographic_distribution'),
    (r'^experiment/distribution/$', 'experiment_distribution'),
    (r'^friends/atsignup/$', 'friends_at_signup'),
    (r'^referral/distribution/$', 'referral_distribution'),
    (r'^build/friendnet/$', 'build_friend_net'),
    (r'^friends/signedup/$', 'count_friends'),
    (r'^winner/add/$', 'winner_add'),
    (r'^participants/$', 'participants'),
)
