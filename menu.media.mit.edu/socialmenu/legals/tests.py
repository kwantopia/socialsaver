"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from legals.models import *
from django.contrib.auth.models import User
from common.models import OTNUser
import time, json, hashlib, string, uuid
from datetime import datetime, date, timedelta
from facebookconnect.models import FacebookProfile

class SimpleTest(TestCase):

    fixtures = ['fixtures/init_setup.json']

    def redirect_contains(self, redirect_chain, text):
        """
            assert that redirect chain contains text
        """
        for r in redirect_chain:
            if r[0].find(text) > -1:
                return True
        print "redirect chain %s does not contain %s"%(redirect_chain, text)
        self.failIfEqual(True, True)

    def redirect_notcontains(self, redirect_chain, text):
        """
            assert that redirect chain does not contain text
        """
        for r in redirect_chain:
            if r[0].find(text) == -1:
                return True
        print "redirect chain %s contains %s"%(redirect_chain, text)
        self.failIfEqual(True, True)

    def test_order(self):
        """
            Testing ordering process
        """
        u = User(username='kwan', password='test')
        u.save()
        o = Order(user=u, table=TableCode.objects.all()[0])
        o.last_update()
        o.save()

        m = MenuItem.objects.get(id=5)
        r = MenuItemReview(item=m)
        r.save()

        o.items.add(r)
        o.last_update()
        time.sleep(5)

        m = MenuItem.objects.get(id=25)
        r = MenuItemReview(item=m)
        r.save()

        o.items.add(r)
        o.last_update()
        print "Order created: %d",o.id

    def test_multiple_order(self):
        """
            Testing multiple people ordering and TableCode assigning 
            specific experiment ID and also making the TableCode no
            longer usable
        """
        # different people login with same table code
        u1 = OTNUser(username='kwan1', password='test')
        u1.my_email = 'kool1@mit.edu'
        pin1 = '5538'
        u1.pin = hashlib.sha224(pin1).hexdigest()
        u1.save()
        u2 = OTNUser(username='kwan2', password='test')
        u2.my_email = 'kool2@mit.edu'
        pin2 = '5536'
        u2.pin = hashlib.sha224(pin2).hexdigest()
        u2.save()
        u3 = OTNUser(username='kwan3', password='test')
        u3.my_email = 'kool3@mit.edu'
        pin3 = '5537'
        u3.pin = hashlib.sha224(pin3).hexdigest()
        u3.save()
        u4 = OTNUser(username='kwan4', password='test')
        u4.my_email = 'kool4@mit.edu'
        pin4 = '5539'
        u4.pin = hashlib.sha224(pin4).hexdigest()
        u4.save()
        u5 = OTNUser(username='kwan5', password='test')
        u5.my_email = 'kool5@mit.edu'
        pin5 = '5543'
        u5.pin = hashlib.sha224(pin5).hexdigest()
        u5.save()

        udid1 = string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') + string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') 
        udid2 = string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') + string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') 
        udid3 = string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') + string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') 
        udid4 = string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') + string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') 
        udid5 = string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') + string.replace(str(uuid.uuid3(uuid.uuid1(), 'digital menu')),'-', '') 
        lat = -24.4342
        lon = 42.3143
        response = self.client.get("/legals/m/%.6f/%.6f/%s/"%(lat, lon, udid1))
        self.assertContains(response, udid1)

        tcode = str(uuid.uuid3(uuid.uuid1(), 'digital menu'))[:4]
        # insert this table code to use
        tc = TableCode(code=tcode, date=date.today())
        tc.save()
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid1),
                                                        'email':u1.my_email,
                                                        'pin':pin1,
                                                        'table':tcode},
                                                        follow=True)
        self.redirect_notcontains(response.redirect_chain, 'categories/0/' ) 

        # table code has been used
        tc = TableCode.objects.get(code=tcode)
        self.failIfEqual(tc.first_used, None)
        self.failIfEqual(tc.experiment, None)

        # set the table code used time to 29 minutes ago
        tc.first_used = datetime.now()-timedelta(minutes=29)
        tc.save()
        # second person
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid2),
                                                        'email':u2.my_email,
                                                        'pin':pin2,
                                                        'table':tcode},
                                                        follow=True)
        self.redirect_notcontains(response.redirect_chain, 'categories/0/' ) 
        # third person
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid3),
                                                        'email':u3.my_email,
                                                        'pin':pin3,
                                                        'table':tcode},
                                                        follow=True)
        self.redirect_notcontains(response.redirect_chain, 'categories/0/' ) 

        # forth person
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid4),
                                                        'email':u4.my_email,
                                                        'pin':pin4,
                                                        'table':tcode},
                                                        follow=True)
        self.redirect_notcontains(response.redirect_chain, 'categories/0/' ) 

        # fifth person
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid5),
                                                        'email':u5.my_email,
                                                        'pin':pin5,
                                                        'table':tcode},
                                                        follow=True)
        self.redirect_notcontains(response.redirect_chain, 'categories/0/' ) 

        # after 30 minutes, the table code would become unusable
        # set the table code used time to 35 minutes ago
        tc.first_used = datetime.now()-timedelta(minutes=61)
        tc.save()

        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid2),
                                                        'email':u2.my_email,
                                                        'pin':pin2,
                                                        'table':tcode},
                                                        follow=True)
        print "After table code expired:", response.redirect_chain
        self.assertContains(response, 'Table Code is Invalid' ) 

        # third person
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid3),
                                                        'email':u3.my_email,
                                                        'pin':pin3,
                                                        'table':tcode},
                                                        follow=True)
        print "After table code expired:", response.redirect_chain
        self.assertContains(response, 'Table Code is Invalid' ) 


        # bad password 
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid3),
                                                        'email':u3.my_email,
                                                        'pin':'23wewe',
                                                        'table':tcode},
                                                        follow=True)
        print "After bad pin:", response.redirect_chain
        self.assertContains(response, 'Email or PIN did not validate' ) 

        # bad password 
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid3),
                                                        'email':'kool@mit.edu',
                                                        'pin':pin3,
                                                        'table':tcode},
                                                        follow=True)
        print "After bad password:", response.redirect_chain
        self.assertContains(response, 'Email or PIN did not validate' ) 

        # bad table code 
        response = self.client.post("/legals/m/login/", {'lat':str(lat),
                                                        'lon':str(lon),
                                                        'udid':str(udid3),
                                                        'email':'kool@mit.edu',
                                                        'pin':'5533',
                                                        'table':'5555'},
                                                        follow=True)
        print "After bad table code:", response.redirect_chain
        self.assertContains(response, 'Table Code is Invalid' ) 

    def test_feedback(self):
        u = OTNUser(username='kwan', password='test')
        u.my_email = 'kool7@mit.edu'
        u.pin = hashlib.sha224('5533').hexdigest()
        u.save()
        fb = FacebookProfile(user=u, facebook_id=1341341414)
        fb.save()
        f = Feedback(user=u, speed=2, size=3)
        f.save()

        f = Feedback(user=u, speed=1, size=4, comment="It was damn slow!!")
        f.save()

        pin = hashlib.sha224('5533').hexdigest()
        response = self.client.login(email='kool7@mit.edu', pin=pin)
        print response

        response = self.client.get("/legals/feedback/post/")
        print response 

        response = self.client.post("/legals/feedback/post/", {'speed':'2',
                                                'size': '1',
                                                'comment': "It's interesting"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest' )
        print json.dumps(json.loads(response.content), indent=2) 

        response = self.client.post("/legals/feedback/post/", {'speed':'2',
                                                'size': '1'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest' )
        print json.dumps(json.loads(response.content), indent=2) 

    def test_receipt_upload(self):
        u = OTNUser(username='kwan', first_name='Kwan', last_name='Lee', password='test')
        u.my_email = 'kool2@mit.edu'
        u.pin = hashlib.sha224('5533').hexdigest()
        u.save()
        o = Order(user=u, table=TableCode.objects.all()[0])
        o.save()
        o.last_update()

        m = MenuItem.objects.get(id=5)
        r = MenuItemReview(item=m)
        r.save()

        o.items.add(r)

        m = MenuItem.objects.get(id=25)
        r = MenuItemReview(item=m)
        r.save()

        o.items.add(r)
        o.last_update()
        o.save()

        print "Order created: %d",o.id

        pin = hashlib.sha224('5533').hexdigest()
        self.client.login(email='kool@mit.edu', pin=pin)

        # upload receipt
        f = open("test/receipt.png")       
        response = self.client.post("/legals/receipt/upload/", {'order_id':str(o.id), 'receipt':f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest' )
        f.close()
        print json.dumps(json.loads(response.content), indent=2) 

        response = self.client.get("/legals/order/", {'order_id':str(o.id)},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print json.dumps(json.loads(response.content), indent=2) 

        response = self.client.get("/legals/order/", {'order_id':'3'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)
        self.failUnlessEqual(output['result'], '-1')
        print json.dumps(json.loads(response.content), indent=2) 

       
def call_json(c, command, params):
    print 'CALL', command
    response = c.post(command, params) 
    print json.dumps(json.loads(response.content), indent=2)
    return response


def test_reconsider():
    pass

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


