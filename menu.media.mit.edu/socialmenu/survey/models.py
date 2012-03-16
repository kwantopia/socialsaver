from django.db import models
from django.contrib.auth.models import User
import uuid
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
        return "http://%s/survey/%d/"%(settings.HOST_NAME, self.id)

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


class SurveyStatus(models.Model):
    """
        Need to be able to pull surveys that users completed
        Need to be able to pull surveys that users have not completed
        Need to get uuid_token for a user
    """
    __metaclass__ = PolymorphicMetaclass

    user = models.ForeignKey( User )
    survey = models.ForeignKey( Survey )
    uuid_token = models.CharField(max_length=36, default=uuid.uuid4())
    completed = models.BooleanField( default=False )
    complete_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return "%s (%s): %s"%(self.user.username, self.completed, self.survey.title)
 
class EatingHabitSurvey(SurveyStatus):
    """
        Basic cooking survey
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

    grocery_frequency = models.IntegerField(default=0, choices=SHOPPING_CHOICES, verbose_name="How often do you go grocery shopping?")
    cook_company = models.IntegerField(default=0, choices=FREQUENCY_CHOICES, verbose_name="How often do you cook with your friends/family a week?")
    out_company = models.IntegerField(default=0, choices=FREQUENCY_CHOICES, verbose_name="How often do you eat out with your friends/family a week?")

    NONE = 0
    ONE = 1
    TWO = 2
    FIVE = 3

    FRIEND_CHOICES = (
        (NONE, "I usually eat by myself"),
        (ONE, "One"),
        (TWO, "2 to 4"),
        (FIVE, "5 or more"),
    )
    friends = models.IntegerField(default=0, choices=FRIEND_CHOICES, verbose_name="How many different people do you eat with regularly in a week?")

    STRONGLY_AGREE = 0
    AGREE = 1
    NEITHER = 2
    DISAGREE = 3
    STRONGLY_DISAGREE = 4

    LIKERT_CHOICES = (
          (STRONGLY_AGREE, 'Strongly agree'),
          (AGREE, 'Agree'),
          (NEITHER, 'Neither agree nor disagree'),
          (DISAGREE, 'Disagree'),
          (STRONGLY_DISAGREE, 'Strongly disagree'),
        )
    spend_limit = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I have spending limit on my meals when I eat out.")

    LOW = 0
    MID = 1
    HI = 2
    LUXURY = 3
    NOLIMIT = 4

    PRICE_CHOICES = (
        (LOW, '$0~$10'),
        (MID, '$10~$20'),
        (HI, '$20~$30'),
        (LUXURY, '$30 or over'),
        (NOLIMIT, "I don't care about price")
        )
    dollar_limit = models.FloatField(default=0.0, choices=PRICE_CHOICES, verbose_name="On average what is a comfortable range of price you would spend on dinner when eating out?")

    ALL_TIME = 0
    MOST_TIME = 1
    SOME_TIME = 2
    RARELY = 3
    NEVER = 4

    ALONE_CHOICES = (
          (ALL_TIME, 'All the time'),
          (MOST_TIME, 'Most of the time'),
          (SOME_TIME, 'Sometimes'),
          (RARELY, 'Rarely'),
          (NEVER, 'Never'),
        )
    lunch_alone = models.IntegerField(default=0, choices=ALONE_CHOICES, verbose_name="Do you eat lunch by yourself?")
    dinner_alone = models.IntegerField(default=0, choices=ALONE_CHOICES, verbose_name="Do you eat dinner by yourself?")
    fun = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel it's more enjoyable or fun to eat with my friends.")
    busy = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="Most of the times I am too busy to eat with my friends.")
    time = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel it takes too much time to eat with others.")
    happy = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel happier when eating with others.")
    alone = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel happy eating by myself.")
    guilty = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel guilty spending more money while eating with friends.")
    fun_price = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I feel its worth spending more money to eat with my friends.")


# TODO: survey that measures how influential some of your friends are

class MenuInterfaceSurvey(SurveyStatus):
    """
        Menu Interface Survey
    """

    STRONGLY_AGREE = 0
    AGREE = 1
    NEITHER = 2
    DISAGREE = 3
    STRONGLY_DISAGREE = 4

    LIKERT_CHOICES = (
          (STRONGLY_AGREE, 'Strongly agree'),
          (AGREE, 'Agree'),
          (NEITHER, 'Neither agree nor disagree'),
          (DISAGREE, 'Disagree'),
          (STRONGLY_DISAGREE, 'Strongly disagree'),
        )

    usability = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="The menu was easy to use.")

    TOO_SMALL = 0
    SMALL = 1
    ADEQUATE = 2
    LARGE = 3
    TOO_LARGE = 4

    LETTER_SIZES = (
            (TOO_SMALL, 'Too small'),
            (SMALL, 'Small'),
            (ADEQUATE, 'Adequate'),
            (LARGE, 'Large'),
            (TOO_LARGE, 'Too large')
        )
    letter_size = models.IntegerField(default=0, choices=LETTER_SIZES, verbose_name="What did you think about the size of the letters on the menu?")

    TOO_SLOW = 0
    SLOW = 1
    OK = 2
    FAST = 3
    TOO_FAST = 4
    
    SPEED_CHOICES = (
            (TOO_SLOW, 'Too slow'),
            (SLOW, 'Slow'),
            (OK, 'OK'),
            (FAST, 'Fast'),
            (TOO_FAST, 'Too fast')
        )
    speed = models.IntegerField(default=0, choices=SPEED_CHOICES, verbose_name="How was the browsing speed of the menu?")

    DISTRACTING = 0 
    NOT_HELPFUL = 1
    DIDNT_NOTICE = 2
    HELPFUL = 3
    EXTREME = 4
    NOT_APPLICABLE = 5

    HELPFUL_CHOICES = (
        (DISTRACTING, "Distracting/Harmful"),
        (NOT_HELPFUL, "Not helpful"),
        (DIDNT_NOTICE, "Didn't notice"),
        (HELPFUL, "Helpful"),
        (EXTREME, "Extremely helpful"),
        (NOT_APPLICABLE, "Not applicable"),
        )
    people = models.IntegerField(default=0, choices=HELPFUL_CHOICES, verbose_name="Were the social label about other people's choices helpful?") 
    friends = models.IntegerField(default=0, choices=HELPFUL_CHOICES, verbose_name="Were the social label about friend's choices helpful?")
    friends_category = models.IntegerField(default=0, choices=HELPFUL_CHOICES, verbose_name="How did you like the Friend's Choice category?")

    hierarchy = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like the hierarchical menu.")

    ease_hierarchy = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="The hierarchical menu was intuitive to use.")

    phone = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like ordering from the smart phone.")

    preorder = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I would like to preorder my food before going to the restaurant, so there is little wait until eating the food.")

    seating = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I would like to preorder my food before going to the restaurant and have my seats reserved at the same time.")

    payment = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I would like payment to be integrated with digital menu so when I order the food, it is paid for from my account (no need for card or cash).")

    comments = models.TextField(verbose_name="Any other comments you have about the menu or the dining experience:")


class ChoiceToEatSurvey(SurveyStatus):
    """
        How I choose my menu item
    """

    STRONGLY_AGREE = 0
    AGREE = 1
    NEITHER = 2
    DISAGREE = 3
    STRONGLY_DISAGREE = 4

    LIKERT_CHOICES = (
          (STRONGLY_AGREE, 'Strongly agree'),
          (AGREE, 'Agree'),
          (NEITHER, 'Neither agree nor disagree'),
          (DISAGREE, 'Disagree'),
          (STRONGLY_DISAGREE, 'Strongly disagree'),
        )

    plan = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually plan what I want to eat before I choose the restaurant.")
    me = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I choose what I want to eat at the restaurant.")
    friends = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to order what my friends suggest.")
    others = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to see what other people in other tables are eating.")
    chef = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to try what the chef or waiter suggests.")

    """
        How variety of choices one chooses
    """
    uncertain = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I usually do not know what I want to order until I look at the menu.")

    unsure = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="Even after looking at the menu sometimes I am unsure about what to pick.")

    different = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to try different restaurants.")
    spontaneous = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I am spontaneous.  I like to make last minute changes.")
    uniqueness = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I don't like to go with the crowd, so I try to find something different for myself.")
    variety = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I like to try a variety beyond my specific tastes.")
    averse = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I only try something different if my friend suggests.")
    own = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="I don't like to try something different even if my friend suggests.")

class PostTrialSurvey(SurveyStatus):
    """
        Some mix of questions after trial
    """
    STRONGLY_AGREE = 0
    AGREE = 1
    NEITHER = 2
    DISAGREE = 3
    STRONGLY_DISAGREE = 4


    LIKERT_CHOICES = (
          (STRONGLY_AGREE, 'Strongly agree'),
          (AGREE, 'Agree'),
          (NEITHER, 'Neither agree nor disagree'),
          (DISAGREE, 'Disagree'),
          (STRONGLY_DISAGREE, 'Strongly disagree'),
        )


    paper_peek = models.BooleanField(default=True, verbose_name="Did you peek at the paper menu?")
    easy = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="It was more difficult to use than the paper menu.")
    history = models.IntegerField(default=0, choices=LIKERT_CHOICES, verbose_name="It is helpful to see from the web what I have ordered in the past.")

class FriendDistanceSurvey(models.Model):
    status = models.ForeignKey( SurveyStatus, related_name="distances")
    friend = models.ForeignKey( User, related_name="to_friend" )


    DONT_KNOW = 0
    BARELY_KNOW = 1
    KNOW_SOMEWHAT = 2
    KNOW_WELL = 3
    SUPER_CLOSE = 4

    LIKERT_CHOICES = (
          (DONT_KNOW, "Don't know this person"),
          (BARELY_KNOW, 'Barely know (Acquaintance)'),
          (KNOW_SOMEWHAT, 'I somewhat know (Distant friend)'),
          (KNOW_WELL, 'I know well (Close friend)'),
          (SUPER_CLOSE, 'Very close (My buddy or significant other)'),
        )

    distance = models.IntegerField(default=2, choices=LIKERT_CHOICES, verbose_name="How close are you with this person?")
    completed = models.BooleanField( default=False )
    complete_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s (%s): friend distance survey"%(self.user.username, self.completed)


