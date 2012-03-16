from django.conf.urls.defaults import *

urlpatterns = patterns('legals.views',
    (r'^$', 'index'),
    (r'^profile/$', 'profile'),
    (r'^orders/(?P<page>\d{0,4})/$', 'orders'),
    (r'^order/$', 'order'),
    (r'^download/$', 'download'),
    (r'^faq/$', 'faq'),
    (r'^winners/$', 'winners'),
    (r'^update/rating/$', 'update_rating'),
    (r'^update/reason/$', 'update_reason'),
    (r'^update/comment/$', 'update_comment'),
    (r'^feedback/post/$', 'feedback_post'),
    (r'^receipt/upload/$', 'receipt_upload'),
    (r'^m/', include('legals.mobile.urls')),

    (r'^upload/complete/$', 'upload_complete'),
    (r'^upload/test/$', 'upload_page'),

    (r'^tablecodes/migrate/$', 'migrate_table_codes'),
    (r'^presurvey/$', 'legals_presurvey'),

    (r'^gift/$', 'gift'),
    (r'^gift/admin/$', 'gift_admin'),
    (r'^gift/update/$', 'gift_update'),
    (r'^gift/certificate/(?P<subject_id>\d+)/$', 'gift_certificate_form'),

    (r'^guest/list/(?P<signup>\d{1})/$', 'guest_list'),
    (r'^guest/(?P<code>\d+)/$', 'guest_mobile'),
)
