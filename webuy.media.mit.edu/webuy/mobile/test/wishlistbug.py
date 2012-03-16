from mobile.tests import *
from django.test.client import Client

s = SimpleTest()
s.client = Client()

s.test_wishlist()
