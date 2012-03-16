"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
import time, hashlib
from common.models import Friends
from bestbuy.models import *
from facebookconnect.models import *

class SimpleTest(TestCase):

    fixtures = ['categories.json']

    def runTest(self):
        pass

    def setUp(self):
        # create experiments
        exp = Experiment(name="Control", description="Control Group")
        exp.save()
        exp = Experiment(name="Social", description="Social Group")
        exp.save()
        exp = Experiment(name="Popularity", description="Popularity Group")
        exp.save()
        exp = Experiment(name="Friends", description="Friends Group")
        exp.save()

        from datetime import datetime
        exp = Experiment.objects.get(id=2)
        pin = hashlib.sha224('5533').hexdigest()
        try:
            self.kwan = Party.objects.get(id=2)
        except Party.DoesNotExist:
            self.kwan = Party(experiment=exp, name='Kwan Hong Lee', pin=pin, username="kool@mit.edu")
        self.kwan.experiment=exp
        self.kwan.first_name = "Kwan"
        self.kwan.last_name = "Lee"
        self.kwan.email = "kool@mit.edu"
        self.kwan.save()
        kwan_fb, created = FacebookProfile.objects.get_or_create(user=self.kwan, facebook_id=706848)
        kwan_fb.save()

        exp = Experiment.objects.get(id=3)
        
        try:
            self.ben = Party.objects.get(username="ben.viralington@gmail.com")
        except Party.DoesNotExist:
            self.ben = Party(experiment=exp, name='Ben Viralington', pin=pin, username="ben.viralington@gmail.com")
            self.ben.first_name = "Ben"
            self.ben.last_name = "Viralington"
            self.ben.password = '58aa6d5beb9c6c06890c2d40e29779074c89936afd14b4ab27791aac'
            self.ben.proxy_email = 'apps+251599741631.100000812545662.c766be39af2bfc9b48a5bd4c64908627@proxymail.facebook.com'
            self.ben.email = "ben.viralington@gmail.com"
            self.ben.save()
            ben_fb = FacebookProfile(user=self.ben, facebook_id=100000812545662)
            ben_fb.save()

        try:
            self.steph = Party.objects.get(username="niwen.chang@gmail.com")
        except Party.DoesNotExist:
            self.steph = Party(experiment=exp, name='Stephanie N. Chang', pin=pin, username="niwen.chang@gmail.com")
            self.steph.first_name = "Stephanie"
            self.steph.last_name = "Chang"
            self.steph.password = '278627ff12882b9e8b38e7ab66c98d99540b1dce7b3acf9ec8fdb0a5'
            self.steph.proxy_email = 'apps+251599741631.100000812545662.c766be39af2bfc9b48a5bd4c64908627@proxymail.facebook.com'
            self.steph.email = "niwen.chang@gmail.com"
            self.steph.save()
            steph_fb = FacebookProfile(user=self.steph, facebook_id=1025461356)
            steph_fb.save()

        try:
            self.sister = Party.objects.get(username="nihwey.chang@gmail.com")
        except Party.DoesNotExist:
            self.sister = Party(experiment=exp, name='Angela N. Chang', pin=pin, username="nihwey.chang@gmail.com")
            self.sister.first_name = "Angela"
            self.sister.last_name = "Chang"
            self.sister.password = '278627ff12882b9e8b38e7ab66c98d99540b1dce7b3acf9ec8fdb0a5'
            self.sister.proxy_email = 'apps+251599741631.100000812545662.c766be39af2bfc9b48a5bd4c64908627@proxymail.facebook.com'
            self.sister.email = "nihwey.chang@gmail.com"
            self.sister.save()
            sister_fb = FacebookProfile(user=self.sister, facebook_id=778320095)
            sister_fb.save()

        kwan_friends, created = Friends.objects.get_or_create(facebook_id=706848)
        kwan_friends.image = 'http://www.facebook.com/pics/t_silhouette.gif'
        kwan_friends.name = 'Kwan Hong Lee'
        kwan_friends.save()

        ben_friends, created = Friends.objects.get_or_create(facebook_id=100000812545662)
        ben_friends.image = 'http://www.facebook.com/pics/t_silhouette.gif'
        ben_friends.name = 'Ben Viralington'
        ben_friends.save()

        steph_friends, created = Friends.objects.get_or_create(facebook_id=1025461356)
        steph_friends.image = 'http://profile.ak.fbcdn.net/hprofile-ak-snc4/hs624.ash1/27405_1025461356_9717_q.jpg'
        steph_friends.name = 'Stephanie N. Chang'
        steph_friends.save()

        sister_friends, created = Friends.objects.get_or_create(facebook_id=778320095)
        sister_friends.image = 'http://profile.ak.fbcdn.net/hprofile-ak-snc4/hs341.snc4/41373_778320095_7740_q.jpg'
        sister_friends.name = 'Angela Chang'
        sister_friends.save()

        kwan_friends.friends.add(ben_friends)
        kwan_friends.friends.add(steph_friends)
        ben_friends.friends.add(kwan_friends)
        ben_friends.friends.add(steph_friends)
        steph_friends.friends.add(ben_friends)
        steph_friends.friends.add(kwan_friends)
        steph_friends.friends.add(sister_friends)

        # Kwan buys 
        self.kwan_txn1 = Transaction(bb_transaction_id='1',
                party=self.kwan,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.kwan_txn1.save()

        p = Product.objects.get_by_sku(9644845)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=2, line_type='SL',
                                    sale_price=99.99,
                                    product=p,
                                    transaction=self.kwan_txn1)
        line1.save()
        p = Product.objects.get_by_sku(9461076)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=3, line_type='SL',
                                    sale_price=19.99,
                                    product=p,
                                    transaction=self.kwan_txn1)
        line1.save()
        self.kwan_txn2 = Transaction(bb_transaction_id='2',
                party=self.kwan,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.kwan_txn2.save()

        p = Product.objects.get_by_sku(8310847)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=12, line_type='SL',
                                    sale_price=199.99,
                                    product=p,
                                    transaction=self.kwan_txn2)
        line1.save()
        p = Product.objects.get_by_sku(9477005)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=35, line_type='SL',
                                    sale_price=39.99,
                                    product=p,
                                    transaction=self.kwan_txn2)
        line1.save()
        p = Product.objects.get_by_sku(9704268)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=35, line_type='SL',
                                    sale_price=39.99,
                                    product=p,
                                    transaction=self.kwan_txn2)
        line1.save()

        self.kwan_txn3 = Transaction(bb_transaction_id='3',
                party=self.kwan,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.kwan_txn3.save()

        p = Product.objects.get_by_sku(9051036)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=36, line_type='SL',
                                    sale_price=39.99,
                                    product=p,
                                    transaction=self.kwan_txn3)
        line1.save()

        # Ben buys 
        self.ben_txn1 = Transaction(bb_transaction_id='3',
                party=self.ben,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.ben_txn1.save()

        p = Product.objects.get_by_sku(9644845)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=2, line_type='SL',
                                    sale_price=99.99,
                                    product=p,
                                    transaction=self.ben_txn1)
        line1.save()

        p = Product.objects.get_by_sku(9461076)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=3, line_type='SL',
                                    sale_price=19.99,
                                    product=p,
                                    transaction=self.ben_txn1)
        line1.save()

        self.ben_txn2 = Transaction(bb_transaction_id='4',
                party=self.ben,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.ben_txn2.save()

        p = Product.objects.get_by_sku(8310847)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=12, line_type='SL',
                                    sale_price=199.99,
                                    product=p,
                                    transaction=self.ben_txn2)
        line1.save()

        p = Product.objects.get_by_sku(9477005)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=36, line_type='SL',
                                    sale_price=39.99,
                                    product=p,
                                    transaction=self.ben_txn2)
        line1.save()

        p = Product.objects.get_by_sku(8246846)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=45, line_type='SL',
                                    sale_price=39.99,
                                    product=p,
                                    transaction=self.ben_txn2)
        line1.save()
        p = Product.objects.get_by_sku(9723733)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=45, line_type='SL',
                                    sale_price=639.99,
                                    product=p,
                                    transaction=self.ben_txn2)
        line1.save()

        self.ben_txn3 = Transaction(bb_transaction_id='5',
                party=self.ben,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.ben_txn3.save()

        p = Product.objects.get_by_sku(9539154)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=46, line_type='SL',
                                    sale_price=639.99,
                                    product=p,
                                    transaction=self.ben_txn3)
        line1.save()

        # Stephanie buys
        self.steph_txn1 = Transaction(bb_transaction_id='1',
                party=self.steph,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.steph_txn1.save()


        p = Product.objects.get_by_sku(9644845)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=2, line_type='SL',
                                    sale_price=99.99,
                                    product=p,
                                    transaction=self.steph_txn1)
        line1.save()
        p = Product.objects.get_by_sku(9461076)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=3, line_type='SL',
                                    sale_price=19.99,
                                    product=p,
                                    transaction=self.steph_txn1)
        line1.save()

        self.steph_txn2 = Transaction(bb_transaction_id='23',
                party=self.steph,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.steph_txn2.save()

        p = Product.objects.get_by_sku(8310847)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=12, line_type='SL',
                                    sale_price=199.99,
                                    product=p,
                                    transaction=self.steph_txn2)
        line1.save()
        p = Product.objects.get_by_sku(9477005)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=35, line_type='SL',
                                    sale_price=39.99,
                                    product=p,
                                    transaction=self.steph_txn2)
        line1.save()
        p = Product.objects.get_by_sku(9704268)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=35, line_type='SL',
                                    sale_price=39.99,
                                    product=p,
                                    transaction=self.steph_txn2)
        line1.save()

        self.steph_txn3 = Transaction(bb_transaction_id='33',
                party=self.steph,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
        self.steph_txn3.save()

        p = Product.objects.get_by_sku(9746041)
        time.sleep(0.5)
        line1 = TransactionLineItem(line_number=2, line_type='SL',
                                    sale_price=99.99,
                                    product=p,
                                    transaction=self.steph_txn3)
        line1.save()

        # Kwan wishes 3 items
        p = Product.objects.get_by_sku(9757802)
        time.sleep(0.5)
        w = Wishlist(party=self.kwan,
                product=p,
                comment='This is awesome',
                max_price=100)
        w.save()

        p = Product.objects.get_by_sku(9812863)
        time.sleep(0.5)
        w = Wishlist(party=self.kwan,
                product=p,
                max_price=100)
        w.save()

        p = Product.objects.get_by_sku(9746041)
        time.sleep(0.5)
        w = Wishlist(party=self.kwan,
                product=p,
                comment='This is awesome',
                max_price=100)
        w.save()


        # Ben wishes 3 items
        p = Product.objects.get_by_sku(9500453)
        time.sleep(0.5)
        w = Wishlist(party=self.ben,
                product=p,
                comment='This is awesome',
                max_price=100)
        w.save()

        p = Product.objects.get_by_sku(9757802)
        time.sleep(0.5)
        w = Wishlist(party=self.ben,
                product=p,
                comment='This is awesome',
                max_price=100)
        w.save()

        p = Product.objects.get_by_sku(9209331)
        time.sleep(0.5)
        w = Wishlist(party=self.ben,
                product=p,
                comment='This is what i really want',
                max_price=155555.00)
        w.save()

        # Steph wishes 3 items
        p = Product.objects.get_by_sku(9500453)
        time.sleep(0.5)
        w = Wishlist(party=self.steph,
                product=p,
                comment='This is awesome',
                max_price=100)
        w.save()

        p = Product.objects.get_by_sku(9757802)
        time.sleep(0.5)
        w = Wishlist(party=self.steph,
                product=p,
                comment='This is awesome',
                max_price=100)
        w.save()

        p = Product.objects.get_by_sku(9209331)
        time.sleep(0.5)
        w = Wishlist(party=self.steph,
                product=p,
                comment='This is what i really want',
                max_price=155555.00)
        w.save()




        # Kwan asks for review request
        p = Product.objects.get_by_sku(9539154)
        req0 = ReviewRequest(requester=self.kwan, product=p)
        req0.save()

        # Ben has this product
        p = Product.objects.get_by_sku(9723733)
        req1 = ReviewRequest(requester=self.kwan, product=p)
        req1.save()

        # my own product 
        p = Product.objects.get_by_sku(9644845)
        req2 = ReviewRequest(requester=self.kwan, product=p)
        req2.save()


        # Ben asks for review request
        
        # kwan has these products
        p = Product.objects.get_by_sku(9644845)
        self.req3 = ReviewRequest(requester=self.ben, product=p)
        self.req3.save()

        p = Product.objects.get_by_sku(9704268)
        req4 = ReviewRequest(requester=self.ben, product=p)
        req4.save()


        # Ben reviews

        p = Product.objects.get_by_sku(9723733)
        r = Review(reviewer=self.ben, product=p,viewed=1,content="It's a really nice catch")
        r.save()
        r.reply_to.add(req1)

        p = Product.objects.get_by_sku(9539154)
        r = Review(reviewer=self.ben, product=p,viewed=1,content="It's not easy to find such a polished product.")
        r.save()
        r.reply_to.add(req0)


        # Kwan answers review request
        p = Product.objects.get_by_sku(9704268)
        r = Review(reviewer=self.kwan, product=p,viewed=1,content="You don't want to buy this")
        r.save()
        r.reply_to.add(req4)


        #########################################################
        # Feeds
        #########################################################

        p = Product.objects.get_by_sku(9461076)
        f = Feed(actor=self.ben, action=Feed.BOUGHT, product=p)
        f.save()

        p = Product.objects.get_by_sku(9723733)
        f = Feed(actor=self.ben, action=Feed.REVIEWED, product=p)
        f.save()

        p = Product.objects.get_by_sku(9644845)
        f = Feed(actor=self.ben, action=Feed.REQUESTED, product=p)
        f.save()

        p = Product.objects.get_by_sku(9500453)
        f = Feed(actor=self.ben, action=Feed.WISHLIST, product=p)
        f.save()

        p = Product.objects.get_by_sku(9644845)
        f = Feed(actor=self.kwan, action=Feed.BOUGHT, product=p)
        f.save()

        p = Product.objects.get_by_sku(9704268)
        f = Feed(actor=self.kwan, action=Feed.REVIEWED, product=p)
        f.save()

        p = Product.objects.get_by_sku(9723733)
        f = Feed(actor=self.kwan, action=Feed.REQUESTED, product=p)
        f.save()

        p = Product.objects.get_by_sku(9757802)
        f = Feed(actor=self.kwan, action=Feed.WISHLIST, product=p)
        f.save()

        #########################################################
        # Surveys
        ########################################################
        from survey.models import Survey, BasicMobileSurvey, BasicShoppingSurvey
        import datetime
        from django.contrib.auth.models import User
        from django.db import IntegrityError

        # Basic purchase behavior 
        s, created = Survey.objects.get_or_create(title="Basic Mobile Survey", 
                description="Tell us about your usage of mobile phone.",
                model_name="BasicMobileSurvey")
        #s.expires=datetime.datetime.now()+datetime.timedelta(5)
        s.expires = None
        s.save()

        # Shopping survey
        s, created = Survey.objects.get_or_create(title="Basic Shopping Survey", 
                description="Tell us about your shopping habits",
                model_name="BasicShoppingSurvey")
        #s.expires=datetime.datetime.now()+datetime.timedelta(10)
        s.expires = None
        s.save()
 
        self.failUnlessEqual(1 + 1, 2)


    def add_review_requests(self):

        self.ben = Party.objects.get(username="ben.viralington@gmail.com")
        self.kwan = Party.objects.get(username="kool@mit.edu")
        self.steph = Party.objects.get(username="niwen.chang@gmail.com")

        for t in TransactionLineItem.objects.filter(transaction__party=self.ben):

            # Ben has this product
            p = t.product 
            req1 = ReviewRequest(requester=self.kwan, product=p)
            req1.save()
            req1 = ReviewRequest(requester=self.steph, product=p)
            req1.save()

    def add_products( self, email, items, wished_by=None ):
        # 1005011
        # 8696253
        # 9697337
        for i in items:
            p = Product.objects.get_by_sku( i )
            if p is None:
                print "Product does not exist"
                continue
            u = Party.objects.get(email=email)
            txn = Transaction(bb_transaction_id=str(random.randint(10000,10000000)), party=u, key="5", register=38, number=9)
            txn.save()
            line = TransactionLineItem(line_number=1, line_type='SL', unit_quantity=1, sale_price=129.99, product=p, transaction=txn)
            line.save()
    
            if not wished_by:
                u = Party.objects.get(email=wished_by)
                w = Wishlist(party=u, product=p)
                w.save()

    def remove_products( self ):

        txns = TransactionLineItem.objects.filter(product=None)
        for t in txns:
            t.delete()

        wishes = Wishlist.objects.filter(product=None)
        for w in wishes:
            w.delete()

    def deprecated_test(self):

        command = '/m/bought/people/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9539154',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/wish/people/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9757802',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)



        # for social group, allow access to friend
        command = '/m/feed/friend/'
        print 'CALL', command
        response = self.client.post(command, { 'friend_id': '2',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        ################################################################################
        # Test Group View 
        # - Displays the list of ongoing group purchases you are participating
        #   - Shows status of participants 5 left to be fulfilled
        # - Displays the list of group purchases you can join
        #   - Details of the item, people who have joined, and discount 
        # - Displays the list of group purchases you can start
        #   - Details of the item, and initiate group purchase button
        # - Displays the list of group purchases you that has ended
        #       - ones that you have joined (shows success or not fulfilled)
        #       - if success, need to go buy in 7 days
        ################################################################################

        command = '/m/group/ongoing/list/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/group/join/list/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/group/start/list/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/group/ended/list/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)


    def test_wishlist(self):
        user_email='kool@mit.edu'
        user_email='ben.viralington@gmail.com'
        pin = '5533'

        sku_test = '9461076'
        sku_test = '9051036'
        sku_test = '9209331'

        command = '/m/login/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/wishlist/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        """
        command = "/m/review/ask/"
        print 'Test review ask to product I wish'
        print 'CALL', command
        response = self.client.post(command, {'sku':sku_test,
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)
        """

        command = '/m/item/request/'
        print 'CALL:', command
        response = self.client.post(command, {'sku': sku_test,
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)

        command = '/m/item/feed/'
        print 'CALL:', command
        response = self.client.post(command, {'sku': sku_test,
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)

        command = '/m/item/purchases/'
        print 'CALL:', command
        response = self.client.post(command, {'sku': sku_test,
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)

        command = '/m/item/wishlist/'
        print 'CALL:', command
        response = self.client.post(command, {'sku': sku_test,
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)


    def test_purchase(self):

        user_email='kool@mit.edu'
        pin = '5533'
        user_email='ben.viralington@gmail.com'
        pin = '5533'

        sku_test = '9461076'

        ################################################################################
        # Test login
        ################################################################################
        user_email='ben.viralington@gmail.com'
        pin = '5533'
        command = '/m/login/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)

        ################################################################################
        # Test Home View
        # - Displays survey requests
        #   - Show survey
        # - Displays review requests
        #   - Display item view that allows adding of review
        # - Displays feeds
        #   - Display the item view 
        ################################################################################

        command = '/m/home/'
        print 'CALL:', command
        response = self.client.post(command, {
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)

        survey_id = 3
        command = '/m/survey/%d/'%survey_id
        print 'CALL:', command
        response = self.client.get(command)
        print response

        command = '/m/item/request/'
        print 'CALL:', command
        response = self.client.post(command, {'sku': sku_test,
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)

        # invalid item
        command = '/m/item/browse/'
        print 'CALL:', command
        response = self.client.post(command, {'sku': '23422141',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)

        command = '/m/product/post/'
        print 'CALL', command
        response = self.client.post(command, {'product_id':'2',
                                    'sku': sku_test})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)


        ################################################################################
        # Test Purchase History
        # - Displays the item information, add review and what people think about it
        ################################################################################

        command = '/m/purchases/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/item/purchases/'
        print 'CALL', command
        response = self.client.post(command, {'sku':sku_test})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)

        ################################################################################
        # Test Wish List 
        ################################################################################

        command = '/m/wishlist/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/item/purchases/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'sku': '9757802',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/product/1/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/product/post/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'product_id': '1',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        # view each item on wish list
        command = '/m/item/wishlist/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9812863',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        # add item to wish list
        command = '/m/wishlist/add/'
        print 'Test adding new item'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9051036',
                                            'comment': 'I want this for Christmas!!',
                                            'max_price': '125.00',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})

        lastwish = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/wishlist/add/'
        print 'Test adding existing item'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9051036',
                                            'comment': 'I want this for Thanksgiving!!',
                                            'max_price': '125.00',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        repeatwish = json.loads(response.content)
        self.failUnlessEqual('-1', repeatwish['result'])
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/wishlist/item/update/'
        print "Test updating someone else's wish item"
        print 'CALL', command
        response = self.client.post(command, {'wish_id':'4',
                                            'comment': 'I want this for Thanksgiving!!',
                                            'max_price': '122.00',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        otherswish = json.loads(response.content)
        if user_email == 'kool@mit.edu':
            self.failUnlessEqual(otherswish['result'], '-1')
        elif user_email == 'ben.viralington@gmail.com':
            self.failUnlessEqual(otherswish['result'], '4')

        print json.dumps(json.loads(response.content), indent=2)


        command = '/m/wishlist/item/update/'
        print 'Test updating existing wish item'
        print 'CALL', command
        response = self.client.post(command, {'wish_id':lastwish['result'],
                                            'comment': 'I want this for Thanksgiving!!',
                                            'max_price': '122.00',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})

        updatewish = json.loads(response.content)
        self.failUnlessEqual(lastwish['result'], updatewish['result'])
        print json.dumps(json.loads(response.content), indent=2)

        # view each item on wish list
        command = '/m/item/wishlist/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9051036'})
        print json.dumps(json.loads(response.content), indent=2)


        ################################################################################
        # Test Items (Browse, Search, Scan) 
        ################################################################################

        command = '/m/search/'
        print 'CALL', command
        response = self.client.post(command, {'search':'DVD',
                                    'page': '4'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/search/'
        print 'CALL', command
        response = self.client.post(command, {'search':'anime',
                                    'page': '1'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/search/'
        print 'CALL', command
        response = self.client.post(command, {'search':'Netbook',
                                    'page': '1'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/item/browse/'
        print 'CALL', command
        response = self.client.post(command, {'sku':sku_test})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)

        command = '/m/scan/'
        print 'CALL', command
        response = self.client.post(command, {'sku':sku_test})
        print json.dumps(json.loads(response.content), indent=2)
        time.sleep(1)

        command = '/m/browse/categories/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/browse/hot/'
        print 'CALL', command
        response = self.client.post(command, { 'page':'1',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/browse/category/'
        print 'CALL (Only has sub category not products', command
        response = self.client.post(command, {'cat_id':'3',
                                            'page': '1',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/browse/category/'
        print 'CALL', command
        response = self.client.post(command, {'cat_id':'4',
                                            'page': '1',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)


        ################################################################################
        # Test Friends details 
        ################################################################################
        
        command = '/m/friends/wish/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9500453',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)


        command = '/m/friends/bought/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9723733',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/party/'
        print 'CALL', command
        response = self.client.post(command, {'party_id':'2',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        
        party_info = json.loads(response.content)
        if len(party_info["wished"]) > 0:
            query_sku = party_info["wished"][0]["product"]["sku"]

            command = '/m/item/party/'
            print 'CALL:', command
            response = self.client.post(command, {'sku': query_sku,
                                                'lat':'32.32423',
                                                'lon':'-23.2342'})
            print json.dumps(json.loads(response.content), indent=2)
            time.sleep(1)

        if len(party_info["bought"]) > 0:
            query_sku = party_info["bought"][0]["product"]["sku"]
            command = '/m/item/party/'
            print 'CALL:', command
            response = self.client.post(command, {'sku': query_sku,
                                                'lat':'32.32423',
                                                'lon':'-23.2342'})
            print json.dumps(json.loads(response.content), indent=2)
            time.sleep(1)


        ################################################################################
        # Test Reviews 
        ################################################################################

        command = "/m/review/ask/"
        print 'Test review ask to product I wish'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9051036',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)

        rev_req = ReviewRequest.objects.get(id = result["result"])
        w = Wishlist.objects.get(party=rev_req.requester, product=rev_req.product)
        self.failUnlessEqual(w.review, 1)

        command = "/m/review/add/"
        print 'Test review add to product Ben owns'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9461076',
                                            'rating':'3',
                                            'content': 'This is a must buy!!',
                                            'public': 'true',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/logout/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)

        user_email='kool@mit.edu'
        pin = '5533'
        command = '/m/login/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)

        command = "/m/review/add/"
        print 'Test review add to product Kwan owns, but Ben requested for review'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9051036',
                                            'rating':'3',
                                            'content': 'This is a must buy!!',
                                            'public': 'true',
                                            'reply_to': rev_req.id,
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        result = json.loads(response.content)
        print json.dumps(json.loads(response.content), indent=2)

        rev = Review.objects.get(id=result["result"])
        for requests in rev.reply_to.all():
            for w in Wishlist.objects.filter(party=requests.requester, product=rev.product):
                if w.review == 2:
                    updated_review = w.review 
        self.failUnlessEqual(updated_review, 2)

        command = '/m/logout/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)



        user_email='ben.viralington@gmail.com'
        pin = '5533'
        command = '/m/login/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)


        command = "/m/review/read/"
        print 'CALL', command
        response = self.client.post(command, {'review_id':result['result'],
                                                'lat':'32.32423',
                                                'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        user_email='kool@mit.edu'
        pin = '5533'
        command = '/m/login/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)


        command = "/m/review/add/"
        print 'Test review to review request'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9461076',
                                            'rating':'4',
                                            'content': 'This is a must buy!!',
                                            'reply_to': str(self.req3.id),
                                            'public': 'true',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/logout/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)

        user_email='ben.viralington@gmail.com'
        pin = '5533'
        command = '/m/login/'
        print 'CALL:', command
        response = self.client.post(command, {'email': user_email,
                                    'pin': pin,
                                    'lat': '-42.23432',
                                    'lon': '74.234131'})
        print json.dumps(json.loads(response.content), indent=2)


        command = '/m/item/view/reviews/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9461076',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        reviews = json.loads(response.content)
        print reviews


        command = "/m/review/read/"
        print 'CALL', command
        response = self.client.post(command, {'review_id':reviews["reviews"][0]["review_id"],
                                            'lat': '32.432',
                                            'lon': '-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
        
        command = "/m/review/add/"
        print 'Test review to review request'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9644845',
                                            'rating':'3',
                                            'content': 'This is a must buy!!',
                                            'reply_to': str(self.req3.id),
                                            'public': 'true',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/item/view/reviews/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9644845',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
 
        command = "/m/review/add/"
        print "Test review to product I don't own"
        print 'CALL', command
        response = self.client.post(command, {'sku':'9723733',
                                            'rating':'3',
                                            'content': 'This is a must buy!!',
                                            'reply_to': str(self.req3.id),
                                            'public': 'true',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        result = json.loads(response.content)
        if user_email=='kool@mit.edu':
            self.failUnlessEqual(result["result"], '-1')
        elif user_email=='ben.viralington@gmail.com':
            self.failUnlessEqual(result["result"], '1')

        print json.dumps(json.loads(response.content), indent=2)


        command = '/m/item/view/reviews/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9723733',
                                            'lat':'32.32423',
                                            'lon':'-23.2342'})
        print json.dumps(json.loads(response.content), indent=2)
   
        command = '/m/find/store/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9723733',
                                            'lat': 44.862858,
                                            'lon':-93.292763,
                                            'distance': '3'} )
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/item/view/bought/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9723733',
                                            'lat': 44.862858,
                                            'lon':-93.292763} )
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/item/view/wished/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9500453',
                                            'lat': 44.862858,
                                            'lon':-93.292763} )
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/item/view/bb_reviews/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9723733',
                                            'lat': 44.862858,
                                            'lon':-93.292763} )
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/item/view/reviews/'
        print 'CALL', command
        response = self.client.post(command, {'sku':'9723733',
                                            'lat': 44.862858,
                                            'lon':-93.292763} )
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/requests/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat': 44.862858,
                                            'lon':-93.292763} )
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/feeds/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat': 44.862858,
                                            'lon':-93.292763} )
        print json.dumps(json.loads(response.content), indent=2)

        command = '/m/surveys/'
        print 'CALL', command
        response = self.client.post(command, {
                                            'lat': 44.862858,
                                            'lon':-93.292763} )
        print json.dumps(json.loads(response.content), indent=2)

"""
    def test_populate(self):

        # add purchase items
        # add wish items
        # add review requests
        # add response to reviews
        # add reviews

        # call methods
        pass
"""
__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}



