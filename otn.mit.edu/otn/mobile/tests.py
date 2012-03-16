"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from common.models import OTNUser, Experiment
import hashlib

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

    def call_json(self, command, params={}):
        print "CALL MOBILE", command
        response = self.client.post(command, params)
        print response
        print json.dumps(json.loads(response.content), indent=2)
        return json.loads(response.content)

    def call_web(self, command, params={}):
        print "CALL WEB", command
        response = self.client.post(command, params)
        return response

    def runTest(self):
        pass

    def setUp(self):
        exp1, created = Experiment.objects.get_or_create(name="Control", description="Control")
        exp2, created = Experiment.objects.get_or_create(name="Experiment 2", description="Social Individual")
        exp3, created = Experiment.objects.get_or_create(name="Experiment 3", description="Social Popularity")
        exp4, created = Experiment.objects.get_or_create(name="Experiment 4", description="Social Group")
        # load some sample transaction data
        u, created = OTNUser.objects.get_or_create(username="kool", email="kool@mit.edu", experiment=exp1)
        pin = "5533"
        u.pin == hashlib.sha224(pin).hexdigest()
        u.save()

    def test_basic(self):
        method = "/m/login/"
        r = self.call_json(method,  {'email':'kool@mit.edu',
                                'pin': '5533',
                                'lat': '-42.23234',
                                'lon': '52.23424' })

        # test loading of transactions
        method = "/m/load/txns/"
        r = self.call_json(method, {'email': 'kwan.media@gmail.com',
                                    'password': '2testfcn',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # show list of feeds
        r = self.call_json("/m/feeds/", {'page': '0', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/feeds/", {'page': '2', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/feeds/", {'page': '100', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # show coupons

        r = self.call_json("/m/coupons/", {'page': '0', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})


        r = self.call_json("/m/coupons/", {'page': '2', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/coupons/", {'page': '100', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # retrieve coupon
        r = self.call_json("/m/coupon/", {'coupon_id': r["coupons"][0]["id"],
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # search
        r = self.call_json("/m/coupons/filter/", {'query': 'cvs', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # retrieve coupon
        r = self.call_json("/m/coupon/", {'coupon_id': r["coupons"][0]["id"], 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # show list of transactions
        r = self.call_json("/m/txns/", {'page': '0', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/txns/", {'page': '2', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/txns/", {'page': '100', 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/txn/", {'txn_id': r["txns"][0]["id"], 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/txn/", {'txn_id': r["txns"][1]["id"], 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/search/", {'query': "cvs", 
                                    'filter': '0',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/search/", {'query': "cvs", 
                                    'filter': '1',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/search/", {'query': "cvs", 
                                    'filter': '2',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/search/", {'query': "cvs", 
                                    'filter': '3',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # manipulate transaction
        r = self.call_json("/m/split/update/", {'txn_id': 4, 
                                    'split_id': '0',
                                    'name': 'Chocolate',
                                    'price': '2.55',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/split/delete/", {'split_id': 4, 
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/split/update/", {'txn_id': 6, 
                                    'split_id': '0',
                                    'name': 'Chocolate',
                                    'price': '2.55',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/txn/detail/", {'txn_id': 6,
                                    'location': 4,
                                    'detail': 'This is the place to buy kleenex',
                                    'rating': 4,
                                    'sharing': 2,
                                    'category': 5,
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # TODO: need to upload image for transaction detail


        # categories
        r = self.call_json("/m/categories/", {
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})


        r = self.call_json("/m/category/add/", {
                                    'name': 'Bed and Bath',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/category/add/", {
                                    'name': 'Hardware',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/category/add/", {
                                    'name': 'Bed and Bath',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})


        r = self.call_json("/m/categories/", {
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})



        r = self.call_json("/m/profile/", {'query': "cvs", 
                                    'filter': '3',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        # list locations
        r = self.call_json("/m/locations/", {'page': '0',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})

        r = self.call_json("/m/location/", {'loc_id': '22',
                                    'lat': '-42.23234',
                                    'lon': '52.23424'})



from django.test.client import Client
from datetime import date
import random
import json
from web.models import Country, Region, PostalCode, Location, SpendingCategory, Coupon

def initialize():
    """
        Initial data
    """

    categories = ['None',
                'Food',
               'Entertainment',
               'Transportation',
               'Drinks',
               'Coffee',
               'Fashion',
               'Utilities']

    for c in categories:
        cat, created = SpendingCategory.objects.get_or_create(name=c)

    us, created = Country.objects.get_or_create(name="USA", iana_code="us")
    ma, created = Region.objects.get_or_create(name="Massachusetts", country=us)
    ma.abbrv = "MA"
    ma.save()
    boston, created = PostalCode.objects.get_or_create(code="02139", city="Cambridge", region=ma)
    w, created = WesabeLocation.objects.get_or_create(name="Unknown", postal_code=boston)

def loads():
    c = Client()

def add_coupons():
    num_loc = WesabeLocation.objects.all().count()
    for j in xrange(50):
        discount = random.randint(5,25)
        coupon_num = random.randint(1000000,9999999)
        i = random.randint(2,num_loc-1)
        target_loc = WesabeLocation.objects.get(id=i)
        c = Coupon(location=target_loc, dealer="The magistrate dealer",
                content="This is %d%% off coupon"%discount,
                number="%d"%coupon_num,
                details="If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.",
                expiry_date=date(year=2011, month=6, day=30))
        c.save()

def test():
    c = Client()

    method = "/m/login/"
    r = c.post(method,  {'email':'kool@mit.edu',
                            'pin': '5533',
                            'lat': '-42.23234',
                            'lon': '52.23424',
                            'table': 'abcd'})
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    ###########################################################
    # surveys
    ###########################################################
    """
    method = "/m/surveys/"
    r = c.post(method, {'e':'e'})
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/survey/1/"
    r = c.get(method)
    print r
    """
    method = "/m/feeds/"
    r = c.post(method, {'page':'0',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    """
    # web call
    method = "/m/txns/0/"
    r = c.post(method, {'e':'e'})
    print method
    print r
    """

    method = "/m/category/add/"
    r = c.post(method, {'name': 'Toys',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2)

    method = "/m/search/"
    r = c.post(method, {'query': 'lotte', 'filter':'3',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/categories/"
    r = c.post(method, {
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/split/add/"
    r = c.post(method, {'txn_id':'69', 'split_id':'0', 'name':'eBay', 'price':'4.95',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    rdict = json.loads(r.content)
    method = "/m/split/delete/"
    r = c.post(method, {'split_id':rdict["result"],
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/split/add/"
    r = c.post(method, {'txn_id':'69', 'split_id':'0', 'name':'Keyboard', 'price':'8.95',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    rdict = json.loads(r.content)
    method = "/m/split/add/"
    r = c.post(method, {'txn_id':'69', 'split_id':rdict["result"], 'name':'Joystick',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    rdict = json.loads(r.content)
    method = "/m/split/delete/"
    r = c.post(method, {'split_id': rdict["result"],
                        'lat': '-42.23234',
                        'lon': '52.23424',
                    })
    print method
    print json.dumps(json.loads(r.content), indent=2) 


#rdict = json.loads(r.content)
#method = "/m/split/delete/"
#    r = c.post(method, {'split_id': rdict["result"],
#                        'lat': '-42.23234',
#                        'lon': '52.23424',
#                    })
#print method
#print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/txn/"
    r = c.post(method, {'txn_id':'6',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/txn/"
    r = c.post(method, {'txn_id':'35',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/txn/"
    r = c.post(method, {'txn_id':'355',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/locations/"
    r = c.post(method, {
                        'page': '1',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })

    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/txn/detail/"
    r = c.post(method, {'txn_id': '69',
                        'detail': 'Mailed eBay item',
                        'rating': '4',
                        'sharing': '2',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/txn/detail/"
    r = c.post(method, {'txn_id': '69',
                        'location': '3',
                        'category': '5',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/location/"
    r = c.post(method, {'loc_id': '5',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2)

    method = "/m/coupons/"
    r = c.post(method, {'loc_id': '6',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/coupons/all/"
    r = c.post(method, {
                        'page': '1',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/m/txns/"
    r = c.post(method, {
                        'page': '1',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/txn/"
    r = c.post(method, {'txn_id':'6',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/m/txn/"
    r = c.post(method, {'txn_id':'24',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

def test_web_load():
    c = Client()

    method = "/legals/m/login/real/"
    r = c.post(method,  {'email':'kool@mit.edu',
                            'pin': '5533',
                            'lat': '-42.23234',
                            'lon': '52.23424',
                            'table': 'abcd'})
    print method
    print json.dumps(json.loads(r.content), indent=2) 


    method = "/wesabe/ajax/load/"
    r = c.post(method, {'email': 'kwan@media.mit.edu',
                        'password': '2testfcn'})
    print method
    print r.content 
__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

