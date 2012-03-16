from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache

from wesabe import AccountParser, TransactionParser
from forms import WesabeLoginForm, WeatherForm
from common.helpers import JSONHttpResponse, JSHttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from common.models import Friends 
from finance.models import WesabeAccount, WesabeTransaction, LogCategoryCreation, SplitItem, SpendingCategory, WesabeLocation, Coupon
    
import xml.parsers.expat
import platform
import base64
import httplib, urllib
import random
from django.conf import settings
from datetime import datetime

logger = settings.LOGGER

@csrf_exempt
@login_required
def load_data(request):
    """
        Loads Wesabe data given email and password
        
        :url: /wesabe/load/
        
        :param POST['email']:
        :param POST['password']:
    
        :rtype: JSON

        ::

            # successful loading
            {'result':'1'}
            # not a valid form
            {'result':'0'}
            # need to be POST
            {'result':'-1'}
        
    """
        
    # need to check if user has been authenticated
    # if request.user.is_authenticated():
    if request.method == 'POST':
        u = request.user
        form = WesabeLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']


            client_id      = "SocialSaver"    # Change this to the name of your application
            client_version = "1.0"              # Give your application a version number
            system_name    = platform.system()
            system_release = platform.release()
            api_version    = "1.0.0"            # Document which API version you're using
            
            user_agent     = "%s/%s (%s %s) Wesabe-API/%s" % \
                     (client_id, client_version, system_name, system_release, 
                     api_version)
        
    
            credentials = base64.encodestring('%s:%s' % (username, password))[:-1]
    
            header = {"Accept": "application/xml", 
                                     "User-Agent": user_agent, 
                                     "Authorization" : "Basic %s" % credentials}
    
            h = httplib.HTTPSConnection("www.wesabe.com")
            h.request('POST', '/accounts.xml', headers=header)
            r = h.getresponse()
    
            response = r.read()
            logger.debug("finance.views.load_data: "+response)
            if response.find('Wrong') > -1:
                return JSHttpResponse({'result':'-2', 'error': response}) 

    
            p = xml.parsers.expat.ParserCreate()
    
            axml = AccountParser(u.otnuser)
    
            p.StartElementHandler = axml.start_element
            p.EndElementHandler = axml.end_element
            p.CharacterDataHandler = axml.char_data
            
            # save to the DB
            try:
                p.Parse(response)
            except xml.parsers.expat.ExpatError:
                return JSHttpResponse({'result':'-2', 'error': 'Invalid XML, possibly password is wrong'})
               
            for g in axml.accounts:
                account = WesabeAccount.objects.get(guid=g)
                h.request('POST', '/accounts/%s.xml'%g, headers=header)
                #h.request('POST', '/accounts/%s.xml?page=2'%g, headers=header)
                # check newest-txaction char to see if it's same as before
                # that means it's the last page
                r = h.getresponse()
                response = r.read()
                logger.debug("finance.views.transactions: "+response)

                p = xml.parsers.expat.ParserCreate()

                txml = TransactionParser(account)
                p.StartElementHandler = txml.start_element
                p.EndElementHandler = txml.end_element
                p.CharacterDataHandler = txml.char_data
                p.Parse(response)
                        
            h.close()
            return JSONHttpResponse({'result':'1'})
        else:
            return JSONHttpResponse({'result':'0', 'error': form.errors})
    return JSONHttpResponse({'result':'-1', 'error':'Need to POST'})     

@csrf_exempt
@login_required
def ajax_load(request):
    """
        Loads Wesabe data given email and password
        
        :url: /wesabe/ajax/load/
        
        :param POST['email']:
        :param POST['password']:
    
        :rtype: JSON

        ::

            # successful loading
            {'result':'1'}
            # not a valid form
            {'result':'0'}
            # need to be POST
            {'result':'-1'}
        
    """
        
    # need to check if user has been authenticated
    # if request.user.is_authenticated():
    if request.method == 'POST':
        u = request.user
        form = WesabeLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']


            client_id      = "SocialSaver"    # Change this to the name of your application
            client_version = "1.0"              # Give your application a version number
            system_name    = platform.system()
            system_release = platform.release()
            api_version    = "1.0.0"            # Document which API version you're using
            
            user_agent     = "%s/%s (%s %s) Wesabe-API/%s" % \
                     (client_id, client_version, system_name, system_release, 
                     api_version)
        
    
            credentials = base64.encodestring('%s:%s' % (username, password))[:-1]
    
            header = {"Accept": "application/xml", 
                                     "User-Agent": user_agent, 
                                     "Authorization" : "Basic %s" % credentials}
    
            h = httplib.HTTPSConnection("www.wesabe.com")
            h.request('POST', '/accounts.xml', headers=header)
            r = h.getresponse()
    
            response = r.read()
            #print response

            if response.find('Wrong') > -1:
                return JSHttpResponse({'result':'-2', 'error': response}) 

            p = xml.parsers.expat.ParserCreate()
    
            axml = AccountParser(u.otnuser)
    
            p.StartElementHandler = axml.start_element
            p.EndElementHandler = axml.end_element
            p.CharacterDataHandler = axml.char_data
            
            # save to the DB
            try:
                p.Parse(response)
            except xml.parsers.expat.ExpatError:
                return JSHttpResponse({'result':'-2', 'error': 'Invalid XML, possibly password is wrong'})
            
               
            for g in axml.accounts:
                # for each account
                latest = '000'
                last_page = False 
                page = 1
                account = WesabeAccount.objects.get(guid=g)
                while not last_page: 
                    #h.request('POST', '/accounts/%s.xml'%g, headers=header)
                    h.request('POST', '/accounts/%s.xml?page=%d'%(g,page), headers=header)
                    r = h.getresponse()
                    response = r.read()
                    #print "Page: %d"%page 
                    #print response

                    p = xml.parsers.expat.ParserCreate()

                    txml = TransactionParser(account)
                    p.StartElementHandler = txml.start_element
                    p.EndElementHandler = txml.end_element
                    p.CharacterDataHandler = txml.char_data
                    p.Parse(response)

                    # check newest-txaction char to see if it's same as before
                    # that means it's the last page
                    logger.debug("account: %s, latest: %s"%(g, txml.newest_date))
                    if txml.newest_date == "":
                        last_page = True
                    elif latest != txml.newest_date:
                        if page == 1:
                            latest = txml.newest_date
                        page += 1
                    else:
                        last_page = True    
                        
            h.close()
            return JSHttpResponse({'result':'1'})
        else:
            return JSHttpResponse({'result':'0', 'error': form.errors})
    return JSHttpResponse({'result':'-1', 'error':'Need to POST'})


@csrf_exempt
@login_required
def show_transactions(request, page=0):
    """
        Show transactions on the Web site (not for mobile)

        :url: /wesabe/txns/(?P<page>\d+)/

    """
    otnuser = request.user
    user_facebook = otnuser.facebook_profile
    user_friend = Friends.objects.get(facebook_id = user_facebook.facebook_id)
    user_accounts = WesabeAccount.objects.filter(user=otnuser)
    transactions = WesabeTransaction.objects.filter(account__in = user_accounts).order_by('-date')

    paginator = Paginator(transactions, 30) # 30 transactions per page
    friends_list = random.sample(user_friend.friends.all(),10)

    try:
        page = int(page)
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    # If page is empty or invalid, just go to the last one.
    try:
        transactions = paginator.page(page)
    except (EmptyPage, InvalidPage):
        transactions = paginator.page(paginator.num_pages)
        
    return render_to_response(
        "finance/wesabe.html",
        {
        'fbuser': user_facebook,
        'friends_list': friends_list,
        'transactions': transactions,
        },
        context_instance=RequestContext(request)
    )

@csrf_exempt
@login_required
def get_feeds(request):
    """
        Get the feeds of other people

        :url: /wesabe/feeds/

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

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def all_coupons(request):
    """
        Get list of all coupons

        :url: /wesabe/coupons/all/

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

        :url: /wesabe/coupons/filter/

        :param POST['query']: search query for coupons
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::


    """
    r = {}
    u = request.user

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def list_transactions(request):
    """
        Mobile: Get the transactions of the user

        :url: /wesabe/m/txns/

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

    txns = WesabeTransaction.objects.all().order_by('-date')
    if txns.count()%n > 0:
        t_page = txns.count()/n+1
    else:
        t_page = txns.count()/n

    r["count"] = str(txns.count())
    r["page"] = str(page)
    r["total_pages"] = str(t_page)
    r["result"] = [ t.get_json(me=u) for t in txns[start:start+n]]

    return JSONHttpResponse(r)

@never_cache
@csrf_exempt
@login_required
def get_transaction(request):
    """
        Get details of a transaction

        :url: /wesabe/txn/

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
        txn = WesabeTransaction.objects.get(id=txn_id)
        txn.detail.new = False
        txn.detail.save()
        r["id"] = str(txn.id)
        r["basic"] = txn.get_json(level=2, me=u)
        r["details"] = txn.detail.get_json()
        r["splits"] = [i.get_json() for i in txn.splititem_set.all()]
    except WesabeTransaction.DoesNotExist:
        r["id"] = "-1"

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def search_transactions(request):
    """
        :url: /wesabe/search/

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
              "result": [
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
    output = {}
     
    query = request.POST['query']
    filter = int(request.POST['filter'])

    txns = WesabeTransaction.objects.filter(memo__txt__icontains=query)

    output['result'] = [t.get_json(me=u) for t in txns]

    return JSONHttpResponse(output)

@csrf_exempt
@login_required
def remove_transactions(request):
    """
        NOT implemented

        :url: /wesabe/remove/
    """
    return JSONHttpResponse({'result':'-1'})

@csrf_exempt
@login_required
def profile_transactions(request):
    """
        NOT implemented

        :url: /wesabe/profile/
    """
    return JSONHttpResponse({'result':'1'})
                                 
@csrf_exempt
@login_required
def add_split(request):
    """
        Adds split to a transaction

        :url: /wesabe/split/add/

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
        txn = WesabeTransaction.objects.get(id=txn_id)
    except WesabeTransaction.DoesNotExist:
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
        
        :url: /wesabe/split/delete/

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

        :url: /wesabe/categories/

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

        :url: /wesabe/category/add/

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

        :url: /wesabe/txn/detail/

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

    txn = WesabeTransaction.objects.get(id=int(request.POST['txn_id']))
    d = txn.detail
   
    if 'location' in request.POST:
        txn.memo.location = WesabeLocation.objects.get(id=int(request.POST['location']))
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

        :url: /wesabe/locations/

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

    locations = WesabeLocation.objects.all()
    r["total"] = locations.count()
    r["result"] = [l.get_json() for l in locations[start:start+per_page]]

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def show_coupons(request):
    """
        Shows coupons for certain location

        :url: /wesabe/coupons/

        :param POST['loc_id']: WesabeLocation ID
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

    offer_loc = WesabeLocation.objects.get(id=request.POST['loc_id'])

    coupons = Coupon.objects.filter(location=offer_loc)
    r["result"] = [c.get_json() for c in coupons[:3]] 

    return JSONHttpResponse(r)
    
@csrf_exempt
@login_required
def show_location(request):
    """
        Shows a specific location information 

        :url: /wesabe/location/

        :param POST['loc_id']: WesabeLocation ID
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
        loc = WesabeLocation.objects.get(id=request.POST['loc_id'])
        r = loc.get_json(2)
    except WesabeLocation.DoesNotExist:
        r["result"] = "-1"

    return JSONHttpResponse(r)

@csrf_exempt
def post_weather(request):
    """
        Posts weather information every hour

        :url: /wesabe/post/weather/

        :param: series of parameters that map to the Weather model

        :rtype: JSON

        ::

            # if successful
            {'result': '1'}

            # if not successful
            {'result': '-1'}
    """

    r = {}
    if request.method == 'POST':
        password = request.POST.get('password', None)
        if password is not None and password == '134744A8T':
            form = WeatherForm(request.POST)
            if form.is_valid():
                w = form.save(commit=False)
                w.update_time = datetime.strptime(request.POST['update_time'][:-4], "%a, %d %b %Y %I:%M %p")
                w.sunrise = datetime.strptime(request.POST['sunrise'], "%I:%M %p")
                w.sunset = datetime.strptime(request.POST['sunset'], "%I:%M %p")
                w.save()
                r['result'] = '1'
                return JSONHttpResponse(r)
            else:
                r['result'] = '-2'
                r['errors'] = form.errors
                return JSONHttpResponse(r)
        else:
            r['result'] = '-3'
            r['password'] = password
            return JSONHttpResponse(r)

    
    # Not authentic request from cron job or not POST
    r['result'] = '-1'
    return JSONHttpResponse(r)

"""
    TODO:
        Need a add/update location method
"""
