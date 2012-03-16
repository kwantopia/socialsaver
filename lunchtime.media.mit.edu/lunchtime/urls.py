from django.conf.urls.defaults import *
from django.conf import settings
from web.forms import OTNUserCreationForm
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^lunchtime/', include('lunchtime.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^$', 'web.views.index'),
    (r'^logout/$', 'facebookconnect.views.facebook_logout'),
    (r'^admin/', include(admin.site.urls)),

    (r'^facebook/', include('facebookconnect.urls')),
    #(r'^/?$', 'exampleapp.views.index'),
    #(r'^accounts/profile/', 'exampleapp.views.profile'),
    (r'^accounts/profile/', 'web.views.profile'),
    url(r'^accounts/login/$', 'web.views.index', name='auth_login'),
    (r'^techcash/', include('techcash.urls')),
    (r'^push/', include('iphonepush.urls')),
    (r'^m/', include('mobile.urls')),
    (r'^survey/', include('survey.urls')),
    (r'', include('web.urls')),
    #(r'^web/', include('web.urls')),
    (r'^wesabe/', include('finance.urls')),
    (r'^a/', include('analysis.urls')),
)

if settings.LOCAL_DEVELOPMENT:
  urlpatterns += staticfiles_urlpatterns()

"""
    urlpatterns += patterns( 'django.views',
            url(r'%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'static.serve', {'document_root': settings.MEDIA_ROOT, })
    )

    urlpatterns += patterns( 'django.views',
            url(r'%s(?P<path>.*)$' % settings.STYLES_URL[1:], 'static.serve', {'document_root': settings.STYLES_ROOT, }) 
    )

    urlpatterns += patterns( 'django.views',
            url(r'%s(?P<path>.*)$' % settings.SCRIPTS_URL[1:], 'static.serve', {'document_root': settings.SCRIPTS_ROOT, }) 
    )
"""
