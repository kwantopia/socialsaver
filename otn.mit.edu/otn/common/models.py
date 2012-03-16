from django.db import models
from django.contrib.auth.models import User, UserManager
import datetime, time
from sorl.thumbnail.fields import ImageWithThumbnailsField
from httplib2 import Http

# Create your models here.

class Experiment(models.Model):
    name = models.CharField(blank=True, max_length=100) 
    description = models.CharField(blank=True, max_length=200)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.id)+": "+self.name

class OTNUser(User):
    """
        User profile model for the system
    """
    name = models.CharField(max_length=140, blank = True, null=True)
    pin = models.CharField(max_length=128, null=True)
    #mit_id = models.CharField(max_length=9, blank = True, null=True)
    experiment = models.ForeignKey(Experiment)
    phone = models.CharField(null=True, blank=True, max_length=20)

    proxy_email = models.CharField(max_length=255, null=True)
    fb_image = models.CharField(max_length=255, default="")

    image = ImageWithThumbnailsField(upload_to='/users/', thumbnail={'size':(50,50), 'options': ['crop', 'upscale']})

    #voucher = models.BooleanField(default=False)
    # number of visits to Legal's
    #visits = models.IntegerField(default=0)

    updated = models.DateTimeField(auto_now=True)

    REGISTERED = 0
    APPROVED = 1
    ACTIVE = 2
    APPROVE_STATUS = (
                (REGISTERED, 'Registered'),
                (APPROVED, 'Approved'),
                (ACTIVE, 'Active'),
            )

    approved = models.IntegerField(choices=APPROVE_STATUS, default=REGISTERED)
    registered = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    def __unicode__(self):
        if self.name is None:
            return "Unknown Name (%d)"%self.experiment.id
        else:
            return "%s (%d)"%(self.name, self.experiment.id)

    def get_full_name(self):
        if self.name:
            return self.name.title()
        elif self.first_name:
            return "%s %s"%(self.first_name, self.last_name)
        else:
            return "Unknown Name"

    def get_pic(self):
        img_url = "http://www.facebook.com/pics/t_silhouette.gif"
        if self.image:
            img_url = self.image.thumbnail.absolute_url
        elif len(self.pldb_image) > 1:
            img_url = self.pldb_image
        elif len(self.fb_image) > 1:
            img_url = self.fb_image
        else:
            img_url = "http://www.facebook.com/pics/t_silhouette.gif"
        return img_url

    def get_json(self, level=0):
        result['alias'] = self.email.split("@")[0]
        result['id'] = '0'
        result['name'] = 'Anonymous'

        if level == 1:
            result['id'] = str(self.id)
            result['name'] = self.get_full_name()
            result['first_name'] = self.first_name
            result['last_name'] = self.last_name

        result['first_joined'] = str(time.mktime(self.first_joined.timetuple()))

        result['image'] = self.get_pic() 

        result['phone'] = self.phone if self.phone else "Unknown"

        return result

    def link(self):
        first_name = self.first_name if self.first_name else self.name.split(" ")[0]
        return "<a href='tt://person/%d'>%s</a>"%(self.id, first_name)

    def first_name(self):
        return self.name.split()[0]

class SharingProfile(models.Model):
    """
        User's sharability settings
    """
    user = models.OneToOneField(User)

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

    general = models.IntegerField(choices=SHARING_CHOICES, default=PUBLIC)
    laundry = models.IntegerField(choices=SHARING_CHOICES, default=PUBLIC)
    # can have different sharing choices for different categories

class OTNConsent(models.Model):
    """
        Model used to record user consent
    """
    user = models.ForeignKey(User)
    techcash = models.BooleanField(default=True)
    otn = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class Friends(models.Model):
    facebook_id = models.BigIntegerField(unique=True) 
    friends = models.ManyToManyField('self')
    image = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=140, null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def get_image(self):
        h = Http()
        resp, content = h.request( self.image )
        if len(content) > 140:
            return self.image
        else:
            return "http://www.facebook.com/pics/t_silhouette.gif"

    def is_friend(self, fb_id):
        if self.friends.filter(facebook_id=fb_id).exists():
            return True
        else:
            return False

class Location(models.Model):
    """
        Model describing the location or restaurant
    """
    name = models.CharField(max_length=40)
    address = models.CharField(blank=True, max_length=50)
    phone = models.CharField(blank=True,max_length=20)
    description = models.CharField(max_length=140, blank=True)
    icon = models.CharField(max_length=200, blank=True, default="http://mealtime.mit.edu/media/techcash/default_icon.png")
    banner = models.CharField(max_length=200, blank=True, default="http://mealtime.mit.edu/media/techcash/restaurant_banner.png") 
    latitude = models.FloatField(blank=True, default='42.373193')
    longitude = models.FloatField(blank=True, default='-71.094074')
    
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
                }

        if level == 1:
            detail = {'id': str(self.id),
                'name': self.name,
                'address': self.address,
                'phone': '206-818-3624',
                'image': self.icon,
                }

        elif level == 2:

            detail = {'id': str(self.id),
                'name': self.name,
                'address': self.address,
                'phone': '206-818-3624',
                'description': self.description,
                'image': self.icon,
                'banner': self.banner,
                'latitude': str(self.latitude),
                'longitude': str(self.longitude) 
                }

        return detail

    def __unicode__(self):
        return self.name

class Featured(models.Model):

    location = models.ForeignKey(Location)
    day = models.DateField(default=datetime.date.today(), unique=True)
    description = models.CharField(max_length=200, blank=True)
    # the dollar amount discounted
    amount = models.FloatField(default=0.0)
    # the percentage discounted
    percent = models.FloatField(default=0.0)
    pub_date = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(blank=True, null=True)
    image = models.CharField(max_length=200, default="http://mealtime.mit.edu/media/techcash/featured_deal150.jpg")

    def get_json(self):

        if self.expires == None:
            detail = {'id': str(self.id),
                      'location': self.location.get_json(level=2),
                      'description': self.description,
                      'expires': 'None', 
                      'image': self.image
                      }
        else:
            detail = {'id': str(self.id),
                      'location': self.location.get_json(level=2),
                      'description': self.description,
                      'expires': str(time.mktime(self.expires.timetuple())),
                      'image': self.image
                      }

        return detail

    def __unicode__(self):
        return "%s: %s"%(self.location, self.description)

    def get_location(self):
        detail = {
                    'id': str(self.id),
                    'location': self.location.get_json(level=1)
                }
        return detail 

class Winner(models.Model):
    user = models.ForeignKey(OTNUser)
    prize = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

class OTNUserTemp(models.Model):

    first_name = models.CharField(blank=True, max_length=20)
    last_name = models.CharField(blank=True, max_length=20)
    email = models.EmailField()
    mit_id = models.CharField(blank=True, max_length=9)
    experiment = models.IntegerField(default=0)

    def get_json(self):

        detail = {'id': str(self.id),
                  'name': self.first_name+' '+self.last_name,
                  'email': self.email,
                  'mit_id': self.mit_id,                
                  'experiment': str(self.experiment.id),
                  }
        return detail        


