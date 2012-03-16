from django.test.client import Client
from datetime import date
import random
import json
from finance.models import Country, Region, PostalCode, WesabeLocation, SpendingCategory, Coupon

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

    method = "/mobile/login/"
    r = c.post(method,  {'email':'kool@mit.edu',
                            'pin': '5533',
                            'lat': '-42.23234',
                            'lon': '52.23424',
                            'table': 'abcd'})
    print method
    print r.content
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/load/"
    r = c.post(method, {'email':'kwan@media.mit.edu',
                    'password':'2testfcn'})
    print method
    print r
    print json.dumps(json.loads(r.content), indent=2) 

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

    method = "/mobile/login/"
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
    method = "/mobile/surveys/"
    r = c.post(method, {'e':'e'})
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/mobile/survey/1/"
    r = c.get(method)
    print r
    """
    method = "/wesabe/feeds/"
    r = c.post(method, {'page':'0',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    """
    # web call
    method = "/wesabe/txns/0/"
    r = c.post(method, {'e':'e'})
    print method
    print r
    """

    method = "/wesabe/category/add/"
    r = c.post(method, {'name': 'Toys',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2)

    method = "/wesabe/search/"
    r = c.post(method, {'query': 'lotte', 'filter':'3',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/categories/"
    r = c.post(method, {
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/split/add/"
    r = c.post(method, {'txn_id':'69', 'split_id':'0', 'name':'eBay', 'price':'4.95',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    rdict = json.loads(r.content)
    method = "/wesabe/split/delete/"
    r = c.post(method, {'split_id':rdict["result"],
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/split/add/"
    r = c.post(method, {'txn_id':'69', 'split_id':'0', 'name':'Keyboard', 'price':'8.95',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    rdict = json.loads(r.content)
    method = "/wesabe/split/add/"
    r = c.post(method, {'txn_id':'69', 'split_id':rdict["result"], 'name':'Joystick',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    rdict = json.loads(r.content)
    method = "/wesabe/split/delete/"
    r = c.post(method, {'split_id': rdict["result"],
                        'lat': '-42.23234',
                        'lon': '52.23424',
                    })
    print method
    print json.dumps(json.loads(r.content), indent=2) 


#rdict = json.loads(r.content)
#method = "/wesabe/split/delete/"
#    r = c.post(method, {'split_id': rdict["result"],
#                        'lat': '-42.23234',
#                        'lon': '52.23424',
#                    })
#print method
#print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/txn/"
    r = c.post(method, {'txn_id':'6',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/txn/"
    r = c.post(method, {'txn_id':'35',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/txn/"
    r = c.post(method, {'txn_id':'355',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/locations/"
    r = c.post(method, {
                        'page': '1',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })

    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/txn/detail/"
    r = c.post(method, {'txn_id': '69',
                        'detail': 'Mailed eBay item',
                        'rating': '4',
                        'sharing': '2',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/txn/detail/"
    r = c.post(method, {'txn_id': '69',
                        'location': '3',
                        'category': '5',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/location/"
    r = c.post(method, {'loc_id': '5',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2)

    method = "/wesabe/coupons/"
    r = c.post(method, {'loc_id': '6',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/coupons/all/"
    r = c.post(method, {
                        'page': '1',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/m/txns/"
    r = c.post(method, {
                        'page': '1',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/txn/"
    r = c.post(method, {'txn_id':'6',
                        'lat': '-42.23234',
                        'lon': '52.23424',
                        })
    print method
    print json.dumps(json.loads(r.content), indent=2) 

    method = "/wesabe/txn/"
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
