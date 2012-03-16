"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


class ProductTest(TestCase):
    def test_product_sku_search(self):

        from bestbuy.models import Product
        a = Product.objects.get_by_sku(15206162)
        b = a.details()
        self.failUnlessEqual(b['product_id'],'675935')
