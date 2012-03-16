from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^socialmenu/', include('socialmenu.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
 
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^facebook/', include('facebookconnect.urls')),
    (r'^logout/$', 'facebookconnect.views.facebook_logout'),
    (r'^accounts/profile/', 'web.views.profile'),
    (r'^accounts/login/', 'web.views.login_redirect'),

    (r'^restaurant/', include('restaurant.urls')),
    (r'^legals/', include('legals.urls')),
    (r'^mit/', include('mitdining.urls')),
    (r'^survey/', include('survey.urls')),
    (r'^web/', include('web.urls')),
    (r'^pickadishlocal/', include('presurvey.urls')),
    (r'^pickadishdev/', include('presurvey.urls')),
    (r'^pickadish/', include('presurvey.urls')),
    (r'^wesabe/', include('finance.urls')),
    (r'^a/', include('analysis.urls')),
    (r'^$', 'web.views.index'),
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
