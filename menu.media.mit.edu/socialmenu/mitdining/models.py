from django.db import models
from django.contrib.auth.models import User
from common.models import Experiment

# Create your models here.

class StoreCategory(models.Model):
    """
        Used for MIT neighborhood dining
        i.e. House Dining, Trucks, Student Center
    """
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name


class Store(models.Model):
    """
        Store name
    """
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=20, null=True)
    state = models.CharField(max_length=2, null=True)
    phone = models.CharField(max_length=20, null=True)
    store_category = models.ForeignKey(StoreCategory)

    def __unicode__(self):
        return self.name

class Category(models.Model):
    """
        Menu category
        The store can have no category in which case it will have
        the "Default" category
    """
    name = models.CharField(max_length=30)
    description = models.CharField(null=True, max_length=500)
    store = models.ForeignKey(Store)

    def __unicode__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()
    description = models.CharField(null=True, max_length=500)
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
    comment = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

class Order(models.Model):
    user = models.ForeignKey(User, related_name='mit_order')
    items = models.ManyToManyField(MenuItemReview, related_name='mit_ordered')
    timestamp = models.DateTimeField(auto_now_add=True)
    #: for specifying which table it was ordered from to track groups
    table = models.CharField(max_length=10, blank=True)

    class Meta:
        get_latest_by='timestamp'

    def when_ordered(self):
        info = {}
        info['name'] = self.user.first_name
        info['date'] = self.timestamp.strftime("%b %d, %Y %I:%M:%S %p")
        return info

    def total_price(self):
        total = 0
        price = ''
        for d in self.items.all():
            if d.item.price > 0:
                total += d.item.price
            else:
                detail = d.item.get_json()
                price += detail['price_hi'] + '+' 

        if total > 0:
            price += "$%.2f"%total
        elif price[-1]=='+':
            price = price[:-1]

        return price

    def get_json(self):
        dishes = []
        for review in self.items.all():
            dishes.append({
                    'review_id': str(review.id),
                    'id': str(review.item.id),
                    'name': review.item.name,
                    'rating': review.rating,
                    'comment': review.comment})
        # order detail
        detail = { 'id': str(self.id),
            'user': self.user.first_name,
            'date': self.timestamp.strftime("%b %d, %Y - %I:%M:%S %p"),
            'dishes': dishes,
            'total': self.total_price()
        }

        return detail

    def __unicode__(self):
        dishes = self.items.all()
        ordered = []
        for d in dishes:
            ordered.append(d.item.name)
        return "%s ordered %s"%(self.user.id, ordered)

class Event(models.Model):
    user = models.ForeignKey(User, related_name='mit_event')
    timestamp = models.DateTimeField(auto_now_add=True)

class EventStoreCategory(models.Model):
    event = models.OneToOneField(Event, primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class EventStore(models.Model):
    event = models.OneToOneField(Event, primary_key=True)
    store = models.ForeignKey(Store)

class EventCategory(models.Model):
    event = models.OneToOneField(Event, primary_key=True)
    category = models.ForeignKey(Category)

class EventMenuItem(models.Model):
    event = models.OneToOneField(Event, primary_key=True)
    item = models.ForeignKey(MenuItem)
    # mark or unmark
    UNMARK = 0
    MARK = 1
    ACTIONS = (
            (MARK, 'mark'),
            (UNMARK, 'unmark'),
    )
    action = models.IntegerField(choices=ACTIONS)
    num_people = models.IntegerField(default=0)
    influencers = models.ManyToManyField(User, related_name="mit_influenced")

class EventAlternate(models.Model):
    """
        Model used to track alternate
    """
    event = models.OneToOneField(Event, primary_key=True)
    item = models.ForeignKey(MenuItem, related_name='mit_originally_chosen')
    influencer = models.ForeignKey(User, related_name='mit_influenced_change')
    alternate = models.ForeignKey(MenuItem, related_name='mit_alternately_chosen')
    experiment = models.ForeignKey(Experiment, related_name='mit_alternates')
