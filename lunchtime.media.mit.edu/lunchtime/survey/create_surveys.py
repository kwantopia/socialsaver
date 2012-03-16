from survey.models import Survey, BasicFoodSurvey, EatingCompanySurvey, EatingOutSurvey, DigitalReceiptSurvey
# import additional survey models here
import datetime
from django.contrib.auth.models import User
from django.db import IntegrityError

# Basic cooking survey
s, created = Survey.objects.get_or_create(title="Basic Food Survey", 
        description="Tell us about your food related habits.",
        model_name="BasicFoodSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(5)
s.expires = None
s.save()

"""
# replicate this on other surveys if you want to precreate surveys
if created:
    for u in User.objects.all().exclude(username='admin'):
        b = eval("%s(user=u, survey=s)"%s.model_name)
        b.save()
"""

# Eating company survey
s, created = Survey.objects.get_or_create(title="Eating Company Survey", 
        description="Tell us about your social dining habits",
        model_name="EatingCompanySurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(10)
s.expires = None
s.save()

s, created = Survey.objects.get_or_create(title="Eating Out Survey",
        description="Tell us about your eating out habits.",
        model_name="EatingOutSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(20)
s.expires = None
s.save()

"""
# Friends survey
s, created = Survey.objects.get_or_create(title="Friends Survey",
        description="How often do you meet this person in a week?",
        model_name="FriendsSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(5)
s.expires = None
s.save()
"""

s, created = Survey.objects.get_or_create(title="Digital Receipt Survey",
        description="Tell us about your experience with MealTime.",
        model_name="DigitalReceiptSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(20)
s.expires = None
s.save()


