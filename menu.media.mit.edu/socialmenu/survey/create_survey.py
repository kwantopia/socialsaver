from survey.models import Survey, SurveyStatus, EatingHabitSurvey, MenuInterfaceSurvey, ChoiceToEatSurvey
import datetime
from django.contrib.auth.models import User
from django.db import IntegrityError
import uuid

TOTAL_SURVEYS = 2 

# Eating habit survey
s, created = Survey.objects.get_or_create(title="Eating Habit Survey", 
        description="Tell us about your dining habits.",
        model_name="EatingHabitSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(25) 
s.expires=None
s.save()
"""
if created:
    for u in User.objects.all().exclude(username='admin'):
        if SurveyStatus.objects.filter(user=u).count() < TOTAL_SURVEYS:
            b = eval("%s(user=u, survey=s)"%s.model_name)
            b.uuid_token = uuid.uuid4()
            b.save()
"""
# Menu interface survey 
s, created = Survey.objects.get_or_create(title="Menu Interface Survey", 
        description="Tell us about your experience with Digital Menu.",
        model_name="MenuInterfaceSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(25)
s.expires=None
s.save()

"""
if created:
    for u in User.objects.all().exclude(username='admin'):
        if SurveyStatus.objects.filter(user=u).count() < TOTAL_SURVEYS:
            b = eval("%s(user=u, survey=s)"%s.model_name)
            b.uuid_token = uuid.uuid4()
            b.save()
"""

# Menu interface survey 
s, created = Survey.objects.get_or_create(title="How You Choose Survey", 
        description="Tell us about how you make choices on food.",
        model_name="ChoiceToEatSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(25)
s.expires=None
s.save()

# Friend distance survey 
s, created = Survey.objects.get_or_create(title="Friend Relationship Survey", 
        description="Tell us about your friends.",
        model_name="SurveyStatus")
#s.expires=datetime.datetime.now()+datetime.timedelta(25) 
s.expires=None
s.save()

