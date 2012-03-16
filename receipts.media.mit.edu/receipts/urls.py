from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^receipts/', include('receipts.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^facebook/', include('facebookconnect.urls')),
    (r'^push/', include('iphonepush.urls')),
    (r'^shoebox/', include('shoebox.urls')),
    (r'^$', 'web.views.index'),
    (r'^logout/$', 'facebookconnect.views.facebook_logout'),
    (r'^accounts/profile/', 'web.views.profile'),
    (r'^accounts/login/$', 'web.views.account_login'),
    (r'^web/', include('web.urls')),
)

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns( 'django.views',
            url(r'%s(?P<path>.*)/$' % settings.MEDIA_URL[1:], 'static.serve', {'document_root': settings.MEDIA_ROOT, })
    )
