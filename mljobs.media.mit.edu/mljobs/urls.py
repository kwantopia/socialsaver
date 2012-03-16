from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# havent created a basicframe.urls .py file but will and then will change this to grab from that dir

urlpatterns = patterns('',
    (r'^/?', include('basicframe.urls')),

    # Example:
    # (r'^mljobs/', include('mljobs.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns( 'django.views',
            url(r'%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'static.serve', {'document_root': settings.MEDIA_ROOT, })
    )

    urlpatterns += patterns( 'django.views',
            url(r'%s(?P<path>.*)$' % settings.STYLES_URL[1:], 'static.serve', {'document_root': settings.STYLES_ROOT, }) 
    )

    urlpatterns += patterns( 'django.views',
            url(r'%s(?P<path>.*)$' % settings.SCRIPTS_URL[1:], 'static.serve', {'document_root': settings.SCRIPTS_ROOT, }) 
    )   
