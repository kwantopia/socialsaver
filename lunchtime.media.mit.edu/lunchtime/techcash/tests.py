"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
import json

class SimpleTest(TestCase):

    fixtures = ['fixtures/lunch_alert_test.json']

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

    def test_lunch_alert(self):
        response = self.client.post("/techcash/lunch/alert/", {'code':'sendpeople2lunch'})
        r = json.loads(response.content)

        self.failUnlessEqual(r['result'], '1')


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

