"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from common.models import Experiment, OTNUser
from web.models import Feed

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

    def runTest(self):
        pass

    def populate_people(self):
        self.eric, created = OTNUser.objects.get_or_create(username="stephanie", email="eshyu@mit.edu", my_email="eshyu@mit.edu")
        print "hello"

    def initialize(self):
        Experiment.objects.get_or_create(name="Control", description="1")
        Experiment.objects.get_or_create(name="Exp 2", description="2")
        Experiment.objects.get_or_create(name="Exp 3", description="3")
        Experiment.objects.get_or_create(name="Exp 4", description="4")

    def test_feeds(self):
        self.populate_people()

        response = self.client.get( "/feeds/latest/" )
        self.assertContains(response, "feed3", count=1)
        response = self.client.get( "/feeds/public/" )
        response = self.client.get( "/feeds/personal/" )
        response = self.client.get( "/feed/", {'feed_id': 2})

        self.assertContains(response, "feed2")

    def setUp(self):
        Experiment.objects.get_or_create(name="Control", description="1")
        Experiment.objects.get_or_create(name="Exp 2", description="2")
        Experiment.objects.get_or_create(name="Exp 3", description="3")
        Experiment.objects.get_or_create(name="Exp 4", description="4")
        
        self.niwen, created = OTNUser.objects.get_or_create(username="niwen", email="niwen@mit.edu", my_email="niwen@mit.edu")
        self.kwan, created = OTNUser.objects.get_or_create(username="kwan", email="kool@mit.edu", my_email="kool@mit.edu")
        self.eunice, created = OTNUser.objects.get_or_create(username="eunice", email="engiarta@mit.edu", my_email="engiarta@mit.edu")
        
        
        
        f1 = Feed(actor=self.niwen, action=Feed.PAID, params="Bertuccis")
        f1.save()
        f2 = Feed(actor=self.niwen, action=Feed.VISITED, params="Bank of America")
        f2.save()
        f3 = Feed(actor=self.kwan, action=Feed.FEE, params="Anna's")
        f3.save()
        f4 = Feed(actor=self.eunice, action=Feed.PAID, params="Starbucks")
        f4.save()
        f5 = Feed(actor=self.eunice, action=Feed.VISITED, params="Cosi")
        f5.save()
        
    def test_feeds(self):
        print "testing feeds"
        response = self.client.get( "/feeds/latest/" )
        self.assertContains(response, "feed5", count=1)
        response = self.client.get( "/feeds/public/" )
        response = self.client.get( "/feeds/personal/" )
        response = self.client.get( "/feed/", {'feed_id': 2})
        self.assertContains(response, "feed2")
        
    def test_login(self):
        response = self.client.get("/facebook/login/", {"email":"ben.viralington@gmail.com", "password":"beviral123"})
        print response.content

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

