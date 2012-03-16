from django.db import models
from django.contrib.auth.models import User
from common.models import OTNUser
import uuid
from django.conf import settings
import time
from polymorphic.models import *

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
        return 'http://%s/mobile/survey/%d/'%(settings.HOST_NAME, self.id)

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

    __metaclass__ = PolymorphicMetaclass

    user = models.ForeignKey( User )
    survey = models.ForeignKey( Survey )
    uuid_token = models.CharField(max_length=36, default=str(uuid.uuid4()))
    completed = models.BooleanField( default=False )
    complete_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return "%s (%s):%s"%(self.user.username, self.completed, self.survey.title)

class BasicFoodSurvey(SurveyStatus):
    """
        How many times one cooks with others 
    """

    RARELY = 0
    ONCE = 1
    HALF = 2
    FIVE = 3
    WEEKENDS = 4
    EVERYDAY = 5

    FREQUENCY_CHOICES = (
            ( RARELY, 'Rarely' ),
            ( ONCE, 'Once' ),
            ( WEEKENDS, 'Only on weekends'),
            ( HALF, '2 to 4 times a week'),
            ( FIVE, 'At least 5 days a week'),
            ( EVERYDAY, 'Every day of the week'),
        )

    cook_frequency = models.IntegerField(default=0, choices=FREQUENCY_CHOICES, verbose_name="How many times do you cook a week?")

    MORE_ONCE = 0
    ONCE = 1
    BI_WEEKLY = 2
    MONTH = 3
    NEVER = 4

    SHOPPING_CHOICES = (
        (MORE_ONCE, 'More than once a week'),
        (ONCE, 'Once a week'),
        (BI_WEEKLY, 'Once every two weeks'),
        (MONTH, 'Once a month'),
        (NEVER, 'Never'),
      )

    grocery_frequency = models.IntegerField(default=0, choices=SHOPPING_CHOICES, verbose_name="How many times do you go grocery shopping a month?")
    spend_limit = models.BooleanField(default=False, verbose_name="Do you have a spending limit on your groceries?")
    dollar_limit = models.FloatField(default=0.0, verbose_name="How much $ do you spend on average per grocery shopping?")

    """
        How variety of choices one chooses
    """
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


    different = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to try different restaurants.")
    spontaneous = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I am spontaneous.  I like to make last minute changes.")
    uniqueness = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to do things that others don't do and try to distinguish myself.")
    variety = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to try a variety of restaurants beyond my specific tastes.")
    averse = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I only try a new or different place if my friends suggest.")
    own = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I don't like to try different places even if my friend suggests.")
    regret = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I have regretted going to a place my friend suggested.")
    expert = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I try different places if I hear from Zagat, newspaper or other expert reviews.")
    yelp = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="Yelp is my primary means of deciding where to go.")
    yelp_community = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I consider Yelp community as trusted source of recommendations.")
    share = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I often share with others about my experiences at different restaurants.")


class EatingCompanySurvey(SurveyStatus):
    """
        How often one eats with other people
    """

    RARELY = 0
    ONCE = 1
    HALF = 2
    FIVE = 3
    WEEKENDS = 4
    EVERYDAY = 5

    FREQUENCY_CHOICES = (
            ( RARELY, 'Rarely' ),
            ( ONCE, 'Once a week' ),
            ( WEEKENDS, 'Only on weekends'),
            ( HALF, '2 to 4 times a week'),
            ( FIVE, 'At least 5 days a week'),
            ( EVERYDAY, 'Every day of the week'),
        )

    cook_company = models.IntegerField(default=0, choices=FREQUENCY_CHOICES, verbose_name="How often do you cook with your friends a week?")

    out_company = models.IntegerField(default=0, choices=FREQUENCY_CHOICES, verbose_name="How often do you eat with your friends a week?")

    ONE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    DIFFERENT = 4

    FRIEND_CHOICES = (
                (ONE, 'Same person all the time'),
                (TWO, 'Two different friends'),
                (THREE, 'Three different friends'),
                (FOUR, 'Four different friends'),
                (DIFFERENT, 'More than 5'),
            )
    friends = models.IntegerField(default=0, choices=FRIEND_CHOICES, verbose_name="How many distinct friends do you eat with in a week?")

    friend_group = models.IntegerField(default=0, choices=FRIEND_CHOICES, verbose_name="If you eat with friends, how big is the group usually?")

    lunch_alone = models.BooleanField(default=False, choices=FREQUENCY_CHOICES, verbose_name="Do you usually eat lunch by yourself?")
    dinner_alone = models.BooleanField(default=False, choices=FREQUENCY_CHOICES, verbose_name="Do you usually eat dinner by yourself?")

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

    """
        What people feel about eating with other people
    """
    fun = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel it's fun to eat with my friends.")
    waste = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel it's waste of time to eat with my friends.")
    time = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel it takes too much time to eat with others.")
    happy = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel happy to eat with others.")
    alone = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel happy eating by myself.")
    together = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="If I had more time and money I would eat more with others.")

class EatingOutSurvey(SurveyStatus):
    """
        Eating out habits
    """

    RARELY = 0
    ONCE = 1
    HALF = 2
    FIVE = 3
    WEEKENDS = 4
    EVERYDAY = 5

    FREQUENCY_CHOICES = (
            ( RARELY, 'Rarely' ),
            ( ONCE, 'Once a week' ),
            ( WEEKENDS, 'Only on weekends'),
            ( HALF, '2 to 4 times a week'),
            ( FIVE, 'At least 5 days a week'),
            ( EVERYDAY, 'Every day of the week'),
        )

    frequency = models.IntegerField(default=0, choices=FREQUENCY_CHOICES, verbose_name="How many times do you eat at restaurants in a week?")
    dining = models.IntegerField(default=0, choices=FREQUENCY_CHOICES, verbose_name="How many times do you eat at campus dining in a week?")
    spending_limit = models.BooleanField(default=False, verbose_name="Do you have a spending limit when you eat at a restaurant?")
    dollar_limit = models.FloatField(default=0.0, verbose_name="What is your average spending $ per meal when you eat at a restaurant?")

    """
        How I choose where to eat 
    """
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

    cheap = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually try to find the cheapest place I can eat.")
    health = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I consider how healthy the food is when I consider a place to eat.")
    plan = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually plan what I want to eat before I choose the restaurant.")
    me = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I choose what I want to eat at the restaurant.")
    friends = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to try what my friends suggest at the restaurant.")
    regret = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I have had experience regretting after choosing what my friends suggested.")
    others = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to see what other people are eating in other tables.")
    chef = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to try what the chef or waiter suggests.")
    popular = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="When I am at a fancy restaurant, I like to pick the most popular dish.")
    expensive = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="When I am at a fancy restaurant, I like to pick the most cheap dish.")
    taste = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually only eat what fits my taste.")

class DigitalReceiptSurvey(SurveyStatus):
    """
        Design survey
    """
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

    helpful = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="It was helpful to know my history of transactions on the phone.")
    sharing = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I was comfortable sharing the locations I transacted with my friends.")
    stats = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="Basic statistics on where I go frequently was helpful to know.")
    stats_change = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="Basic statistics made me to try different places that I go less often.")
    popularity = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="Knowing which places were popular was helpful to know.")
    friends = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="It was helpful to know where my friends frequently go to.")
    talk = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="MealTime allowed me to talk with friends about places to eat together.")
    new = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="MealTime allowed me to get to know new places I could eat.")
    reviews = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="MealTime reviews of locations were helpful.")
    reputation = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I was aware that MealTime reviews could only be made by people who actually made transaction at the location.")
    spending = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I was more aware of my TechCASH spending through MealTime.")
    changed = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I think MealTime changed my spending behavior and eating locations.")
    general = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I believe MealTime like application could be helpful if it were linked to my credit or debit card.")

    cheap = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="If I had the goal of saving on cost, I would like MealTime to suggest me with cheap places to eat.")

    healthy = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="If I had the goal of eating healthy, I would like MealTime to suggest me healthy places to eat.")

    comments = models.TextField(verbose_name="Any other comments about your experiences:")
    

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
    
    
