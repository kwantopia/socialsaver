from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^bestbuy/', include('bestbuy.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'web.views.index', name='auth_login'),
    (r'', include('web.urls')),
    (r'^m/', include('mobile.urls')),
    (r'^survey/', include('survey.urls')),
    (r'^facebook/', include('facebookconnect.urls')),
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

