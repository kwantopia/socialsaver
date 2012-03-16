from django.contrib import admin
from models import Survey, SurveyStatus

class SurveyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['-created']

class SurveyStatusAdmin(admin.ModelAdmin):
    pass

admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyStatus, SurveyStatusAdmin)

