from django.db import models
from django.contrib.auth.models import User
from common.models import Experiment
from datetime import datetime, date, timedelta
import random, time
from sorl.thumbnail.fields import ImageWithThumbnailsField
from django.conf import settings

# Create your models here.

logger = settings.LOGGER
TC_EXPIRE_MINS = settings.TC_EXPIRE_MINS

class HumanSubjectCompensation(models.Model):
    """
        Human subject compensation related information
    """
    user = models.OneToOneField(User)
    address = models.CharField(max_length=200, default="No address")
    city = models.CharField(max_length=50, default="No city")
    state = models.CharField(max_length=30, default="No state")
    zipcode = models.CharField(max_length=10, default="00000", verbose_name="Zip Code") 
    verified = models.BooleanField(default=False)
    certificates = models.TextField(blank=True, verbose_name="Certificates (separate using comma)")
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%d\t%s\t%s\t%s"%(self.verified, self.user.otnuser.my_email, self.address, self.updated.strftime("%m/%d/%y"))

class Store(models.Model):
    """
        Store name
    """
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=20, null=True)
    state = models.CharField(max_length=2, null=True)
    phone = models.CharField(max_length=20, null=True)

    def __unicode__(self):
        return self.name

class TableCodeManager(models.Manager):

    def check_code( self, c ):
        """
            Checks if code c is a valid code that can be used

            returns table code object with experiment assigned
        """
        valid_today = self.filter(code=c, date=date.today())
        today_new = valid_today.filter(first_used=None)
        logger.debug("Checking table code: %s"%c)
        if today_new.count() > 0:
            use_code = today_new[0]
            logger.debug("You can use table code: %s", use_code.code)
            # use this
            use_code.first_used = datetime.now() 
            use_code.save()
            # assign experiment
            random.seed(hash(time.time()))
            exp_no = random.randint(1, Experiment.objects.filter(active=True).count())
            # only for manually testing set exp_no explicitly
            #exp_no = 4
            exp = Experiment.objects.get(id=exp_no)
            use_code.experiment = exp
            use_code.save()
            return use_code 
        else:
            # see if there are any used table code that are still valid 
            today_used = valid_today.filter(first_used__gt=datetime.now()-timedelta(minutes=TC_EXPIRE_MINS))
            if today_used.count() > 0:
                logger.debug("You can use table code: %s", today_used[0].code)
                # only for manual testing set exp explicitly and use this
                #exp = Experiment.objects.get(id=4)
                tc = today_used[0]
                #tc.experiment = exp
                #tc.save()
                return tc 
        # this code cannot be used
        return None 

class TableCode(models.Model):
    """
        Table code

        4 character codes that are assigned to each day
    """
    code = models.CharField(max_length=4)
    experiment = models.ForeignKey(Experiment, null=True)
    date = models.DateField()
    # first time it was used
    first_used = models.DateTimeField(null=True)
    # expires after being used
    expired = models.BooleanField(default=False)

    objects = TableCodeManager()

    def __unicode__(self):
        return self.code

class Category(models.Model):
    """
        Menu category
    """
    name = models.CharField(max_length=30)
    description = models.CharField(null=True, max_length=500)

    def __unicode__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField(default=0.0)
    description = models.CharField(null=True, blank=True, max_length=500)
    category = models.ForeignKey(Category)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def get_json(self):

        detail = {
            'id': str(self.id),
            'name': self.name,
            'price': "$%.2f"%self.price,
            'description': self.description,
            'category': self.category.name
        }

        if self.price < 0:
            detail['price'] = "Market Price"

        try: 
            multiple =  OptionPrice.objects.get(item=self)
            detail = {
                'id': str(self.id),
                'name': self.name,
                'price': str(multiple),
                'price_low': multiple.get_json()['price_one'],
                'price_hi': multiple.get_json()['price_two'],
                'description': self.description,
                'category': self.category.name
            }
           
        except OptionPrice.DoesNotExist:
            pass
        return detail

    def cost(self):
        if self.price == -1:
            return 35
        elif self.price == -2:
            return OptionPrice.objects.get(item=self).price_one
        else:
            return self.price

class ChefChoice(models.Model):
    item = models.ForeignKey(MenuItem)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(default=date.today()+timedelta(7))

    def __unicode__(self):
        return self.item.name

class OptionPrice(models.Model):
    item = models.OneToOneField(MenuItem)
    option_one = models.CharField(max_length=20)
    price_one = models.FloatField()
    option_two = models.CharField(max_length=20)
    price_two = models.FloatField()

    def __unicode__(self):
        return "%s $%.2f %s $%.2f" % (self.option_one, self.price_one, self.option_two, self.price_two)

    def get_json(self):
        detail = { 
                'option_one': self.option_one,
                'price_one': "$%.2f"%self.price_one,
                'option_two': self.option_two,
                'price_two': "$%.2f"%self.price_two,
        }
        return detail

class MenuItemReview(models.Model):
    item = models.ForeignKey(MenuItem)
    
    NOT_RATED = 0
    POOR = 1
    FAIR = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5

    RATING_CHOICES = (
        (NOT_RATED, 'Not Rated'),
        (POOR, 'Poor'),
        (FAIR, 'Fair'),
        (AVERAGE, 'Average'),
        (GOOD, 'Good'),
        (EXCELLENT, 'Excellent'),
    )

    rating = models.IntegerField(choices=RATING_CHOICES, default=NOT_RATED)

    #: reason for ordering
    NOT_CHOSEN = 0
    PLANNED = 1
    NOT_REMEMBER = 2
    SOMETHING_NEW = 3
    HEALTH = 4
    PRICE = 5
    FRIEND_SUGGESTED = 6
    OTHERS_LIKE = 7
    LIKE_IT = 8
    STAFF = 9
    OTHER = 10 

    REASON_CHOICES = (
        (NOT_CHOSEN, "No choice has been made"),
        (PLANNED, "Been planning to visit Legal's to eat this"),
        (NOT_REMEMBER, "I do not remember"),
        (SOMETHING_NEW, "I wanted to try something new"),
        (HEALTH, "I wanted something healthy"),
        (PRICE, "It was reasonably priced"),
        (FRIEND_SUGGESTED, "My friend(s) suggested that I try it"),
        (OTHERS_LIKE, "Other people seem to like it"),
        (LIKE_IT, "I particularly like the dish"),
        (STAFF, "Suggested by waiting staff"),
        (OTHER, "Other (please comment below)"),
    )
    reason = models.IntegerField(choices=REASON_CHOICES, default=NOT_CHOSEN)
    comment = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

class Order(models.Model):
    user = models.ForeignKey(User, related_name='legals_order')
    items = models.ManyToManyField(MenuItemReview, related_name='legals_ordered')
    timestamp = models.DateTimeField(auto_now_add=True)
    #: tracks the last time any part of the order was updated
    updated = models.DateTimeField(auto_now=True)
    #: for specifying which table it was ordered from to track groups
    table = models.ForeignKey(TableCode, related_name='table_orders')
    receipt = ImageWithThumbnailsField(upload_to="receipts/%Y/%m/%d", thumbnail={'size': (75,100), 'options': ['crop', 'upscale']})
    #: set to True after human verification
    verified = models.BooleanField(default=False)

    class Meta:
        get_latest_by='timestamp'

    def when_ordered(self):
        info = {}
        info['name'] = self.user.first_name
        info['date'] = self.timestamp.strftime("%b %d, %Y %I:%M:%S %p")
        return info

    def last_update(self):
        self.updated = datetime.now()
        self.save()

    def total_price(self):
        total = 0
        price = ''
        for d in self.items.all():
            if d.item.price > 0:
                total += d.item.price
            elif d.item.price == -2:
                detail = d.item.get_json()
                price += detail['price_hi'] + '+' 
            else:
                price += 'Market Price' + '+'

        if total > 0:
            price += "$%.2f"%total
        elif price[-1]=='+':
            price = price[:-1]

        return price

    def total_price_value(self):
        total = 0
        price = ''
        for d in self.items.all():
            if d.item.price > 0:
                total += d.item.price
            elif d.item.price == -2:
                detail = d.item.get_json()
                total += float(detail['price_hi'][1:])
            else:
                total += 35
        if total > 0:
            price += "$%.2f"%total
        elif price[-1]=='+':
            price = price[:-1]

        return total 

    def get_json(self):
        dishes = []
        for review in self.items.all():
            dishes.append({
                    'review_id': str(review.id),
                    'id': str(review.item.id),
                    'name': review.item.name,
                    'rating': review.rating,
                    'reason': review.reason,
                    'comment': review.comment})
        # order detail
        detail = { 'id': str(self.id),
            'user': self.user.first_name,
            'date': self.timestamp.strftime("%b %d, %Y - %I:%M:%S %p"),
            'dishes': dishes,
            'total': self.total_price(),
            'receipt': self.receipt.url if self.receipt else None,
            'thumbnail': self.receipt.thumbnail.absolute_url if self.receipt else None
        }

        return detail

    def __unicode__(self):
        dishes = self.items.all()
        ordered = []
        for d in dishes:
            ordered.append(d.item.name)
        return "%s ordered %s on %s"%(self.user.id, ordered, self.timestamp)

    def num_items(self):
        return self.items.count()

    def num_common_orders(self, o):
        a = set()
        b = set()

        for m in self.items.all():
            a.add(m.item.id)

        for m in o.items.all():
            b.add(m.item.id)
    
        return len(a & b)

    def common_orders(self, o):
        a = set()
        b = set()

        for m in self.items.all():
            a.add(m.item.id)

        for m in o.items.all():
            b.add(m.item.id)
    
        return a & b

class Feedback(models.Model):
    user = models.ForeignKey(User)

    TOO_SLOW = 0
    SLOW = 1
    ADEQUATE = 2
    FAST = 3
    TOO_FAST = 4

    SPEED_CHOICES = (
            ( TOO_SLOW, 'Too slow' ),
            ( SLOW, 'Slow' ),
            ( ADEQUATE, 'Adequate' ),
            ( FAST, 'Fast'),
            ( TOO_FAST, 'Too Fast' ),
        )

    speed = models.IntegerField(choices=SPEED_CHOICES, default=TOO_FAST)

    TOO_SMALL = 0
    SMALL = 1
    ADEQUATE = 2
    BIG = 3
    TOO_BIG = 4

    SIZE_CHOICES = (
            ( TOO_SMALL, 'Too small' ),
            ( SMALL, 'Small' ),
            ( ADEQUATE, 'Adequate' ),
            ( BIG, 'Big'),
            ( TOO_BIG, 'Too big' ),
        )


    size = models.IntegerField(choices=SIZE_CHOICES, default=TOO_BIG) 
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

# used before user has logged in
class EventAccess(models.Model):
    udid=models.CharField(max_length=64)
    #: when bad login
    bad=models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)

class Event(models.Model):
    user = models.ForeignKey(User, related_name='legals_event')
    order = models.ForeignKey(Order, null=True)
    experiment = models.ForeignKey(Experiment)
    timestamp = models.DateTimeField(auto_now_add=True)
    params = models.TextField()

class EventBasic(Event):
    table_code = models.ForeignKey(TableCode, null=True)

    LOGIN_VALID = 0     # login valid with table code
    LOGIN_OUTSIDE = 1   # login from outside restaurant, no table code
    LOGIN_INVALID = 2   # failed login attempt
    MY_ORDER = 3        # view my order
    LOGIN_TEST = 4      # when tested from shell

    ACTIONS = (
            (LOGIN_VALID, 'login valid'),
            (LOGIN_OUTSIDE, 'login outside'),
            (LOGIN_INVALID, 'login invalid'),
            (MY_ORDER, 'my order'),
            (LOGIN_TEST, 'login test'),
    )
    action = models.IntegerField(choices=ACTIONS)
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    comment = models.TextField()

    def __unicode__(self):
        return "%s %s"%(EventBasic.ACTIONS[self.action][1], self.timestamp)

class EventCategory(Event):
    category = models.ForeignKey(Category)

    def __unicode__(self):
        return "%s %s"%(self.category.name, self.timestamp)

class EventSpecial(Event):
    ALLERGIES = 0
    FRIENDS = 1
    CHEFS = 2

    SPECIALS = (
        (ALLERGIES, 'allergies'),
        (FRIENDS, 'friends'),
        (CHEFS, 'chefs'),
    )

    category = models.IntegerField(choices=SPECIALS)

    def __unicode__(self):
        return "%s %s"%(EventSpecial.SPECIALS[self.category][1], self.timestamp)

class EventMenuItem(Event):
    item = models.ForeignKey(MenuItem)

    # mark or unmark
    UNMARK = 0
    MARK = 1
    CONSIDER = 2
    RECONSIDER = 3

    ACTIONS = (
            (UNMARK, 'unmark'),
            (MARK, 'mark'),
            (CONSIDER, 'consider'),
            (RECONSIDER, 'reconsider'),
    )
    action = models.IntegerField(choices=ACTIONS)
    num_people = models.IntegerField(default=0)
    influencers = models.ManyToManyField(User, related_name="legals_influenced")

    def __unicode__(self):
        return "%s %s %s"%(EventMenuItem.ACTIONS[self.action][1], self.item.name, self.timestamp)

class EventAlternate(Event):
    """
        Model used to track alternate
    """
    item = models.ForeignKey(MenuItem, related_name='legals_originally_chosen')
    influencer = models.ForeignKey(User, related_name='legals_influenced_change')
    alternate = models.ForeignKey(MenuItem, related_name='legals_alternately_chosen')

