"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
import json
from datetime import datetime, date
from techcash.models import Receipt
from survey.models import DigitalReceiptSurvey
from common.models import Winner

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


from django.test.client import Client

c = Client()

def select_winner():
    response = c.post("/a/winner/", {'code':'ch00seW199Er'})
    print response

def test_winner():
    response = c.post("/a/winner/", {'code':'ch00seW199Er', 'test':'1'})
    print response

def latest_joined(prev=3):
    response = c.post("/a/latest/", {'days':prev})
    results = json.loads(response.content)
    for r in results:
        print r

def notify_latest():
    response = c.post("/a/add/otn/", {'code': 'ch00seW199Er'})
    results = json.loads(response.content)
    print results["result"]

def friend_stats():
    response = c.post("/a/friend/stats/", {'e':'e'})
    print response

def social_winner():
    response = c.post("/a/winner/social/", {'code':'ch00seW199Er',
                                            'winners': [524823364, 1368751152]})
    print response

def get_emails():
    response = c.post("/a/emails/get/", {'code':'ch00seW199Er'})
    print response

def last_week_winners():
    response = c.post("/a/last/week/winners/", {'code':'ch00seW199Er'})
    
    r = json.loads(response.content)
    if r["result"] == "1":
        # print people
        for w in r["winners"]:
            print w[0],w[1]
    else:
        print "Wrong access code"

def past_winners(days=7):
    response = c.post("/a/past/winners/%s/"%days, {'code':'ch00seW199Er'})
    
    r = json.loads(response.content)
    if r["result"] == "1":
        # print people
        for w in r["winners"]:
            print w[0],w[1]
    else:
        print "Wrong access code"

def add_feature():
    response = c.post("/a/feature/", {'code':'ch00seW199Er'})
    print response

def check_reviews():
    d = date.today() #-timedelta(5)
    win_begin = datetime(year=d.year, month=d.month, day=d.day,
            hour=0, minute=0, second=0)
    win_end = datetime(year=d.year, month=d.month, day=d.day,
            hour=23, minute=59, second=59)

    print Receipt.objects.filter(last_update__lt=win_end, last_update__gt=win_begin).values_list("txn__user", flat=True).distinct()

from django.core.mail import send_mail
from common.models import OTNUser

def send_survey_email():
    msgs = ''' 
Hi there!

    Hope you are successfully finishing up your finals.  Also, if you haven't seen, to cheer you for your finals the discount "Features" in MealTime is running until the end of the trial.  
    
    This terms MealTime trial is also coming to an end.  For those who have finished the finals, I would like to invite you to fill out the surveys in http://mealtime.mit.edu (after login).  Your feedback is extremely valuable!  To thank you for your input, $50 gift certificates will be raffled for each survey.

Good luck with your finals! 

MealTime Team
    ''' 
    p_emails = OTNUser.objects.all().values_list('my_email', flat=True)
    p_emails = ["virot@mit.edu",
    "john_t@mit.edu",
    "martian@mit.edu",
    "eastsonlee@gmail.com",
    "wennaijun@hotmail.com",
    "abusedusers@gmail.com",
    "rdixit@mit.edu",
    "yod@mit.edu",
    "mhmeisner@gmail.com",
    "dyn@mit.edu",
    "gjtucker@mit.edu",
    "beccacuevas@bellsouth.net"]

    for e in p_emails:
        send_mail("By Sunday: MealTime surveys to win $50 gift certificates", msgs, 'MealTime! <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

def send_survey_may21():
    msgs = ''' 
Hi there!

    Please fill out the surveys in http://mealtime.mit.edu (after login).  Your feedback is extremely valuable!  Regardless of whether you used MealTime or not, you are all eligible.  To thank you for your input, $50 gift certificates will be raffled for each survey (4 raffles).

Wish you a great summer!

MealTime Team

--------------------------------
There was a bug with the Eating Company Survey so apologize for those who have to fill it out again.

    ''' 
    p_emails = OTNUser.objects.all().values_list('my_email', flat=True)

    for e in p_emails:
        send_mail("By Sunday: MealTime surveys to win $50 gift certificates", msgs, 'MealTime! <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

def send_survey_may24():
    msgs = ''' 
Hi there!

    Please fill out the surveys in http://mealtime.mit.edu (after login).  Your feedback is extremely extremely valuable!  Regardless of whether you used MealTime or not, you are all eligible.  To thank you for your input, $50 gift certificates will be raffled for each survey (4 raffles) TONIGHT.

Wish you a great summer!

MealTime Team

--------------------------------
There was a bug with the Eating Company Survey so apologize for those who have to fill it out again.

    ''' 
    p_emails = OTNUser.objects.all().values_list('my_email', flat=True)

    for e in p_emails:
        send_mail("By Tonight!!: MealTime surveys to win $50 gift certificates", msgs, 'MealTime! <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

def send_survey_reminder_may26():
    msgs = ''' 
Hi there!

    Please fill out the surveys at http://mealtime.mit.edu (after login).  Your feedback is extremely helpful!  Regardless of whether you used MealTime or not, you are all eligible.  To thank you for your input, $50 gift certificates will be raffled for each survey (4 raffles).

    For those waiting for the iPad winner, sorry for the delay.  This week is Media Lab sponsor open house week and I have been swamped.  After enough surveys have been filled out, I hope to get all the raffles done by tomorrow and announce the winners by tomorrow midnight.

Thank you!

MealTime Team

    ''' 
    p_emails = OTNUser.objects.all().values_list('my_email', flat=True)

    p_emails = ['rdixit@mit.edu',
                'virot@mit.edu',
                'yod@mit.edu',
                'wennaijun@hotmail.com',
                'mhmeisner@gmail.com',
                'gjtucker@mit.edu',
                'beccacuevas@bellsouth.net',
                'justinwbutler@gmail.com',
                'kool@mit.edu',
                'dexymistera@yahoo.com',
                'dyn@mit.edu']

    for e in p_emails:
        send_mail("Please fill out the survey for a chance to win $50", msgs, 'MealTime! <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

def send_ipad_winner():
    msgs = ''' 
Hi there!

    Thank you for participating in the MealTime trial.  For those of you who still haven't filled out, please help us by filling out the surveys at http://mealtime.mit.edu/survey/ (after logging in through Facebook Connect).  Your feedback is IMMENSELY valuable for research.

    I would like to announce that Victoria Hammett is the winner of the iPad!

    Winners of 4 survey raffles for $50 gift certificates are:

    1. Bob Chen
    2. Michael Snively
    3. Pooja Shah
    4. Carin King

    Please send me an e-mail on what type of gift certificate you would like (Amazon/Apple/Legal Sea Foods are available).

    There will be more coming soon!  

MealTime Team

    ''' 
    p_emails = OTNUser.objects.all().values_list('my_email', flat=True)
    p_emails = ['mhmeisner@gmail.com',
    'gjtucker@mit.edu',
    'beccacuevas@bellsouth.net',
    'justinwbutler@gmail.com',
    'dyn@mit.edu',
    'dexymistera@yahoo.com']


    for e in p_emails:
        send_mail("iPad Winner", msgs, 'MealTime! <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

def survey_incomplete():
    msgs = ''' 
Hi there!

    Thank you for participating in the MealTime trial.  For those of you who still haven't filled out, please help us by filling out the survey at http://mealtime.mit.edu/survey/ (after logging in through Facebook Connect).  Your feedback is IMMENSELY valuable for research.

    I would like to announce that Victoria Hammett is the winner of the iPad!

    Winners of 4 raffles for $50 gift certificates are:

    1. Bob Chen
    2. Michael Snively
    3. Pooja Shah
    4. Carin King

    There will be more coming soon!  

MealTime Team

    ''' 

    completed_users = DigitalReceiptSurvey.objects.all().values_list('user__id', flat=True)
    p_emails = OTNUser.objects.exclude(id__in=completed_users).values_list('my_email', flat=True)

    for e in p_emails:
        send_mail("Please complete the survey", msgs, 'MealTime! <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e


def final_winners():

    u = OTNUser.objects.get(name="Victoria Hammett")
    w = Winner(user=u, prize="$550 Apple gift certificate")
    w.save()
    u = OTNUser.objects.get(name="Bob Chen")
    w = Winner(user=u, prize="$50 Amazon gift certificate")
    w.save()
    u = OTNUser.objects.get(name="Michael Snively")
    w = Winner(user=u, prize="$50 Amazon gift certificate")
    w.save()
    u = OTNUser.objects.get(name="Pooja Shah")
    w = Winner(user=u, prize="$50 Amazon gift certificate")
    w.save()
    u = OTNUser.objects.get(name="Carin King")
    w = Winner(user=u, prize="$50 Amazon gift certificate")
    w.save()

