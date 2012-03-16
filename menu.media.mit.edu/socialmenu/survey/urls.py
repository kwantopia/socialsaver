from django.conf.urls.defaults import *

urlpatterns = patterns('survey.views',
    (r'^$', 'surveys'),
    (r'^(?P<survey_id>\d+)/$', 'survey'),
    (r'^friends/$', 'friend_survey'),
)
