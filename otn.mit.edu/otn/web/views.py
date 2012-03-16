# Create your views here.
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from finance import buxfer
from common.models import OTNUser, Friends
from survey.models import Survey
from facebookconnect.models import FacebookProfile
from django.conf import settings
from web.models import *
from web.forms import *
import hashlib
from datetime import date, datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from common.helpers import JSONHttpResponse, JSHttpResponse

logger = settings.LOGGER

GOOGLE_API_KEY = settings.GOOGLE_API_KEY

def index(request):
    """
        Index page showing public information 
    """
    data = {}
    data['GOOGLE_API_KEY'] = GOOGLE_API_KEY

    if request.user.is_authenticated():
        return HttpResponseRedirect("/home/")

    return render_to_response("web/index.html",
            data,
            context_instance=RequestContext(request))

@login_required
def home(request):
    """
        Home page showing personal information including
        public feeds, recent updates
    """
    data = {
        'username': request.user.username
    }
    data['GOOGLE_API_KEY'] = GOOGLE_API_KEY

    u = request.user

    try:
        fb_profile = u.facebook_profile
        data["fb_profile"] = fb_profile
    except FacebookProfile.DoesNotExist:
        return render_to_response("facebook/logout.html",
                                  data,
                                  context_instance=RequestContext(request)) 

    # if my friend list was never created, create one
    my, me_created = Friends.objects.get_or_create(facebook_id = fb_profile.facebook_id)
    if me_created:
        my.image = fb_profile.picture_url
        my.name = fb_profile.full_name
        my.save()

    # update friends list
    if me_created or my.last_update < datetime.now()-timedelta(14):
          
        # get Facebook friends
        friendList = request.user.facebook_profile.get_friends_profiles()
        logger.debug( "Facebook friends of %d: %s"%(fb_profile.facebook_id,str(friendList)) )
        for friend_info in friendList:
            friend, created = Friends.objects.get_or_create(facebook_id = friend_info['uid'])

            friend.image = friend_info['pic_square'] 
            friend.name = friend_info['name']
            friend.save()
            my.friends.add(friend)

    # get friends signed up
    participant_fb_ids = FacebookProfile.objects.all().values("facebook_id")
    friends_list = my.friends.filter(facebook_id__in=participant_fb_ids)
        
    data["friends_list"] = friends_list

    # get feeds
    data["feeds"] = Feed.objects.all().order_by("-timestamp")

    return render_to_response("web/home.html",
            data,
            context_instance=RequestContext(request))

@login_required
def feeds(request):
    """
        Feeds page showing private Feeds
    """
    data = {}

    return render_to_response("web/feeds.html",
            data,
            context_instance=RequestContext(request))


@login_required
def location(request, location_id):
    """
        Location information page

        :url: /location/(?P<location_id>\d+)/
    """
    u = request.user
    data = {}

    return render_to_response("web/location.html",
            data,
            context_instance=RequestContext(request))

@login_required
def coupons(request, location_id=0, page=1):
    """
        Coupons for a specific location
        
    """
    u = request.user
    data = {}

    return render_to_response("web/coupons.html",
            data,
            context_instance=RequestContext(request))

@login_required
def coupon(request):
    """
        Specific coupon information 
        
        :param POST["coupon_id"]: coupon ID
    """
    u = request.user
    data = {}

    return render_to_response("web/coupon.html",
            data,
            context_instance=RequestContext(request))


@login_required
def profile(request):
    """
        Show my profile 
    """
    u = request.user
    data = {}

    if request.method=="POST":
        if len(request.POST['first']) > 0:
            if request.POST['first'] == request.POST['second']:
                # change pin
                u.otnuser.pin = hashlib.sha224(request.POST['first']).hexdigest()
                u.otnuser.save()

                return JSONHttpResponse({'prompt': 'PIN has been updated', 'result': 1})
            
            else:
                return JSONHttpResponse({'prompt': 'PIN does not match, please re-enter', 'result': -1})

    else:
        return render_to_response("web/profile.html",
            data,
            context_instance=RequestContext(request))


@csrf_exempt
@login_required
def load_trans(request):
    """
        Loads Buxfer data given email and password
        
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
        
    if request.method == 'POST':
        u = request.user
        
        form = BuxferLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']

            b = buxfer.BuxferInterface()

            # pass username and password
            if b.buxfer_login(username, password):
            
                accts = b.get_accounts()
                for a in accts:
                    acct, created = Account.objects.get_or_create(user=u.otnuser, account_id=a['id'], name=a['name'], balance=a['balance'])
                    acct.save()
                    
                    final = 1 
                    p = 1   # page number
                    while final != 0:  
                        txns, final, total = b.get_transactions(a['id'], page=p)
                        # TODO: iterate through txns and insert into model
                        for t in txns:
                            m, created = Memo.objects.get_or_create(txt=t['description'])
                            m.save()
                            
                            trans, created = Transaction.objects.get_or_create(account=acct, amount="%.2f"%t['amount'], purchase_date=datetime.strptime(t['date']+" "+str(date.today().year), '%d %b %Y'), memo=m, transaction_id=t['id'])
                            trans.save()

                            r, created = Receipt.objects.get_or_create(txn=trans)
                            r.save()
                            
                        p += 1    # if no transactions are on page, then filter = len(response["transactions"]) = 0

                return JSONHttpResponse({'result':'1'})
        else:
            return JSONHttpResponse({'result':'0', 'error': form.errors})
    return JSONHttpResponse({'result':'-1', 'error':'Incorrect username or password.'})


@login_required
def transactions(request, sort="date_desc", page=1):
    """
        List of my transactions 

        :url: /transactions/(?P<page>\d+)/
    """
    u = request.user
    data = {}
    data['GOOGLE_API_KEY'] = GOOGLE_API_KEY

    txns = Transaction.objects.filter(account__user=u.otnuser).order_by("-purchase_date")

    paginator = Paginator(txns, 10)

    try:
        page = int(page)
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    try:
        txn_pages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        txn_pages = paginator.page(paginator.num_pages)

    data["transactions"] = txn_pages
    data["sort"] = sort

    return render_to_response("web/transactions.html",
            data,
            context_instance=RequestContext(request))

@login_required
def update_description(request):
    """

        :param POST['transaction_id']: the transaction I am modifying
        :param POST['description']: the detail

        :url: /web/update/description/

    """
    result = {'result':'0'}
    u = request.user

    if request.method == "POST":

        # get the transaction and description
        transaction_id = request.POST['transaction_id'].split('_')[1]
        description = request.POST['description']

        # see if the transaction belongs to the user.
        transaction = Transaction.objects.get(id = int(transaction_id))
        #logger.debug("Got transaction %d for %s"%(transaction.id, request.user.otnuser.name))
        #logger.debug("Modifying receipt for transaction %d"%transaction.id)
        receipt = transaction.receipt
        receipt.detail = description
        receipt.save()
        result['result'] = receipt.detail

        # add a feed
        f = Feed(actor=u.otnuser, action=Feed.REVIEWED, txn=transaction) 
        f.save()

    return HttpResponse(result['result'])

@login_required
def update_rating(request):
    """

        :param POST['transaction_id']: the transaction I am modifying
        :param POST['rating']: the rating value 

        :url: /web/update/rating/

    """

    result = {'result':'Not Rated'}
    u = request.user

    if request.method == "POST":

        # get the transaction and description
        transaction_id = request.POST['transaction_id']
        logger.debug("transaction_id:%s"%transaction_id)
        rating = request.POST['rating']

        # see if the transaction belongs to the user.
        transaction = Transaction.objects.get(id = int(transaction_id))
        #if transaction.account__user == request.user.otnuser:
        receipt = transaction.receipt
        receipt.rating = int(rating)
        receipt.save()
        result['result'] = receipt.RATING_CHOICES[receipt.rating][1]

        # add a feed
        f = Feed(actor=u.otnuser, action=Feed.RATED, txn=transaction) 
        f.save()

    return JSONHttpResponse(result)


@login_required
def user(request, user_id):
    """
        Shows user information

        :url: /user/(?P<user_id>\d+)/
    """
    data = {}
    u = request.user

    p = OTNUser.objects.get(id=user_id)

    #data["otnuser"] = OTNUser.objects.get(id=user_id)

    data['p'] = p
    data['fbuser'] = p.facebook_profile
    data['txns'] = Transaction.objects.filter(account__user=p).order_by("-purchase_date")[:3]
    
    # get friends
    participant_fb_ids = FacebookProfile.objects.all().values("facebook_id")
    my = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id)
    data['friends_list'] = my.friends.filter(facebook_id__in=participant_fb_ids)

    
    return render_to_response("web/user.html",
            data,
            context_instance=RequestContext(request))

@login_required
def friend(request, friend_id):
    """
        Shows friends information (purchases/wishes/reviews)

        :url: /friend/(?P<user_id>\d+)/
    """
    data = {}
    u = request.user
    
    f = Friends.objects.get(id=friend_id)
    
    p = OTNUser.objects.get(facebook_profile__facebook_id=f.facebook_id)

    #data["otnuser"] = OTNUser.objects.get(id=user_id)

    data['p'] = p
    data['fbuser'] = p.facebook_profile
    data['txns'] = Transaction.objects.filter(account__user=p).order_by("-purchase_date")[:3]
    
    # get friends
    participant_fb_ids = FacebookProfile.objects.all().values("facebook_id")
    my = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id)
    data['friends_list'] = my.friends.filter(facebook_id__in=participant_fb_ids)

    return render_to_response("web/user.html",
            data,
            context_instance=RequestContext(request))

@login_required
def winners(request):
    """
        Return winners

        :url: /winners/
    """
    data = {}
    u = request.user

    return render_to_response("web/winners.html",
            data,
            context_instance=RequestContext(request))

@login_required
def wishlist(request, page=1):
    data = {}
    u = request.user
    return render_to_response("web/wishlist.html",
            data,
            context_instance=RequestContext(request))

def otn_consent(request):
    data = {}
    u = request.user
    return render_to_response("web/otnconsent.html",
            data,
            context_instance=RequestContext(request))


def mobile(request):
    data = {}
    u = request.user
    
    if u.is_anonymous():
        data['log'] = False
    else:
        data['log'] = True
        
    return render_to_response('web/mobile.html', 
            data, context_instance=RequestContext(request))

def about(request):
    data = {}
    u = request.user
    
    if u.is_anonymous():
        data['log'] = False
    else:
        data['log'] = True
        
    return render_to_response('web/about.html', 
            data, context_instance=RequestContext(request))

def faq(request):
    data = {}
    u = request.user
    
    if u.is_anonymous():
        data['log'] = False
    else:
        data['log'] = True
        
    return render_to_response('web/faq.html', 
            data, context_instance=RequestContext(request))
