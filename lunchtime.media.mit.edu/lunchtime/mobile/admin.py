from django.contrib import admin
from models import Event 

class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp' 

admin.site.register(Event, EventAdmin)
    

