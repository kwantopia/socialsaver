from django.conf.urls.defaults import *

urlpatterns = patterns('presurvey.views',
    (r'^$', 'legals_population_survey'),
    (r'^legals/$', 'dummy_page'),
    (r'^legals/completed/$', 'completed'),
    (r'^legals/invite/$', 'invite_more'),
    # Define other pages you want to create here
)

