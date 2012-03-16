from django.db import models
from django.contrib.auth.models import User
import uuid
from django.conf import settings
import time

# Create your models here.

"""
    1. Survey is generated with questions and possible answers in one form
    2. It is sent out to the users with url that contains the uuid token
    3. When user completes the survey, it is submitted with uuid
    4. SurveyStatus will be marked completed

    Test
    1. Create users
    2. Use test survey and generate SurveyStatus for each user
    3. When users open web or mobile application, the survey should show up
    4. The users fill out the survey and submit
    5. Survey be recorded and updated
"""

class Survey(models.Model):
    """
        Class for managing surveys.
    """
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=100, unique=True)
    # if null it never expires
    expires = models.DateTimeField(null=True, blank=True)

    def url(self):
        """
            get url of the survey    
        """
        return 'http://%s/m/survey/%d/'%(settings.HOST_NAME, self.id)

    def summary(self):
        if self.expires == None:
            detail = {
                    'id': str(self.id),
                    'title': self.title,
                    'description': self.description,
                    'expires': 'None', 
                    'url': self.url(),
                    }
        else:
            detail = {
                    'id': str(self.id),
                    'title': self.title,
                    'description': self.description,
                    'expires': str(time.mktime(self.expires.timetuple())),
                    'url': self.url(),
                    }
        return detail

    def __unicode__(self):
        return self.title

class SurveyStatus(models.Model):
    """
        Need to be able to pull surveys that users completed
        Need to be able to pull surveys that users have not completed
        Need to get uuid_token for a user
    """

    user = models.ForeignKey( User )
    survey = models.ForeignKey( Survey )
    uuid_token = models.CharField(max_length=36, default=str(uuid.uuid4()))
    completed = models.BooleanField( default=False )
    complete_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return "%s (%s):%s"%(self.user.username, self.completed, self.survey.title)

class BasicMobileSurvey(SurveyStatus):
    """
        Basic mobile phone usage behavior 
    """

    NONE = 0
    FIVE = 1
    FIFTEEN = 2
    THIRTY = 3
    MORE = 4

    APP_COUNT = (
            ( NONE, "I don't download apps"),
            ( FIVE, "Less than 5 downloaded"),
            ( FIFTEEN, "I have a screenful (about 15 apps)"),
            ( THIRTY, "I have two screenful (about 30 apps)"),
            ( MORE, "I have many more applications"),
        )
    apps = models.IntegerField(default=0, choices=APP_COUNT, verbose_name="How many applications have you downloaded on the phone?")

    RARELY = 0
    ONE = 1
    TWO = 2
    FOUR = 3
    EVERY = 4

    APP_DOWNLOAD = (
            ( RARELY, "I rarely download"),
            ( ONE, "I try one a week"),
            ( TWO, "I download a couple a week"),
            ( FOUR, "I download quite a few"),
            ( EVERY, "I download new apps all the time"),
        )

    download = models.IntegerField(default=0, choices=APP_DOWNLOAD, verbose_name="How many applications do you download a week?")

    games = models.BooleanField(default=False, verbose_name="I regularly play games on the phone")
    stock = models.BooleanField(default=False, verbose_name="I track stocks on the phone")
    weather = models.BooleanField(default=False, verbose_name="I check the weather regularly on the phone")
    finance = models.BooleanField(default=False, verbose_name="I manage my personal finance on the phone")


class BasicShoppingSurvey(SurveyStatus):
    """
        How often one eats with other people
    """

    RARELY = 0
    ONCE = 1
    TWICE = 2
    WEEKENDS = 4
    FOUR = 3
    MORE = 5

    FREQUENCY_CHOICES = (
            ( RARELY, 'Rarely' ),
            ( ONCE, 'Once a month' ),
            ( TWICE, 'Twice a month'),
            ( WEEKENDS, 'Some weekends'),
            ( FOUR, 'Every weekend'),
            ( MORE, 'More often'),
        )

    frequency = models.IntegerField(default=0, choices=FREQUENCY_CHOICES, verbose_name="How many times do you visit BestBuy in a month?")

    alone = models.BooleanField(default=False, verbose_name="I usually go shopping by myself.")
    friend = models.BooleanField(default=False, verbose_name="I usually go with friends.")
    family = models.BooleanField(default=False, verbose_name="I usually go with my family.")

    STRONGLY_AGREE = 0
    AGREE = 1
    NEITHER = 2
    DISAGREE = 3
    STRONGLY_DISAGREE = 4

    LIKERT_CHOICES = (
            ( STRONGLY_AGREE, 'Strongly agree'),
            ( AGREE, 'Agree'),
            ( NEITHER, 'Neither agree nor disagree'),
            ( DISAGREE, 'Disagree'),
            ( STRONGLY_DISAGREE, 'Strongly disagree'),
        )

    online_review = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="Online reviews are my source of trusted information.")
    friend_review = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I respect my friends opinions on electronics.")
    experience_review = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I would like to talk to someone who has actually bought and experienced the item.")

    planned = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually plan for purchasing an item and purchase.")
    compare_price = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually compare price on the Internet before I make purchase.")
    compare_product_online = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually compare different product alternatives on the Internet before I make purchase.")
    compare_product_store = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually compare different product alternatives in the store before I make purchase.")

    impulse = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to go to the store and buy things when I like to.")

    sale = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually wait for a sale before buying electronics products.")

class ChoiceToEatSurvey(SurveyStatus):
    """
        How I choose my menu item
    """
    plan = models.BooleanField(default=False, verbose_name="I usually plan what I want to eat before I choose the restaurant")
    me = models.BooleanField(default=False, verbose_name="I choose what I want to eat at the restaurant")
    friends = models.BooleanField(default=False, verbose_name="I like to try what my friend's suggest")
    others = models.BooleanField(default=False, verbose_name="I like to see what other people in other tables are eating")
    chef = models.BooleanField(default=False, verbose_name="I like to try what the chef or waiter suggests")

    """
        How variety of choices one chooses
    """

    different = models.BooleanField(default=False, verbose_name="I like to try different restaurants.")
    spontaneous = models.BooleanField(default=False, verbose_name="I am spontaneous.  I like to make last minute changes.")
    uniqueness = models.BooleanField(default=False, verbose_name="I like to do things that others don't do and try to distinguish myself.")
    variety = models.BooleanField(default=False, verbose_name="I like to try a variety beyond my specific tastes.")
    averse = models.BooleanField(default=False, verbose_name="I only try something different if my friend suggests.")
    own = models.BooleanField(default=False, verbose_name="I don't like to try something different even if my friend suggests.")


class FriendsSurvey(SurveyStatus):
    """
        How often you meet a person in a week
    """

    DAILY = 7
    WEEKLY_FEW = 6
    WEEKLY_ONCE = 5
    MONTHLY = 4
    YEARLY_ONCE = 1
    NEVER = 0

    MEETING_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY_FEW, 'A few times a week'),
        (WEEKLY_ONCE, 'Once a week'),
        (MONTHLY, 'Monthly'),
        (YEARLY_ONCE, 'Once a year'),
        (NEVER, 'Never'),
        )
        
    meetings = models.IntegerField(choices=MEETING_CHOICES, default=NEVER, verbose_name="How often I meet with this person.")
    #friend = models.ForeignKey(User, related_name="friend_meet_survey")
    
    
