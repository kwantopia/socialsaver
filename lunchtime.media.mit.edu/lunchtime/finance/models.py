from django.db import models
from common.models import OTNUser
import time
from sorl.thumbnail.fields import ImageWithThumbnailsField

class SpendingCategory(models.Model):
    name = models.CharField(max_length=50)
    
    def get_json(self):
        """
            :return: json format of category information
        """
        return {'id': self.id, 'name': self.name}

    def __unicode__(self):
        return self.name.capitalize()

# Create your models here.
class WesabeAccount(models.Model):
    user = models.ForeignKey(OTNUser)
    guid = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=50)
    balance = models.FloatField()

    def __unicode__(self):
        return "%s %s %.2f"%(self.user.username, self.guid, self.balance)
   
    def get_json(self):
        result = {
                'id': str(self.id),
                'name': self.name,
                'balance': str(self.balance)
                }
        return result

class Country(models.Model):
    """
        class that stores countries and their codes
    """
    name = models.CharField(max_length=50)
    iana_code = models.CharField(max_length=2)

class Region(models.Model):
    name = models.CharField(max_length=100)
    abbrv = models.CharField(max_length=10)
    country = models.ForeignKey(Country)

class PostalCode(models.Model):
    """ 
        class that stores zip code, city and state (region) in US
        for international use region
    """
    code = models.CharField(max_length=15)
    ext = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=50)
    region = models.ForeignKey(Region)

class WesabeLocation(models.Model):
    """
        Some locations that are logged in Wesabe has a 
        wesabe location ID
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=140, blank=True)
    wesabe_id = models.IntegerField(unique=True, null=True)

    address1 = models.CharField(null=True, blank=True, max_length=100)
    address2 = models.CharField(null=True, blank=True, max_length=100)
    postal_code = models.ForeignKey(PostalCode)
    phone = models.CharField(blank=True,max_length=20)

    latitude = models.FloatField(blank=True, default='42.373193')
    longitude = models.FloatField(blank=True, default='-71.094074')

    icon = ImageWithThumbnailsField(upload_to="wesabe/locations/icons/", max_length=200, thumbnail={'size': (50,50), 'options':['crop', 'upscale']}) 
    banner = ImageWithThumbnailsField(upload_to="wesabe/locations/banners/", max_length=200, thumbnail={'size': (320,50), 'options':['crop', 'upscale']}) 

    # TODO: Need to populate location types
    EATERY = 0
    LAUNDRY = 1
    SERVICE = 2
    PRODUCT = 3
    ADMIN = 4

    LOC_TYPES = (
            (EATERY, 'food'),
            (LAUNDRY, 'laundry'),
            (SERVICE, 'service'),
            (PRODUCT, 'product'),
            (ADMIN, 'admin'),
        )

    type = models.IntegerField(choices=LOC_TYPES, default=EATERY) 

    def get_json(self, level=0):
        """
            :param level: 0 if basic info of location, name and phone number
                            1 if all information is address and phone
                            2 if all information including description

        """

        detail = {'id': str(self.id),
                'name': self.name,
                'icon': self.icon.thumbnail.absolute_url if self.icon else "http://mealtime.mit.edu/media/techcash/default_icon.png",
                }

        if level == 1:
            detail = {'id': str(self.id),
                'name': self.name,
                'address': self.address1,
                'phone': '206-818-3624',
                'icon': self.icon.thumbnail.absolute_url if self.icon else "http://mealtime.mit.edu/media/techcash/default_icon.png",
                }

        elif level == 2:

            detail = {'id': str(self.id),
                'name': self.name,
                'address': self.address1,
                'phone': '206-818-3624',
                'description': self.description,
                'icon': self.icon.thumbnail.absolute_url if self.icon else "http://mealtime.mit.edu/media/techcash/default_icon.png",
                'banner': self.banner.thumbnail.absolute_url if self.banner else "http://mealtime.mit.edu/media/techcash/restaurant_banner.png",
                'latitude': str(self.latitude),
                'longitude': str(self.longitude) 
                }

        return detail

    def __unicode__(self):
        return self.name


    
class Memo(models.Model):
    """
        Maps memo's to locations
    """
    txt = models.CharField(max_length=200)
    # null True since location might not be identified
    location = models.ForeignKey(WesabeLocation, null=True)

class WesabeTransaction(models.Model):
    account = models.ForeignKey(WesabeAccount)
    amount = models.FloatField()
    date = models.DateTimeField()
    memo = models.ForeignKey(Memo)
    guid = models.CharField(max_length=64, unique=True)
    
    def get_json(self, level=0, me=None):
        # TODO: calculate number of others who also
        # transacted similarly
        
        result = {
                      'id': str(self.id),
                      'amount': "%.2f"%self.amount,
                      'timestamp': str(time.mktime(self.date.timetuple())),
                      'date': self.date.strftime("%b %d, %Y"),
                      'memo': self.memo.txt,
                      'location': self.memo.location.get_json(),
                      'new': str(self.detail.new),
                }

        # get num of coupons
        coupons = Coupon.objects.filter(location=self.memo.location).count()
        if coupons > 0:
            result["coupons"] = str(coupons)

        if level == 2:
            result = {
                      'id': str(self.id),
                      'amount': str(self.amount),
                      'timestamp': str(time.mktime(self.date.timetuple())),
                      'date': self.date.strftime("%b %d, %Y"),
                      'memo': self.memo.txt,
                      'location': self.memo.location.get_json(),
                      'new': str(self.detail.new),
                      'guid': self.guid,
                      }
            # get coupon details
            if coupons > 0:
                result["coupons"] = str(coupons)
                result["coupon_list"] = []
                for c in Coupon.objects.filter(location=self.memo.location):
                    result["coupon_list"].append(c.get_json())
        
        if me:
            if me.experiment.id == 2:
                # social group
                result['people'] = ['Bob', 'Tiger', 'Julie']
            elif me.experiment.id == 3:
                result['people'] = '9'
        return result  
 
class Detail(models.Model):
    """
        Any additionally processed details
        Sharability, rating, category
        TODO: need to add tagging functionality
    """
    txn = models.OneToOneField(WesabeTransaction)
    detail = models.TextField(blank=True)
    rating = models.IntegerField(default=0)

    PRIVATE = 0
    FRIENDS = 1
    COMMUNITY = 2
    PUBLIC = 3

    SHARING_CHOICES = (
        (PRIVATE, 'Private'),
        (FRIENDS, 'Friends'),
        (COMMUNITY, 'Community'),
        (PUBLIC, 'Public'),
    )

    sharing = models.IntegerField(choices=SHARING_CHOICES, default=PUBLIC)
    image = ImageWithThumbnailsField(upload_to="wesabe/%Y/%m/%d", max_length=200, thumbnail={'size': (50,50), 'options':['crop', 'upscale']}) 
    category = models.ForeignKey(SpendingCategory)
    # indicates whether this receipt has been viewed or not
    new = models.BooleanField(default=True)
    last_update = models.DateTimeField(auto_now=True)

    def get_json(self):
        result = {}

        result["id"] = str(self.id)
        result["detail"] = self.detail
        result["rating"] = str(self.rating) 
        result["sharing"] = str(self.sharing) 
        if self.image:
            result["image"] = self.image.url
        else:
            result["image"] = "/media/wesabe/heart.png"
        result["category"] = self.category.get_json()
        result["new"] = str(self.new)
        result["last_update"] = self.last_update.strftime("%b %d, %Y - %I:%M:%S %p")
        result["last_timestamp"] = str(time.mktime(self.last_update.timetuple())) 
        return result

class SplitItem(models.Model):
    txn = models.ForeignKey(WesabeTransaction)
    name = models.CharField(max_length=50)
    price = models.FloatField()

    def get_json(self):
        result = {}

        result["id"] = str(self.id)
        result["name"] = self.name
        result["price"] = "%.2f"%self.price

        return result

class Coupon(models.Model):
    location = models.ForeignKey(WesabeLocation)
    dealer = models.CharField(max_length=50)
    content = models.CharField(max_length=100)
    # Internet coupon number
    number = models.CharField(max_length=12)
    # any details and restrictions
    details = models.TextField()
    icon = ImageWithThumbnailsField(upload_to="wesabe/coupons/icons/%Y/%m/%d", max_length=200, thumbnail={'size': (50,50), 'options':['crop', 'upscale']}) 
    banner = ImageWithThumbnailsField(upload_to="wesabe/coupons/banners/%Y/%m/%d", max_length=200, thumbnail={'size': (320,200), 'options':['crop', 'upscale']}) 
    expiry_date = models.DateField(null=True)
    posted = models.DateTimeField(auto_now_add=True)

    def get_json(self):
        result = {}

        result = {
            "id": str(self.id),
            "location": self.location.get_json(),
            "dealer" : self.dealer,
            "content" : self.content,
            "number" : self.number,
            "details" : self.details,
            "expiry_date" : self.expiry_date.strftime("%m/%d/%y"),
            'icon' : self.icon.thumbnail.absolute_url if self.icon else "http://mealtime.mit.edu/media/techcash/default_icon.png",
            'banner' : self.banner.thumbnail.absolute_url if self.banner else "http://mealtime.mit.edu/media/techcash/restaurant_banner.png",
        }
        return result

class Weather(models.Model):
    # wind
    direction = models.FloatField()
    speed = models.FloatField()
    chill = models.FloatField()

    # atmosphere
    pressure = models.FloatField()
    rising = models.FloatField()
    visibility = models.FloatField()
    humidity = models.FloatField()

    # sun
    sunrise = models.TimeField()
    sunset = models.TimeField()

    # current temp
    update_time = models.DateTimeField()
    description = models.CharField(max_length=50)
    code = models.IntegerField()
    temp = models.IntegerField()

    # forecast
    forecast1_code = models.IntegerField()
    forecast1_text = models.CharField(max_length=50)
    forecast1_high = models.IntegerField()
    forecast1_low = models.IntegerField()
    forecast1_date = models.DateField()

    SUN = 0
    MON = 1
    TUE = 2
    WED = 3
    THU = 4
    FRI = 5
    SAT = 6
    DAY_CHOICES = (
            (SUN, 'Sun'),
            (MON, 'Mon'),
            (TUE, 'Tue'),
            (WED, 'Wed'),
            (THU, 'Thu'),
            (FRI, 'Fri'),
            (SAT, 'Sat'),
        )
    forecast1_day = models.IntegerField(choices=DAY_CHOICES)

    forecast2_code = models.IntegerField()
    forecast2_text = models.CharField(max_length=50)
    forecast2_high = models.IntegerField()
    forecast2_low = models.IntegerField()
    forecast2_date = models.DateField()
    forecast2_day = models.IntegerField(choices=DAY_CHOICES)

#############################################################
# For tracking
#############################################################
class LogCategoryCreation(models.Model):
    category = models.ForeignKey(SpendingCategory)
    user = models.ForeignKey(OTNUser)
    #: the time the category was created
    timestamp = models.DateTimeField(auto_now_add=True)


