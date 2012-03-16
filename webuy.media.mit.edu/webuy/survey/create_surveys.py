from survey.models import Survey, BasicMobileSurvey, BasicShoppingSurvey, ChoiceToEatSurvey
# import additional survey models here
import datetime
from django.contrib.auth.models import User
from django.db import IntegrityError

# Basic purchase behavior 
s, created = Survey.objects.get_or_create(title="Basic Mobile Survey", 
        description="Tell us about your usage of mobile phone.",
        model_name="BasicMobileSurvey")
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
"""
# Shopping survey
s, created = Survey.objects.get_or_create(title="Basic Shopping Survey", 
        description="Tell us about your electronics shopping habits",
        model_name="BasicShoppingSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(10)
s.expires = None
s.save()
"""
"""
# Friends survey
s, created = Survey.objects.get_or_create(title="Friends Survey",
        description="How often do you meet this person in a week?",
        model_name="FriendsSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(5)
s.expires = None
s.save()
"""

# Taste survey
s, created = Survey.objects.get_or_create(title="Eating Choice Survey", 
        description="Tell us about your eating choice habits",
        model_name="ChoiceToEatSurvey")
#s.expires=datetime.datetime.now()+datetime.timedelta(10)
s.expires = None
s.save()

