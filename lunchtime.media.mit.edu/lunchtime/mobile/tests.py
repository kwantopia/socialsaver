"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
import uuid, string, hashlib, json
import json

from common.models import OTNUser, Experiment

class SimpleTest(TestCase):

    def direct_test(self):
        self.client = Client()
        self.test_email = 'kool@mit.edu'
        self.test_pin = '5533'
        self.test_login()

    def runTest(self):
        pass

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

    def setUp(self):
        self.test_email = 'kool@mit.edu'
        self.test_pin = '5533'
        u, created = OTNUser.objects.get_or_create(my_email=self.test_email)
        self.failUnlessEqual(created, True)
        u.pin = hashlib.sha224(self.test_pin).hexdigest()
        u.save()

        e = Experiment(description="Control group")
        e.save()
        e = Experiment(description="Friends group")
        e.save()
        e = Experiment(description="Anonymous Popularity group")
        e.save()
        e = Experiment(description="Anonymous friends group")
        e.save()

    def call_json(self, command, params={}):
        print 'CALL MOBILE', command
        response = self.client.post(command,params)
        print response
        print json.dumps(json.loads(response.content), indent=2)
        return json.loads(response.content)

    def call_web(self, command, params={}):
        print 'CALL WEB', command
        response = self.client.post(command,params)
        return response

    def test_login(self):
        # test register iPhone

        uuid_bad = str(uuid.uuid4()).replace("-","")
        uuid_good = str(uuid.uuid4()).replace("-","") + uuid_bad

        r = self.call_web("/m/register/", {'udid':uuid_good})
        self.assertRedirects(r, "/accounts/login/?next=/m/register/")

        r = self.call_json("/m/login/", {'email': self.test_email,
                                            'pin': self.test_pin,
                                            'lat': '-43.23432',
                                            'lon': '23.2342'})

        self.failUnlessEqual(r['result'], '1')

        r = self.call_json("/m/register/", {'udid':uuid_bad})
        self.failUnlessEqual(r["result"], "-1")

        r = self.call_json("/m/register/", {'udid':uuid_good})
        self.failUnlessEqual(r["result"], "1")

        # test feeds
        #for experiment 1, 2, 3, 4

        u = OTNUser.objects.get(my_email=self.test_email)
        u.experiment = Experiment.objects.get(id=1)
        u.save()

        r = self.call_json("/m/feeds/1/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
    
        r = self.call_json("/m/feeds/2/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
 
        r = self.call_json("/m/feeds/a/2/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
 
        u = OTNUser.objects.get(my_email=self.test_email)
        u.experiment = Experiment.objects.get(id=2)
        u.save()

        r = self.call_json("/m/feeds/1/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
    
        r = self.call_json("/m/feeds/a/1/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})

        r = self.call_json("/m/feeds/2/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
 
        u = OTNUser.objects.get(my_email=self.test_email)
        u.experiment = Experiment.objects.get(id=3)
        u.save()
    
        r = self.call_json("/m/feeds/1/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
    
        r = self.call_json("/m/feeds/a/1/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})

        r = self.call_json("/m/feeds/2/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
 
        u = OTNUser.objects.get(my_email=self.test_email)
        u.experiment = Experiment.objects.get(id=4)
        u.save()

        r = self.call_json("/m/feeds/1/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
    
        r = self.call_json("/m/feeds/2/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})
        r = self.call_json("/m/feeds/a/2/", { 'lat': '-43.23432',
                                            'lon': '23.2342'})

 
    def test_location(self):
        """
            Test activity, menu and dish selection calls
        """
        r = self.call_json("/m/login/", {'email': self.test_email,
                                            'pin': self.test_pin,
                                            'lat': '-43.23432',
                                            'lon': '23.2342'})

        self.failUnlessEqual(r['result'], '1')

        response = self.call_json("/m/activity/", {'location_id': '5',
                                            'lat': '-43.23432',
                                            'lon': '23.2342'})


        # list of menu items
        response = self.call_json("/m/menu/", {'location_id': '5',
                                            'lat': '-43.23432',
                                            'lon': '23.2342'})


        # particular category 
        response = self.call_json("/m/menu/category/", {
                                            'location_id': '3',
                                            'category_id': '5',
                                            'lat': '-43.23432',
                                            'lon': '23.2342'})


        # particular dish
        response = self.call_json("/m/menu/dish/", {'dish_id': '5',
                                            'lat': '-43.23432',
                                            'lon': '23.2342'})


        # rate dishes
        response = self.call_json("/m/menu/dish/rate/", {'dish_id': '5',
                                            'thumbs': '1',
                                            'lat': '-43.23432',
                                            'lon': '23.2342'})

        response = self.call_json("/m/menu/dish/rate/", {'dish_id': '7',
                                            'thumbs': '-1',
                                            'lat': '-43.23432',
                                            'lon': '23.2342'})


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

c = Client()

def login():
    #user_email='kool@mit.edu'
    #pin = '5533'
    # user_email='yod@mit.edu'
    # pin = '123456'
    user_email="eshyu@mit.edu"
    pin = '9221'

    command = '/mobile/login/'
    print 'CALL:',command
    response = c.post(command, {'email': user_email, 
                                        'pin':pin,
                                        'lat':'-42.7823742',
                                        'lon':'74.234141'})
    print response.status_code

def receipt_stats():

    command = '/mobile/receipts/month/'
    print 'CALL:', command
    response = c.get(command)
    print json.dumps(json.loads(response.content), indent=2)

def location_log():
    login()
    command = "/mobile/location/log/"
    print 'CALL:', command
    response = c.post(command, {'lat': "-56.2342",
                                'lon': "71.23525"})
    print response

def push_registration():
    orig = "a57bfc3659c2e1255fdbb0da21d57e4781c4631bb18c9b0a977bd3029487e959"
    # random udid
    udid1 = string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') + string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '')

    # push registration test
    response = c.post("/mobile/register/", {'udid': orig} )
    print response

    from common.models import OTNUser
    from iphonepush.models import iPhone

    u = OTNUser.objects.get(my_email=user_email)
    p = iPhone.objects.get(user=u)
    print p.udid
