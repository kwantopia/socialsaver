# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth import authenticate, login, logout

from common.helpers import JSONHttpResponse, JSHttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from common.models import Friends 

from finance import buxfer
from web.models import Coupon, Account, Transaction, Memo, SplitItem, LogCategoryCreation, SplitItem, SpendingCategory, Event
from survey.models import SurveyStatus
    
import xml.parsers.expat
import platform
import base64
import httplib, urllib, hashlib
import random
from django.conf import settings
from datetime import datetime

logger = settings.LOGGER

@csrf_exempt
def login_ws(request):
    """
        Login method

        :url: /m/login/
        
        :param POST['email']: email
        :param POST['pin']: PIN of the user
        :param POST['lat']: latitude of the phone
        :param POST['lon']: longitude of the phone

        :rtype: JSON
        
        ::

            # `experiment` is the experimental group
            #   1: control group
            #   2: social group
            #   3: anonymous social group

            # `surveys` is the number of surveys that needs to be filled

            # login success
            {'result':'1', 'experiment': '1', 'surveys': '2'}
            # login failure
            {'result':'-1'}

    """

    email = request.POST['email'].lower()
    pin = hashlib.sha224(request.POST['pin']).hexdigest()
    user = authenticate(email=email, pin=pin)
    if user is not None:
        login(request, user)
        logger.debug( "User %s authenticated and logged in"%email )
        exp_group = user.experiment.id
        # check the number of surveys that needs to be filled out
        surveys = SurveyStatus.objects.filter(user=user, completed=False).count() 
        # log latitude and longitude
        if 'lat' in request.POST:
            event = Event(user=user, action=Event.LOGIN, latitude=float(request.POST['lat']), longitude=float(request.POST['lon']))
            event.save()
        return JSONHttpResponse({'result': '1', 'experiment': str(exp_group), 'surveys':str(surveys)})          
    else:
        return JSONHttpResponse({'result': '-1'})

@csrf_exempt
@login_required
def load_transactions(request):
    """

        :url: /m/load/txns/

        :param POST['email']: for buxfer login
        :param POST['password']: for buxfer
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::



    """
    u = request.user
    r = {}
        
    # use the e-mail and password to login
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    if email is None or password is None:
        r['result'] = '-1'
    else:
        # load from buxfer
        b = buxfer.BuxferInterfac()
        
        success = b.buxfer_login(sys.argv[1], sys.argv[2])

        if success:
            accts = b.get_accounts()
            for a in accts:
                account, created = Account.objects.get_or_create(user=u, account_id = account["id"], name=account["name"], bank=account["bank"])
                account.balance = account["balance"]
                account.last_synced=account["lastSynced"]
                account.save()

                final = 1
                p = 1   # page number
                while final != 0: 
                    txns, final, total = b.get_transactions( a, page=p)
                    # iterate through txns and insert into model
                    for txn in txns:
                        memo, created = Memo.objects.get_or_create(txt=txn['description'])
                        t, created = Transaction.objects.get_or_create(account=account, transaction_id=txn['id'], amount=txn['amount']) 
                        t.memo = memo
                        t.save()
                    p += 1

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def get_feeds(request):
    """
        Get the feeds of other people

        :url: /m/feeds/

        :param POST['page']: page number
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            {
              "result": [
                {
                  "location": {
                    "id": "78", 
                    "name": "McDonalds"
                  }, 
                  "item": {
                    "price": "3.53", 
                    "id": "37", 
                    "name": "Fish Burger"
                  }, 
                  "txt": "Billy buys at McDonalds", 
                  "user": {
                    "first_name": "Billy", 
                    "id": "5"
                  }, 
                  "timestamp": "1268093098.035414"
                }, 
                {
                  "location": {
                    "id": "178", 
                    "name": "Economy Hardware"
                  }, 
                  "item": {
                    "price": "13.53", 
                    "id": "38", 
                    "name": "Book Shelf"
                  }, 
                  "txt": "Billy buys at Economy Hardware", 
                  "user": {
                    "first_name": "Billy", 
                    "id": "5"
                  }, 
                  "timestamp": "1268123098.035414"
                }
              ]
            }

    """
    u = request.user
    r = {}

    """
    r = {'result':[
                    {
                        'txt': 'Billy buys at McDonalds',
                        'user': {'id': '5',
                                'first_name': 'Billy'
                                },
                        'item': {'id': '37',
                                'name': 'Fish Burger',
                                'price': '3.53',
                        },
                        'location': {'id': '78',
                                'name': 'McDonalds'
                        },
                        'timestamp': '1268093098.035414',
                      },
                      {
                        'txt': 'Billy buys at Economy Hardware',
                        'user': {'id': '5',
                                'first_name': 'Billy'
                                },
                        'item': {'id': '38',
                                'name': 'Book Shelf',
                                'price': '13.53',
                        },
                        'location': {'id': '178',
                                'name': 'Economy Hardware'
                        },
                        'timestamp': '1268123098.035414',
                      }
                ]

            }

    """

    r['feeds'] = [f.get_json(me=u) for f in Feeds.objects.all()]
    # TODO: need to exclude feeds of myself
    #r['feeds'] = [f.get_json(me=u) for f in Feeds.objects.exclude(actor=u)]

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def all_coupons(request):
    """
        Get list of all coupons

        :url: /m/coupons/all/

        :param POST['page']: page num
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            {
              "total": "50", 
              "page": "4",
              "total_pages": "3",
              "coupons": [
                {
                  "location": {
                    "id": "10", 
                    "name": "Amazon.com", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "number": "7070685", 
                  "dealer": "The magistrate dealer", 
                  "content": "This is 7% off coupon", 
                  "expiry_date": "06/30/11", 
                  "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                  "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                  "id": "51", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "location": {
                    "id": "10", 
                    "name": "Amazon.com", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "number": "3869341", 
                  "dealer": "The magistrate dealer", 
                  "content": "This is 11% off coupon", 
                  "expiry_date": "06/30/11", 
                  "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                  "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                  "id": "52", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "location": {
                    "id": "4", 
                    "name": "Caltrain", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "number": "8262159", 
                  "dealer": "The magistrate dealer", 
                  "content": "This is 13% off coupon", 
                  "expiry_date": "06/30/11", 
                  "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                  "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                  "id": "53", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "location": {
                    "id": "8", 
                    "name": "Hostway", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "number": "5827508", 
                  "dealer": "The magistrate dealer", 
                  "content": "This is 24% off coupon", 
                  "expiry_date": "06/30/11", 
                  "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                  "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                  "id": "54", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "location": {
                    "id": "5", 
                    "name": "Ti Couz", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "number": "7113756", 
                  "dealer": "The magistrate dealer", 
                  "content": "This is 22% off coupon", 
                  "expiry_date": "06/30/11", 
                  "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                  "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                  "id": "55", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
              ]
            }

    """
    r = {}
    # TODO: filter by user
    u = request.user

    page = int(request.POST['page'])
    per_page = 10

    if page < 1:
        page = 1
    start = (page-1)*per_page

    coupons = Coupon.objects.all()
    if coupons.count()%per_page > 0:
        t_page = coupons.count()/per_page+1
    else:
        t_page = coupons.count()/per_page
    r["total"] = str(coupons.count())
    r["page"] = str(page)
    r["total_pages"] = str(t_page)
    r["coupons"] = [c.get_json() for c in coupons[start:start+per_page]] 

    return JSONHttpResponse(r)
 
@csrf_exempt
@login_required
def filter_coupons(request):
    """
        Filter coupons for specific criteria 

        :url: /m/coupons/filter/

        :param POST['query']: search query for coupons
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::


    """
    r = {}
    u = request.user

    r["coupons"] = [c.get_json() in Coupon.objects.filter(name__icontains=request.POST['query'])]

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def get_coupon(request):
    """
        Get a particular coupon

        :url: /m/coupon/

        :param POST['coupon_id']: coupon ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude 

    """
    r = {}
    u = request.user
    c = Coupon.objects.get(id=request.POST['coupon_id'])
    r["coupon"] = c.get_json()

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def list_transactions(request):
    """
        Mobile: Get the transactions of the user

        :url: /m/txns/

        :param POST['page']: page number (start from 1: default)
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::


            # total number of transactions and list of transactions
            # result = [] if no more transactions left to show

            {
              "count": "126", 
              "page": "5",
              "total_pages": "7",
              "result": [
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1270011600.0", 
                  "memo": "KEEP THE CHANGE TRANSFER TO ACCT 1187 FOR 03/31/10", 
                  "amount": "-0.37", 
                  "location": {
                    "id": "1", 
                    "name": "Unknown", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 31, 2010", 
                  "new": "True", 
                  "id": "29"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1270011600.0", 
                  "memo": "Ti Couz", 
                  "amount": "-39.63", 
                  "location": {
                    "id": "5", 
                    "name": "Ti Couz", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 31, 2010", 
                  "new": "True", 
                  "id": "30"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1269925200.0", 
                  "memo": "KEEP THE CHANGE TRANSFER TO ACCT 1187 FOR 03/30/10", 
                  "amount": "-0.02", 
                  "location": {
                    "id": "1", 
                    "name": "Unknown", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 30, 2010", 
                  "new": "True", 
                  "id": "26"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1269925200.0", 
                  "memo": "WALZWERK 03/28 CARD #8321 PURCHASE #24013390088016457446103 SAN FRANCISCO, CA", 
                  "amount": "-28.00", 
                  "location": {
                    "id": "1", 
                    "name": "Unknown", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 30, 2010", 
                  "new": "True", 
                  "id": "27"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1269925200.0", 
                  "memo": "DAMON'S 03/29 CARD #8321 PURCHASE #24071050088158137158150 CAMBRIDGE, MA", 
                  "amount": "-9.98", 
                  "location": {
                    "id": "1", 
                    "name": "Unknown", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 30, 2010", 
                  "new": "True", 
                  "id": "28"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1269925200.0", 
                  "memo": "MARRIOTT 337H4CAMBRG B CAMBRIDGE", 
                  "amount": "-2.12", 
                  "location": {
                    "id": "1", 
                    "name": "Unknown", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 30, 2010", 
                  "new": "True", 
                  "id": "126"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1269838800.0", 
                  "memo": "KEEP THE CHANGE TRANSFER TO ACCT 1187 FOR 03/29/10", 
                  "amount": "-0.75", 
                  "location": {
                    "id": "1", 
                    "name": "Unknown", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 29, 2010", 
                  "new": "True", 
                  "id": "21"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1269838800.0", 
                  "memo": "KRUNG SIAM THAI 03/25 CARD #8321 PURCHASE #24431050085206232600218 MOUNTAIN VIEW, CA", 
                  "amount": "-24.00", 
                  "location": {
                    "id": "1", 
                    "name": "Unknown", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 29, 2010", 
                  "new": "True", 
                  "id": "22"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1269838800.0", 
                  "memo": "Atm Withdrawl", 
                  "amount": "-80.00", 
                  "location": {
                    "id": "3", 
                    "name": "Atm Withdrawl", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 29, 2010", 
                  "new": "True", 
                  "id": "23"
                }, 
                {
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1269838800.0", 
                  "memo": "Caltrain", 
                  "amount": "-5.00", 
                  "location": {
                    "id": "4", 
                    "name": "Caltrain", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 29, 2010", 
                  "new": "True", 
                  "id": "24"
                },
                {
                  "timestamp": "1269835200.0", 
                  "memo": "Caltrain", 
                  "amount": "-5.00", 
                  "location": {
                    "id": "4", 
                    "name": "Caltrain", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "date": "Mar 29, 2010", 
                  "new": "True", 
                  "id": "24", 
                  "coupons": "10"
                }, 
              ]
            }

    """
    r = {}
    u = request.user

    n = 20

    page = int(request.POST.get('page','1'))

    if page < 1:
        page = 1
    start = (page-1)*n

    txns = Transaction.objects.all().order_by('-date')
    if txns.count()%n > 0:
        t_page = txns.count()/n+1
    else:
        t_page = txns.count()/n

    r["count"] = str(txns.count())
    r["page"] = str(page)
    r["total_pages"] = str(t_page)
    r["txns"] = [ t.get_json(me=u) for t in txns[start:start+n]]

    return JSONHttpResponse(r)

@never_cache
@csrf_exempt
@login_required
def get_transaction(request):
    """
        Get details of a transaction

        :url: /m/txn/

        :param POST['txn_id']: transaction id
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            # if transaction id is invalid
            {"id": "-1"}

            # 'people' field won't exist for control group: experiment group 1
            # 'people' field will have list of names if experiment group 2
            # 'people' field will have number like '9' if experiment group 3

            # for sharing variable
            PRIVATE = 0
            FRIENDS = 1
            COMMUNITY = 2
            PUBLIC = 3
            # rating is 0 through 5

            {
              "id": "69", 
              "basic": {
                "location": {
                  "id": "3", 
                  "name": "Transaction Fee",
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                "people": [
                  "Bob", 
                  "Tiger", 
                  "Julie"
                ], 
                "timestamp": "1261893600.0", 
                "memo": "NASHOBA VALLEY SKI ARE WESTFORD", 
                "amount": "-50.00", 
                "date": "Dec 27, 2009", 
                "new": "True", 
                "id": "69"
              }, 
              "details": {
                "category": {
                  "id": 5, 
                  "name": "Drinks"
                }, 
                "rating": "4", 
                "sharing": "2", 
                "last_timestamp": "1270270561.0", 
                "image": "/media/wesabe/heart.png", 
                "detail": "Mailed eBay item", 
                "last_update": "Apr 02, 2010 - 11:56:01 PM", 
                "new": "True", 
                "id": "69"
              }, 

              "splits": [
                {
                  "price": "0.00", 
                  "id": "2", 
                  "name": "Joystick"
                }, 
                {
                  "price": "0.00", 
                  "id": "4", 
                  "name": "Joystick"
                }, 
              ]
            }

            # if there's coupon there's a "coupons" key with number of coupons
            # and "coupon_list" key with list of coupon details
            {
              "id": "24", 
              "basic": {
                "timestamp": "1269835200.0", 
                "memo": "Caltrain", 
                "amount": "-5.0", 
                "location": {
                  "id": "4", 
                  "name": "Caltrain", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                "coupons": "10",
                "coupon_list": [
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "8262159", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 13% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "53", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "6191012", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 16% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "63", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "5669954", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 7% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "65", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "9156268", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 9% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "67", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "4736762", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 24% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "76", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "6965929", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 9% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "83", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "8033937", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 17% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "85", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "9921835", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 17% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "87", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "3125458", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 14% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "92", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  {
                    "location": {
                      "id": "4", 
                      "name": "Caltrain", 
                      "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                    }, 
                    "number": "2909411", 
                    "dealer": "The magistrate dealer", 
                    "content": "This is 6% off coupon", 
                    "expiry_date": "06/30/11", 
                    "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                    "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                    "id": "98", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }
                ], 
                "date": "Mar 29, 2010", 
                "new": "False", 
                "guid": "7bab7f15f8416505655bc3e63f4d1000b5907307080e1e91ca6e3d1e61189761", 
                "id": "24"
              }, 
              "details": {
                "category": {
                  "id": 1, 
                  "name": "None"
                }, 
                "rating": "0", 
                "sharing": "3", 
                "last_timestamp": "1272520119.0", 
                "image": "/media/wesabe/heart.png", 
                "detail": "", 
                "last_update": "Apr 29, 2010 - 01:48:39 AM", 
                "new": "False", 
                "id": "24"
              }, 
              "splits": []
            }

    """

    u = request.user
    txn_id = int(request.POST['txn_id'])
    r = {}
    try:
        txn = Transaction.objects.get(id=txn_id)
        txn.detail.new = False
        txn.detail.save()
        r["id"] = str(txn.id)
        r["basic"] = txn.get_json(level=2, me=u)
        r["details"] = txn.detail.get_json()
        r["splits"] = [i.get_json() for i in txn.splititem_set.all()]
    except Transaction.DoesNotExist:
        r["id"] = "-1"

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def search_transactions(request):
    """
        :url: /m/search/

        :param POST['query']: the term it is searching
        :param POST['filter']: the filter '0' for my transactions
                                '1' for friends
                                '2' for community
                                '3' for public
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            # the people value will be '0' for control group and be
            # '7' if it's in anonymous social group where they see
            # how many others have made similar transaction.
        
            {
              "txns": [
                {
                  "location": {
                    "id": "1", 
                    "name": "Unknown",
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "people": [
                    "Bob", 
                    "Tiger", 
                    "Julie"
                  ], 
                  "timestamp": "1259560800.0", 
                  "memo": "LOTTE FOOD MARKET 11-30 CUSTOMER 8321 PURCHASE #481098 CAMBRIDGE MA", 
                  "amount": "-70.66", 
                  "date": "Nov 30, 2009", 
                  "new": "True", 
                  "id": "21"
                }
              ]
            }

    """
   
    u = request.user
    r = {}
     
    query = request.POST['query']
    filter = int(request.POST['filter'])

    txns = Transaction.objects.filter(memo__txt__icontains=query)

    r['txns'] = [t.get_json(me=u) for t in txns]

    return JSONHttpResponse(output)


@csrf_exempt
@login_required
def profile_transactions(request):
    """
        NOT implemented

        :url: /m/profile/
    """
    return JSONHttpResponse({'result':'1'})
                                 
@csrf_exempt
@login_required
def update_split(request):
    """
        Adds split to a transaction

        :url: /m/split/update/

        :param POST['txn_id']: transaction you are adding details to
        :param POST['split_id']: 0 if new split id
        :param POST['name']: name of split 
        :param POST['price']: price of split 
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::
            
            # if txn is invalid
            {'result':'-1'}
            # the new split id
            {'result':'5'}

    """
    u = request.user
    txn_id = int(request.POST['txn_id'])
    try:
        txn = Transaction.objects.get(id=txn_id)
    except Transaction.DoesNotExist:
        return JSONHttpResponse({'result':'-1'})
    split_id = int(request.POST['split_id'])
    if 'name' in request.POST:
        name = request.POST['name']
    else:
        name = 'Unknown'
    if 'price' in request.POST:
        price = float(request.POST['price'])
    else:
        price = 0

    if split_id == 0:
        d = SplitItem(txn=txn, name=name, price=price)
        d.save()
    else:
        d = SplitItem.objects.get(id=split_id)
        d.name = name
        d.price = price
        d.save()

    return JSONHttpResponse({'result':str(d.id)})

@csrf_exempt
@login_required
def delete_split(request):
    """
        Remove split item of a transaction
        
        :url: /m/split/delete/

        :param POST['split_id']: ID of split item that needs to be removed
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        :: 

            # if split item does not exist
            {'result': '-1'}
            # deleted split item id
            {'result': '5'}
    """
       
    r = {}
    split_id = request.POST['split_id']
    try:
        d = SplitItem.objects.get(id=int(split_id))
        r["result"] = str(d.id)
        d.delete()
    except SplitItem.DoesNotExist:
        r["result"] = "-1"
    return JSONHttpResponse(r)


@csrf_exempt
@login_required
def list_categories(request):
    """
        List predefined categories

        :url: /m/categories/

        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            # if empty
            {'result': []}
            # if there are predefined list of categories
            {'result': [
                        {'id':'5', 'name': 'Fruit'}, 
                        {'id':'6', 'name': 'Dinner'},
                        {'id':'7', 'name': 'Appliance'}
                       ]
            }
    """

    l = SpendingCategory.objects.all()
    categories = [ c.get_json() for c in l]

    return JSONHttpResponse( {'result': categories} )


@csrf_exempt
@login_required
def category_add(request):
    """
        Add category, save who added the category

        :url: /m/category/add/

        :param POST['name']: name of category
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            # i is a number, the id of the new category
            {'result': 'i'} 
            # if category already exists
            {'result': '-1'}
    """

    r = {}
    u = request.user
    category = request.POST["name"]
    new_cat, created = SpendingCategory.objects.get_or_create(name=category)
    if created: 
        l = LogCategoryCreation(category=new_cat, user=u)
        l.save()
        r["result"] = str(new_cat.id)
    else:    
        r["result"] = "-1"
    return JSONHttpResponse(r) 

@csrf_exempt
@login_required
def update_detail(request):
    """
        Updates detail of a transaction

        :url: /m/txn/detail/

        The following parameter is required:

        :param POST["txn_id"]: transaction id you are updating

        The following parameters are optional:

        :param POST["location"]: location id you are updating
        :param POST["detail"]: detail comment you are updating
        :param POST["rating"]: rating you are updating
        :param POST["sharing"]: sharing you are updating
        :param POST["image"]: image file you are updating (NOT supported yet)
        :param POST["category"]: category id you are updating
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            # if successful it returns the txn detail id
            # (this is different from txn_id)
            {'result':'5'}
    
    """

    txn = Transaction.objects.get(id=int(request.POST['txn_id']))
    d = txn.detail
   
    if 'location' in request.POST:
        txn.memo.location = Location.objects.get(id=int(request.POST['location']))
        txn.memo.save()
    if 'detail' in request.POST:
        d.detail = request.POST['detail']
    if 'rating' in request.POST:
        d.rating = int(request.POST['rating'])
    if 'sharing' in request.POST:
        d.sharing = int(request.POST['sharing'])
    if 'category' in request.POST:
        d.category = SpendingCategory.objects.get(id=int(request.POST['category']))

    d.save()

    return JSONHttpResponse({'result':str(d.id)})

@csrf_exempt
@login_required
def list_locations(request):
    """
        Get list of locations

        :url: /m/locations/

        :param POST['page']: page number starting from 1
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::
            
            # if empty
            {'result': []}
            # if there are predefined list of categories

            {
              "total": 11, 
              "result": [
                {
                  "id": "1", 
                  "name": "Unknown", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "2", 
                  "name": "ATM Withdrawal", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "3", 
                  "name": "Atm Withdrawl", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "4", 
                  "name": "Caltrain", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "5", 
                  "name": "Ti Couz", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "6", 
                  "name": "Finance Charge", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "7", 
                  "name": "Exxonmobil", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "8", 
                  "name": "Hostway", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "9", 
                  "name": "Credit Card Payment", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "id": "10", 
                  "name": "Amazon.com", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }
              ]
            }


    """


    r = {}
    # filter by user
    u = request.user

    per_page = 10

    page = int(request.POST['page'])
    if page < 1:
        page = 1

    start = (page-1)*per_page

    locations = Location.objects.all()
    r["total"] = locations.count()
    r["result"] = [l.get_json() for l in locations[start:start+per_page]]

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def show_coupons(request):
    """
        Shows coupons for certain location

        :url: /m/coupons/for/

        :param POST['loc_id']: Location ID
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            # if no coupons
            {'result':[]}

            # else

            {
              "result": [
                {
                  "location": {
                    "id": "6", 
                    "name": "Finance Charge", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "number": "3008839", 
                  "dealer": "The magistrate dealer", 
                  "content": "This is 23% off coupon", 
                  "expiry_date": "06/30/11", 
                  "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                  "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                  "id": "1", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "location": {
                    "id": "6", 
                    "name": "Finance Charge", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "number": "4099143", 
                  "dealer": "The magistrate dealer", 
                  "content": "This is 10% off coupon", 
                  "expiry_date": "06/30/11", 
                  "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                  "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                  "id": "2", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }, 
                {
                  "location": {
                    "id": "6", 
                    "name": "Finance Charge", 
                    "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                  }, 
                  "number": "9176602", 
                  "dealer": "The magistrate dealer", 
                  "content": "This is 7% off coupon", 
                  "expiry_date": "06/30/11", 
                  "details": "If you bring the coupon to the store, it can be used to get a discount at the point of sale.  Restriction applies to certain brands.", 
                  "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
                  "id": "3", 
                  "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png"
                }
              ]
            }

    """
    r = {}
    # TODO: filter by user
    u = request.user

    offer_loc = Location.objects.get(id=request.POST['loc_id'])

    coupons = Coupon.objects.filter(location=offer_loc)
    r["result"] = [c.get_json() for c in coupons[:3]] 

    return JSONHttpResponse(r)
    
@csrf_exempt
@login_required
def show_location(request):
    """
        Shows a specific location information 

        :url: /m/location/

        :param POST['loc_id']: Location ID
        :param POST['lat']: latitude 
        :param POST['lon']: longitude 
        
        :rtype: JSON

        ::

            # if not exist
            {"result": "-1"}

            # if exist
            {
              "name": "Le's", 
              "icon": "http://mealtime.mit.edu/media/techcash/default_icon.png",
              "longitude": "-71.094074", 
              "phone": "206-818-3624", 
              "address": null, 
              "latitude": "42.373193", 
              "banner": "http://mealtime.mit.edu/media/techcash/restaurant_banner.png", 
              "id": "5", 
              "description": ""
            }

    """
    r = {}
    u = request.user

    # TODO: label location with social information

    try:
        loc = Location.objects.get(id=request.POST['loc_id'])
        r = loc.get_json(2)
    except Location.DoesNotExist:
        r["result"] = "-1"

    return JSONHttpResponse(r)

