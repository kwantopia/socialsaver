from django.conf.urls.defaults import *

urlpatterns = patterns('restaurant.views',
    (r'^init/legals/$', 'init_legals_menu'),
    (r'^init/mit/$', 'init_mit_menu'),
    (r'^init/store/categories/$', 'init_store_categories'),
)
