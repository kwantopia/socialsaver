from django.db import models
from django.contrib.auth.models import User, UserManager
from premix import StoreQuery, ProductQuery
from django.conf import settings
from common.models import Experiment, Friends
import time
import httplib, urllib
import json
import re
from httplib2 import Http

# Create your models here.

api_key = settings.BESTBUY_API_KEY
logger = settings.LOGGER

class Party(User):
    # BestBuy data
    party_id = models.BigIntegerField(null=True)
    middle_name = models.CharField(max_length=20, null=True)
    name_suffix = models.CharField(max_length=10, null=True)
    birth_month = models.IntegerField(null=True)
    birth_day = models.IntegerField(null=True)

    # full name from Facebook
    name = models.CharField(max_length=50)
    alias = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='/users/', max_length=200, blank=True, default="" )
    pin = models.CharField(max_length=200)
    experiment = models.ForeignKey(Experiment, default=1)

    proxy_email = models.CharField(max_length=128, null=True)

    first_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    def get_json(self, level=0):
        detail = {}

        # TODO: need to identify the user based on experiment
        detail['alias'] = self.alias if self.alias else self.username.split("@")[0]
        detail['name'] = 'Anonymous'
        detail['id'] = '0'
        anonymous = True
        if level == 1:
            detail['id'] = str(self.id)
            anonymous = False
            detail['name'] = self.name
            detail['first_name'] = self.first_name
            detail['last_name'] = self.last_name
            phones = self.phone_set.filter(primary=True)
            detail['phone'] = phones[0] if phones.count() > 0 else ""
        detail['first_joined'] = str(time.mktime(self.first_joined.timetuple())) 

        if self.image and not anonymous:
            h = Http()
            resp, content = h.request( self.image.url )
            if len(content) > 70:
                detail['image'] = self.image.url
            else:
                detail['image'] = "http://www.facebook.com/pics/t_silhouette.gif"
        else:
            detail['image'] = "http://www.facebook.com/pics/t_silhouette.gif"
 
        return detail

    def friends(self):
        """
            Finds friend party objects
        """
        my_friends = Friends.objects.get(facebook_id=self.facebook_profile.facebook_id).friends.values_list('facebook_id', flat=True)
        fs = Party.objects.filter(facebook_profile__facebook_id__in=my_friends)
        return fs

    def display_name(self, exp=2):
        """
            Used by feed, based on the experiment
        """
        if exp in [2,4]:
            return self.first_name
        else:
            return "Anonymous"

class Account(models.Model):
    account_id = models.BigIntegerField()
    party = models.ForeignKey(Party)
    status_code = models.CharField(max_length=1)

    RWZ = 0
    SILVER = 1

    TYPE_CHOICES = (
                (RWZ, 'RWZ'),
                (SILVER, 'Silver')
            )
    type_code = models.IntegerField(choices=TYPE_CHOICES, default=RWZ) 

    category = models.CharField(max_length=20)
    category_description = models.CharField(max_length=20)
    number = models.CharField(max_length=20)
    points = models.IntegerField()
    tier = models.CharField(max_length=30)

class Certificate(models.Model):
    certificate_id = models.BigIntegerField()
    account = models.ForeignKey(Account)
    amount = models.IntegerField()
    barcode_number = models.CharField(max_length=50)
    issued_date = models.DateTimeField()
    expired_date = models.DateTimeField()

    ISSUED = 0
    REDEEMED = 1

    STATUS_CHOICES = (
            ( ISSUED, "Issued" ),
            ( REDEEMED, "Redeemed" ),
        )

    status = models.IntegerField(choices=STATUS_CHOICES, default=ISSUED)

class Email(models.Model):
    """
        either BestBuy e-mail or Facebook e-mail
    """
    email_id = models.BigIntegerField()
    party = models.ForeignKey(Party, related_name="emails")

    HOME = 0
    WORK = 1
    OTN = 2

    TYPE_CHOICES = (
            (HOME, 'HOME'),
            (WORK, 'WORK'),
            (OTN, 'OTN'),
            )

    type_code = models.IntegerField(choices=TYPE_CHOICES, default=HOME) 
    email = models.CharField(max_length=256)
    primary = models.BooleanField(default=False)

class Phone(models.Model):
    phone_id = models.IntegerField()
    party = models.ForeignKey(Party)

    HOME = 0
    CELL = 1
    WORK = 2

    TYPE_CHOICES = (
            (HOME, 'HOME'),
            (CELL, 'CELL'),
            (WORK, 'WORK'),
        )

    type_code = models.IntegerField(choices=TYPE_CHOICES, default=HOME) 
    country_code = models.CharField(max_length=5)
    area_code = models.CharField(max_length=5)
    number = models.CharField(max_length=10)
    primary = models.BooleanField(default=False)

class Address(models.Model):
    address_id = models.IntegerField()
    party = models.ForeignKey(Party)

    HOME = 0
    WORK = 1

    TYPE_CHOICES = (
            (HOME, 'HOME'),
            (WORK, 'WORK'),
        )

    type_code = models.IntegerField(choices=TYPE_CHOICES, default=HOME) 
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True, null=True)
    municipality = models.CharField(max_length=30, blank=True, null=True)
    #: state for US
    region = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=20)
    primary = models.BooleanField(default=False)

class Location(models.Model):
    location_id = models.IntegerField()
    name = models.CharField(max_length=100)

class CategoryManager(models.Manager):
    
    def load_categories( self ):
        global api_key

        h = httplib.HTTPConnection('api.remix.bestbuy.com' )
        h.request('GET', '/v1/categories?format=json&apiKey=%s'%api_key)
        r = h.getresponse()
        logger.debug( "HTTP output: %s, reason: %s"%(r.status, r.reason) )

        response = json.loads(r.read())

        total_pages = response['totalPages']

        for i in xrange(1,total_pages+1):
            # load category and populate category table 
            h = httplib.HTTPConnection('api.remix.bestbuy.com' )
            h.request('GET', '/v1/categories?page=%d&format=json&apiKey=%s'%(i,api_key))
            r = h.getresponse()
            logger.debug( "Category page %d, HTTP output: %s, reason: %s"%(i, r.status, r.reason) )

            response = json.loads(r.read())
            #print response
            for c in response['categories']:
                category, created = self.get_or_create(category_id=c["id"], name=c["name"])
                logger.debug( "Category created: %s, %s"%(c["id"], c["name"]) )
                c["path"].reverse()
                for p in c["path"][1:]:
                    parent_cat, created = self.get_or_create(category_id=p["id"], name=p["name"])
                    logger.debug( "Parent category created: %s, %s"%(p["id"], p["name"]) )
                    category.parent = parent_cat
                    category.save()
                    category = parent_cat
            time.sleep(1)

class Category(models.Model):

    category_id = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', related_name="children", null=True)

    objects = CategoryManager()

    def __unicode__(self):
        return self.name

    def get_json(self):
        detail = {}

        detail['id'] = str(self.id)
        detail['category_id'] = self.category_id
        detail['name'] = self.name
        # number of child categories
        detail['num_children'] = str(self.children.count())

        return detail

def fix_signs(name):
    """
        Converts:
            Ratchet & Clank Future: A Crack in Time - PlayStation 3
        to
            Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3

        but avoids converting:

            Sony VAIO Laptop with Intel&#174; Core&#153;2 Duo Processor - Brown
    """
    m = re.search('&[ \w]', name)
    if m:
        fixed = name.replace('&', '&amp;')
        return fixed
    else:
        return name

class ProductManager(models.Manager):
    
    def get_by_product_id( self, product_id):
        query = ProductQuery.all().filter('product_id =', product_id)
        result = query.fetch(api_key)

        if result.total > 0:
            p = result.products[0]
        else:
            return None

        product, created = self.get_or_create(sku=p.sku)
        if created:
            product.name = fix_signs(p.name)
            product.album_title = "" if getattr(p, 'album_title', "") is None else getattr(p, 'album_title', "")
            product.artist_name = "" if getattr(p, 'artist_name', "") is None else getattr(p, 'artist_name', "")
            product.sku_description = p.name if p.name else p.artist_name

            product.url = "" if p.url is None else p.url
            product.cart_url = "" if p.add_to_cart_url is None else p.add_to_cart_url 
 
            product.save()
        return product

    def get_by_sku( self, sku ):
        if self.filter(sku=sku).count() > 0:
            # exists in the db
            p = self.get(sku=sku)
            if p.product_id is not None:
                return p

        query = ProductQuery.sku(sku).show_all()
        p = query.fetch(api_key)
        if p is None:
            return None

        product, created = self.get_or_create(sku=p.sku)
        product.product_id = p.product_id

        product.name = fix_signs(p.name)
        product.album_title = "" if getattr(p, 'album_title', "") is None else getattr(p, 'album_title', "")
        product.artist_name = "" if getattr(p, 'artist_name', "") is None else getattr(p, 'artist_name', "")
        product.sku_description = p.name if p.name else p.artist_name
        # get the lowest category in the hierarchy 
        product.category, created = Category.objects.get_or_create(category_id=p.category_path[-1]["id"])
        product.regular_price = p.regular_price
        product.sale_price = p.sale_price
        product.on_sale = p.on_sale
        product.new = p.new
        product.thumbnail_image = "" if p.thumbnail_image is None else p.thumbnail_image
        product.medium_image = "" if p.medium_image is None else p.medium_image
        product.customer_review_average = 0.0 if p.customer_review_average is None else p.customer_review_average
        product.customer_review_count = 0 if p.customer_review_count == None else p.customer_review_count
        product.url = "" if p.url is None else p.url
        product.cart_url = "" if p.add_to_cart_url is None else p.add_to_cart_url 
        product.save()

        return product 
        
    def get_by_upc( self, upc ):
        query = ProductQuery.all().filter('upc =', upc)
        result = query.fetch(api_key)
        if result.total > 0:
            p = result.products[0]
        else:
            return None

        product, created = self.get_or_create(sku=p.sku)
        if created:
            product.product_id = p.product_id
            product.name = fix_signs(p.name)
            product.album_title = "" if getattr(p, 'album_title', "") is None else getattr(p, 'album_title', "")
            product.artist_name = "" if getattr(p, 'artist_name', "") is None else getattr(p, 'artist_name', "")
            product.sku_description = p.name if p.name else p.artist_name
            # get the lowest category in the hierarchy 
            product.category = Category.objects.get(category_id=p.category_path[-1]["id"])
            product.regular_price = p.regular_price
            product.sale_price = p.sale_price
            product.on_sale = p.on_sale
            product.new = p.new
            product.thumbnail_image = p.thumbnail_image
            product.medium_image = p.medium_image
            product.customer_review_average = p.customer_review_average
            product.customer_review_count = 0 if p.customer_review_count == None else p.customer_review_count
            product.url = "" if p.url is None else p.url
            product.cart_url = "" if p.add_to_cart_url is None else p.add_to_cart_url 
            product.save()
        return product 

    def filter_category( self, cat_id, page=1, me=None):
        """
            :param cat_id: the BestBuy category ID
        """
        results = {} 

        query = ProductQuery.all().filter('category_path.id =', cat_id)
        result = query.fetch(api_key, page=page)
        if result.total > 0:
            results['total_pages'] = result.total_pages
            results['products'] = []
            for p in result.products:
                product, created = self.get_or_create(sku=p.sku)
                if created:
                    product.product_id = p.product_id
                    product.name = fix_signs(p.name)
                    product.album_title = "" if getattr(p, 'album_title', "") is None else getattr(p, 'album_title', "")
                    product.artist_name = "" if getattr(p, 'artist_name', "") is None else getattr(p, 'artist_name', "")
                    product.sku_description = p.name if p.name else p.artist_name
                    # get the lowest category in the hierarchy 
                    product.category = Category.objects.get(category_id=p.category_path[-1]["id"])
                    product.regular_price = p.regular_price
                    product.sale_price = p.sale_price
                    product.on_sale = p.on_sale
                    product.new = p.new
                    product.thumbnail_image = "" if p.thumbnail_image is None else p.thumbnail_image
                    product.medium_image = "" if p.medium_image is None else p.medium_image
                    product.customer_review_average = 0.0 if p.customer_review_average is None else p.customer_review_average
                    product.customer_review_count = 0 if p.customer_review_count == None else p.customer_review_count
                    product.url = "" if p.url is None else p.url
                    product.cart_url = "" if p.add_to_cart_url is None else p.add_to_cart_url 

                    product.save()
                results['products'].append(product.details(me))
                        
        return results

    def search(self, s, page=1, me=None):
        results = {} 

        # search by name, artist_name, short description
        query = ProductQuery.all().extend('name =', "%s*"%s).extend('album_title =', "%s*"%s).extend('artist_name =', "%s*"%s).extend('short_description =', "%s*"%s)
        result = query.fetch(api_key, page=page)
        if result.total > 0:
            results['total_pages'] = result.total_pages
            results['products'] = []
            for p in result.products:
                #print sku
                if len(p.category_path) == 0:
                    continue
                product, created = self.get_or_create(sku=p.sku)
                if created:
                    product.product_id = p.product_id
                    product.name = fix_signs(p.name)
                    product.album_title = "" if getattr(p, 'album_title', "") is None else getattr(p, 'album_title', "")
                    product.artist_name = "" if getattr(p, 'artist_name', "") is None else getattr(p, 'artist_name', "")
                    product.sku_description = p.name if p.name else p.artist_name
                    # get the lowest category in the hierarchy 
                    #print p.category_path
                    product.category = Category.objects.get(category_id=p.category_path[-1]["id"])
                    product.regular_price = p.regular_price
                    product.sale_price = p.sale_price
                    product.on_sale = p.on_sale
                    product.new = p.new
                    product.thumbnail_image = "" if p.thumbnail_image is None else p.thumbnail_image
                    product.medium_image = "" if p.medium_image is None else p.medium_image
                    product.customer_review_average = 0.0 if p.customer_review_average is None else p.customer_review_average
                    product.customer_review_count = 0 if p.customer_review_count == None else p.customer_review_count
                    product.url = "" if p.url is None else p.url
                    product.cart_url = "" if p.add_to_cart_url is None else p.add_to_cart_url 

                    product.save()
                results['products'].append(product.details(me))
                        
        return results
         
class Product(models.Model):
    """
        Stores products
    """
    sku = models.IntegerField(default=0, unique=True)  
    sku_description = models.CharField(max_length=150, default="XXX")
    sku_plu_text = models.CharField(max_length=20, blank=True, default="")

    product_id = models.BigIntegerField(default=0) 
    name = models.CharField(max_length=100, default="") 
    album_title = models.CharField(max_length=100, blank=True, default="") 
    artist_name = models.CharField(max_length=100, blank=True, default="") 
    category = models.ForeignKey(Category, null=True) 
    regular_price = models.FloatField(null=True) 
    sale_price = models.FloatField(null=True) 
    on_sale = models.BooleanField(default=False) 
    new = models.BooleanField(default=False) 
    thumbnail_image = models.CharField(max_length=128, default="") 
    medium_image = models.CharField(max_length=128, default="")
    customer_review_average = models.FloatField(default=0.0) 
    customer_review_count = models.IntegerField(default=0) 
    url = models.CharField(max_length=255, default="")
    cart_url = models.CharField(max_length=255, default="")

    objects = ProductManager()

    def get_json(self, level=0):
        detail = {}

        detail["id"] = str(self.id)
        detail["sku"] = str(self.sku)

        return detail

    def wished_by(self):
        return self.in_wishes.filter(fulfilled=False).count()

    def details(self, me=None):
        """
            me is Party object that signifies myself who's looking at info
        """
        # check if the details are already there
        if self.product_id is None:
            query = ProductQuery.sku(self.sku).show_all()
            p = query.fetch(api_key)
            if p is None: 
                return {}

            self.product_id = p.product_id
            self.name = fix_signs(p.name)
            product.album_title = "" if getattr(p, 'album_title', "") is None else getattr(p, 'album_title', "")
            product.artist_name = "" if getattr(p, 'artist_name', "") is None else getattr(p, 'artist_name', "")
            self.sku_description = p.name if p.name else p.artist_name
            # get the lowest category in the hierarchy 
            self.category = Category.objects.get(category_id=p.category_path[-1]["id"])
            self.regular_price = p.regular_price
            self.sale_price = p.sale_price
            self.on_sale = p.on_sale
            self.new = p.new
            self.thumbnail_image = "" if p.thumbnail_image is None else p.thumbnail_image
            self.medium_image = "" if p.medium_image is None else p.medium_image
            self.customer_review_average = 0.0 if p.customer_review_average is None else p.customer_review_average
            self.customer_review_count = 0 if p.customer_review_count == None else p.customer_review_count
            self.url = "" if p.url is None else p.url
            self.cart_url = "" if p.add_to_cart_url is None else p.add_to_cart_url 

            self.save()

        detail = {}

        detail['sku'] = str(self.sku)
        detail['product_id'] = str(self.product_id)
        detail['name'] = self.name
        detail['album_title'] = self.album_title
        detail['artist_name'] = self.artist_name
        # exclude most highlevel Best Buy category
        detail['category'] = self.category.name
        detail['regular_price'] = "%.2f"%self.regular_price
        detail['sale_price'] = "%.2f"%self.sale_price
        detail['on_sale'] = self.on_sale
        detail['new'] = self.new
        detail['thumbnail_image'] = self.thumbnail_image
        detail['medium_image'] = self.medium_image
        detail['customer_review_average'] = "%.1f"%(self.customer_review_average if self.customer_review_average else 0)
        detail['customer_review_count'] = str(self.customer_review_count)
    

        detail['wished_by'] = ""
        detail['bought_by'] = "" 
        detail['review_request'] = ""
        detail['num_wished'] = '0'
        detail['num_bought'] = '0'
        detail['num_requested'] = '0'
        detail['url'] = self.url
        detail['cart_url'] = self.cart_url

        if me is not None:

            # for experiment 1 and when nobody wishes or bought it
            if me.experiment.id == 2:
                # exclude reviews that I have requested and reviews that I have already replied
                reqs = ReviewRequest.objects.exclude(requester=me).filter(product=self, requester__in=me.friends()).exclude(replies__reviewer=me)
                if reqs.count() > 0:
                    detail['num_requested'] = str(reqs.count())
                    request_str = "Requested review by "
                    for q in reqs:
                        request_str += q.requester.first_name + ", "
                    detail['review_request'] = request_str[:-2]

                wishes = Wishlist.objects.filter(product=self, party__in=me.friends())
                if wishes.count() > 0:
                    detail['num_wished'] = str(wishes.count())
                    wish_str = "Wished by "
                    for w in wishes:
                        wish_str += w.party.first_name + ", "
                    detail['wished_by'] = wish_str[:-2] 
                purchases = TransactionLineItem.objects.filter(product=self, transaction__party__in=me.friends())
                if purchases.count() > 0:
                    detail['num_bought'] = str(purchases.count())
                    purchase_str = "Bought by "
                    for b in purchases:
                        purchase_str += b.transaction.party.first_name + ", "
                    detail['bought_by'] = purchase_str[:-2]
            elif me.experiment.id == 3:
                # exclude reviews that I have requested and reviews that I have already replied
                num_reqs = ReviewRequest.objects.exclude(requester=me).filter(product=self).exclude(replies__reviewer=me).count()
                if num_reqs > 0:
                    detail['num_requested'] = str(num_reqs)
                    detail['review_request'] = "%d people requested for review"%num_reqs if num_reqs > 1 else "%d person requested for review"%num_reqs

                num_wish = Wishlist.objects.filter(product=self).exclude(party=me).count()
                if num_wish > 0:
                    detail['num_wished'] = str(num_wish)
                    detail['wished_by'] = "%d people want this"%num_wish if num_wish > 1 else "%d person want this"%num_wish
                num_bought = TransactionLineItem.objects.filter(product=self).exclude(transaction__party=me).count()
                if num_bought > 0:
                    detail['num_bought'] = str(num_bought)
                    detail['bought_by'] = "%d people bought this"%num_bought if num_bought > 1 else "%d person bought this"%num_bought
            elif me.experiment.id == 4:
                # exclude reviews that I have requested and reviews that I have already replied
                reqs = ReviewRequest.objects.exclude(requester=me).filter(product=self, requester__in=me.friends()).exclude(replies__reviewer=me)
                if reqs.count() > 0:
                    detail['num_requested'] = str(reqs.count())
                    detail['review_request'] = "%d friends requested for review"%reqs.count() if reqs.count() > 1 else "%d friend requested for review"%reqs.count()

                num_wish = Wishlist.objects.filter(product=self).exclude(party=me).count()
                if num_wish > 0:
                    detail['num_wished'] = str(wishes.count())
                    detail['wished_by'] = "%d friends want this"%num_wish if num_wish > 1 else "%d friend want this"%num_wish
                num_bought = TransactionLineItem.objects.filter(product=self).exclude(transaction__party=me).count()
                if num_bought > 0:
                    detail['num_bought'] = str(bought.count())
                    detail['bought_by'] = "%d friends bought this"%num_bought if num_bought > 1 else "%d friend bought this"%num_bought

        return detail 

    def get_name(self):
        # check if the details are already there
        if self.product_id is None:
            query = ProductQuery.sku(self.sku).show_all()
            p = query.fetch(api_key)
            if p is None: 
                return {}

            self.product_id = p.product_id
            self.name = fix_signs(p.name)
            self.album_title = p.get('album_title', None)
            self.artist_name = p.get('artist_name', None)
            self.sku_description = p.name if p.name else p.artist_name
            # get the lowest category in the hierarchy 
            self.category = Category.objects.get(category_id=p.category_path[-1]["id"])
            self.regular_price = p.regular_price
            self.sale_price = p.sale_price
            self.on_sale = p.on_sale
            self.new = p.new
            self.thumbnail_image = p.thumbnail_image
            self.medium_image = p.medium_image
            self.customer_review_average = p.customer_review_average
            self.customer_review_count = p.customer_review_count
            self.url = p.url
            self.cart_url = p.add_to_cart_url

            self.save()

        return self.name

    def __unicode__(self):
        return self.name

class Feed(models.Model):
    actor = models.ForeignKey(Party, related_name="feeds")

    BOUGHT = 0
    REVIEWED = 1
    REQUESTED = 2
    WISHLIST = 3        # added to wish list
    GROUP_START = 4     # started group purchase
    GROUP_JOIN = 5      # joined group purchase
    GROUP_EXPIRES = 6   # expires in an hour
    GROUP_ENDED = 7     # group purchase ended
    UPDATED_REVIEW = 8

    ACTION_CHOICES = (
        (BOUGHT, 'bought'),
        (REVIEWED, 'reviewed'),
        (REQUESTED, 'requested review for'),
        (WISHLIST, 'wishes to buy'),
        (GROUP_START, 'started group purchase of'),
        (GROUP_JOIN, 'joined group purchase of'),
        (GROUP_EXPIRES, 'Group purchase expires in an hour:'),
        (GROUP_ENDED, 'Group purchase ended:'),
        (UPDATED_REVIEW, 'updated review for'),
    )
    action = models.IntegerField(choices=ACTION_CHOICES, default=BOUGHT)
    product = models.ForeignKey(Product, related_name="in_feeds")
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_json(self, me=None, android=False):
        detail = {}

        exp_id = 0
        if me:
            if me.experiment.id in [2,4]:
                detail['actor'] = self.actor.get_json(level=1)
            else:
                detail['actor'] = self.actor.get_json()
            exp_id = me.experiment.id
        else:
            detail['actor'] = self.actor.get_json()

        if android:
            detail['feed'] = "<font color='#127524'><b>%s</b></font> %s <font color='#127524'><b>%s</b></font>"%(self.actor.display_name(exp_id), 
                                                    Feed.ACTION_CHOICES[self.action][1],
                                                    self.product.get_name())
            detail['sku'] = str(self.product.sku)
            #detail['item_url'] = "/m/product/%s/"%self.product.id 
            detail['item_url'] = "/m/item/feed/"
        else:
            #detail['product'] = self.product.details(me)
            detail['feed'] = "<a href='tt://party/%d'>%s</a> %s <a href='tt://product/%d'>%s</a>"%(self.actor.id, 
                                    self.actor.display_name(exp_id), 
                                    Feed.ACTION_CHOICES[self.action][1],
                                    self.product.sku,
                                    self.product.get_name())

        return detail

    def __unicode__(self):
        return "%s %s %s"%(self.actor.display_name(), 
                                    Feed.ACTION_CHOICES[self.action][1],
                                    self.product.get_name())

    def markup(self):
        return "<a href='/user/%d/'>%s</a> %s <a href='/product/%d/'>%s</a>"%(
                                    self.actor.id,
                                    self.actor.display_name(), 
                                    Feed.ACTION_CHOICES[self.action][1],
                                    self.product.id,
                                    self.product.get_name())
        

class Transaction(models.Model):
    bb_transaction_id = models.CharField(max_length=10)
    party = models.ForeignKey(Party)

    STORE = 0
    ONLINE = 1

    SOURCE_CHOICES = (
                (STORE, 'Store'),
                (ONLINE, 'Online'),
            )
    source = models.IntegerField(choices=SOURCE_CHOICES, default=STORE)
    key = models.CharField(max_length=20)
    register = models.IntegerField()
    number = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)

class TransactionLineItem(models.Model):
    """
        Purchase of an item
    """
    line_number = models.IntegerField()

    # SL is sale, TX is tax
    line_type = models.CharField(max_length=2)
    unit_quantity = models.IntegerField(default=1)
    # need to make sure when loading from BestBuy that it's divided by 100.00
    sale_price = models.FloatField()

    # product is null in case it's a refund or tax
    product = models.ForeignKey(Product, null=True)
    transaction = models.ForeignKey(Transaction)

    def get_json(self, level=0, me=None):
        detail = {}

        detail['party'] = self.transaction.party.get_json()
        if level == 1:
            detail['product'] = self.product.details(me)
        detail['unit_quantity'] = str(self.unit_quantity)
        detail['sale_price'] = "%.2f"%self.sale_price
        detail['purchase_date'] = str(time.mktime(self.transaction.timestamp.timetuple()))
        detail['source'] = Transaction.SOURCE_CHOICES[self.transaction.source][1]

        return detail

    def details(self):
        detail = {}
        detail['product'] = self.product.details()
        detail['unit_quantity'] = str(self.unit_quantity)
        detail['sale_price'] = "%.2f"%self.sale_price
        detail['purchase_date'] = str(time.mktime(self.transaction.timestamp.timetuple()))
        detail['source'] = Transaction.SOURCE_CHOICES[self.transaction.source][1]
        return detail

    def __unicode__(self):
        return self.product.name

class GroupPurchase(models.Model):
    """
        Used to track group purchases
    """
    initiator = models.ForeignKey(Party, related_name="initiated_group_purchases")
    invited = models.ManyToManyField(Party, related_name="invited_group_purchases")
    participants = models.ManyToManyField(Party, related_name="participating_group_purchases")

    product = models.ForeignKey(Product, related_name="group_purchases")

    discount_rate = models.FloatField(default=0.0)
    #: minimum number of users to fulfill
    min_number = models.IntegerField(default=0)

    initiated = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expire_date = models.DateTimeField()

    #: group purchase fulfilled
    fulfilled = models.BooleanField(default=False)
    fulfilled_date = models.DateTimeField()

class Wishlist(models.Model):

    party = models.ForeignKey(Party, related_name="wishlist" )
    product = models.ForeignKey(Product, related_name="in_wishes")

    comment = models.CharField(max_length=200, blank=True, default="")
    max_price = models.FloatField(default=0.00)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # the day when it was fulfilled
    fulfilled_date = models.DateTimeField(null=True)
    fulfilled = models.BooleanField(default=False)

    #user removal
    removed = models.BooleanField(default=False)
    remove_date = models.DateTimeField(null=True)

    NOT_REQUESTED = 0
    REVIEW_REQUESTED = 1
    REVIEW_RESPONDED = 2

    REVIEW_CHOICES = (
                    ( NOT_REQUESTED, 'Not Requested' ),
                    ( REVIEW_REQUESTED, 'Review Requested' ),
                    ( REVIEW_RESPONDED, 'Review Responsed' ),
                    )
    review = models.IntegerField(choices=REVIEW_CHOICES, default=NOT_REQUESTED)

    group = models.ForeignKey( GroupPurchase, null=True )

    def __unicode__(self):
        return self.party.name + " wishes " + self.product.name

    def get_json(self, level=0, me=None):
        detail = {}

        detail["wish_id"] = str(self.id)
        if level == 1:
            detail['product'] = self.product.details(me)
        if me:
            if me.experiment.id in [1,3]:
                detail["party"] = self.party.get_json()
            else:
                detail["party"] = self.party.get_json(1)
        else:
            detail["party"] = self.party.get_json()

        detail["max_price"] = "%.2f"%self.max_price
        detail["comment"] = self.comment 
        detail["added"] = str(time.mktime(self.added.timetuple())) 
        detail["fulfilled"] = str(self.fulfilled)
        detail["removed"] = str(self.removed)
        detail["pending"] = str(self.review)

        # if a review to a review request has not been viewed
        new_reviews = 0

        # if there's a review requested
        if ReviewRequest.objects.filter(product=self.product, requester=me).exists():
            my_request = ReviewRequest.objects.filter(product=self.product, requester=me)[0]
            for r in Review.objects.exclude(reviewer=me).filter(product=self.product):
                # TODO: only add if reviewer is my friend
                r.reply_to.add(my_request)
                    
            new_reviews = Review.objects.filter(product=self.product).count() - Review.objects.filter(product=self.product, viewed_by=me).count()

        detail["new_reviews"] = "0"
        if me is not None:
            detail["new_reviews"] = str(new_reviews)

        return detail

    def get_wish_summary(self, me):
        detail = {}
        detail["wish_id"] = str(self.id)
        if me.experiment.id in [1,3]:
            detail["party"] = self.party.get_json()
        else:
            detail["party"] = self.party.get_json(1)
        detail["max_price"] = "%.2f"%self.max_price
        detail["comment"] = self.comment 
        detail["added"] = str(time.mktime(self.added.timetuple())) 
        detail["fulfilled"] = str(self.fulfilled)
        detail["pending"] = str(self.review)

        # if a review to a review request has not been viewed
        new_reviews = 0

        # if there's a review requested
        if ReviewRequest.objects.filter(product=self.product, requester=me).exists():

            my_request = ReviewRequest.objects.filter(product=self.product, requester=me)[0]
            for r in Review.objects.exclude(reviewer=me).filter(product=self.product):
                # TODO: only add if reviewer is my friend
                r.reply_to.add(my_request)
                
            new_reviews = Review.objects.filter(product=self.product).count() - Review.objects.filter(product=self.product, viewed_by=me).count()

        detail["new_reviews"] = "0"
        if me is not None:
            detail["new_reviews"] = str(new_reviews)

        return detail

    def details(self):
        """ Does not return party information """
        detail = {}

        detail["wish_id"] = str(self.id)
        detail['product'] = self.product.details()
        detail["max_price"] = "%.2f"%self.max_price
        detail["comment"] = self.comment 
        detail["added"] = str(time.mktime(self.added.timetuple())) 
        detail["fulfilled"] = str(self.fulfilled)
        detail["pending"] = str(self.review)

        return detail


class DiscountDetail(models.Model):

    min_people = models.IntegerField()
    discount_rate = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

class ReviewRequest(models.Model):

    requester = models.ForeignKey(Party, related_name="requested")
    product = models.ForeignKey(Product, related_name="review_requests")

    requested = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def __unicode__(self):
        return self.requester.name + " requests " + self.product.name


    def get_json(self, me=None):
        detail = {}

        detail['request_id'] = str(self.id)
        if me is None or me.experiment.id in [1,3]:
            detail['requester'] = self.requester.get_json(1)
            detail['product'] = self.product.details(me)
            detail['requested'] = str(time.mktime(self.requested.timetuple())) 
        else:
            detail['requester'] = self.requester.get_json(1)
            detail['product'] = self.product.details(me)
            detail['requested'] = str(time.mktime(self.requested.timetuple())) 

        return detail

class Store(models.Model):
    store_id = models.IntegerField()
    name = models.CharField(max_length=50)
    long_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=10)
    postal_code = models.CharField(max_length=10)
    full_postal_code = models.CharField(max_length=12)
    country = models.CharField(max_length=20)
    lat = models.FloatField(default=0.0)
    lon = models.FloatField(default=0.0)
    phone = models.CharField(max_length=20)
    #  "hours": "Mon: 10-9; Tue: 10-9; Wed: 10-9; Thurs: 10-9; Fri: 9-9; Sat: 9-9; Sun: 10-7",
    hours = models.CharField(max_length=100)
    distance = models.FloatField(default=0.0)

class Review(models.Model):
    """
        It also covers responses to review request, 
        public=False when answered for personal requests
    """
    reviewer = models.ForeignKey(Party, related_name="reviewed")
    product = models.ForeignKey(Product, related_name="reviews")
    first_reviewed = models.BooleanField(default=False)     # use to check first review: if not r.first_reviewed
    posted = models.DateTimeField(auto_now_add=True)
    viewed = models.IntegerField(default=0)
    public = models.BooleanField(default=True)
    reply_to = models.ManyToManyField(ReviewRequest, null=True, related_name="replies")
    content = models.TextField(verbose_name="comments")
    viewed_by = models.ManyToManyField(Party, related_name="viewed_reviews")

    NOT_RATED = 0
    DONT_BUY = 1
    BAD = 2
    OK = 3
    GOOD = 4
    EXCELLENT = 5

    RATING_CHOICES = (
            (NOT_RATED, "Not Rated"),
            (DONT_BUY, "1: Not worth buying"),
            (BAD, "2: It's bad"),
            (OK, "3: It's ok"),
            (GOOD, "4: It's good"),
            (EXCELLENT, "5: Best buy"),
            )
    rating = models.IntegerField(choices=RATING_CHOICES, default=NOT_RATED)

    def get_json(self, level=0, me=None):
        detail = {}

        detail['review_id'] = str(self.id)
        if level == 1:
                detail['product'] = self.product.get_json()
        detail['content'] = self.content 
        detail['rating'] = str(self.rating)
        detail['viewed'] = str(self.viewed)
        
        #reply to a review request (tells how many people have been asking)
        detail['replied'] = True if self.reply_to.all().count() > 0 else False
        detail['posted'] = str(time.mktime(self.posted.timetuple()))
            
        if me.experiment.id in [1,3] or self.public:
            # anonymous reviews
            detail['reviewer'] = self.reviewer.get_json()           
        else:
            # experiment 2, 4 (friends and friends anonymous)
            detail['reviewer'] = self.reviewer.get_json(1)

        return detail

    def __unicode__(self):
        return self.reviewer.name + " reviewed " + self.product.name + "--" + str(self.id)
