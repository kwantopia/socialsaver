# Create your views here.
import time
import hashlib, random
from common.helpers import JSONHttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.template import RequestContext
from facebookconnect.models import FacebookProfile
from common.models import OTNUser, Location, Friends, Featured 
from mobile.models import Event, CallEvent, FeaturedEvent, FeedEvent
from mobile.forms import IPhoneRegisterForm, UpdateTransactionForm
from iphonepush.models import iPhone, sendMessageToPhoneGroup
from techcash.models import TechCashTransaction, Receipt, TechCashBalance
from survey.models import Survey, SurveyStatus, BasicFoodSurvey, EatingCompanySurvey, EatingOutSurvey, DigitalReceiptSurvey
from survey.forms import BasicFoodSurveyForm, EatingCompanySurveyForm, EatingOutSurveyForm, DigitalReceiptSurveyForm
from django.conf import settings
import operator, uuid
from django.db.models import Count, Sum, Q
from datetime import datetime, date, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.decorators import login_required

logger = settings.LOGGER

@login_required
@csrf_exempt
def register(request):
    """
        Registers the token for iPhone

        :url: /m/register/

        :param POST['udid']: the token

        :rtype: JSON

        ::

            # successful
            {'result':'1'}
            # failed registration
            {'result':'-1', 'form_errors':form.errors}
            # if not logged in
            returns home page of MealTime

    """
    if request.method == 'POST':
        form = IPhoneRegisterForm( request.POST )
        if form.is_valid():
            p, created = iPhone.objects.get_or_create(user=request.user)
            p.udid = form.cleaned_data['udid']
            if len(p.udid) != 64:
                return JSONHttpResponse({'result': '-1', 'form_errors':form.errors})
            p.save()
            return JSONHttpResponse({'result': '1'})
        else:
            return JSONHttpResponse({'result': '-1', 'form_errors':form.errors})
    else:
        form = IPhoneRegisterForm()
        # only used when GET request is made through web page
        return render_to_response( 'registerform.html', { 'form': form, } )

def feed_compose(t, exp=3, android=False):
    """
        Internal method

        :param t: contains "num_txns", "location" (id of location)
    """
    if exp == 3:
        people_str = "people"
    if exp == 4:
        people_str = "friends"

    location_name = Location.objects.get(id=t["location"]).name
    num_txns = t["num_txns"]

    if android:
        feed = {} 
        feed_str = "%d %s visited <font color='%s'><b>%s</b></font>"%(num_txns, people_str, settings.FEED_COLOR, location_name)
        feed['location'] = t["location"]
        feed['str'] = feed_str
    else:
        feed_str = "%d %s visited <a href='tt://location/%d'>%s</a>"%(num_txns, people_str, t["location"], location_name)
        feed = feed_str
    return feed

def feed_retrieve(request, page, android=False):
    """
        Internal method for outputting feed
    """
    u = request.user
    experiment = u.otnuser.experiment.id
    
    data = {}
    per_page = settings.FEEDS_PER_PAGE 

    # last 36 hours
    past_hours = 12 
    # take out days from timedelta for deployment
    past_days = 700
    d = datetime.now() - timedelta(days=past_days, hours=past_hours)

    page = int(page)
    if page < 1:
        page = 1

    data["news"] = "This is a noteworthy news"
    if experiment == 1:
        txns = TechCashTransaction.objects.filter(timestamp__gt=d).order_by("-timestamp")
        data["total_pages"] = txns.count()/per_page if txns.count()%per_page == 0 else txns.count()/per_page+1
        if page > data["total_pages"]:
            page = data["total_pages"]
        data["feeds"] = [t.feed(experiment, android) for t in txns[per_page*(page-1):per_page*page]]
    elif experiment == 2:
        active_ids = FacebookProfile.objects.all().values('facebook_id')
        user_friend_ids = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id).friends.filter(facebook_id__in=active_ids).values('facebook_id')

        txns = TechCashTransaction.objects.filter(timestamp__gt=d, user__facebook_profile__facebook_id__in=user_friend_ids).order_by("-timestamp")

        data["total_pages"] = txns.count()/per_page if txns.count()%per_page == 0 else txns.count()/per_page+1

        if page > data["total_pages"]:
            if data["total_pages"] > 0:
                page = data["total_pages"]
        data["feeds"] = [t.feed(experiment, android) for t in txns[per_page*(page-1):per_page*page]]
    elif experiment == 3:
        txns = TechCashTransaction.objects.values("location").annotate(num_txns=Count("location")).filter(timestamp__gt=d)
        data["total_pages"] = txns.count()/per_page if txns.count()%per_page == 0 else txns.count()/per_page+1
        if page > data["total_pages"]:
            page = data["total_pages"]
        data["feeds"] = [feed_compose(t, experiment, android) for t in txns[per_page*(page-1):per_page*page]]
    elif experiment == 4:
        active_ids = FacebookProfile.objects.all().values('facebook_id')
        user_friend_ids = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id).friends.filter(facebook_id__in=active_ids).values('facebook_id')

        txns = TechCashTransaction.objects.filter(timestamp__gt=d, user__facebook_profile__facebook_id__in=user_friend_ids).values("location").annotate(num_txns=Count("location"))
        data["total_pages"] = txns.count()/per_page if txns.count()%per_page == 0 else txns.count()/per_page+1
        if page > data["total_pages"]:
            page = data["total_pages"]
        data["feeds"] = [feed_compose(t, experiment, android) for t in txns[per_page*(page-1):per_page*page]]
    
    data["page"] = page


    return data

@csrf_exempt
@login_required
def feeds(request, page):
    """
        Returns 20 most recent feeds about friends (iPhone)
        Use :meth:`feeds_android` for Android
 
        :url: /m/feeds/(?P<page>\d+)/

        :param page: page number >= 1 
        :param POST['lat']: latitude
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            # for experiment 1
            # show list of locations
            # i.e. New transaction at Anna's Taqueria (time)

            {
              "news": "This is a noteworthy news", 
              "feeds": [
                "Someone visited <a href='tt://location/37'>SAP Payroll Reset</a>", 
                "Someone visited <a href='tt://location/37'>SAP Payroll Reset</a>", 
                "Someone visited <a href='tt://location/329'>Westgate Dryer #22</a>", 
                "Someone visited <a href='tt://location/326'>Westgate Washer #3</a>", 
                "Someone visited <a href='tt://location/316'>Westgate Washer #4</a>"
              ], 
              "total_pages": 426, 
              "page": 2
            }


            # for experiment 2
            # show list of transactions by friends
            {
              "news": "This is a noteworthy news", 
              "feeds": [
                "<a href='tt://user/9'>Michael</a> visited <a href='tt://location/42'>June's Work Station</a>", 
                "<a href='tt://user/7'>Calvin</a> visited <a href='tt://location/11'>Laverde's Market</a>", 
                "<a href='tt://user/7'>Calvin</a> visited <a href='tt://location/51'>Burton Dryer #12</a>", 
                "<a href='tt://user/7'>Calvin</a> visited <a href='tt://location/45'>Burton Dryer #10</a>", 
                "<a href='tt://user/7'>Calvin</a> visited <a href='tt://location/137'>Burton Dryer #11</a>"
              ], 
              "total_pages": 15, 
              "page": 2
            }


            # for experiment 3
            # show list of locations with number of people last hour
            {
              "news": "This is a noteworthy news", 
              "feeds": [
                "64 people visited <a href='tt://location/2'>Anna's Taqueria</a>", 
                "1 people visited <a href='tt://location/3'>Au Bon Pain Main St #2</a>", 
                "25 people visited <a href='tt://location/4'>Shinkansen Japan</a>", 
                "33 people visited <a href='tt://location/5'>Sepal</a>", 
                "1 people visited <a href='tt://location/6'>Tang Washer #3</a>"
              ], 
              "total_pages": 45, 
              "page": 1
            }


            # for experiment 4
            # show list of transactions with number of friends
            {
              "news": "This is a noteworthy news", 
              "feeds": [
                "1 friends visited <a href='tt://location/326'>Westgate Washer #3</a>", 
                "2 friends visited <a href='tt://location/54'>Burton Washer#5</a>", 
                "1 friends visited <a href='tt://location/316'>Westgate Washer #4</a>", 
                "1 friends visited <a href='tt://location/175'>New House Washer #1</a>", 
                "1 friends visited <a href='tt://location/49'>Burton Washer #8</a>"
              ], 
              "total_pages": 7, 
              "page": 2
            }



    """

    data = feed_retrieve( request, page )


    return JSONHttpResponse(data)

@csrf_exempt
@login_required
def feeds_android(request, page):
    """
        Returns 20 most recent feeds about friends
    
        :url: /m/feeds/a/(?P<page>\d+)/

        :param page: page number >= 1 
        :param POST['lat']: latitude
        :param POST['lon']: longitude 

        :rtype: JSON

        ::

            # for experiment 1
            # show list of locations
            # i.e. New transaction at Anna's Taqueria (time)
            {
              "news": "This is a noteworthy news", 
              "feeds": [
                {
                  "feed_str": "Someone visited <font color='#127524'><b>SAP Payroll Reset</b></font>", 
                  "location": 37
                }, 
                {
                  "feed_str": "Someone visited <font color='#127524'><b>SAP Payroll Reset</b></font>", 
                  "location": 37
                }, 
                {
                  "feed_str": "Someone visited <font color='#127524'><b>Westgate Dryer #22</b></font>", 
                  "location": 329
                }, 
                {
                  "feed_str": "Someone visited <font color='#127524'><b>Westgate Washer #3</b></font>", 
                  "location": 326
                }, 
                {
                  "feed_str": "Someone visited <font color='#127524'><b>Westgate Washer #4</b></font>", 
                  "location": 316
                }
              ], 
              "total_pages": 426, 
              "page": 2
            }


            # for experiment 2
            # show list of transactions by friends

            {
              "news": "This is a noteworthy news", 
              "feeds": [
                {
                  "feed_str": "<font color='#127524'><b>Dawei</b></font> visited <font color='#127524'><b>Westgate Dryer #22</b></font>", 
                  "location": 329, 
                  "actor": 8
                }, 
                {
                  "feed_str": "<font color='#127524'><b>Dawei</b></font> visited <font color='#127524'><b>Westgate Washer #3</b></font>", 
                  "location": 326, 
                  "actor": 8
                }, 
                {
                  "feed_str": "<font color='#127524'><b>Dawei</b></font> visited <font color='#127524'><b>Westgate Washer #4</b></font>", 
                  "location": 316, 
                  "actor": 8
                }, 
                {
                  "feed_str": "<font color='#127524'><b>Dawei</b></font> visited <font color='#127524'><b>Subway #1</b></font>", 
                  "location": 58, 
                  "actor": 8
                }, 
                {
                  "feed_str": "<font color='#127524'><b>Yod</b></font> visited <font color='#127524'><b>June's Work Station</b></font>", 
                  "location": 42, 
                  "actor": 4
                }
              ], 
              "total_pages": 15, 
              "page": 1
            }

            # for experiment 3
            # show list of locations with number of people last hour
            {
              "news": "This is a noteworthy news", 
              "feeds": [
                {
                  "location": 2, 
                  "str": "64 people visited <font color='#127524'><b>Anna's Taqueria</b></font>"
                }, 
                {
                  "location": 3, 
                  "str": "1 people visited <font color='#127524'><b>Au Bon Pain Main St #2</b></font>"
                }, 
                {
                  "location": 4, 
                  "str": "25 people visited <font color='#127524'><b>Shinkansen Japan</b></font>"
                }, 
                {
                  "location": 5, 
                  "str": "33 people visited <font color='#127524'><b>Sepal</b></font>"
                }, 
                {
                  "location": 6, 
                  "str": "1 people visited <font color='#127524'><b>Tang Washer #3</b></font>"
                }
              ], 
              "total_pages": 45, 
              "page": 1
            }


            # for experiment 4
            # show list of transactions with number of friends
            {
              "news": "This is a noteworthy news", 
              "feeds": [
                {
                  "location": 326, 
                  "str": "1 friends visited <font color='#127524'><b>Westgate Washer #3</b></font>"
                }, 
                {
                  "location": 54, 
                  "str": "2 friends visited <font color='#127524'><b>Burton Washer#5</b></font>"
                }, 
                {
                  "location": 316, 
                  "str": "1 friends visited <font color='#127524'><b>Westgate Washer #4</b></font>"
                }, 
                {
                  "location": 175, 
                  "str": "1 friends visited <font color='#127524'><b>New House Washer #1</b></font>"
                }, 
                {
                  "location": 49, 
                  "str": "1 friends visited <font color='#127524'><b>Burton Washer #8</b></font>"
                }
              ], 
              "total_pages": 7, 
              "page": 2
            }


    """

    data = feed_retrieve(request, page, True)

    return JSONHttpResponse(data)


@csrf_exempt
@login_required
def activity(request):
    """
        Returns the recent activity level at a certain location and
        TODO: weekly average activity levels at this time

        :url: /m/activity/

        :param POST['location_id']: ID of the location (Location table)
        :param POST['lat']: latitude where it is accessed
        :param POST['lon']: longitude where it is accessed

        :rtype: JSON
        ::

            # you can just load the url as an image
            # the current size is 300x140

            {
              "graph": "http://chart.apis.google.com/chart?chs=300x140&cht=lxy&chco=FF0000,00FF00&chd=t:5,15,30,45,60,90|0,0,0,0,0,0&chxt=x,x,y,y&chxr=0,0,90,15|2,0,100&chxl=1:|minutes|3:|people&chxp=1,50|3,50", 
              "traffic": [
                "5 mins ago: 0 people visited", 
                "15 mins ago: 0 people visited", 
                "30 mins ago: 0 people visited", 
                "45 mins ago: 0 people visited", 
                "60 mins ago: 0 people visited", 
                "90 mins ago: 0 people visited"
              ], 
              "location": {
                "id": "5", 
                "name": "Sepal"
              }
            }

    """

    data = {}
    u = request.user
    d = datetime.now() - timedelta(days=100)

    data["traffic"] = []
    location_id = request.POST['location_id']

    data["location"] = Location.objects.get(id=location_id).get_json(level=0)
    t = [0, 5, 15, 30, 45, 60, 90]
    mins = ""
    people = ""
    for i in xrange(0, 6): 
        dfrom = d - timedelta(minutes=t[i+1])
        dto = d - timedelta(minutes=t[i])
        txns = TechCashTransaction.objects.filter(location=location_id, timestamp__gt=dfrom, timestamp__lt=dto)
        data["traffic"].append("%d mins ago: %d people visited"%(t[i+1], txns.count()))
        mins += str(t[i+1]) + ","
        people += str(txns.count()) + ","
        
    # generate a google graph
    data["graph"] = "http://chart.apis.google.com/chart?chs=300x140&cht=lxy&chco=FF0000,00FF00&chd=t:%s|%s&chxt=x,x,y,y&chxr=0,0,90,15|2,0,100&chxl=1:|minutes|3:|people&chxp=1,50|3,50"%(mins[:-1], people[:-1])
     
    # TODO: during each day for this location
        
    return JSONHttpResponse(data)

@csrf_exempt
@login_required
def menu(request):
    """
        Returns the top menu of a location if the location is a
        valid eating place


        :param POST['location_id']:
        :param POST['lat']:
        :param POST['lon']:
    """

    data = {}
    u = request.user

    return JSONHttpResponse(data)

@csrf_exempt
@login_required
def menu_category(request):
    """
        Returns the top menu of a location if the location is a
        valid eating place

        :url: /m/menu/category/

        :param POST['location_id']: The location id
        :param POST['category_id']: The category id
        :param POST['thumbs']: 1 for thumbs up, -1 for thumbs down,
                    thumbs up or down indicating quick review or recommendation
        :param POST['lat']:
        :param POST['lon']:

    """

    data = {}
    u = request.user


    return JSONHttpResponse(data)

@csrf_exempt
@login_required
def menu_dish(request):
    """
        Returns the top menu of a location if the location is a
        valid eating place

        :url: /m/menu/dish/

        :param POST['location_id']: The location id
        :param POST['category_id']: The category id
        :param POST['thumbs']: 1 for thumbs up, -1 for thumbs down,
                    thumbs up or down indicating quick review or recommendation
        :param POST['lat']:
        :param POST['lon']:

    """

    data = {}
    u = request.user


    return JSONHttpResponse(data)


@csrf_exempt
@login_required
def menu_dish_rate(request):
    """
        Returns the top menu of a location if the location is a
        valid eating place

        :url: /m/menu/dish/rate/

        :param POST['dish_id']: The dish id
        :param POST['thumbs']: 1 for thumbs up, -1 for thumbs down,
                    thumbs up or down indicating quick review or recommendation
        :param POST['lat']:
        :param POST['lon']:

    """

    data = {}
    u = request.user


    return JSONHttpResponse(data)


@csrf_exempt
@login_required
def receipts(request, last):
    """
        Return latest 10 receipts

        :url: /m/receipts/(?P<last>\d+)/

        :param last: 0 if getting the first 10 receipts, or transaction ID to filter the next 10 recent transactions 

        :rtype: JSON

        ::

            # if user is not authenticated
            output = {}

            # if there are no transactions yet
            {'balance': {'name': 'John Doe',
                        'balance': '0.00',
                        'timestamp': '1266640560.40214'
                        },
                'more': '0',
                'receipts': []
            }
            
            # if user has data
            {'balance': {'name': 'John Doe',            # name
                        'balance': '55.40',             # total left
                        'timestamp': '2352515151'       # last updated
                        },
             'more': '1',       # 0 if there aren't any more txns
             'receipts':
            [
            
                {"rating": "0", 
                    "sharing": "3", 
                    "detail": "", 
                    "techcash": {"timestamp": "1256940463.0", 
                            "amount": "4.85", 
                            "id": "108", 
                            "location": {"phone": "", 
                                        "image": "http://www.yourgigs.com.au/static/common/images/pin_restaurant2.png", 
                                        "address": "", 
                                        "id": "4", 
                                        "name": "Anna's Taqueria"}
                            }, 
                    "new": "True", 
                    "accompanied": "True", 
                    "id": "108"}, 
                {"rating": "0", 
                    "sharing": "3", 
                    "detail": "", 
                    "techcash": {"timestamp": "1256832428.0", 
                                "amount": "4.85", 
                                "id": "103", 
                                "location": {"phone": "", 
                                            "image": "http://www.yourgigs.com.au/static/common/images/pin_restaurant2.png", 
                                            "address": "", 
                                            "id": "4", 
                                            "name": "Anna's Taqueria"}
                                }, 
                    "new": "True", 
                    "accompanied": "False", 
                    "id": "103"}, 

            ]
            }
    """ 
    total = 10
    
    output = {}
    if request.user.is_authenticated():
        otnuser = request.user
        # for testing 
        #user = User.objects.get(id=2)
        # get total balance
        try:
            bal = TechCashBalance.objects.get(user=otnuser)
            output['balance'] = bal.get_json()
        except TechCashBalance.DoesNotExist:
            output['balance'] = { 
                                'user': otnuser.name,
                                'balance': '0.00',
                                'timestamp': str(time.time())
                                }
            output['more'] = '0'
            output['receipts'] = []
            return JSONHttpResponse(output)

        output['more'] = '0'
        last = int(last)
        if last == 0:
            txns = TechCashTransaction.objects.filter(user=otnuser, location__type=Location.EATERY).order_by('-timestamp')
        else:
            txns = TechCashTransaction.objects.filter(user=otnuser, id__lt=last, location__type=Location.EATERY).order_by('-timestamp')
        if txns.count() > total:
            output['more'] = '1'
        txns = txns[:total]
        receipts = [Receipt.objects.get(txn=transaction) for transaction in txns]

        output['receipts'] = [r.get_json() for r in receipts]
        # log event
        event = Event(user=otnuser, action=Event.RECEIPTS)
        event.save()

    return JSONHttpResponse(output)
    
@csrf_exempt
def receipts_month(request):
    """
        Return aggregate of month's transactions, sorted by total amount

        :url: /m/receipts/month/

        :rtype: JSON

        ::

            # when there are no transactions
            {"user": {"name": "Kwan Hong Lee", 
                         "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5", 
                         "id": "2", 
                         "phone": "617-909-2101", 
                         "experiment": "1", 
                         "email": "kool@mit.edu"
                     }, 
                "places": []
            }

            # when there are transactions
            {'user':
                {'id': str(self.id),
                  'name': self.name,
                  'phone': self.phone,
                  'experiment': str(self.experiment.id),
                  'image': self.image
                 },
            'places':
            [
                {
                "location": {"name": "Subway",
                        "id": "27",
                        "image": "http://lunchtime-dev.media.mit.edu/media/Subway.png",
                        "description": "Very Long!",
                        "phone": "617-234-4500"
                        },
                "amount": "50.75",
                "latest": str(time.time()),
                "count": "5",
                "rating": "2",
                },
                {
                "location": {"name": "Anna's Taqueria",
                        "id": "7",
                        "image": "http://lunchtime-dev.media.mit.edu/media/Annas.png",
                        "description": "Caramba!",
                        "phone": "617-234-1245"
                        },           
                "amount": "70.65",
                "latest": str(time.time()),
                "count": "10",
                "rating": "4"
                }
            ]
            }
    """

    output = {}
    if request.user.is_authenticated():
        # for testing 
        #u = User.objects.get(id=3)
        otnuser = request.user
        output['user'] = otnuser.get_json(level=1)

        # get all the location that the user has been to
        locations = TechCashTransaction.objects.filter(user=otnuser, location__type=Location.EATERY).order_by('location').values('location', 'location__name', 'location__icon').distinct()
        # for each location, need to get the number of transactions and the last
        # time they have been in that location  
        visits = []
        for l in locations:
            txns = TechCashTransaction.objects.filter(user=otnuser, location=l['location']).order_by('-timestamp')
            v = {}
            v['count'] = txns.count()
            v['latest'] = str(time.mktime(txns[0].timestamp.timetuple())) 
            v['amount'] = txns.aggregate(Sum('amount'))['amount__sum']

            # get average rating
            receipts = Receipt.objects.filter(txn__user=otnuser, txn__location=l['location'])
            sum = receipts.aggregate(Sum('rating'))
            #print sum
            count = receipts.count()
            v['rating'] = str(round(sum['rating__sum']/float(count)))
            v['location'] = Location.objects.get(id=l['location']).get_json(level=1)
            visits.append( v )
        # sort by number of visits and change num of visits to string
        # reverse=True so in JSON it is sorted
        visits = sorted(visits, key=operator.itemgetter('amount'), reverse=True)
        map(amount_to_str, visits)
        
        output['places'] = visits

        event = FeedEvent(user=otnuser, experiment=otnuser.experiment.id, 
                        action=FeedEvent.RECEIPTS_MONTH,
                        params=str(output))

    return JSONHttpResponse(output)
  

@csrf_exempt
def check_lunchtime(request):
    """
        Android: Checks if it's lunch time
        
        :url: /m/check/lunchtime/

        :rtype: JSON

        ::

            # if lunch time for friend influence group
            {"result":"1", "time": "00:00:00", "msg":"See where friend's have eaten."}
            # if lunch time for popularity group
            {"result":"1", "time": "00:00:00", "msg":"See what's happening"}
            # if not
            {"result":"-1"}
    """

    r = {"result":"-1", 
        "time": "00:00:00",
        "msg":"It's time for lunch! Want suggestions?"}

    if(request.user.is_authenticated()):
        user = request.user
        transactions = TechCashTransaction.objects.filter(user = user, location__type=Location.EATERY)
        transactions = [transaction for transaction in transactions if transaction.timestamp.hour >= 11 and transaction.timestamp.hour <= 14]
        if(len(transactions) > 0):
            minutes = sum([transaction.timestamp.minute for transaction in transactions]) / len (transactions)
            hours = sum([transaction.timestamp.hour for transaction in transactions]) / len (transactions)
            r = {"result":"1",
                 "time":str(hours) + ":" + str(minutes) + ":00",
                 "msg":"It's time for lunch! Want suggestions?"}


    return JSONHttpResponse(r)

@csrf_exempt
def check_receipt(request):
    """
        Android: Check for new receipt

        :url: /m/check/receipt/

        :rtype: JSON

        ::

            # if receipt, send summary
            {"result":"1",
             "receipts":
             [{
            "id":"24",
            "msg": "$7.68 has been spent at Subway",
            "location": {"name": "Subway",
                    "id": "27",
                    "image": "http://lunchtime-dev.media.mit.edu/media/Subway.png",
                    "description": "Very Long!",
                    "phone": "617-234-4500"
                    },
                "amount": "7.68",
                "timestamp": str(time.time()),
                "rating": "4",
            }]
            }
            # if no receipts
            {"result":"-1"}

            
    """
    r = {"result":"1",
            "receipts": [{"id":"24",
            "msg": "$7.68 has been spent at Subway",
            "location": {"name": "Subway",
                    "id": "27",
                    "image": "http://lunchtime-dev.media.mit.edu/media/Subway.png",
                    "description": "Very Long!",
                    "phone": "617-234-4500"
                    },
                "amount": "7.68",
                "timestamp": str(time.time()),
                "rating": "4",
            }]
        }
    return JSONHttpResponse(r)

@never_cache
@csrf_exempt
def surveys(request):
    """

        Return surveys to the mobile, :data:`expires` is "None" if there is no expiry date
        for the survey

        :url: /m/surveys/

        :rtype: JSON

        ::

            # if user is not authenticated it returns empty survey list
            {}
            # if there are no surveys
            {'surveys': []}
            # else
            {'surveys': [
                {'id': '5',
                    'title': 'Character survey',
                    'description': 'We would like to find the character',
                    'expires': str(time.time()-432000),         # 'None' if there's no expiry time
                    'url': 'http://lunchtime-dev.media.mit.edu/surveys/5/',
                },
                {'id': '10',
                    'title': 'Sleeping time survey',
                    'description': 'How much time do you sleep in a week?',
                    'expires': str(time.time()-864000),
                    'url': 'http://lunchtime-dev.media.mit.edu/surveys/10/',
                }
                ]
            }

    """
    # create a survey status
    output = {}

    if request.user.is_authenticated():
        output['surveys'] = []
        u = request.user
        surveys = Survey.objects.all()
        for s in surveys:
            if s.expires is None or s.expires > datetime.now():
                # create survey status
                query = "%s.objects.get_or_create(survey=s, user=u)"%s.model_name
                logger.debug(query)
                status, created = eval(query)
                if created:
                    status.uuid_token = uuid.uuid4()
                    status.save()
                if not status.completed:
                    output['surveys'].append(s.summary())

        event = Event(user=request.user, action=Event.SURVEYS)
        event.save()

    return JSONHttpResponse(output)

@never_cache
@csrf_exempt
def survey(request, survey_id):
    """
        Returns the survey web page

        :url: /m/survey/(?P<survey_id>\d+)/

        # only when submitting/POSTing form
        :param POST['uuid_token']: the uuid_token of survey
    """
    if request.user.is_authenticated():

        u = request.user
        survey_id = int(survey_id)
        if request.method =='POST':
            try:
                survey_meta = Survey.objects.get(id=survey_id)
            except Survey.DoesNotExist:
                return render_to_response('survey/m/notexist.html',
                        context_instance=RequestContext(request))
            status = eval("%s.objects.get(user=request.user, uuid_token=request.POST['uuid_token'])"%survey_meta.model_name)
            form = eval("%sForm( request.POST, instance=status)"%survey_meta.model_name)
        
            if form.is_valid():
                status.completed = True
                status.complete_date = datetime.now() 
                form.save()

                event = Event(user=request.user, action=Event.SURVEY_COMPLETE, params="{'id':%s, 'uuid':%s}"%(status.id, request.POST['uuid_token']))
                event.save()

                return render_to_response('survey/m/completed.html')
            else:
                return render_to_response('survey/m/basic.html', 
                                            {'form':form,
                                            'survey_id': survey_id,
                                            'uuid_token': status.uuid_token,
                                            'errors':form.errors},
                                            context_instance=RequestContext(request))
        else:
            uuid = ""
            form = None 
            try:
                s = Survey.objects.get(id=survey_id)
                status = eval("%s.objects.get(user=u,survey=s)"%s.model_name)
                form = eval("%sForm()"%s.model_name)
            except Survey.DoesNotExist:
                return render_to_response('survey/m/notexist.html', 
                            context_instance=RequestContext(request))

            return render_to_response('survey/m/basic.html', {'form':form,
                                'survey_id': survey_id,
                                'uuid_token': status.uuid_token},
                                context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")

def keys_to_str( b ):
    """
        Utility function to convert integer to string in a dictionary
        
        for :meth:`friend_trace`
    """
    # converts location id to str
    b['location'] = str(b['location'])
    b['count'] = str(b['count'])
 
def count_to_str( b ):
    """
        Utility function to convert integer to string in a dictionary
        
        for :meth:`location_trace` and :meth:`places` for experiment 2
    """
    b['count'] = str(b['count'])

def amount_to_str( b ):
    """
        Utility function to convert integer to string in a dictionary
        
        for :meth:`receipts_month` 
    """
    b['amount'] = "%.2f"%b['amount']
 
def popularity_to_str( b ):
    """
        Utility function to convert integer to string in a dictionary

        for :meth:`places`
    """
    b['popularity'] = str(b['popularity'])

@csrf_exempt
def friend_trace(request, friend_id):
    """
        Returns aggregated number of visits to different locations
        
        :url: /m/friend/trace/(?P<friend_id>\d+)/

        :rtype: JSON

        ::

            # if user is not authenticated
            output = {}
            # if friend does not exist
            output = {'result':'-1'}

            # else
            {'user':
                {'id': str(self.id),
                  'name': self.name,
                  'phone': self.phone,
                  'experiment': str(self.experiment.id),
                  'image': self.image
                 },
            'places':
                [
                    {'location': '5',
                     'location__name': "Anna's Taqueria",   # note two underscores
                     'location__icon': "url",          # note two underscores
                     'count': '6',                      # number of times they visited
                     'latest': '1256669771.0',          # last time they visited
                    },
                    {'location': '7',
                     'location__name': "Johnny's",
                     'location__icon': "url",          
                     'count': '3',
                     'latest': '1256665771.0',
                    },
                    {'location': '8',
                     'location__name': "Subway", 
                     'location__icon': "url",         
                     'count': '1',
                     'latest': '1256659771.0',
                    }
                ]
            }
                    
 
    """

    output = {}
    if request.user.is_authenticated():
        try:
            friend = OTNUser.objects.get(id=friend_id)
        except OTNUser.DoesNotExist:
            return JSONHttpResponse({'result':'-1'})
        output['user'] = friend.get_json(level=1)
        # get all the location that the user has been to
        locations = TechCashTransaction.objects.filter(user=friend, location__type=Location.EATERY).order_by('location').values('location', 'location__name', 'location__icon').distinct()
        # for each location, need to get the number of transactions and the last
        # time they have been in that location  
        visits = []
        for l in locations:
            txns = TechCashTransaction.objects.filter(user=friend, location=l['location']).order_by('-timestamp')
            v = l
            v['count'] = txns.count()
            v['latest'] = str(time.mktime(txns[0].timestamp.timetuple())) 
            visits.append( v )
        # sort by number of visits and change num of visits to string
        # reverse=True so in JSON it is sorted
        visits = sorted(visits, key=operator.itemgetter('count'), reverse=True)
        map(keys_to_str, visits)
        
        output['places'] = visits

        event = FeedEvent(user=request.user, experiment=request.user.experiment.id, 
                        action=FeedEvent.FRIEND_TRACE,
                        params=str(output))
        event.save()
       
    return JSONHttpResponse(output)
            
@csrf_exempt
def location_trace(request, location_id):
    """
        How many people have been to this restaurant

        :url: /m/location/trace/(?P<location_id>\d+)/

        :param location_id: location to get trace for

        :return: friends who visited the restaurant (location) 

        :rtype: JSON
        
        ::

            # if user is not authenticated
            output = {}

            # else
            output = {
                    "location": {"name": "Subway",
                                "id": "27",
                                "image": "http://lunchtime-dev.media.mit.edu/media/Subway.png",
                                "banner": "http://lunchtime-dev.media.mit.edu/media/Subway.png",
                                "description": "Very Long!",
                                "phone": "617-234-4500",
                                'address': self.address,
                                'latitude': str(self.latitude),
                                'longitude': str(self.longitude),
                                },

                    "people":[
                                {'user': {'id': '58',
                                             'name': 'Yod P',
                                             'phone': '617-929-2341',
                                             'experiment': '2',
                                            "image": "http://lunchtime-dev.media.mit.edu/media/usernull.jpg",
                                        },
                                'latest': str(time.time()-2342111),
                                'count': '15',
                                },
                                {'user': {'id': '158',
                                             'name': 'Ilya V',
                                             'phone': '617-929-2341',
                                             'experiment': '0',
                                            "image": "http://lunchtime-dev.media.mit.edu/media/usernull.jpg",
                                        },
                                'latest': str(time.time()-2346111),
                                'count': '12',
                                },
                                {'user': {'id': '458',
                                             'name': 'Calvin F',
                                             'phone': '617-929-2341',
                                             'experiment': '1',
                                            "image": "http://lunchtime-dev.media.mit.edu/media/usernull.jpg",
                                        },
                                'latest': str(time.time()-2342501),
                                'count': '5',
                                },
                                {'user': {'id': '358',
                                             'name': 'Kwan Lee',
                                             'phone': '617-929-2341',
                                             'experiment': '1',
                                            "image": "http://lunchtime-dev.media.mit.edu/media/usernull.jpg",
                                        },
                                'latest': str(time.time()-2342661),
                                'count': '2',
                                }
                            ]
                    }
 
    """

    output = {}

    if request.user.is_authenticated():
        user = request.user
        # for testing assign a user
        #user = User.objects.get(id=3)
        active_ids = FacebookProfile.objects.all().values('facebook_id')
        user_friend_ids = Friends.objects.get(facebook_id=user.facebook_profile.facebook_id).friends.filter(facebook_id__in=active_ids).values('facebook_id')

        location_id = int(location_id)
        location = Location.objects.get(id=location_id)
        output['location'] = location.get_json(level=2)

        people = []

        friend_txns = TechCashTransaction.objects.filter(location=location, user__facebook_profile__facebook_id__in=user_friend_ids)
        for e in user_friend_ids:
            u = {}
            try:
                friend_otn = OTNUser.objects.get(facebook_profile__facebook_id=e['facebook_id'])
                u['user'] = friend_otn.get_json(level=1)
                f_txns = friend_txns.filter(user__facebook_profile__facebook_id=e['facebook_id'])
                if f_txns.count() > 0:
                    u['latest'] = str(time.mktime(f_txns[0].timestamp.timetuple()))
                else:
                    # if there are no transactions by this friend, skip over
                    continue 
                u['count'] = f_txns.count()
                people.append(u)
            except OTNUser.DoesNotExist:
                # The facebook user is not registered with OTN
                pass

        people.sort(key=operator.itemgetter('count'), reverse=True)
        map(count_to_str, people)
        output['people'] = people
        
        # log event
        event = FeedEvent(user=user, experiment=user.experiment.id, 
                        action=FeedEvent.LOCATION_TRACE,
                        params=str(output))
        event.save()
                        
    return JSONHttpResponse(output)

@csrf_exempt
def reviews(request,user_id,location_id):
    """
        Returns comments by people, up to 10 comments by user_id
        and up to 10 comments by others.  If there are no comments
        :personal: and :general: fields return empty array ([])

        :url: /m/reviews/(?P<user_id>\d+)/(?P<location_id>\d+)/

        :param user_id: if 0 it is for only public information, else 
                    specific person's user id
        :param location_id: the location that we are retrieving the review

        :rtype: JSON

        ::
            
            # if user is not authenticated
            output = {}
            # if user with user_id does not exist
            output = {'result':'-1'}
            # if location_id does not exist
            output = {'result':'-2'}
            # user has never been here 
            output = {'result':'-3'}

            # else
            output = {
                'user':
                    {'id': str(self.id),
                      'name': self.name,
                      'phone': self.phone,
                      'experiment': str(self.experiment.id),
                      'image': self.image
                     },
                "rating": '3.5',    # average rating by the user
                "location": {"name": "Subway",
                            "id": "27",
                            "image": "http://lunchtime-dev.media.mit.edu/media/Subway-Icon.png",
                            "banner": "http://lunchtime-dev.media.mit.edu/media/Subway.png",
                            "phone": "617-234-4500",
                            'address': self.address,
                            'latitude': str(self.latitude),
                            'longitude': str(self.longitude) 

                            },
                'personal': 
                    [
                        {'id': str(self.id),
                        'timestamp': str(time.mktime(self.txn.timestamp.timetuple())),
                        'rating': str(self.rating),
                        'comment': self.detail
                        },
                        {'id': str(self.id),
                        'timestamp': str(time.mktime(self.txn.timestamp.timetuple())),
                        'rating': str(self.rating),
                        'comment': self.detail
                        },
                        {'id': str(self.id),
                        'timestamp': str(time.mktime(self.txn.timestamp.timetuple())),
                        'rating': str(self.rating),
                        'comment': self.detail
                        },

                    ],

                'general': [
                        {'id': str(self.id),
                        'timestamp': str(time.mktime(self.txn.timestamp.timetuple())),
                        'rating': str(self.rating),
                        'comment': self.detail
                        },
                        {'id': str(self.id),
                        'timestamp': str(time.mktime(self.txn.timestamp.timetuple())),
                        'rating': str(self.rating),
                        'comment': self.detail
                        },
                        {'id': str(self.id),
                        'timestamp': str(time.mktime(self.txn.timestamp.timetuple())),
                        'rating': str(self.rating),
                        'comment': self.detail
                        }
                    ]
            }
    """
    total = 20      # number of receipts to look at for comment
    output = {}

    if request.user.is_authenticated():
        location = Location.objects.get(id=int(location_id))
        try:
            output['location'] = location.get_json(level=2)
        except Location.DoesNotExist:
            return JSONHttpResponse({'result':'-2'})

        output['user'] = ''
        output['personal'] = [] 
        output['general'] = []

        if user_id == '0':

            # general comments
            receipts = Receipt.objects.filter(txn__location=location)
            if receipts.count() < 1:
                # nobody has ever been here
                #return JSONHttpResponse({'result':'-3'})
                return JSONHttpResponse(output)

            for r in receipts.exclude(detail="")[:total]:
                # rating, comment, date
                if len(r.detail) > 0:
                    output['general'].append( r.get_review() )

            sum = receipts.aggregate(Sum('rating'))
            #print sum
            count = receipts.count()
            output['rating'] = str(round(sum['rating__sum']/float(count)))

        else:
            try:
                p = OTNUser.objects.get(id=user_id)
            except OTNUser.DoesNotExist:
                return JSONHttpResponse({'result':'-1'})
            output['user'] = p.get_json(level=1)
            # for testing
            #p = OTNUser.objects.get(id=3)

            # user comments
            receipts = Receipt.objects.filter(txn__location=location,txn__user=p)
            if receipts.count() > 0:
                # if user has been here
                sum = receipts.aggregate(Sum('rating'))
                #print sum
                count = receipts.count()
                output['rating'] = str(round(sum['rating__sum']/float(count)))

                for r in receipts.exclude(detail="")[:total]:
                    # rating, comment, date
                    if len(r.detail) > 0:
                        output['personal'].append( r.get_review() )

            # general comments
            receipts_general = Receipt.objects.filter(txn__location=location).exclude(detail="")

            #receipts_general = Receipt.objects.filter(txn__location=location).exclude(txn__user=p)
            for r in receipts_general[:total]:
                # rating, comment, date
                if len(r.detail) > 0:
                    output['general'].append( r.get_review() )

        # log event request
        event = FeedEvent(user=request.user, experiment=request.user.experiment.id, 
                        action=FeedEvent.REVIEWS,
                        params=str(output))
        event.save()

    return JSONHttpResponse(output)

@csrf_exempt
def user(request, user_id):
    """
        :url: /m/user/(?P<user_id>\d+)/
        :param user_id: the User id
        :return: get information of a user, do not display experiment information
        :rtype: JSON

        ::

            {'id': str(self.id),
              'name': self.name,
              'phone': self.phone,
              'experiment': str(self.experiment),
              'image': self.image
            }
 
    """
    user = User.objects.get(id = int(user_id))
    
    event = Event(user=request.user, action=Event.USER, params="{'id':%s}"%user_id)
    event.save()
    return JSONHttpResponse(user.get_json(level=1))

@never_cache
@csrf_exempt
def receipt(request, receipt_id):

    """
        :url: /m/receipt/(?P<receipt_id>\d+)/
        :return: receipt information, mark the receipt viewed
        :rtype: JSON

        ::
        
            # if you own this receipt
            {'id': str(self.id),
                'techcash': {
                    'id': str(self.id),
                    'location': {
                        'id': '5',
                        'name': "Anna's Taqueria",
                    }
                    'amount': str(self.amount),
                    'timestamp': str(time.mktime(self.timestamp.timetuple())),
                },
                'rating': str(self.rating),
                'sharing': str(self.sharing),
                'accompanied': 'True' or 'False',
                'detail': self.detail,
                'new': str(self.new)
            }

            # else if not your receipt
            {'id': '-1'}
 
    """

    args = {}

    receipt_obj = Receipt.objects.get(id = int(receipt_id))
    if receipt_obj.txn.user != request.user:
        # if not my receipt, return -1
        return JSONHttpResponse({'id':'-1'})
    else:
        # mark the receipt viewed
        receipt_obj.new = False
        receipt_obj.save()
        # log event
        event = Event(user=request.user, action=Event.RECEIPT,
                    params="{'receipt_id':%s}"%receipt_id)
        event.save()

        return JSONHttpResponse(receipt_obj.get_json())

@never_cache
@csrf_exempt
def location(request, location_id):
    """
        :url: /m/location/(?P<location_id>\d+)/
        :return: location from id
        :rtype: JSON

        ::

            {'id': str(self.id),
             'name': self.name,
             'phone': self.phone,
             'description': self.description,
             'image': self.image
            }
    """
    location = Location.objects.get(id = int(location_id))
    event = Event(user=request.user, action=Event.LOCATION, params="{'id':%s}"%location_id)
    event.save()

    return JSONHttpResponse(location.get_json(level=2))

def get_basic_locations(last, output):
    """
        used by :meth:`places` to get the basic existing locations 
        when there are no locations that friends have visited 
        or for experiment=1
    """
    total = 10
    locations = []

    # sort by popularity but do not display the social information
    last = int(last)
    # sort the locations by popularity
    places = Location.objects.filter(type=Location.EATERY).exclude(id=1).annotate(popularity=Count('techcashtransaction')).order_by('-popularity')
    output['more'] = '0'
    if places.count() > (last+1)*total:
        output['more'] = str(last+1) 
    for p in places[last*total:(last+1)*total]:
        places_dict = {}
        places_dict['location'] = p.get_json(level=2)
        locations.append(places_dict)
        
    output['locations'] = locations

    return output

@csrf_exempt
def places(request, last):
    """
        :url: /m/places/(?P<last>\d+)/

        :param last: 0 for most recent 10 feeds, or page number 1,2,3... or
            :data:`last` transaction ID 

            1. Get more locations (make last='more' field that is returned)
                Just locations
            2. Get more locations (make last='more' field that is returned)
                Locations with friends who have been there
            3. Get more locations (make last='more' field that is returned)
                Locations with popularity
            4. Get more locations (make last='more' field that is returned)
                Locations with friends and popularity mixed
            5. Get more feeds (last is the last transaction ID)
                Locations showing one person is going there
            6. Get more feeds (last is the last transaction ID)
                Friend feeds

        :rtype: JSON

        ::

            'more' field is in each output dictionary
                '1' if there's more data
                '0' if there's no more data

            if experiment == 1:
                # just show some of the restaurants
                # if there are no featured, then no 'featured' field
                output = {
                         'featured': 
                            {'id': '7',
                             'location':
                                 { 'id': '6',
                                    'name': "Anna's Taqueria",
                                    'phone': '617-324-2662',
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                 },
                            }
                        'locations':
                            [
                                "location":
                                {
                                    'id': '5',
                                    'name': 'Subway',
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-494-6600',
                                    'description': 'Long subs',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Subway.png'
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Subway.png'
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',
                                },
                                "location":
                                {
                                    'id': '6',
                                    'name': "Anna's Taqueria",
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-324-2662',
                                    'description': 'Taco Mex',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Annas.png'
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Annas.png'
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',
                                }
                            ]
                }
                
            elif experiment == 2:
                # if there are no locations visited by friends
                # list same as experiment == 1

                # if there are locations visited by friends
                output = {
                        'locations':
                        [
                            {'location':
                                {
                                    'id': '5',
                                    'name': 'Subway',
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-494-6600',
                                    'description': 'Long subs',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Subway.png',
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Subway.png',
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',
                                },
                            'friends': 'Yod, Michael, Ilya, ...'  # up to 30 chars
                            'count': '5'    # number of friends
                            },
                            {'location':
                                {
                                    'id': '6',
                                    'name': "Anna's Taqueria",
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-324-2662',
                                    'description': 'Taco Mex',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',                                
                                },
                            'friends': 'Kwan, John, Polychronis',
                            'count': '3'
                            }
                        ]
                }

            elif experiment == 3:
                # if there are no locations visited by friends
                # list same as experiment == 1


                # show list of restaurants and how many people have been (popularity)
                output = {
                        'locations':
                        [
                            {'location':
                                {
                                    'id': '5',
                                    'name': 'Subway',
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-494-6600',
                                    'description': 'Long subs',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Subway.png',
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Subway.png',
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',
                                },
                            'popularity': '55'
                            },
                            {'location':
                                {
                                    'id': '6',
                                    'name': "Anna's Taqueria",
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-324-2662',
                                    'description': 'Taco Mex',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',                                
                                },
                            'popularity': '32'
                            }
                        ]
                }
            elif experiment == 4:
                # if there are no locations visited by friends
                # list same as experiment == 1

                # show list of restaurants and show mix of friends and popularity 
                output = {
                        'locations':
                        [
                            {'location':
                                {
                                    'id': '5',
                                    'name': 'Subway',
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-494-6600',
                                    'description': 'Long subs',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Subway.png',
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Subway.png',
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',
                                },
                            'popularity': '55'
                            },
                            {'location':
                                {
                                    'id': '6',
                                    'name': "Anna's Taqueria",
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-324-2662',
                                    'description': 'Taco Mex',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',                                
                                },
                            'popularity': '32'
                            },
                            {'location':
                                {
                                    'id': '6',
                                    'name': "Anna's Taqueria",
                                    'address': '77 Mass Av, Cambridge, MA',
                                    'phone': '617-324-2662',
                                    'description': 'Taco Mex',
                                    'image': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                    'banner': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                    'latitude': '42.2341',
                                    'longitude': '-72.324',                                
                                },
                            'friends': 'Kwan, John, Polychronis',
                            'count': '3'
                            }

                        ]
                }
               
            elif experiment == 5:
                # same output as experiment 2 but with people "going to the location"
            elif experiment == 6:
                {"locations": [{"phone": "", 
                               "description": "", 
                               "id": "1", 
                               "image": "http://www.yourgigs.com.au/static/common/images/pin_restaurant2.png", 
                               "name": "New House Dryer #1"}, 
                            {"phone": "", 
                               "description": "", 
                               "id": "2", 
                               "image": "http://www.yourgigs.com.au/static/common/images/pin_restaurant2.png", 
                               "name": "New House Washer #8"}, 
                            {"phone": "", 
                                "description": "", 
                                "id": "4", 
                                "image": "http://www.yourgigs.com.au/static/common/images/pin_restaurant2.png", 
                                "name": "Anna's Taqueria"}
                            ],
                "transactions": [{"techcash": 
                         {
                          "amount": "0.75", 
                          "user": {"phone": "", 
                                "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=7d3adb92e2175ffb402072f853787796&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv222%2F1841%2F61%2Fq1087500981_5826.jpg&v=5", 
                                "experiment": "2", 
                                "id": "1", 
                                "name": "Yod Phumpong Watanaprakornkul"}, 
                          "id": "97", 
                          "timestamp": "1256518320.0", 
                          "location": {"phone": "", 
                                "description": "", 
                                "id": "41", 
                                "image": "http://www.yourgigs.com.au/static/common/images/pin_restaurant2.png", 
                                "name": "New House Dryer #10"}
                         }, 
                         "id": "97", 
                         "rating": "0"
                        }, 
                        {"techcash": 
                            {
                                "amount": "0.75", 
                                "user": {"phone": "", 
                                    "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=7d3adb92e2175ffb402072f853787796&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv222%2F1841%2F61%2Fq1087500981_5826.jpg&v=5", 
                                    "experiment": "2", 
                                    "id": "1", 
                                    "name": "Yod Phumpong Watanaprakornkul"}, 
                                "id": "100", 
                                "timestamp": "1256515380.0", 
                                "location": {"phone": "", 
                                    "description": "", 
                                    "id": "21", 
                                    "image": "http://www.yourgigs.com.au/static/common/images/pin_restaurant2.png", 
                                    "name": "New House WAsher #10"}
                            }, 
                            "id": "100", 
                            "rating": "0"},
                        ]
                }



    """

    user = ''
    total = 10

    output = {}
    transactions = []
    locations = []
    
    if(request.user.is_authenticated()):
        otnuser = request.user.otnuser
        facebook_profile = otnuser.facebook_profile
        
        #: check which experimental group user is in
        experiment = otnuser.experiment.id
 
        logger.debug( "User is in experiment: %d"%experiment)

        if last == '0':
            try:
                # handle feature
                featured = Featured.objects.get(day=date.today())
                output['featured'] = featured.get_location() 
            except Featured.DoesNotExist:
                # no feature today
                pass

        if experiment == 1:
            output = get_basic_locations(last, output)
        elif experiment == 2:
            last = int(last)
            # friend's facebook_id's
            fs = Friends.objects.get(facebook_id=facebook_profile.facebook_id).friends.values('facebook_id')
            # places popular by my friends
            places = Location.objects.filter(type=Location.EATERY, techcashtransaction__timestamp__gt=datetime.today()-timedelta(300), techcashtransaction__user__facebook_profile__facebook_id__in=fs).annotate(popularity=Count('techcashtransaction')).order_by('-popularity')

            if places.count() == 0:
                output = get_basic_locations(last, output)
            else:
                output['more'] = '0'
                if places.count() > (last+1)*total:
                    output['more'] = str(last+1) 
                for p in places[last*total:(last+1)*total]:
                    places_dict = {}
                    places_dict['location'] = p.get_json(level=2)

                    # get all friend's of this user
                    # find if these friends have transactions in this location
                    # TODO: if Friends had reference to OTNUser, this would be simpler
                    friends = p.techcashtransaction_set.filter(user__facebook_profile__facebook_id__in=fs).order_by('user__first_name').distinct().values('user__first_name')
                    places_dict['count'] = friends.count()
                    names = ""
                    if friends.count() > 0:
                        names = friends[0]['user__first_name']
                        for f in friends[1:3]:
                            names += ', ' + f['user__first_name']
                        if places_dict['count'] > 3:
                            names += ',...'
                    places_dict['friends'] = names
                    locations.append(places_dict)

                locations.sort(key=operator.itemgetter('count'), reverse=True)
                map(count_to_str, locations)
       
                output['locations'] = locations

        elif experiment == 3:
            # true popularity
            last = int(last)
            # sort the locations by popularity
            places = Location.objects.exclude(id=1).filter(techcashtransaction__timestamp__gt=datetime.today()-timedelta(7),type=Location.EATERY).annotate(popularity=Count('techcashtransaction')).order_by('-popularity')

            if places.count() == 0:
                output = get_basic_locations(last, output)
            else:
                output['more'] = '0'
                if places.count() > (last+1)*total:
                    output['more'] = str(last+1) 
                for p in places[last*total:(last+1)*total]:
                    places_dict = {}
                    places_dict['location'] = p.get_json(level=2)
                    places_dict['popularity'] = p.popularity
                    locations.append(places_dict)
                    
                # convert popularity to string
                map(popularity_to_str, locations)
                output['locations'] = locations
        elif experiment == 4:
            # mix of popularity and friends
            last = int(last)
            # all places except Unknown location
            places = Location.objects.filter(type=Location.EATERY).exclude(id=1)

            if places.count() == 0:
                output = get_basic_locations(last, output)
            else:
                output['more'] = '0'
                if places.count() > total:
                    output['more'] = str(last+1)
                
                for p in places[last*total:(last+1)*total]:
                    places_dict = {}
                    places_dict['location'] = p.get_json(level=2)
                    places_dict['popularity'] = str(int(random.random()*10))
                    locations.append(places_dict)
                output['locations'] = locations
        elif experiment == 5:
            # shows people who plan to go somewhere
            last = int(last)
            # friend's facebook_id's
            fs = Friends.objects.get(facebook_id=facebook_profile.facebook_id).friends.values('facebook_id')
            # places popular by my friends
            places = Location.objects.filter(type=Location.EATERY, techcashtransaction__user__facebook_profile__facebook_id__in=fs).annotate(popularity=Count('techcashtransaction')).order_by('-popularity')

            if places.count() == 0:
                output = get_basic_locations(last, output)
            else:
                output['more'] = '0'
                if places.count() > (last+1)*total:
                    output['more'] = str(last+1) 
                for p in places[last*total:(last+1)*total]:
                    places_dict = {}
                    places_dict['location'] = p.get_json(level=2)

                    # get all friend's of this user
                    # find if these friends have transactions in this location
                    # TODO: if Friends had reference to OTNUser, this would be simpler
                    friends = p.techcashtransaction_set.filter(user__facebook_profile__facebook_id__in=fs).order_by('user__first_name').distinct().values('user__first_name')
                    places_dict['count'] = friends.count()
                    names = ""
                    if friends.count() > 0:
                        names = friends[0]['user__first_name']
                        for f in friends[1:3]:
                            names += ', ' + f['user__first_name']
                        if places_dict['count'] > 3:
                            names += ',...'
                    places_dict['friends'] = names
                    locations.append(places_dict)

                locations.sort(key=operator.itemgetter('count'), reverse=True)
                map(count_to_str, locations)
       
                output['locations'] = locations
        elif experiment == 6: 
            user_friend = Friends.objects.get(facebook_id = facebook_profile.facebook_id)
    
            # create a list of friends who are site users and facebook friends.
            otn_friends = []
            
            for friend in user_friend.friends.all():
                try:
                    f = FacebookProfile.objects.get(facebook_id= friend.facebook_id)
                    otn_friends.append(f.user)
                except:
                    pass
    
            # find the list of transactions for friends of site users.
            last = int(last)
    
            if last == 0:
                for otn_user in otn_friends:
        
                    user_transactions = TechCashTransaction.objects.filter(user = otn_user, location__type=Location.EATERY)
                    transactions += user_transactions
            else:
                last_feed = TechCashTransaction.objects.get(id=last)
                for otn_user in otn_friends:
        
                    user_transactions = TechCashTransaction.objects.filter(user = otn_user, timestamp__lt=last_feed.timestamp, location__type=Location.EATERY)
                    transactions += user_transactions
    
            transactions.sort(key=operator.attrgetter('timestamp'))
            transactions.reverse()
            output['more'] = '0'
            if len(transactions) > total:
                output['more'] = '1'
            transactions = transactions[:total]
            transactions = [Receipt.objects.get(txn=transaction) for transaction in transactions]
        
            location_id = {}
            for transaction in transactions:
                if(not location_id.has_key(transaction.txn.location.id)):
                    location_id[transaction.txn.location.id] = transaction.txn.location
    
            output["locations"] = [location_id[key].get_json(level=2) for key in location_id.keys()]
            output["transactions"] = [transaction.get_json(public=True) for transaction in transactions]

        event = FeedEvent(user=otnuser, experiment=experiment, 
                        action=FeedEvent.FEED,
                        params=str(output))
        event.save()
    return JSONHttpResponse(output)

@csrf_exempt
def feature_detail(request):
    """
        Returns the details of the feature

        :url: /m/featured/

        :param POST['feature_id']: feature_id
        :param POST['lat']: latitude
        :param POST['lon']: longitude
    
        :rtype: JSON

        ::

            {'feature': {'id': '5',
                          'location':
                                    {
                                        'id': '6',
                                        'name': "Anna's Taqueria",
                                        'address': '77 Mass Av, Cambridge, MA',
                                        'phone': '617-324-2662',
                                        'description': 'Taco Mex',
                                        'image': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                        'banner': 'http://lunchtime-dev.media.mit.edu/media/Annas.png',
                                        'latitude': '42.2341',
                                        'longitude': '-72.324',                                
                                    },
                              'description': '5% off at Annas Taqueria',
                              'expires': '23425151514',     # 'None' if there is no expiration date
                              'image': 'http://lunchtime.media.mit.edu/media/techcash/featured_deal150.jpg",
                        }
            }

    """

    output = {}

    if request.user.is_authenticated():
        if request.method == 'POST':
            feature = Featured.objects.get(id=int(request.POST['feature_id']))
            output['feature'] = feature.get_json()

            # record that the user has seen the feature
            event = FeaturedEvent(user=request.user, featured=feature,
                    action=FeaturedEvent.LOCATION_FEATURED,
                    latitude=request.POST['lat'],
                    longitude=request.POST['lon'])
            event.save()

            # return details of the feature
    return JSONHttpResponse(output)

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
def location_log(request):
    """
        Logs location of the user

        :url: /m/location/log/

        :param POST['lat']: latitude of the phone
        :param POST['lon']: longitude of the phone

        :rtype: JSON

        ::

            # always returns success
            {'result':'1'}
    """

    user = request.user

    event = Event(user=user, action=Event.LOCATION_LOG, latitude=float(request.POST['lat']), longitude=float(request.POST['lon']))
    event.save()

    return JSONHttpResponse({'result': '1'})

@csrf_exempt
def logout_ws(request):
    """
        Clears session data for the user

        :url: /m/logout/

        :rtype: JSON

        ::

            # always returns success
            {'result':'1'}
    """
    logout(request)
    return JSONHttpResponse({'result':'1'})

@csrf_exempt
def call_user(request, otn_user):
    """
        Method that logs that a user called another user
        
        :url: /m/call/(?P<otn_user>\d+)/
        
        :param otn_user: the OTN user ID
        :param POST['type']: call or sms or email
        :param POST['lat']: latitude
        :param POST['lon']: longitude
        
        :rtype: JSON

        ::
        
            # if logged successfully
            {'result':'1'}
            # if user is not logged in 
            {'result': '-1'}
            # if data is not correct
            {'result': '-2'}
    """
    if request.user.is_authenticated():
        if request.POST['type'] == 'call':
            event = CallEvent(caller=request.user, 
                        callee=OTNUser.objects.get(id=int(otn_user)),
                        action=CallEvent.CALLED)
            event.save()
        elif request.POST['type'] == 'sms':
            event = CallEvent(caller=request.user, 
                        callee=OTNUser.objects.get(id=int(otn_user)),
                        action=CallEvent.SMSED)
            event.save()
        elif request.POST['type'] == 'email':
            event = CallEvent(caller=request.user, 
                        callee=OTNUser.objects.get(id=int(otn_user)),
                        action=CallEvent.EMAILED)
            event.save()
        else:
            return JSONHttpResponse({'result':'-2'})
        logger.debug(event)
        if 'lat' in request.POST: 
            event.latitude=float(request.POST['lat']) 
            event.longitude=float(request.POST['lon'])
            event.save()
    else:
        return JSONHttpResponse({'result':'-1'})
    return JSONHttpResponse({'result':'1'})
    
    
@csrf_exempt
def call_log(request):
    """ 
        Method that logs how long a user talked to another user
        
        :url: /m/call/log/
        
        :param POST['otn_user']: OTN user ID
        :param POST['duration']: duration of the call in minutes
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if logged successfully
            {'result':'1'}
            # if user is not logged in 
            {'result': '-1'}

    """
    if request.user.is_authenticated():
        event = CallEvent(caller=request.user,
                callee=OTNUser.objects.get(id=int(request.POST['otn_user'])),
                action=CallEvent.TALKED,
                value=int(request.POST['duration']))
        event.save()
        if 'lat' in request.POST: 
            event.latitude=float(request.POST['lat']) 
            event.longitude=float(request.POST['lon'])
            event.save()
    else:
        return JSONHttpResponse({'result':'-1'})
    return JSONHttpResponse({'result':'1'})
    
@never_cache
@csrf_exempt
def update_txn(request):
    """
        Updates sharing, rating, comment data on a transaction
        
        :url: /m/update/txn/

        Any of the fields rating, sharing, with_friends and comment can be updated individually or together

        :param POST['txn_id']: Transaction ID - Required field is the Receipt object ID
        :param POST['rating']: The rating on this item, 
            0 to 5
        :param POST['sharing']: How open you want to share (0-3);
            PRIVATE=0, FRIENDS=1, COMMUNITY=2, PUBLIC=3
        :param POST['accompanied']: 1 if True, 0 if False
        :param POST['comment']: The comment information

        :rtype: JSON

        ::

            # if successfully saved
            {'result':'1'}
            # when form is not valid
            {'result':'-1'}
            # when method is not POST
            {'result':'-2'}
            # if user is not authenticated
            {'result':'-3'}
    """
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = UpdateTransactionForm(request.POST, request.FILES)
            if form.is_valid():
                r = Receipt.objects.get(id=form.cleaned_data['txn_id'])
                if 'rating' in request.POST:
                    r.rating = form.cleaned_data['rating']
                if 'sharing' in request.POST:
                    r.sharing = form.cleaned_data['sharing']
                if 'comment' in request.POST:
                    r.detail = form.cleaned_data['comment']
                if 'accompanied' in request.POST:
                    r.accompanied = form.cleaned_data['accompanied']
                r.save()
                return JSONHttpResponse({'result':'1'})
            else:
                # data is invalid
                return JSONHttpResponse({'result':'-1'})
        else:
            # method must be POST
            return JSONHttpResponse({'result':'-2'})
    else:
        return JSONHttpResponse({'result':'-3'})

@csrf_exempt
def notify_lunchtime(request):
    """
        Notifies the phones about lunch time
        
        :url: /m/notify/lunch/

        :param POST['password']: So that not anybody can send it

        :rtype: JSON

        ::
            
            # not authorized to send message
            {'result':'-1'}
            # successful
            {'result':'1'}
            # not a post message
            {'result':'0'}
    """

    if request.method == 'POST':
        if request.POST['password'] == '15389099':
            phones = iPhone.objects.all()   
            sendMessageToPhoneGroup(phones, "Where do you want to go today?", sound="default", custom_params={'msg_type':'lunch'}, sandbox=False)
            return JSONHttpResponse({'result':'1'})
        else:
            return JSONHttpResponse({'result':'-1'})
    else:
        return JSONHttpResponse({'result':'0'})


