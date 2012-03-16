# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from common.helpers import JSONHttpResponse
from bestbuy.models import *
from survey.models import * 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_control, never_cache
from survey.models import *
from survey.forms import *
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import hashlib, re, json
from mobile.models import Event
from django.db.models import Count
from django.template import RequestContext
from survey.models import Survey, BasicMobileSurvey, BasicShoppingSurvey, ChoiceToEatSurvey
from survey.forms import BasicMobileSurveyForm, BasicShoppingSurveyForm, ChoiceToEatSurveyForm

api_key = settings.BESTBUY_API_KEY

logger = settings.LOGGER

###############################
# view_purchase
# - request for reviews
# - return subtitles as full text
# view_wish
# - return subtitles as text
# 

@csrf_exempt
def login_mobile(request):
    """
        Logs into the system

        :param POST['email']: email
        :param POST['pin']: PIN of the user
        :param POST['lat']: latitude of the phone
        :param POST['lon']: longitude of the phone

        :rtype: JSON

        ::

            # `experiment` is the experimental group
            #   1: control group
            #   2: social group (friend's names)
            #   3: anonymous people group (number of people)
            #   4: anonymous friends group (number of friends)

            # login success
            {'result':'1', 'experiment': '1', 'first_name': Eric}
            # login failure
            {'result':'-1'}

    """

    email = request.POST['email'].lower()
    pin = hashlib.sha224(request.POST['pin']).hexdigest()
    user = authenticate(username=email, pin=pin)
    if user is not None:
        login(request, user)
        logger.debug( "User %s authenticated and logged in"%email )
        exp_group = user.experiment.id
        # log latitude and longitude
        if 'lat' in request.POST:
            event = Event(user=user, action=Event.LOGIN, latitude=float(request.POST['lat']), longitude=float(request.POST['lon']))
            event.save()
        return JSONHttpResponse({'result': '1', 'experiment': str(exp_group), 'first_name': str(user.first_name)})          
    else:
        return JSONHttpResponse({'result': '-1'})


    # TODO: if basic login, send to Home
    #       if group purchase alert, send to that specific group purchase info
    #       if price down alert, send to the item 
    return JSONHttpResponse()

@csrf_exempt
def logout_mobile(request):
    """
        Logout of Shoppley app

        :url: /m/logout/

        :param POST['lat']:
        :param POST['lon']:

        :rtype: JSON

        ::

            {'result': '1'}

    """

    logout(request)
    return JSONHttpResponse({'result':'1'})

@csrf_exempt
@login_required
def home(request):
    """
        Returns surveys, requests for reviews,
        and feeds of what is happening by friends or others

        :url: /m/home/

        :param POST['lat']:
        :param POST['lon']:

        :rtype: JSON

        ::

            {
              "review_requests": [
                {
                  "requested": "1280005940.0", 
                  "product": {
                    "regular_price": "19.99", 
                    "bought_by": "2 people bought this", 
                    "wished_by": "", 
                    "num_requested": "1", 
                    "sku": "9644845", 
                    "num_bought": "2", 
                    "on_sale": false, 
                    "customer_review_count": "1", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9644/9644845s.jpg", 
                    "new": false, 
                    "review_request": "1 person requested for review", 
                    "category": "Action & Adventure", 
                    "artist_name": "", 
                    "sale_price": "19.99", 
                    "product_id": "1218136348111", 
                    "customer_review_average": "4.0", 
                    "name": "Jak and Daxter: The Lost Frontier - PlayStation 2", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9644845&type=product&id=1218136348111&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9644845"
                  }, 
                  "request_id": "2", 
                  "requester": {
                    "first_name": "Kwan", 
                    "last_name": "Lee", 
                    "name": "Kwan Hong Lee", 
                    "alias": "kool", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "phone": "", 
                    "first_joined": "1280005924.0", 
                    "id": "1"
                  }
                }
              ], 
              "surveys": [
                {
                  "url": "http://webuy-dev.mit.edu/m/survey/1/", 
                  "title": "Basic Mobile Survey", 
                  "expires": "None", 
                  "description": "Tell us about your usage of mobile phone.", 
                  "id": "1"
                }, 
                {
                  "url": "http://webuy-dev.mit.edu/m/survey/2/", 
                  "title": "Basic Shopping Survey", 
                  "expires": "None", 
                  "description": "Tell us about your shopping habits", 
                  "id": "2"
                }
              ], 
              "feeds": [
                {
                  "feed": "<a href='tt://party/1'>Kwan</a> bought <a href='tt://product/9644845'>Jak and Daxter: The Lost Frontier - PlayStation 2</a>", 
                  "actor": {
                    "alias": "kool", 
                    "first_joined": "1280005924.0", 
                    "id": "1", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }
                }, 
                {
                  "feed": "<a href='tt://party/1'>Kwan</a> reviewed <a href='tt://product/9704268'>Clerks - UMD Video for Sony PSP</a>", 
                  "actor": {
                    "alias": "kool", 
                    "first_joined": "1280005924.0", 
                    "id": "1", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }
                }, 
                {
                  "feed": "<a href='tt://party/1'>Kwan</a> requested review for <a href='tt://product/9723733'>Sony VAIO Laptop with Intel&#174; Core&#153;2 Duo Processor - Brown</a>", 
                  "actor": {
                    "alias": "kool", 
                    "first_joined": "1280005924.0", 
                    "id": "1", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }
                }, 
                {
                  "feed": "<a href='tt://party/1'>Kwan</a> wishes to buy <a href='tt://product/9757802'>Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue</a>", 
                  "actor": {
                    "alias": "kool", 
                    "first_joined": "1280005924.0", 
                    "id": "1", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }
                }
              ]
            }    

    """

    result = {}
    
    result['surveys'] = []
    result['review_requests'] = []

    u = request.user

    # get surveys
    surveys = Survey.objects.all()
    for s in surveys:
        status, created = eval("%s.objects.get_or_create(survey=s, user=u)"%s.model_name)
        if created:
            status.uuid_token = uuid.uuid4()
            status.save()
        if not status.completed:
            result['surveys'].append(s.summary())
    
    my_products = TransactionLineItem.objects.filter(transaction__party=u).values('product')
    # Find review requests related to product I have purchased, that I haven't reviewed 
    reqs = ReviewRequest.objects.exclude(requester=u).filter(product__in=my_products).exclude(replies__reviewer=u)
    
    for r in reqs:
        result['review_requests'].append(r.get_json(me=u))

    # TODO: Group purchase requests

    # get other people's feeds, filter by friends if in social group
    feeds = Feed.objects.exclude(actor=u)
    result['feeds'] = [ f.get_json(me=u) for f in feeds ]

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def home_surveys(request):
    """
        Returns surveys for the home screen on Android

        :url: /m/surveys/

        :param POST['lat']:
        :param POST['lon']:

        :rtype: JSON

        ::

            {
              "surveys": [
                {
                  "url": "http://webuy-dev.mit.edu/m/survey/1/", 
                  "title": "Basic Mobile Survey", 
                  "expires": "None", 
                  "description": "Tell us about your usage of mobile phone.", 
                  "id": "1"
                }, 
                {
                  "url": "http://webuy-dev.mit.edu/m/survey/2/", 
                  "title": "Basic Shopping Survey", 
                  "expires": "None", 
                  "description": "Tell us about your shopping habits", 
                  "id": "2"
                }
              ]
            }    

    """

    result = {}
    
    result['surveys'] = []

    u = request.user

    # get surveys
    surveys = Survey.objects.all()
    for s in surveys:
        status, created = eval("%s.objects.get_or_create(survey=s, user=u)"%s.model_name)
        if created:
            status.uuid_token = uuid.uuid4()
            status.save()
        if not status.completed:
            result['surveys'].append(s.summary())

    return JSONHttpResponse( result )

@csrf_exempt
@login_required
def home_feeds(request):
    """
        Returns feeds of what is happening by friends or others
        Used by Android App

        :url: /m/feeds/

        :param POST['lat']:
        :param POST['lon']:

        :rtype: JSON

        ::

            {
              "feeds": [
                {
                  "feed": "<font color='green'><b>Kwan</b></font> wishes to buy <font color='green'><b>Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue</b></font>", 
                  "sku": "9757802", 
                  "item_url": "/m/product/9/", 
                  "actor": {
                    "alias": "kool", 
                    "first_joined": "1280005924.0", 
                    "id": "1", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }
                }, 
                {
                  "feed": "<font color='green'><b>Kwan</b></font> requested review for <font color='green'><b>Sony VAIO Laptop with Intel&#174; Core&#153;2 Duo Processor - Brown</b></font>", 
                  "sku": "9723733", 
                  "item_url": "/m/product/7/", 
                  "actor": {
                    "alias": "kool", 
                    "first_joined": "1280005924.0", 
                    "id": "1", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }
                }, 
                {
                  "feed": "<font color='green'><b>Kwan</b></font> reviewed <font color='green'><b>Clerks - UMD Video for Sony PSP</b></font>", 
                  "sku": "9704268", 
                  "item_url": "/m/product/5/", 
                  "actor": {
                    "alias": "kool", 
                    "first_joined": "1280005924.0", 
                    "id": "1", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }
                }, 
                {
                  "feed": "<font color='green'><b>Kwan</b></font> bought <font color='green'><b>Jak and Daxter: The Lost Frontier - PlayStation 2</b></font>", 
                  "sku": "9644845", 
                  "item_url": "/m/product/1/", 
                  "actor": {
                    "alias": "kool", 
                    "first_joined": "1280005924.0", 
                    "id": "1", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }
                }
              ]
            }
    """
    result = {}
    
    result['feeds'] = []

    u = request.user


    # get other people's feeds, filter by friends if in social group
    feeds = Feed.objects.exclude(actor=u).order_by('-timestamp')
    result['feeds'] = [ f.get_json(me=u, android=True) for f in feeds ]

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def home_requests(request):
    """
        Returns requests for reviews
        Used by Android App

        :url: /m/requests/

        :param POST['lat']:
        :param POST['lon']:

        :rtype: JSON

        ::

            {
              "review_requests": [
                {
                  "requested": "1273479609.0", 
                  "product": {
                    "sku": "9644845", 
                    "category": "Action & Adventure", 
                    "customer_review_average": "4.0", 
                    "product_id": "1218136348111", 
                    "regular_price": "19.99", 
                    "num_bought": "1", 
                    "new": false, 
                    "bought_by": "1 person bought this", 
                    "wished_by": "", 
                    "on_sale": false, 
                    "artist_name": "", 
                    "num_wished": "0", 
                    "medium_image": "", 
                    "num_requested": "1", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9644/9644845s.jpg", 
                    "album_title": "", 
                    "sale_price": "19.99", 
                    "customer_review_count": "1", 
                    "review_request": "1 person requested for review", 
                    "name": "Jak and Daxter: The Lost Frontier - PlayStation 2"
                  }, 
                  "request_id": "2", 
                  "requester": {
                    "first_name": "Kwan", 
                    "last_name": "Lee", 
                    "name": "Kwan Hong Lee", 
                    "alias": "kool", 
                    "image": "", 
                    "phone": "", 
                    "first_joined": "1273479599.0", 
                    "id": "1"
                  }
                }
              ]
            }

    """

    result = {}
    
    result['review_requests'] = []

    u = request.user

    my_products = TransactionLineItem.objects.filter(transaction__party=u).values('product')

    # Find review requests related to product I have purchased, that I haven't reviewed 

    reqs = ReviewRequest.objects.exclude(requester=u).filter(product__in=my_products)
     
    for r in reqs:
        rev = Review.objects.filter(product=r.product, reviewer=u)
        if rev.exists():
            # if there is an existing review then link it to the request
            review = rev[0]
            review.reply_to.add(r)
            review.save()
        elif not r.replies.filter(reviewer=u).exists():
            result['review_requests'].append(r.get_json(me=u))

    return JSONHttpResponse( result )

@login_required
def survey(request, survey_id):
    """
        Displays a specific survey

        :url: /m/survey/(?P<survey_id>\d+)/

        :param POST['uuid_token']: UUID token for this survey

        :rtype: HTML 


    """
    u = request.user
    survey_id = int(survey_id)
    if request.method =='POST':
        try:
            survey_meta = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            return render_to_response('survey/m/notexist.html')
        survey = eval("%s.objects.get(user=request.user, uuid_token=request.POST['uuid_token'])"%survey_meta.model_name)
        form = eval("%sForm( request.POST, instance=survey)"%survey_meta.model_name)
    
        if form.is_valid():
            survey.completed = True
            survey.complete_date = datetime.datetime.now() 
            form.save()
            return render_to_response('survey/m/completed.html')
        else:
            return render_to_response('survey/m/basic.html', 
                                        {'form':form,
                                        'survey_id': survey_id,
                                        'uuid': survey.uuid_token,
                                        'errors':form.errors})
    else:
        uuid = ""
        form = None 
        try:
            s = Survey.objects.get(id=survey_id)
            status = eval("%s.objects.get(user=u,survey=s)"%s.model_name)
            form = eval("%sForm()"%s.model_name)
        except Survey.DoesNotExist:
            return render_to_response('survey/m/notexist.html')

        return render_to_response('survey/m/basic.html', {'form':form,
                            'survey_id': survey_id,
                            'uuid_token': status.uuid_token},
                            context_instance=RequestContext(request))

@csrf_exempt
@login_required
def product(request, product_id):
    """
        Accessed when user clicks a product from Feed
        WeBuy product id search, convert to sku and return same as 
        :meth:`item()`

        :url: /m/product/(?P<product_id>\d+)/

        :param product_id: the product id in WeBuy

        :rtype: JSON

        ::

            # if not exist
            {'result':'0'}

            # if exist
            {
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "regular_price": "19.99", 
                "bought_by": "2 people bought this", 
                "wished_by": "", 
                "num_requested": "1", 
                "sku": "9644845", 
                "num_bought": "2", 
                "on_sale": false, 
                "customer_review_count": "1", 
                "num_wished": "0", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9644/9644845s.jpg", 
                "new": false, 
                "review_request": "1 person requested for review", 
                "category": "Action & Adventure", 
                "artist_name": "", 
                "sale_price": "19.99", 
                "product_id": "1218136348111", 
                "customer_review_average": "4.0", 
                "name": "Jak and Daxter: The Lost Frontier - PlayStation 2", 
                "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9644845&type=product&id=1218136348111&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                "medium_image": "", 
                "album_title": "", 
                "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9644845"
              }, 
              "add_review": "/m/review/add/", 
              "ask_review": "", 
              "add_wish": ""
            }

    """

    u = request.user
    try:
        p = Product.objects.get(id=product_id)
        request.POST['sku'] = p.sku
        result = item(u, p.sku)
    except Product.DoesNotExist:
        result = {'result':'0'}
    return JSONHttpResponse( result )


@csrf_exempt
@login_required
def product_post(request):
    """
        Accessed when user clicks a product from Feed (<b>from Android only</b>)
        WeBuy product id search, convert to sku and return same as 
        :meth:`item()`

        :url: /m/product/

        :param POST['product_id']: the product id in Shoppley 

        :rtype: JSON

        ::

            # if not exist
            {'result':'0'}

            # if exist
            {
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "regular_price": "39.99", 
                "bought_by": "2 people bought this", 
                "wished_by": "", 
                "num_requested": "0", 
                "sku": "9461076", 
                "num_bought": "2", 
                "on_sale": false, 
                "customer_review_count": "22", 
                "num_wished": "0", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9461/9461076s.jpg", 
                "new": false, 
                "review_request": "", 
                "category": "Action & Adventure", 
                "artist_name": "", 
                "sale_price": "39.99", 
                "product_id": "1218108383576", 
                "customer_review_average": "5.0", 
                "name": "Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3", 
                "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9461076&type=product&id=1218108383576&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                "medium_image": "", 
                "album_title": "", 
                "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9461076"
              }, 
              "add_review": "/m/review/add/", 
              "ask_review": "", 
              "add_wish": ""
            }

    """

    u = request.user
    try:
        p = Product.objects.get(id=request.POST['product_id'])
        request.POST['sku'] = p.sku
        result = item(u, p.sku)
    except Product.DoesNotExist:
        result = {'result':'0'}
    return JSONHttpResponse( result )

@csrf_exempt
@login_required
def view_party(request):
    """


        Views a specific user
        Accessed from Feeds

        :url: /m/party/

        :param POST['party_id']: id of the user
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if friend then show up to 10 purchases and 10 wishes
            {
              "wished": [
                {
                  "wish_id": "10", 
                  "comment": "I want this for Thanksgiving!!", 
                  "product": {
                    "regular_price": "149.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9051036", 
                    "num_bought": "0", 
                    "on_sale": true, 
                    "customer_review_count": "0", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9051/9051036_r.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Laptop Batteries", 
                    "artist_name": "", 
                    "sale_price": "127.49", 
                    "product_id": "1218012528492", 
                    "customer_review_average": "0.0", 
                    "name": "Lenmar Battery for Select Toshiba Laptops", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9051036&type=product&id=1218012528492&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9051/9051036fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9051036"
                  }, 
                  "added": "1280005948.0", 
                  "fulfilled": "False", 
                  "max_price": "122.00"
                }, 
                {
                  "wish_id": "6", 
                  "comment": "This is what i really want", 
                  "product": {
                    "regular_price": "39.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9209331", 
                    "num_bought": "0", 
                    "on_sale": false, 
                    "customer_review_count": "2", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9209/9209331_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Boomboxes", 
                    "artist_name": "", 
                    "sale_price": "39.99", 
                    "product_id": "1218059404120", 
                    "customer_review_average": "2.0", 
                    "name": "Sony CD-R/RW Boombox with AM/FM Tuner - Pink", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9209331&type=product&id=1218059404120&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9209/9209331fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9209331"
                  }, 
                  "added": "1280005938.0", 
                  "fulfilled": "False", 
                  "max_price": "155555.00"
                }, 
                {
                  "wish_id": "5", 
                  "comment": "This is awesome", 
                  "product": {
                    "regular_price": "169.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9757802", 
                    "num_bought": "0", 
                    "on_sale": true, 
                    "customer_review_count": "8", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Standard", 
                    "artist_name": "", 
                    "sale_price": "149.99", 
                    "product_id": "1218177249463", 
                    "customer_review_average": "4.8", 
                    "name": "Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9757802&type=product&id=1218177249463&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9757802"
                  }, 
                  "added": "1280005937.0", 
                  "fulfilled": "False", 
                  "max_price": "100.00"
                }
              ], 
              "bought": [
                {
                  "sale_price": "639.99", 
                  "product": {
                    "regular_price": "729.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9539154", 
                    "num_bought": "0", 
                    "on_sale": false, 
                    "customer_review_count": "61", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9539/9539154_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Everyday Laptops", 
                    "artist_name": "", 
                    "sale_price": "729.99", 
                    "product_id": "1218120538238", 
                    "customer_review_average": "4.0", 
                    "name": "Dell Studio Laptop with Intel&#174; Core&#153;2 Duo Processor - Midnight Blue", 
                    "url": "", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9539/9539154fp.gif", 
                    "album_title": "", 
                    "cart_url": ""
                  }, 
                  "unit_quantity": "1", 
                  "purchase_date": "1280005931.0", 
                  "source": "Store"
                }, 
                {
                  "sale_price": "199.99", 
                  "product": {
                    "regular_price": "26.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "8310847", 
                    "num_bought": "0", 
                    "on_sale": true, 
                    "customer_review_count": "41", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/8310/8310847_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Secure Digital", 
                    "artist_name": "", 
                    "sale_price": "14.99", 
                    "product_id": "1173578368387", 
                    "customer_review_average": "3.8", 
                    "name": "PNY 4GB Secure Digital High Capacity Memory Card", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=8310847&type=product&id=1173578368387&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/8310/8310847fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=8310847"
                  }, 
                  "unit_quantity": "1", 
                  "purchase_date": "1280005928.0", 
                  "source": "Store"
                }, 
                {
                  "sale_price": "39.99", 
                  "product": {
                    "regular_price": "19.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9477005", 
                    "num_bought": "0", 
                    "on_sale": false, 
                    "customer_review_count": "4", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9477/9477005s.jpg", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Action & Adventure", 
                    "artist_name": "", 
                    "sale_price": "19.99", 
                    "product_id": "1218112360550", 
                    "customer_review_average": "3.5", 
                    "name": "James Cameron's Avatar: The Game - PSP", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9477005&type=product&id=1218112360550&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9477005"
                  }, 
                  "unit_quantity": "1", 
                  "purchase_date": "1280005928.0", 
                  "source": "Store"
                }
              ]
            }
            # if not friend, only show 3 purchases and 3 wishes
            
    """
    result = {}

    u = request.user
    other = Party.objects.get(id=request.POST['party_id'])
    if other in u.friends():
        # this other person is a friend so show all details
        bought = TransactionLineItem.objects.filter(transaction__party=other).order_by('-transaction__timestamp')
        wishes = Wishlist.objects.filter(party=other).order_by('-added')

        result['bought'] = [b.details() for b in bought[:10]]
        result['wished'] = [w.details() for w in wishes[:10]]
 
    else:
        # just show some details
        bought = TransactionLineItem.objects.filter(transaction__party=other).order_by('-transaction__timestamp')
        wishes = Wishlist.objects.filter(party=other).order_by('-added')

        result['bought'] = [b.details() for b in bought[:3]]
        result['wished'] = [w.details() for w in wishes[:3]]
    
    return JSONHttpResponse(result)
 

def item( u, sku ):

    result = {}

    p = Product.objects.get_by_sku(sku)
    if p is not None:
        result['item'] = p.details(u)
        # add to wish list?
        result['add_wish'] = ""
        result['ask_review'] = ""
        if Wishlist.objects.filter(product=p, party=u).count() > 0:
            # already added to wish list and review not requested
            wish = Wishlist.objects.filter(product=p, party=u)[0]
            result['wished'] = wish.get_wish_summary(u)
            if not ReviewRequest.objects.filter(requester=u, product=p).exists():
                result['ask_review'] = "/m/review/ask/"
        elif p.transactionlineitem_set.filter(transaction__party=u).count() == 0:
            # if not bought, you can add to wish list
            result['add_wish'] = "/m/wishlist/add/"

        result['add_review'] = ""
        if p.transactionlineitem_set.filter(transaction__party=u).count() > 0 and Review.objects.filter(product=p, reviewer=u).count() == 0:
            # if bought and not reviewed you can add review
            result['add_review'] = "/m/review/add/"
            
        reviews = Review.objects.filter(product=p)
        result['reviews'] = {'count': str(reviews.count()),
                            'reviews': [r.get_json(me=u) for r in reviews]}

    else:
        result['result'] = '0'

    return result

@never_cache
@csrf_exempt
@login_required
def item_from_browse(request):
    """
        Get specific item
        Accessed from search or browse

        :url: /m/item/browse/

        :param POST['sku']: Item SKU 
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if product doesn't exist
            {'result':'0'}

            # if product exists ("wished" key exists if item is wished by me already)
            {
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "regular_price": "39.99", 
                "bought_by": "2 people bought this", 
                "wished_by": "", 
                "num_requested": "0", 
                "sku": "9461076", 
                "num_bought": "2", 
                "on_sale": false, 
                "customer_review_count": "22", 
                "num_wished": "0", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9461/9461076s.jpg", 
                "new": false, 
                "review_request": "", 
                "category": "Action & Adventure", 
                "artist_name": "", 
                "sale_price": "39.99", 
                "product_id": "1218108383576", 
                "customer_review_average": "5.0", 
                "name": "Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3", 
                "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9461076&type=product&id=1218108383576&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                "medium_image": "", 
                "album_title": "", 
                "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9461076"
              }, 
              "add_review": "/m/review/add/", 
              "ask_review": "", 
              "add_wish": ""
            }    

    """

    result = item( request.user, request.POST['sku'] )

    return JSONHttpResponse(result)

@never_cache
@csrf_exempt
@login_required
def item_from_party(request):
    """
        Get specific item
        Accessed from a person's personal list of wish list or purchases

        :url: /m/item/party/

        :param POST['sku']: Item SKU 
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if product doesn't exist
            {'result':'0'}

            # if product exists ("wished" key exists if item is wished by me already)
            {
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "regular_price": "39.99", 
                "bought_by": "2 people bought this", 
                "wished_by": "", 
                "num_requested": "0", 
                "sku": "9461076", 
                "num_bought": "2", 
                "on_sale": false, 
                "customer_review_count": "22", 
                "num_wished": "0", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9461/9461076s.jpg", 
                "new": false, 
                "review_request": "", 
                "category": "Action & Adventure", 
                "artist_name": "", 
                "sale_price": "39.99", 
                "product_id": "1218108383576", 
                "customer_review_average": "5.0", 
                "name": "Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3", 
                "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9461076&type=product&id=1218108383576&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                "medium_image": "", 
                "album_title": "", 
                "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9461076"
              }, 
              "add_review": "/m/review/add/", 
              "ask_review": "", 
              "add_wish": ""
            }    

    """

    result = item( request.user, request.POST['sku'] )

    return JSONHttpResponse(result)

@never_cache
@csrf_exempt
@login_required
def item_from_feed(request):
    """
        Get specific item from the feed

        :url: /m/item/feed/

        :param POST['sku']: Item SKU 
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if product doesn't exist
            {'result':'0'}

            # if product exists
            {
              "wished": {
                "wish_id": "1", 
                "comment": "This is awesome", 
                "added": "1273123728.0", 
                "fulfilled": "False", 
                "new_reviews": "0", 
                "party": {
                  "first_name": "Kwan", 
                  "last_name": "Lee", 
                  "name": "Kwan Hong Lee", 
                  "alias": "kool", 
                  "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5", 
                  "phone": "", 
                  "first_joined": "1267990187.0", 
                  "id": "2"
                }, 
                "pending": "0",
                "max_price": "100.00"
              }, 
              "add_wish": "", 
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "sku": "9757802", 
                "category": "Standard", 
                "customer_review_average": "4.5", 
                "product_id": "1218177249463", 
                "regular_price": "169.99", 
                "num_bought": "0", 
                "new": false, 
                "bought_by": "", 
                "wished_by": "Wished by Ben", 
                "on_sale": true, 
                "artist_name": "", 
                "num_wished": "1", 
                "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802fp.gif", 
                "num_requested": "0", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802_s.gif", 
                "album_title": "", 
                "sale_price": "149.99", 
                "customer_review_count": "4", 
                "review_request": "", 
                "name": "Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue"
              }, 
              "add_review": "", 
              "ask_review": "/m/review/ask/"
            }
    """

    result = item( request.user, request.POST['sku'] )

    return JSONHttpResponse(result)

@never_cache
@csrf_exempt
@login_required
def item_from_friends(request):
    """
        Get specific item from a person's own list of wishlist and purchases

        :url: /m/item/friends/

        :param POST['sku']: Item SKU 
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if product doesn't exist
            {'result':'0'}

            # if product exists
            {
              "wished": {
                "wish_id": "1", 
                "comment": "This is awesome", 
                "added": "1273123728.0", 
                "fulfilled": "False", 
                "new_reviews": "0", 
                "party": {
                  "first_name": "Kwan", 
                  "last_name": "Lee", 
                  "name": "Kwan Hong Lee", 
                  "alias": "kool", 
                  "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5", 
                  "phone": "", 
                  "first_joined": "1267990187.0", 
                  "id": "2"
                }, 
                "max_price": "100.00"
                "pending": "0",
              }, 
              "add_wish": "", 
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "sku": "9757802", 
                "category": "Standard", 
                "customer_review_average": "4.5", 
                "product_id": "1218177249463", 
                "regular_price": "169.99", 
                "num_bought": "0", 
                "new": false, 
                "bought_by": "", 
                "wished_by": "Wished by Ben", 
                "on_sale": true, 
                "artist_name": "", 
                "num_wished": "1", 
                "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802fp.gif", 
                "num_requested": "0", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802_s.gif", 
                "album_title": "", 
                "sale_price": "149.99", 
                "customer_review_count": "4", 
                "review_request": "", 
                "name": "Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue"
              }, 
              "add_review": "", 
              "ask_review": "/m/review/ask/"
            }
    """

    result = item( request.user, request.POST['sku'] )

    return JSONHttpResponse(result)



@never_cache
@csrf_exempt
@login_required
def item_from_purchases(request):
    """
        Item view like :meth:`item()` that shows when you click an item from purchase history

        Add a review
        Details
        What others have done
        
        :url: /m/item/purchases/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if user never bought this item
            {'result':'-1'}

            # if product does not exist
            {'result':'0'}

            # if bought, returns product details
            {
              "wished": {
                "wish_id": "5", 
                "comment": "This is awesome", 
                "added": "1280005937.0", 
                "fulfilled": "False", 
                "new_reviews": "0", 
                "party": {
                  "alias": "ben.viralington", 
                  "first_joined": "1280005924.0", 
                  "id": "2", 
                  "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                  "name": "Anonymous"
                }, 
                "max_price": "100.00", 
                "pending": "0"
              }, 
              "add_wish": "", 
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "regular_price": "169.99", 
                "bought_by": "", 
                "wished_by": "2 people want this", 
                "num_requested": "0", 
                "sku": "9757802", 
                "num_bought": "0", 
                "on_sale": true, 
                "customer_review_count": "8", 
                "num_wished": "2", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802_s.gif", 
                "new": false, 
                "review_request": "", 
                "category": "Standard", 
                "artist_name": "", 
                "sale_price": "149.99", 
                "product_id": "1218177249463", 
                "customer_review_average": "4.8", 
                "name": "Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue", 
                "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9757802&type=product&id=1218177249463&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802fp.gif", 
                "album_title": "", 
                "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9757802"
              }, 
              "add_review": "", 
              "ask_review": "/m/review/ask/"
            }
    """

    result = item( request.user, request.POST['sku'] )

    return JSONHttpResponse(result)



@never_cache
@csrf_exempt
@login_required
def item_from_wishlist(request):
    """
        Similar to :meth:`item()` view but have option of request for 
        review (solicitation, friend's reactions, feedback)

        Alert if price drop option

        Set max_price

        :url: /m/item/wishlist/

        :param POST['sku']: item ID 
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # user never had item on wish list
            {'result': '-1'}

            # product is not found
            {'result': '0'}

            # if wished return product details
            {
              "wished": {
                "wish_id": "10", 
                "comment": "I want this for Thanksgiving!!", 
                "added": "1280005948.0", 
                "fulfilled": "False", 
                "new_reviews": "0", 
                "party": {
                  "alias": "ben.viralington", 
                  "first_joined": "1280005924.0", 
                  "id": "2", 
                  "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                  "name": "Anonymous"
                }, 
                "max_price": "122.00", 
                "pending": "0"
              }, 
              "add_wish": "", 
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "regular_price": "149.99", 
                "bought_by": "", 
                "wished_by": "", 
                "num_requested": "0", 
                "sku": "9051036", 
                "num_bought": "0", 
                "on_sale": true, 
                "customer_review_count": "0", 
                "num_wished": "0", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9051/9051036_r.gif", 
                "new": false, 
                "review_request": "", 
                "category": "Laptop Batteries", 
                "artist_name": "", 
                "sale_price": "127.49", 
                "product_id": "1218012528492", 
                "customer_review_average": "0.0", 
                "name": "Lenmar Battery for Select Toshiba Laptops", 
                "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9051036&type=product&id=1218012528492&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9051/9051036fp.gif", 
                "album_title": "", 
                "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9051036"
              }, 
              "add_review": "", 
              "ask_review": "/m/review/ask/"
            }
    """

    result = item( request.user, request.POST['sku'] )

    return JSONHttpResponse(result)


@csrf_exempt
@login_required
def item_from_request(request):
    """
        Item view when one can add review.
        It can come from Home - Yod is requesting a review for this item
        or it can come from Purchase History/Item/Add Review 

        No need to show "Add to wish list" button since already bought

        :url: /m/item/request/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if user never bought this item
            {'result':'-1'}

            # if product does not exist
            {'result':'0'}

            # if bought, returns product details
            {
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "item": {
                "regular_price": "39.99", 
                "bought_by": "2 people bought this", 
                "wished_by": "", 
                "num_requested": "0", 
                "sku": "9461076", 
                "num_bought": "2", 
                "on_sale": false, 
                "customer_review_count": "22", 
                "num_wished": "0", 
                "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9461/9461076s.jpg", 
                "new": false, 
                "review_request": "", 
                "category": "Action & Adventure", 
                "artist_name": "", 
                "sale_price": "39.99", 
                "product_id": "1218108383576", 
                "customer_review_average": "5.0", 
                "name": "Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3", 
                "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9461076&type=product&id=1218108383576&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                "medium_image": "", 
                "album_title": "", 
                "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9461076"
              }, 
              "add_review": "/m/review/add/", 
              "ask_review": "", 
              "add_wish": ""
            }
    """

    result = item( request.user, request.POST['sku'] )

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def item_view_bought(request):
    """
        When user clicks 
        
            * 3 people bought, 
            * Bought by John, Ben
            * 5 friends bought

        it shows details of what they think about these items

        :url: /m/item/view/bought/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if in experiment 1 or 3 'people' field wouldn't have
            # first_name, last_name and phone

            # if in experiment 2, 4
            {
              "people": [
                {
                  "first_name": "Ben", 
                  "last_name": "Viralington", 
                  "name": "Ben", 
                  "alias": "ben.viralington", 
                  "image": "", 
                  "phone": "", 
                  "first_joined": "1273119474.0", 
                  "id": "3"
                }
              ] 
            }    

            # if in experiment 1, 3
            {
              "people": [
                {
                  "alias": "ben.viralington", 
                  "first_joined": "1279683812.0", 
                  "id": "2", 
                  "image": "", 
                  "name": "Anonymous"
                }
              ]
            }

    """

    r = {}
    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])
    if p is not None:
        #r = p.details(u)

        if u.experiment.id in [1,3]:
            purchases = TransactionLineItem.objects.filter(product=p).exclude(transaction__party=u)
            r['people'] = [pu.transaction.party.get_json() for pu in purchases]
        else:
            purchases = TransactionLineItem.objects.filter(product=p, transaction__party__in=u.friends()).exclude(transaction__party=u)
            r['people'] = [pu.transaction.party.get_json(level=1) for pu in purchases]

        #reviews = Review.objects.filter(product=p)
        #r['reviews'] = {'count': str(reviews.count()),
        #                         'reviews': [rev.get_json(me=u) for rev in reviews]}
    else:
        r['result'] = '0'

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def item_view_wished(request):
    """
        When user clicks 

            * 3 people wished, 
            * Wished by John, Ben
            * 5 friends wish 

        it shows details of what they think about these items

        :url: /m/item/view/wished/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude


        :rtype: JSON

        ::

            {
              "wished": [
                {
                  "wish_id": "7", 
                  "comment": "This is awesome", 
                  "added": "1279683826.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "alias": "niwen.chang", 
                    "first_joined": "1279683812.0", 
                    "id": "3", 
                    "image": "", 
                    "name": "Anonymous"
                  }, 
                  "max_price": "100.00"
                }, 
                {
                  "wish_id": "4", 
                  "comment": "I want this for Thanksgiving!!", 
                  "added": "1279683824.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1279683812.0", 
                    "id": "2", 
                    "image": "", 
                    "name": "Anonymous"
                  }, 
                  "max_price": "122.00"
                }
              ]
            }

    """
    r = {}
    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])
    if p is not None:
        #r = p.details(u)

        wished = Wishlist.objects.filter(product=p).exclude(party=u)
        r['wished'] = [w.get_json(me=u) for w in wished]
    else:
        r['result'] = '0'

    return JSONHttpResponse(r)

@csrf_exempt
@login_required
def item_view_reviews(request):
    """
        For showing reviews by anonymous public or friend reviews
        Put reviews that are response to request at the top 
        and there will be other reviews

        :url: /m/item/view/reviews/

        :param POST['sku']: sku of Item
        :param POST['lat']: latitude
        :param POST['lon']: longitude
        :param POST['page']: page num

        :rtype: JSON

        ::

            # if product does not exist
            {'result': '0'}

            # return reviews for this product
            # experiment group 2, 4 will have first_name and last_name fields also in reviewer

            {
              "count": "1", 
              "reviews": [
                {
                  "replied": false, 
                  "rating": "3", 
                  "review_id": "4", 
                  "content": "This is a must buy!!", 
                  "reviewer": {
                    "alias": "ben.viralington", 
                    "first_joined": "1279683812.0", 
                    "id": "2", 
                    "image": "", 
                    "name": "Anonymous"
                  }, 
                  "viewed": "0", 
                  "posted": "1279683840.0"
                }
              ]
            }

    """

    result = {}
    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])
    if p is not None:
        # product details are not needed
        #result = p.details(u)

        reviews = Review.objects.filter(product=p).exclude(reviewer=u)
        result['count'] = str(reviews.count())
        result['reviews'] = [r.get_json(me=u) for r in reviews]
    else:
        result['result'] = '0'

    return JSONHttpResponse(result)


@csrf_exempt
@login_required
def item_view_bestbuy_reviews(request):
    """
        Return reviews from BestBuy for specific items

        :TODO: Need to figure out how to get reviews from BestBuy

        :url: /m/item/view/bb_reviews/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            {
              "regular_price": "649.99", 
              "bought_by": "", 
              "wished_by": "", 
              "num_requested": "0", 
              "sku": "9723733", 
              "num_bought": "0", 
              "on_sale": false, 
              "customer_review_count": "10", 
              "num_wished": "0", 
              "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9723/9723733_s.gif", 
              "new": false, 
              "review_request": "", 
              "category": "Everyday Laptops", 
              "artist_name": "", 
              "sale_price": "649.99", 
              "product_id": "1218159864039", 
              "customer_review_average": "4.2", 
              "name": "Sony VAIO Laptop with Intel&#174; Core&#153;2 Duo Processor - Brown", 
              "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9723733&type=product&id=1218159864039&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
              "reviews": [], 
              "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9723/9723733fp.gif", 
              "album_title": "", 
              "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9723733"
            }

    """
    r = {}
    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])
    if p is not None:
        r = p.details(u)

        r['reviews'] = []
    else:
        r['result'] = '0'

    return JSONHttpResponse(r)



@csrf_exempt
@login_required
def wishlist_add(request):
    """
        Add item to wish list

        :url: /m/wishlist/add/

        :param POST['sku']: sku of item 
        :param POST['comment']: post "" if not specified.  Any comment user adds about wish item
        :param POST['max_price']: post '0.00' if not specified 
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # return the new id in wishlist > 0
            {'result': '5'}

            # return if product does not exist
            {'result': '0'}

            # already on wish list
            {'result': '-1'}

    """

    result = {}

    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])

    if p is None:
        result["result"] = '0'
    else:
        w, created = Wishlist.objects.get_or_create(party=u, product=p)
        if created:
            w.comment=request.POST['comment']
            w.max_price=float(request.POST['max_price'])
            w.save() 
            result["result"] = str(w.id)
        else:
            result["result"] = '-1'
            
        # add a feed
        f = Feed(actor=u, action=Feed.WISHLIST, product=p) 
        f.save()
 
    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def wish_item_update(request):
    """
        Update comment or max price on wish item

        :url: /m/wishlist/item/update/

        :param POST['wish_id']: wish item ID
        :param POST['comment']: comment
        :param POST['max_price']: max_price

        :rtype: JSON

        ::

            # if wish item does not exist or you don't own this on your wish list
            {'result': '-1'}     
            # updated wish_id
            {'result': '6'}
    """
    result = {}

    u = request.user

    try:
        w = Wishlist.objects.get(party=u, id=int(request.POST['wish_id']))
    except Wishlist.DoesNotExist:
        result["result"] = '-1'
        return JSONHttpResponse(result)

    comment = request.POST.get('comment', None)
    if comment:
        w.comment = comment
    max_price = request.POST.get('max_price', None)
    if max_price:
        w.max_price = max_price
    w.save()

    result["result"] = str(w.id)

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def review_ask(request):
    """
        Ask for item review

        :url: /m/review/ask/

        :param POST['sku']: sku of item
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if product does not exist
            {'result': '0'}

            # I don't have this item on wish list
            {'result': '-1'}

            # else, newly created Request Review object ID
            {'result': '7'}
    """

    result = {}
    u = request.user
    p = Product.objects.get_by_sku(request.POST['sku'])

    if p is None:
        result["result"] = '0'

    # change wish review request pending status
    for w in Wishlist.objects.filter(product=p, party=u):
        w.review = Wishlist.REVIEW_REQUESTED 
        w.save()

    req, created = ReviewRequest.objects.get_or_create(requester=u, product=p)

    # could replace above line with these lines if it causes trouble
    #if not ReviewRequest.objects.filter(requester=u.party, product=p).exists():
    #    r = ReviewRequest(requester=u.party, product=p)
    #    r.save()

    # any previous reviews related to this request is linked
    for rev in Review.objects.filter(product=p):
        rev.reply_to.add(req)

    result['result'] = str(req.id)

    # add a feed
    f = Feed(actor=u, action=Feed.REQUESTED, product=p) 
    f.save()

    # TODO: notify others that review requested

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def review_add(request):
    """
        Add a review to an item

        :url: /m/review/add/

        :param POST['sku']: sku of item
        :param POST['lat']: latitude
        :param POST['lon']: longitude
        :param POST['reply_to']: ReviewRequest ID that review is replying to, don't send this
                                if not replying to anything
        :param POST['rating']: rating 0-5  (0 is not rated)
        :param POST['content']: content of review 
        :param POST['public']: 'true' (if public), 'false' if not

        :rtype: JSON

        ::

            # if product does not exist
            {'result': '0'}

            # I don't own this item 
            {'result': '-1'}

            # else, newly created Review object ID
            {'result': '7'}
    """
    result = {}

    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])

    if p is None:
        result["result"] = '0'
    elif TransactionLineItem.objects.filter(transaction__party=u, product=p).count() > 0:
        # need to check if I bought this item

        r, created = Review.objects.get_or_create(reviewer=u, product=p)
        r.content =request.POST['content']
        r.rating=int(request.POST['rating'])

        # reply to review request
        rto = request.POST.get('reply_to', None)
        if rto:
            rev_request = ReviewRequest.objects.get(id=int(rto))
            r.reply_to.add(rev_request)
            # change wish item review status to review=2
            for w in Wishlist.objects.filter(product=p, party=rev_request.requester):
                w.review = Wishlist.REVIEW_RESPONDED
                w.save()
        
        r.public = bool(request.POST['public'])
        r.save() 

        # add a feed
        f = Feed(actor=u, action=Feed.REVIEWED, product=p) 
        f.save()
        
        result["result"] = str(r.id)
    else:
        result['result'] = '-1'

    return JSONHttpResponse(result)



@csrf_exempt
@login_required
def review_read(request):
    """
        Read a review so show details of review

        :url: /m/review/read/

        :param POST['review_id']: id of the review
        :param POST['lat']: latitude
        :param POST['lon']: longitude



        :rtype: JSON

        ::
            
            # if review does not exist
            {}

            # else
            {
              "replied": false, 
              "rating": "3", 
              "review_id": "4", 
              "content": "This is a must buy!!", 
              "reviewer": {
                "alias": "kool", 
                "first_joined": "1267990187.0", 
                "id": "2", 
                "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5"
              }, 
              "viewed": "0", 
              "posted": "1273123739.0"
            }    

    """
    u = request.user

    result = {}
    try:
        review = Review.objects.get(id=request.POST['review_id'])
        result = review.get_json(me=u)
        review.viewed_by.add(u)
    except Review.DoesNotExist:
        pass 
    
    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def view_friends_bought(request):
    """
        Shows friends who bought the item and their reviews
        The iphone will show each in a cell and allow to click to see full review

        :url: /m/friends/bought/

        :param POST['sku']: item sku 
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if product doesn't exist
            {'result': '0'}

            # review of friends
            {
              "count": "1", 
              "reviews": [
                {
                  "replied": true, 
                  "rating": "0", 
                  "review_id": "1", 
                  "content": "It's a really nice catch", 
                  "reviewer": {
                    "alias": "ben.viralington", 
                    "first_joined": "1273123721.0", 
                    "id": "3", 
                    "image": ""
                  }, 
                  "viewed": "1", 
                  "posted": "1273123731.0"
                }
              ]
            }
    """

    result = {}

    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])
    if p is not None:
        my_friends = u.friends()
        #print my_friends
        reviews = Review.objects.filter(product=p, reviewer__in=my_friends)
        result['count'] = str(reviews.count())
        result['reviews'] = [r.get_json(me=u) for r in reviews]
    else:
        result['result'] = '0'

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def view_friends_wish(request):
    """
        Shows friends that wish this item and their comments
        The iPhone will show each in a cell and allow to click to see full comment

        :url: /m/friends/wish/

        :param POST['sku']: item sku 
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            {
              "wishes": [
                {
                  "wish_id": "4", 
                  "comment": "This is awesome", 
                  "added": "1273123730.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "first_name": "Ben", 
                    "last_name": "Viralington", 
                    "name": "Ben", 
                    "alias": "ben.viralington", 
                    "image": "", 
                    "phone": "", 
                    "first_joined": "1273123721.0", 
                    "id": "3"
                  }, 
                  "max_price": "100.00"
                }
              ]
            }  
    """

    result = {}

    u = request.user

    my_friends = u.friends()
    logger.debug("Friends of %s: %s"%(u,my_friends))
    wishes = Wishlist.objects.filter(product__sku=int(request.POST['sku']), party__in=my_friends)
    result['wishes'] = [w.get_json(me=u) for w in wishes]

    return JSONHttpResponse(result)

       

@csrf_exempt
@login_required
def search(request):
    """
        View for searching, 

        :url: /m/search/

        :param POST['search']: search query, sku, name
        :param POST['page']: page number
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            {
              "total_pages": 15, 
              "products": [
                {
                  "regular_price": "94.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "1004895", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "0", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/1004/1004895_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "USB Cables & Hubs", 
                  "artist_name": "", 
                  "sale_price": "94.99", 
                  "product_id": "1218207655369", 
                  "customer_review_average": "0.0", 
                  "name": "Apricorn NetDock 4-Port USB Laptop Hub with Optical Drive - Black", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=1004895&type=product&id=1218207655369&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/1004/1004895fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=1004895"
                }, 
                {
                  "regular_price": "349.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9980759", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "0", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9980/9980759_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "349.99", 
                  "product_id": "1218204944002", 
                  "customer_review_average": "0.0", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - Black", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9980759&type=product&id=1218204944002&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9980/9980759fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9980759"
                }, 
                {
                  "regular_price": "249.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9965963", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "0", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9965/9965963_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "249.99", 
                  "product_id": "1218202474601", 
                  "customer_review_average": "0.0", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - Black", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9965963&type=product&id=1218202474601&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9965/9965963fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9965963"
                }, 
                {
                  "regular_price": "349.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9966726", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "4", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9966/9966726_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "349.99", 
                  "product_id": "1218202948227", 
                  "customer_review_average": "5.0", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - Black Aluminum", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9966726&type=product&id=1218202948227&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9966/9966726fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9966726"
                }, 
                {
                  "regular_price": "349.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9966308", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "2", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9966/9966308_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "349.99", 
                  "product_id": "1218202473595", 
                  "customer_review_average": "5.0", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - Deep Red", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9966308&type=product&id=1218202473595&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9966/9966308fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9966308"
                }, 
                {
                  "regular_price": "299.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9705433", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "56", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9705/9705433_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "299.99", 
                  "product_id": "1218154378164", 
                  "customer_review_average": "4.3", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - Midnight Blue", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9705433&type=product&id=1218154378164&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9705/9705433fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9705433"
                }, 
                {
                  "regular_price": "249.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9982578", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "1", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9982/9982578_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "249.99", 
                  "product_id": "1218205381903", 
                  "customer_review_average": "5.0", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - Midnight Blue", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9982578&type=product&id=1218205381903&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9982/9982578fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9982578"
                }, 
                {
                  "regular_price": "249.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9981921", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "0", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9981/9981921_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "249.99", 
                  "product_id": "1218205381691", 
                  "customer_review_average": "0.0", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - Pink", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9981921&type=product&id=1218205381691&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9981/9981921fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9981921"
                }, 
                {
                  "regular_price": "349.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9980777", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "0", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9980/9980777_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "349.99", 
                  "product_id": "1218204945072", 
                  "customer_review_average": "0.0", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - White", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9980777&type=product&id=1218204945072&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9980/9980777fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9980777"
                }, 
                {
                  "regular_price": "379.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "1018325", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "0", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/1018/1018325_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "See All Netbooks", 
                  "artist_name": "", 
                  "sale_price": "379.99", 
                  "product_id": "1218210033545", 
                  "customer_review_average": "0.0", 
                  "name": "Asus Eee PC Netbook / Intel&#174; Atom&#153; Processor / 10.1\" Display / 1GB Memory - White Aluminum", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=1018325&type=product&id=1218210033545&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/1018/1018325fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=1018325"
                }
              ]
            }    

    """

    result = {'products':[]}

    u = request.user

    query = request.POST['search'].lower().strip()
    page = request.POST.get('page', 1)

    if re.match("\d+", query):
        # if number
        p = Product.objects.get_by_sku(query)
        if p is None:
            p = Product.object.get_by_upc(query)
        
        if p is not None:
            result['products'] = [p.details(u)]
    else:
        # do free text search
        result = Product.objects.search( query, page, u )
    
    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def scan_item(request):
    """
        Called after an item is scanned and returns search results 
        of scanning an item

        :url: /m/scan/

        :param POST['sku']: bar code, sku, name, if upc is received, it will also check for it
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if product does not exist
            {'products': []}

            # if exists
            {
              "products": [
                {
                  "regular_price": "39.99", 
                  "bought_by": "2 people bought this", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9461076", 
                  "num_bought": "2", 
                  "on_sale": false, 
                  "customer_review_count": "22", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9461/9461076s.jpg", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Action & Adventure", 
                  "artist_name": "", 
                  "sale_price": "39.99", 
                  "product_id": "1218108383576", 
                  "customer_review_average": "5.0", 
                  "name": "Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9461076&type=product&id=1218108383576&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9461076"
                }
              ]
            }
    """
    result = {'products':[]}
    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])
    if p is None:
        p = Product.objects.get_by_upc(request.POST['sku'])
     
    if p is not None:
        result['products'] = [p.details(u)]

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def browse_categories(request):
    """
        Should display categories alphabetically
        and also have What's Hot at the top

        :url: /m/browse/categories/

        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::
    
            {
              "categories": [
                {
                  "num_children": "13", 
                  "category_id": "abcat0010000", 
                  "id": "1", 
                  "name": "Gift Center"
                }, 
                {
                  "num_children": "8", 
                  "category_id": "abcat0100000", 
                  "id": "12", 
                  "name": "TV & Video"
                }, 
                {
                  "num_children": "8", 
                  "category_id": "abcat0200000", 
                  "id": "84", 
                  "name": "Audio"
                }, 
                {
                  "num_children": "9", 
                  "category_id": "abcat0300000", 
                  "id": "146", 
                  "name": "Car & GPS"
                }, 
                {
                  "num_children": "18", 
                  "category_id": "abcat0900000", 
                  "id": "154", 
                  "name": "Home & Appliances"
                }, 
                {
                  "num_children": "6", 
                  "category_id": "abcat0400000", 
                  "id": "206", 
                  "name": "Cameras & Camcorders"
                }, 
                {
                  "num_children": "13", 
                  "category_id": "abcat0500000", 
                  "id": "272", 
                  "name": "Computers"
                }, 
                {
                  "num_children": "2", 
                  "category_id": "abcat0600000", 
                  "id": "427", 
                  "name": "Music & Movies"
                }, 
                {
                  "num_children": "16", 
                  "category_id": "abcat0700000", 
                  "id": "428", 
                  "name": "Video Games & Gadgets"
                }, 
                {
                  "num_children": "8", 
                  "category_id": "abcat0800000", 
                  "id": "537", 
                  "name": "Mobile Phones & Office"
                }, 
                {
                  "num_children": "0", 
                  "category_id": "cat09000", 
                  "id": "1020", 
                  "name": "Gift Cards"
                }, 
                {
                  "num_children": "2", 
                  "category_id": "pcmcat144600050035", 
                  "id": "1047", 
                  "name": "More Categories"
                }, 
                {
                  "num_children": "10", 
                  "category_id": "pcmcat128500050004", 
                  "id": "1063", 
                  "name": "Name Brands"
                }, 
                {
                  "num_children": "5", 
                  "category_id": "pcmcat138100050018", 
                  "id": "1082", 
                  "name": "Geek Squad"
                }, 
                {
                  "num_children": "4", 
                  "category_id": "pcmcat139900050002", 
                  "id": "1105", 
                  "name": "Magnolia Home Theater"
                }, 
                {
                  "num_children": "1", 
                  "category_id": "pcmcat142300050026", 
                  "id": "1114", 
                  "name": "Outlet Center"
                }
              ]
            }
    """

    result = {}

    u = request.user

    top = Category.objects.get(name="Best Buy")
    result['categories'] = [c.get_json() for c in top.children.all()]
    
    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def browse_category(request):
    """
        Display child categories or items if no child categories 

        :url: /m/browse/category/

        :param POST['cat_id']: the id of category in WeBuy, not category_id (which is BestBuy category id)
        :param POST['page']: page number
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if there's sub category
            {
              "products": [], 
              "categories": [
                {
                  "num_children": "0", 
                  "category_id": "abcat0012004", 
                  "id": "4", 
                  "name": "Music, Movies & More"
                }
              ]
            }

            # if there are products
            {
              "total_pages": 1, 
              "products": [
                {
                  "regular_price": "399.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "8509438", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "82", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/8509/8509438_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Music, Movies & More", 
                  "artist_name": "", 
                  "sale_price": "399.99", 
                  "product_id": "1186005749503", 
                  "customer_review_average": "4.8", 
                  "name": "Bose&#174; SoundDock&#174; Portable Digital Music System for Apple&#174; iPod&#174; - Black", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=8509438&type=product&id=1186005749503&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/8509/8509438fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=8509438"
                }
              ]
            }
    """

    result = {'categories':[], 'products':[]}

    u = request.user

    page = request.POST.get('page', 1)

    cat = Category.objects.get(id=request.POST['cat_id'])
    if cat.children.count() > 0:
        result['categories'] = [c.get_json() for c in cat.children.all()]
    else:
        # display items
        result = Product.objects.filter_category(cat.category_id, page, u) 

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def browse_hot(request):
    """
        Display top 5 items that are wished, and top 5 items that are bought

        :url: /m/browse/hot/

        :param POST['page']: the page number
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            {
              "wished": [
                {
                  "regular_price": "169.99", 
                  "bought_by": "", 
                  "wished_by": "2 people want this", 
                  "num_requested": "0", 
                  "sku": "9757802", 
                  "num_bought": "0", 
                  "on_sale": true, 
                  "customer_review_count": "8", 
                  "num_wished": "2", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Standard", 
                  "artist_name": "", 
                  "sale_price": "149.99", 
                  "product_id": "1218177249463", 
                  "customer_review_average": "4.8", 
                  "name": "Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9757802&type=product&id=1218177249463&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9757802"
                }, 
                {
                  "regular_price": "39.99", 
                  "bought_by": "", 
                  "wished_by": "1 person want this", 
                  "num_requested": "0", 
                  "sku": "9209331", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "2", 
                  "num_wished": "1", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9209/9209331_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Boomboxes", 
                  "artist_name": "", 
                  "sale_price": "39.99", 
                  "product_id": "1218059404120", 
                  "customer_review_average": "2.0", 
                  "name": "Sony CD-R/RW Boombox with AM/FM Tuner - Pink", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9209331&type=product&id=1218059404120&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9209/9209331fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9209331"
                }, 
                {
                  "regular_price": "299.98", 
                  "bought_by": "", 
                  "wished_by": "1 person want this", 
                  "num_requested": "0", 
                  "sku": "9500453", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "4", 
                  "num_wished": "1", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9500/9500453_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Blu-ray Players", 
                  "artist_name": "", 
                  "sale_price": "299.98", 
                  "product_id": "1218115045351", 
                  "customer_review_average": "3.3", 
                  "name": "Sony Blu-ray Disc Player with 1080p Output", 
                  "url": "", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9500/9500453fp.gif", 
                  "album_title": "", 
                  "cart_url": ""
                }, 
                {
                  "regular_price": "169.99", 
                  "bought_by": "", 
                  "wished_by": "1 person want this", 
                  "num_requested": "0", 
                  "sku": "9746041", 
                  "num_bought": "0", 
                  "on_sale": false, 
                  "customer_review_count": "6", 
                  "num_wished": "1", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9746/9746041_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "", 
                  "artist_name": "", 
                  "sale_price": "169.99", 
                  "product_id": "1218166193361", 
                  "customer_review_average": "2.7", 
                  "name": "Sony bloggie High-Definition Digital Camcorder with 2.4\" LCD Monitor - Purple", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9746041&type=product&id=1218166193361&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9746/9746041fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9746041"
                }, 
                {
                  "regular_price": "149.99", 
                  "bought_by": "", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9051036", 
                  "num_bought": "0", 
                  "on_sale": true, 
                  "customer_review_count": "0", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9051/9051036_r.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Laptop Batteries", 
                  "artist_name": "", 
                  "sale_price": "127.49", 
                  "product_id": "1218012528492", 
                  "customer_review_average": "0.0", 
                  "name": "Lenmar Battery for Select Toshiba Laptops", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9051036&type=product&id=1218012528492&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9051/9051036fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9051036"
                }
              ], 
              "bought": [
                {
                  "regular_price": "19.99", 
                  "bought_by": "2 people bought this", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9477005", 
                  "num_bought": "2", 
                  "on_sale": false, 
                  "customer_review_count": "4", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9477/9477005s.jpg", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Action & Adventure", 
                  "artist_name": "", 
                  "sale_price": "19.99", 
                  "product_id": "1218112360550", 
                  "customer_review_average": "3.5", 
                  "name": "James Cameron's Avatar: The Game - PSP", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9477005&type=product&id=1218112360550&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9477005"
                }, 
                {
                  "regular_price": "39.99", 
                  "bought_by": "2 people bought this", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9461076", 
                  "num_bought": "2", 
                  "on_sale": false, 
                  "customer_review_count": "22", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9461/9461076s.jpg", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Action & Adventure", 
                  "artist_name": "", 
                  "sale_price": "39.99", 
                  "product_id": "1218108383576", 
                  "customer_review_average": "5.0", 
                  "name": "Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9461076&type=product&id=1218108383576&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9461076"
                }, 
                {
                  "regular_price": "19.99", 
                  "bought_by": "2 people bought this", 
                  "wished_by": "", 
                  "num_requested": "1", 
                  "sku": "9644845", 
                  "num_bought": "2", 
                  "on_sale": false, 
                  "customer_review_count": "1", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9644/9644845s.jpg", 
                  "new": false, 
                  "review_request": "1 person requested for review", 
                  "category": "Action & Adventure", 
                  "artist_name": "", 
                  "sale_price": "19.99", 
                  "product_id": "1218136348111", 
                  "customer_review_average": "4.0", 
                  "name": "Jak and Daxter: The Lost Frontier - PlayStation 2", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9644845&type=product&id=1218136348111&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9644845"
                }, 
                {
                  "regular_price": "26.99", 
                  "bought_by": "2 people bought this", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "8310847", 
                  "num_bought": "2", 
                  "on_sale": true, 
                  "customer_review_count": "41", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/8310/8310847_s.gif", 
                  "new": false, 
                  "review_request": "", 
                  "category": "Secure Digital", 
                  "artist_name": "", 
                  "sale_price": "14.99", 
                  "product_id": "1173578368387", 
                  "customer_review_average": "3.8", 
                  "name": "PNY 4GB Secure Digital High Capacity Memory Card", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=8310847&type=product&id=1173578368387&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/8310/8310847fp.gif", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=8310847"
                }, 
                {
                  "regular_price": "9.99", 
                  "bought_by": "2 people bought this", 
                  "wished_by": "", 
                  "num_requested": "0", 
                  "sku": "9704268", 
                  "num_bought": "2", 
                  "on_sale": false, 
                  "customer_review_count": "0", 
                  "num_wished": "0", 
                  "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9704/9704268s.jpg", 
                  "new": false, 
                  "review_request": "", 
                  "category": "PSP Movies", 
                  "artist_name": "", 
                  "sale_price": "9.99", 
                  "product_id": "1218153426006", 
                  "customer_review_average": "0.0", 
                  "name": "Clerks - UMD Video for Sony PSP", 
                  "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9704268&type=product&id=1218153426006&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                  "medium_image": "", 
                  "album_title": "", 
                  "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9704268"
                }
              ]
            }

    """

    result = {}

    u = request.user

    popular_products = TransactionLineItem.objects.values('product').annotate(num_bought=Count('product')).order_by('-num_bought')[:5] 
    popular_wishes = Wishlist.objects.values('product').annotate(num_wishes=Count('product')).order_by('-num_wishes')[:5]

    result['bought'] = [Product.objects.get(id=p['product']).details(u) for p in popular_products]

    result['wished'] = [Product.objects.get(id=p['product']).details(u) for p in popular_wishes]

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def view_purchases(request):
    """
        Purchase history view that shows when you bought the items
        It may show that someone would like review of it
        It also shows if friends have bought it if in social group

        :url: /m/purchases/

        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if no items
            {'bought': []}

            # else
            {
              "bought": [
                {
                  "product": {
                    "regular_price": "729.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9539154", 
                    "num_bought": "0", 
                    "on_sale": false, 
                    "customer_review_count": "61", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9539/9539154_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Everyday Laptops", 
                    "artist_name": "", 
                    "sale_price": "729.99", 
                    "product_id": "1218120538238", 
                    "customer_review_average": "4.0", 
                    "name": "Dell Studio Laptop with Intel&#174; Core&#153;2 Duo Processor - Midnight Blue", 
                    "url": "", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9539/9539154fp.gif", 
                    "album_title": "", 
                    "cart_url": ""
                  }, 
                  "source": "Store", 
                  "purchase_date": "1280005931.0", 
                  "sale_price": "639.99", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "unit_quantity": "1"
                }, 
                {
                  "product": {
                    "regular_price": "26.99", 
                    "bought_by": "2 people bought this", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "8310847", 
                    "num_bought": "2", 
                    "on_sale": true, 
                    "customer_review_count": "41", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/8310/8310847_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Secure Digital", 
                    "artist_name": "", 
                    "sale_price": "14.99", 
                    "product_id": "1173578368387", 
                    "customer_review_average": "3.8", 
                    "name": "PNY 4GB Secure Digital High Capacity Memory Card", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=8310847&type=product&id=1173578368387&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/8310/8310847fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=8310847"
                  }, 
                  "source": "Store", 
                  "purchase_date": "1280005928.0", 
                  "sale_price": "199.99", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "unit_quantity": "1"
                }, 
                {
                  "product": {
                    "regular_price": "19.99", 
                    "bought_by": "2 people bought this", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9477005", 
                    "num_bought": "2", 
                    "on_sale": false, 
                    "customer_review_count": "4", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9477/9477005s.jpg", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Action & Adventure", 
                    "artist_name": "", 
                    "sale_price": "19.99", 
                    "product_id": "1218112360550", 
                    "customer_review_average": "3.5", 
                    "name": "James Cameron's Avatar: The Game - PSP", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9477005&type=product&id=1218112360550&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9477005"
                  }, 
                  "source": "Store", 
                  "purchase_date": "1280005928.0", 
                  "sale_price": "39.99", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "unit_quantity": "1"
                }, 
                {
                  "product": {
                    "regular_price": "199.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "8246846", 
                    "num_bought": "0", 
                    "on_sale": false, 
                    "customer_review_count": "0", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/8246/8246846_r.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Amps", 
                    "artist_name": "", 
                    "sale_price": "199.99", 
                    "product_id": "1169512106756", 
                    "customer_review_average": "0.0", 
                    "name": "Sony Class AB 600W Bridgeable 4-Channel Marine Amplifier", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=8246846&type=product&id=1169512106756&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/8246/8246846fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=8246846"
                  }, 
                  "source": "Store", 
                  "purchase_date": "1280005928.0", 
                  "sale_price": "39.99", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "unit_quantity": "1"
                }, 
                {
                  "product": {
                    "regular_price": "649.99", 
                    "bought_by": "", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9723733", 
                    "num_bought": "0", 
                    "on_sale": false, 
                    "customer_review_count": "10", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9723/9723733_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Everyday Laptops", 
                    "artist_name": "", 
                    "sale_price": "649.99", 
                    "product_id": "1218159864039", 
                    "customer_review_average": "4.2", 
                    "name": "Sony VAIO Laptop with Intel&#174; Core&#153;2 Duo Processor - Brown", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9723733&type=product&id=1218159864039&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9723/9723733fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9723733"
                  }, 
                  "source": "Store", 
                  "purchase_date": "1280005928.0", 
                  "sale_price": "639.99", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "unit_quantity": "1"
                }, 
                {
                  "product": {
                    "regular_price": "19.99", 
                    "bought_by": "2 people bought this", 
                    "wished_by": "", 
                    "num_requested": "1", 
                    "sku": "9644845", 
                    "num_bought": "2", 
                    "on_sale": false, 
                    "customer_review_count": "1", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9644/9644845s.jpg", 
                    "new": false, 
                    "review_request": "1 person requested for review", 
                    "category": "Action & Adventure", 
                    "artist_name": "", 
                    "sale_price": "19.99", 
                    "product_id": "1218136348111", 
                    "customer_review_average": "4.0", 
                    "name": "Jak and Daxter: The Lost Frontier - PlayStation 2", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9644845&type=product&id=1218136348111&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9644845"
                  }, 
                  "source": "Store", 
                  "purchase_date": "1280005927.0", 
                  "sale_price": "99.99", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "unit_quantity": "1"
                }, 
                {
                  "product": {
                    "regular_price": "39.99", 
                    "bought_by": "2 people bought this", 
                    "wished_by": "", 
                    "num_requested": "0", 
                    "sku": "9461076", 
                    "num_bought": "2", 
                    "on_sale": false, 
                    "customer_review_count": "22", 
                    "num_wished": "0", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9461/9461076s.jpg", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Action & Adventure", 
                    "artist_name": "", 
                    "sale_price": "39.99", 
                    "product_id": "1218108383576", 
                    "customer_review_average": "5.0", 
                    "name": "Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9461076&type=product&id=1218108383576&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9461076"
                  }, 
                  "source": "Store", 
                  "purchase_date": "1280005927.0", 
                  "sale_price": "19.99", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "unit_quantity": "1"
                }
              ]
            }    

    """

    result = {'bought':[]}

    u = request.user

    bought = TransactionLineItem.objects.filter(transaction__party=u).order_by('-transaction__timestamp')

    result['bought'] = [b.get_json(level=1, me=u) for b in bought]
    
    return JSONHttpResponse(result)

@never_cache
@csrf_exempt
@login_required
def view_wishlist(request):
    """
        Shows list of items on wish list and comments
        people say about it
        If in social group, it says if friends also wish or have bought it

        :url: /m/wishlist/

        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            # if no items
            {'wishes': []}

            # else
            {
              "wishes": [
                {
                  "wish_id": "6", 
                  "comment": "This is what i really want", 
                  "product": {
                    "regular_price": "39.99", 
                    "bought_by": "", 
                    "wished_by": "1 person want this", 
                    "num_requested": "0", 
                    "sku": "9209331", 
                    "num_bought": "0", 
                    "on_sale": false, 
                    "customer_review_count": "2", 
                    "num_wished": "1", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9209/9209331_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Boomboxes", 
                    "artist_name": "", 
                    "sale_price": "39.99", 
                    "product_id": "1218059404120", 
                    "customer_review_average": "2.0", 
                    "name": "Sony CD-R/RW Boombox with AM/FM Tuner - Pink", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9209331&type=product&id=1218059404120&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9209/9209331fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9209331"
                  }, 
                  "added": "1280005938.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "removed": "False", 
                  "max_price": "155555.00", 
                  "pending": "0"
                }, 
                {
                  "wish_id": "5", 
                  "comment": "This is awesome", 
                  "product": {
                    "regular_price": "169.99", 
                    "bought_by": "", 
                    "wished_by": "2 people want this", 
                    "num_requested": "0", 
                    "sku": "9757802", 
                    "num_bought": "0", 
                    "on_sale": true, 
                    "customer_review_count": "8", 
                    "num_wished": "2", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Standard", 
                    "artist_name": "", 
                    "sale_price": "149.99", 
                    "product_id": "1218177249463", 
                    "customer_review_average": "4.8", 
                    "name": "Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue", 
                    "url": "http://www.bestbuy.com/site/olspage.jsp?skuId=9757802&type=product&id=1218177249463&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9757/9757802fp.gif", 
                    "album_title": "", 
                    "cart_url": "http://www.bestbuy.com/site/olspage.jsp?id=pcmcat152200050035&type=category&cmp=RMX&ky=2erUVvZJiTEW7AskaBED4Scv13ZEwmy2O&qvsids=9757802"
                  }, 
                  "added": "1280005937.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "removed": "False", 
                  "max_price": "100.00", 
                  "pending": "0"
                }, 
                {
                  "wish_id": "4", 
                  "comment": "This is awesome", 
                  "product": {
                    "regular_price": "299.98", 
                    "bought_by": "", 
                    "wished_by": "1 person want this", 
                    "num_requested": "0", 
                    "sku": "9500453", 
                    "num_bought": "0", 
                    "on_sale": false, 
                    "customer_review_count": "4", 
                    "num_wished": "1", 
                    "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9500/9500453_s.gif", 
                    "new": false, 
                    "review_request": "", 
                    "category": "Blu-ray Players", 
                    "artist_name": "", 
                    "sale_price": "299.98", 
                    "product_id": "1218115045351", 
                    "customer_review_average": "3.3", 
                    "name": "Sony Blu-ray Disc Player with 1080p Output", 
                    "url": "", 
                    "medium_image": "http://images.bestbuy.com/BestBuy_US/images/products/9500/9500453fp.gif", 
                    "album_title": "", 
                    "cart_url": ""
                  }, 
                  "added": "1280005937.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "alias": "ben.viralington", 
                    "first_joined": "1280005924.0", 
                    "id": "2", 
                    "image": "http://www.facebook.com/pics/t_silhouette.gif", 
                    "name": "Anonymous"
                  }, 
                  "removed": "False", 
                  "max_price": "100.00", 
                  "pending": "0"
                }
              ]
            }
    """
    result = {'wishes':[]}

    u = request.user

    wishes = Wishlist.objects.filter(party=u).exclude(fulfilled=True).order_by('-added') 

    result['wishes'] = [w.get_json(level=1, me=u) for w in wishes]

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def find_store(request):
    """
        Finds the store that has this item

        :url: /m/find/stores/

        :param POST['sku']: item you are interested in
        :param POST['lat']: current latitude
        :param POST['lon']: current longitude
        :param POST['distance']: the distance around this lat/lon

        :rtype: JSON

        ::  

            # sample query: 44.862858,-93.292763, 5
            # if no result 
            {'result':'-1'}

            # else
            {
              "result": {
                "city": "Richfield", 
                "postalCode": "55423", 
                "name": "Richfield", 
                "distance": 0.029999999999999999, 
                "country": "US", 
                "region": "MN", 
                "storeId": 281, 
                "hours": "Mon: 10-9; Tue: 10-9; Wed: 10-9; Thurs: 10-9; Fri: 9-9; Sat: 9-9; Sun: 10-7", 
                "phone": "612-861-3917", 
                "fullPostalCode": "55423", 
                "longName": "Best Buy - Richfield", 
                "lat": 44.863312000000001, 
                "lng": -93.292557000000002, 
                "address": "1000 West 78th St." 
              }
            }
        
    """
    r = {'result':'-1'}
    
    import httplib, urllib

    h = httplib.HTTPConnection("api.remix.bestbuy.com")
    lat = request.POST['lat']
    lon = request.POST['lon']
    distance = request.POST['distance']

    h.request('GET', '/v1/stores(area(%s,%s,%s))?format=json&apiKey=%s'%(lat, lon, distance, api_key))

    result = h.getresponse()
    logger.info( "BestBuy Location HTTP output: %s, reason: %s"%(result.status, result.reason) )
    response = json.loads(result.read())

    stores = response.get("stores", [])
    if len(stores) > 0: 
        r['result'] = stores[0]

    return JSONHttpResponse(r)


