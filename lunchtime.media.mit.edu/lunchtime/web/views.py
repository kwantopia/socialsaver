from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template import RequestContext
from common.models import Friends, OTNUser, Location, SharingProfile, Winner
from facebookconnect.models import FacebookProfile
from django.contrib.auth.models import User
from common.helpers import JSONHttpResponse
from techcash.models import TechCashTransaction, TechCashBalance, Receipt
from finance.models import WesabeAccount
from survey.models import Survey 
import random, time, operator
import hashlib
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.views.decorators.cache import cache_control, never_cache
from web.models import HumanSubjectCompensation
from web.forms import HumanSubjectForm
from django.db.models import Sum

from mobile.models import *

logger = settings.LOGGER

GOOGLE_API_KEY = settings.GOOGLE_API_KEY

def index(request):
    """
        Index page showing public information 
    """
    data = {

    }

    if request.user.is_authenticated():
        return HttpResponseRedirect("/home/")

    return render_to_response("web2/index.html",
            data,
            context_instance=RequestContext(request))

@login_required
def home(request):
    """
        Displays the front page depending on whether the user is logged in 
        or not
    """
    fb_profile = ''
    friends_list = []
    transactions = []
    linked = {}
    surveys = []

    otnuser = request.user

    try:
        fb_profile = otnuser.facebook_profile
    except FacebookProfile.DoesNotExist:
        return render_to_response("web2/index.html",
                                  data,
                                  context_instance=RequestContext(request))

    transactions = TechCashTransaction.objects.filter(user = otnuser).order_by('-timestamp')[:3]
     
     
    # if my friend list was never created, create one
    my, me_created = Friends.objects.get_or_create(facebook_id = fb_profile.facebook_id)
    if me_created:
        my.image = fb_profile.picture_url
        my.name = fb_profile.full_name
        my.save()

    # if friend list update has been more than two weeks, update friends list
    if me_created or my.last_update < datetime.today()-timedelta(14):
          
        # get Facebook friends
        friendList = request.user.facebook_profile.get_friends_profiles()
        #logger.debug( "Facebook friends of %d: %s"%(fb_profile.facebook_id,str(friendList)) )
        for friend_info in friendList:
            friend, created = Friends.objects.get_or_create(facebook_id = friend_info['uid'])
            if created:
                friend.image = friend_info['pic_square'] 
                friend.name = friend_info['name']
                friend.save()
            my.friends.add(friend)

    # get friends signed up
    participant_fb_ids = FacebookProfile.objects.all().values("facebook_id")
    friends_list = my.friends.filter(facebook_id__in=participant_fb_ids)

    """
    # random sampling of friends
    if friends_list.count() > 10:
        random.seed(random.random())
        friends_list = random.sample(friends_list,10)
    """
    # get friends that transacted common transactions
    try:
        my = Friends.objects.get(facebook_id = fb_profile.facebook_id)
        if friends_list.count() > 0:
            friend_fb_ids = my.friends.values('facebook_id')
            for transaction in transactions:
                # Generate the friends list for the location
                friends = TechCashTransaction.objects.filter(location = transaction.location, user__facebook_profile__facebook_id__in = friend_fb_ids).values('user').distinct()
                transaction.friends = []
                for f in friends:
                    g = User.objects.get(id = f['user'])
                    friend = Friends.objects.get(facebook_id=g.facebook_profile.facebook_id)
                    transaction.friends.append(friend)
    except Friends.DoesNotExist:
        logger.debug("Displaying index page: User %d does not have any friends."%fb_profile.facebook_id)
        pass

    # Get latest surveys
    surveys = Survey.objects.filter(surveystatus__user = otnuser, surveystatus__completed = False)
    
    try:
        init_balance = TechCashBalance.objects.get(user=otnuser)
        linked['techcash'] = init_balance.initialized 
    except TechCashBalance.DoesNotExist:
        linked['techcash'] = False
    if WesabeAccount.objects.filter(user=otnuser).exists():
        linked['wesabe'] = True
    else:
        linked['wesabe'] = False

    stores = Location.objects.filter(type=Location.EATERY).count()
    people = OTNUser.objects.all().count()
    txns = TechCashTransaction.objects.all().count()

    winner = False 
    if Winner.objects.filter(user=otnuser).exists():
        winner = True

    return render_to_response(
        "web2/home.html",
        {
        'fbuser': fb_profile,
        'friends_list': friends_list,
        'transactions': transactions,
        'linked': linked,
        'surveys': surveys,
        'stores': stores,
        'people': people,
        'n_txns': txns,
        'winner': winner,
        'GOOGLE_API_KEY': GOOGLE_API_KEY
        },
        context_instance=RequestContext(request)
    )
  

@never_cache
@login_required
def profile(request):
    """
        GET: Shows profile
        POST: Updates PIN and default transaction sociability

        :url: /profile/

    """
    u = request.user
    fb_user = u.facebook_profile

    sharing = SharingProfile.objects.get(user=u)

    if request.method=="POST":
        # change default preferences for sharing
        sharing.general = int(request.POST['sharing'])
        sharing.save()

        if len(request.POST['first']) > 0:
            if request.POST['first'] == request.POST['second']:
                # change pin
                u.otnuser.pin = hashlib.sha224(request.POST['first']).hexdigest()
                u.otnuser.save()
            else:
                sharing = SharingProfile.objects.get(user=u)
                prompt = 'PIN does not match, please reenter'
                return render_to_response('web2/profile.html', 
                        {'prompt':prompt,
                        'fbuser': fb_user,
                        'sharing': sharing.general },
                        context_instance=RequestContext(request))
        # after POST changing sharing and PIN
        return HttpResponseRedirect("/home")
    else:
        return render_to_response(
            "web2/profile.html",
            {
                'fbuser': fb_user,
                'sharing': sharing.general,
            },
            context_instance=RequestContext(request)
        )

@login_required
def friends_transactions(request, friend_id):
    """
        Summarize friend's transactions
    """
    u = request.user
    data = {}

    
    # get friends
    participant_fb_ids = FacebookProfile.objects.all().values("facebook_id")
    my = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id)
    data['friends_list'] = my.friends.filter(facebook_id__in=participant_fb_ids)
    
    friend = Friends.objects.get(id=friend_id)
    data['f'] = friend
    otnuser = OTNUser.objects.get(facebook_profile__facebook_id=friend.facebook_id)
    # get all the location that the user has been to
    locations = TechCashTransaction.objects.filter(user=otnuser, location__type=Location.EATERY).order_by('location').values('location', 'location__name', 'location__icon').distinct()
    # for each location, need to get the number of transactions and the last
    # time they have been in that location  
    visits = []
    for l in locations:
        txns = TechCashTransaction.objects.filter(user=otnuser, location=l['location']).order_by('-timestamp')
        v = {}
        v['count'] = txns.count()
        v['latest'] = txns[0].timestamp 
        v['amount'] = txns.aggregate(Sum('amount'))['amount__sum']

        # get average rating
        receipts = Receipt.objects.filter(txn__user=otnuser, txn__location=l['location'])
        sum = receipts.aggregate(Sum('rating'))
        #print sum
        count = receipts.count()
        v['rating'] = int(round(sum['rating__sum']/float(count)))
        v['location'] = Location.objects.get(id=l['location']).get_json(level=1)
        visits.append( v )
    # sort by number of visits and change num of visits to string
    # reverse=True so in JSON it is sorted
    visits = sorted(visits, key=operator.itemgetter('amount'), reverse=True)

    data["visits"] = visits[:3]
    
    return render_to_response(
            "web2/friends_transactions.html",
            data,
            context_instance=RequestContext(request))

@login_required
def transactions(request, sort="date_desc", page=1):
    """
        Shows TechCASH transactions
        Sorts by date, alphabetical, amount, location, unrated
    """
    
    fb_profile = ''
    friends_list = ''
    transactions = ''
    if request.user.is_authenticated():
        otnuser = request.user
        fb_profile = otnuser.facebook_profile

        if sort == "date_asc":
            transactions = TechCashTransaction.objects.filter(user=otnuser).order_by('timestamp')
        elif sort == "date_desc":
            transactions = TechCashTransaction.objects.filter(user=otnuser).order_by('-timestamp')
        elif sort == "alph_asc":
            transactions = TechCashTransaction.objects.filter(user=otnuser).order_by('location__name')
        elif sort == "alph_desc":
            transactions = TechCashTransaction.objects.filter(user=otnuser).order_by('-location__name')
        elif sort == "amt_asc":
            transactions = TechCashTransaction.objects.filter(user=otnuser).order_by('amount')
        elif sort == "amt_desc":
            transactions = TechCashTransaction.objects.filter(user=otnuser).order_by('-amount')

        elif sort == "s0":
            transactions = TechCashTransaction.objects.filter(user=otnuser, receipt__sharing=0).order_by('-timestamp')
        elif sort == "s1":
            transactions = TechCashTransaction.objects.filter(user=otnuser, receipt__sharing=1).order_by('-timestamp')
        elif sort == "s2":
            transactions = TechCashTransaction.objects.filter(user=otnuser, receipt__sharing=2).order_by('-timestamp')
        elif sort == "s3":
            transactions = TechCashTransaction.objects.filter(user=otnuser, receipt__sharing=3).order_by('-timestamp')
        elif sort == "unrated":
            transactions = TechCashTransaction.objects.filter(user=otnuser, receipt__rating=0).order_by('-timestamp')
        else:
            if TechCashTransaction.objects.filter(user=otnuser, location__id=int(sort)).exists():
                transactions = TechCashTransaction.objects.filter(user=otnuser, location__id=int(sort)).order_by('-timestamp')
            
        paginator = Paginator(transactions, 3) # 3 transactions per page

        my = Friends.objects.get(facebook_id = fb_profile.facebook_id)
        friends_list = my.friends.all()

        if friends_list.count() > 10:
            random.seed(random.random())
            friends_list = random.sample(friends_list,10)

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
            "web2/transactions.html",
            {
            'fbuser': fb_profile,
            'friends_list': friends_list,
            'transactions': transactions,
            'sort':sort,
            },
            context_instance=RequestContext(request)
        )

@login_required
def update_description(request):
    """

        :param POST['transaction_id']: the transaction I am modifying
        :param POST['description']: the detail

        :url: /web2/update/description/

    """
    result = {'result':'0'}

    if request.user.is_authenticated() and request.method == "POST":

        # get the transaction and description
        transaction_id = request.POST['transaction_id'].split('_')[1]
        description = request.POST['description']

        # see if the transaction belongs to the user.
        transaction = TechCashTransaction.objects.get(id = int(transaction_id))
        #logger.debug("Got transaction %d for %s"%(transaction.id, request.user.otnuser.name))
        if transaction.user.id == request.user.id:
            #logger.debug("Modifying receipt for transaction %d"%transaction.id)
            receipt = transaction.receipt
            receipt.detail = description
            receipt.save()
            result['result'] = receipt.detail 

    return HttpResponse(result['result'])

@login_required
def update_rating(request):
    """

        :param POST['transaction_id']: the transaction I am modifying
        :param POST['rating']: the rating value 

        :url: /web2/update/rating/

    """

    result = {'result':'Not Rated'}

    if request.user.is_authenticated() and request.method == "POST":

        # get the transaction and description
        transaction_id = request.POST['transaction_id']
        logger.debug("transaction_id:%s"%transaction_id)
        rating = request.POST['rating']

        # see if the transaction belongs to the user.
        transaction = TechCashTransaction.objects.get(id = int(transaction_id))
        if transaction.user.id == request.user.id:
            receipt = transaction.receipt
            receipt.rating = int(rating)
            receipt.save()
            result['result'] = receipt.RATING_CHOICES[receipt.rating][1] 

    return JSONHttpResponse(result)
            
@login_required
def update_sharing(request):
    """

        :param POST['transaction_id']: the transaction I am modifying
        :param POST['sharing']: the sharing value 

        :url: /web2/update/sharing/

    """

    result = {'result':'Not updated'}

    if request.user.is_authenticated() and request.method == "POST":

        # get the transaction and description
        transaction_id = request.POST['transaction_id']
        logger.debug("update sharing - transaction_id:%s"%transaction_id)
        sharing = request.POST['sharing']

        # see if the transaction belongs to the user.
        transaction = TechCashTransaction.objects.get(id = int(transaction_id))
        if transaction.user.id == request.user.id:
            receipt = transaction.receipt
            receipt.sharing = int(sharing)
            receipt.save()
            result['result'] = receipt.SHARING_CHOICES[receipt.sharing][1] 

    return JSONHttpResponse(result)
                                                    
        
        
def techcash_consent(request):

    return render_to_response("web2/techcashconsent.html")

def otn_consent(request):

    return render_to_response("web2/lunchtimeconsent.html")


def faq(request):
    data = {}
    
    if request.user.is_anonymous():
        data['fbuser'] = None
        data['log'] = False
    else:
        data['fbuser'] = request.user.facebook_profile
        data['log'] = True
        
    return render_to_response('web2/faq.html', 
            data, context_instance=RequestContext(request))

def mobile(request):
    data = {}
    
    if request.user.is_anonymous():
        data['fbuser'] = None
        data['log'] = False
    else:
        data['fbuser'] = request.user.facebook_profile
        data['log'] = True
        
    return render_to_response('web2/mobile.html', 
            data, context_instance=RequestContext(request))

def about(request):
    data = {}
    
    if request.user.is_anonymous():
        data['fbuser'] = None
        data['log'] = False
    else:
        data['fbuser'] = request.user.facebook_profile
        data['log'] = True
        
    return render_to_response('web2/about.html', 
            data, context_instance=RequestContext(request))

def winners(request):
    """
        Shows list of winners each day

        :url: /web2/winners/
    """

    data = {}
    data['winners'] = Winner.objects.all().order_by('-timestamp')
    if request.user.is_anonymous():
        fb_profile = None
    else:
        fb_profile = request.user.facebook_profile
    data['fbuser'] = fb_profile

    return render_to_response("web2/winners.html", data,
            context_instance=RequestContext(request))

def xd_receiver(request):
    return render_to_response('web2/xd_receiver.html')

def survey(request, n, uid):
    """
        Returns the survey number :n: and adds the uid as a hidden field
        to be submitted

        :param n: the survey number
        :param uid: the unique id to verify that the user has completed survey

    """

    # should return mobile survey if accessed through the phone

    # else return web survey
    return render_to_response('survey/basic.html', {'form': form,
                                                    'uuid':uid})


@login_required
def gift(request):
    """
        Shows user's gift

        :url: /gift/
    """
    data = {}

    u = request.user
    fb_profile = u.facebook_profile
    data['fbuser'] = fb_profile

    comp, created = HumanSubjectCompensation.objects.get_or_create(user=u)
    if request.method == 'POST':
        form = HumanSubjectForm(request.POST, instance=comp)
        if form.is_valid():
            comp = form.save()
            comp.user = u
            comp.verified = True
            comp.save()
    else:
        if created:
            form = HumanSubjectForm()
        else:
            form = HumanSubjectForm(instance=comp)
            
    winner = False 
    if Winner.objects.filter(user=u).exists():
        winner = True
        data['winner'] = True
        data['wins'] = [w for w in Winner.objects.filter(user=u)]

    data['comp'] = comp
    data['form'] = form


    return render_to_response('web2/gift.html',
            data, context_instance=RequestContext(request)) 

def map(request):
    """
        Show all transactions in a map

        :url: /map/
    """
    data = {}
    data["events"] = []
    for e in Event.objects.all():
        if e.latitude != 0:
            data["events"].append( {'name':e.user.name, 'lat':e.latitude, 'lon':e.longitude} )
         
    return render_to_response("web2/map.html",
            data, context_instance=RequestContext(request))
