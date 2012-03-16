from django.conf.urls.defaults import *

urlpatterns = patterns('web.views',
    (r'^/?$', 'index'),
    (r'^profile/$', 'profile'),
    (r'^pin/$', 'pin_manage'),
    (r'^download/$', 'download'),
    (r'^faq/$', 'faq'),
    (r'^download/$', 'download'),
    (r'^consent/techcash/$', 'techcash_consent'),
    (r'^consent/otn/$', 'otn_consent'),
    (r'^test/ajax/$', 'test_ajax'),
    (r'^valid/tablecodes/$', 'table_codes'),
)
