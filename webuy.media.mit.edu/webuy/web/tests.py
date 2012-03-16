"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from bestbuy.models import *
import random
from datetime import datetime

class SimpleTest(TestCase):
    fixtures = ["fixtures/all.yaml"]
    
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)
        
    def setUp(self):
        pass
        
    def create_purchases(self, email, txn_id, skus):
        u = Party.objects.get(email=email)

        u_txn1 = Transaction(bb_transaction_id=txn_id,
                        party=u,
                        source=Transaction.STORE,
                        key='1',
                        register=1,
                        number=1,
                        timestamp=datetime.now())
        u_txn1.save()

        for sku in skus:
            p = Product.objects.get_by_sku(sku)
            time.sleep(0.5)
            line1 = TransactionLineItem(line_number=2, line_type='SL',
                                        sale_price=99.99,
                                        product=p,
                                        transaction=u_txn1)
            line1.save()
        
        if Review.objects.filter(reviewer=u, product=p).exists():
            pass
        else:
            r = Review(reviewer=u, product=p, posted=line1.transaction.timestamp)
            r.save()
            
        
    def test_self(self):
        products = Product.objects.all()
        self.p = random.sample(products, 1)[0]
        sku = self.p.sku
        
        clerks = Product.objects.get(sku=9704268)
        
        niwen = Party.objects.get(email='niwen.chang@gmail.com')
        self.create_purchases('niwen.chang@gmail.com', '200', [clerks.sku])
        
        
        #REQUEST REVIEW (BEN)
        response = self.client.post('/m/login/', {'email':'ben.viralington@gmail.com', 'pin':'5533'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)
        self.failUnlessEqual(result['result'], '1')
        
        ben = Party.objects.get(email='ben.viralington@gmail.com')
        
        if not Wishlist.objects.filter(party=ben, product=clerks).exists():
            w = Wishlist(party=ben, product=clerks)
            w.save()
        else:
            w = Wishlist.objects.get(party=ben, product=clerks)
        
        response = self.client.get( "/request/review/%s/"%clerks.id )
        print ReviewRequest.objects.get(product=clerks, requester=ben).replies.all()
        print Review.objects.get(product=clerks, reviewer=niwen).reply_to.all()
        
        response = self.client.post('/m/logout/', {'email':'ben.viralington@gmail.com', 'pin':'5533'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)
        self.failUnlessEqual(result['result'], '1')
        
        
        #TEST NIWEN'S REVIEWS
        response = self.client.post('/m/login/', {'email':'niwen.chang@gmail.com', 'pin':'1111'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)
        self.failUnlessEqual(result['result'], '1')
        
        response = self.client.get( "/reviews/" )
        self.assertContains(response, clerks.id)
        
        review = Review.objects.get(reviewer=niwen, product=clerks)
        """
        review.rating = 5
        print review.first_reviewed
        if not review.first_reviewed:
            review.first_reviewed = True
        print review.first_reviewed
        review.save()
        """
        response = self.client.post("/update/rating/", {"review_id": review.id,
                                            "rating": 5})
        result = json.loads(response.content)
         
        self.failUnlessEqual(result['result'], "5: Best buy")

        response = self.client.post('/m/logout/', {'email':'niwen.chang@gmail.com', 'pin':'1111'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)
        self.failUnlessEqual(result['result'], '1')
        
        
        #RETEST BEN'S VIEWS
        response = self.client.post('/m/login/', {'email':'ben.viralington@gmail.com', 'pin':'5533'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)
        self.failUnlessEqual(result['result'], '1')
        
        response = self.client.get( "/requests/" )

        req = ReviewRequest.objects.get(product=clerks, requester=ben)
        
        for r in req.replies.all():
            print r
            print r.first_reviewed
        
        for r in req.replies.filter(first_reviewed=True):
            print r
            print r.first_reviewed

        self.assertContains(response, "Reviews Requested - 1")
        self.assertContains(response, "product_name")
        print response.content
        
        response = self.client.post('/m/logout/', {'email':'ben.viralington@gmail.com', 'pin':'5533'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)
        self.failUnlessEqual(result['result'], '1')

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

