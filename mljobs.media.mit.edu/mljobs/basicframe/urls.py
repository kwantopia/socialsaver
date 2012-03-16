from django.conf.urls.defaults import patterns

urlpatterns = patterns ('basicframe.views',
	(r'^login/$', 'login_attempt'),
	(r'^logout/$', 'logout'),
	(r'^profile/$', 'profile'),
	(r'^profile/picture/upload/$', 'profile_pic_upload'),	
	(r'^people/$', 'people'),
	(r'^listings/$', 'listings'),
	(r'^portfolio/$', 'portfolio'),
	(r'^post_listing/$', 'post_listing'),
)