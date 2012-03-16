from django.db import models
from legals.models import MenuItem
from facebookconnect.models import BigIntegerField
import random

# get_facebook_client lets us get the current Facebook object
# from outside of a view, which lets us have cleaner code
from facebook.djangofb import get_facebook_client

class UserManager(models.Manager):
    """Custom manager for a Facebook User."""
    
    def get_current(self):
        """Gets a User object for the logged-in Facebook user."""
        facebook = get_facebook_client()
        user, created = self.get_or_create(id=int(facebook.uid))
        if created:
            # assign experimental group for user 
            user.experiment = random.randint(0,3)
            user.save()
        return user

class User(models.Model):
    """A simple User model for Facebook users."""

    # We use the user's facebook UID as the primary key in our database.
    id = BigIntegerField(primary_key=True)

    INFORM = 0
    INFORM_PEER = 1
    ALTRUISM = 2
    ALTRUISM_PEER = 3

    EXPERIMENT_CHOICES = (
            ( INFORM, 'Information only'),
            ( INFORM_PEER, 'Information with peer participants'),
            ( ALTRUISM, 'Altruism only'),
            ( ALTRUISM_PEER, 'Altruism with peer participants'),
        )
    experiment = models.IntegerField(choices=EXPERIMENT_CHOICES, default=0)
    friends_at_signup = models.IntegerField(default=0)
    friends_str = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    facebook_first_name = models.CharField(max_length=100, blank=True, null=True)
    facebook_last_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    proxied_email = models.CharField(max_length=255, blank=True, null=True)
    birthday_date = models.CharField(max_length=10, blank=True, null=True)
    started = models.DateTimeField(auto_now_add=True)
   
    # Add the custom manager
    objects = UserManager()

class TasteChoice(models.Model):
    sense = models.CharField(max_length=15)

    def __unicode__(self):
        return self.sense

class FriendMapped(models.Model):
    user = models.ForeignKey(User)
    mapped = models.BooleanField(default=False)

class Invited(models.Model):
    user = BigIntegerField() 
    invited = BigIntegerField() 
    timestamp = models.DateTimeField(auto_now_add=True)

class LegalsPopulationSurvey(models.Model):
    facebook_id = BigIntegerField()
    email = models.CharField(max_length=140, blank=True, verbose_name='Your Email (for participating in digital menu trial)')
    referrer = models.CharField(max_length=140, blank=True, verbose_name='Email of referrer (if applicable)')
 
    MALE = 0
    FEMALE = 1
    NEITHER = 2
    SEX_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    sex = models.IntegerField(choices=SEX_CHOICES, default=FEMALE)

    EIGHTEEN = 18 
    TWENTY_SIX = 26
    THIRTY_SIX = 36
    FORTY_SIX = 46
    FIFTY_SIX = 56

    AGE_CHOICES = (
            (EIGHTEEN, '16-25'),
            (TWENTY_SIX, '26-35'),
            (THIRTY_SIX, '36-45'),
            (FORTY_SIX, '46-55'),
            (FIFTY_SIX, '56 or older'),
    )
    age = models.IntegerField(choices=AGE_CHOICES, default=EIGHTEEN)

    DONT_LIKE = 1
    DONT_MIND = 2
    KIND_OF = 3
    ITS_ONE_OF_FAVORITE = 4
    ITS_THE_FAVORITE = 5

    LIKE_CHOICES = (
            (DONT_LIKE, "I don't like sea food"),
            (DONT_MIND, "I don't mind sea food, but I'd rather eat something else"),
            (KIND_OF, "I like sea food"),
            (ITS_ONE_OF_FAVORITE, "It's one of my favorite foods"),
            (ITS_THE_FAVORITE, "It's my favorite food by far!"),
        )

    like_seafood = models.IntegerField(choices=LIKE_CHOICES, default=KIND_OF,verbose_name='How much do you like sea food?' )

    NEVER = 0
    FEW_TIMES_YEAR = 1
    ONCE_A_MONTH = 1
    ONCE_TWO_WEEKS = 2
    ONCE_A_WEEK = 4
    TWO_THREE_WEEK = 10 
    MORE_THAN_FOUR = 20
    EVERYDAY = 30 

    VISIT_CHOICES = (
            (NEVER, 'Never eat out'),
            (FEW_TIMES_YEAR, 'Only a few times a year'),
            (ONCE_A_MONTH, 'Once a month'),
            (ONCE_TWO_WEEKS, 'Once every two weeks'),
            (ONCE_A_WEEK, 'Once a week'),
            (TWO_THREE_WEEK, 'Two, three times a week'),
            (MORE_THAN_FOUR, 'More than 4 times a week'),
            (EVERYDAY, 'Everyday'),
    )

    restaurant_visits = models.IntegerField(choices=VISIT_CHOICES, default=ONCE_A_WEEK, verbose_name='How often do you visit restaurants in a month?')
    seafood_visits = models.IntegerField(choices=VISIT_CHOICES, default=ONCE_A_MONTH, verbose_name='How often do you visit SEA FOOD restaurants in a month?')
    legals_visits = models.BooleanField(default=False, verbose_name='Have you ever been to Legal Sea Foods?')

    NEVER = 0
    ONCE = 1
    THREE = 3
    SIX = 6
    NINE = 9
    MORE = 10 

    LEGALS_VISIT_CHOICES = (
                (NEVER, "Haven't visited"),
                (ONCE, 'Once'),
                (THREE, 'Once a month (About 3 times)'),
                (SIX, 'Twice a month (About 6 times)'),
                (NINE, 'Three times a month (About 9 times)'),
                (MORE, 'More than 10 times'),
            )

    frequency = models.IntegerField(choices=LEGALS_VISIT_CHOICES, default=ONCE, verbose_name="How many times have you visited Legal's in the last 3 months?")
    vegetarian = models.BooleanField(default=False, verbose_name='Are you a vegetarian?')
    zipcode = models.CharField(max_length=5)
    gluten = models.BooleanField(default=False, verbose_name='Are you gluten sensitive? (Require gluten free meal)')
    tastes = models.ManyToManyField(TasteChoice, verbose_name='Pick 3 words that describe your favorite tastes')
    favorite_dishes = models.ManyToManyField(MenuItem, verbose_name='Imagine you are ordering at Legal Sea Foods, pick 5 favorite items that you would like to eat.  Make sure you look at the whole menu!', related_name="pre_favorite_dishes")

    IPHONE = 0
    ANDROID = 1
    PALM_PRE = 2
    BLACKBERRY = 3
    OTHER = 4

    PHONE_CHOICES = (
        (IPHONE, 'iPhone'),
        (ANDROID, 'Android'),
        (PALM_PRE, 'Palm Pre'),
        (BLACKBERRY, 'Blackberry'),
        (OTHER, 'Other'),
    )

    phone_type = models.IntegerField(choices=PHONE_CHOICES, default=IPHONE, verbose_name='What type of phone do you use?')
    timestamp = models.DateTimeField(auto_now_add=True)
    opt_out = models.BooleanField(default=False)

class BostonZip(models.Model):
    zipcode = models.CharField(max_length=5)
    name = models.CharField(max_length=30)
    distance = models.FloatField()
