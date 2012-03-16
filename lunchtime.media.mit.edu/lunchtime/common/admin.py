from django.contrib import admin
from models import OTNUser, Experiment, Location, Featured

class OTNUserAdmin(admin.ModelAdmin):
    search_fields = ['name']

class ExperimentAdmin(admin.ModelAdmin):
    pass

class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']

class FeaturedAdmin(admin.ModelAdmin):
    search_fields = ['location__name', 'description']
    ordering = ['-pub_date']
    date_hierarchy = 'day'

admin.site.register(OTNUser, OTNUserAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Featured, FeaturedAdmin)
