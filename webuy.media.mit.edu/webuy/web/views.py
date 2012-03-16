# Create your views here.
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from bestbuy.models import Party, Feed, Transaction, TransactionLineItem, Wishlist, Product, ReviewRequest, Review
from bestbuy.forms import ReviewForm, PReviewForm
from common.models import Friends
from survey.models import Survey, BasicMobileSurvey, BasicShoppingSurvey 
from survey.forms import BasicMobileSurveyForm, BasicShoppingSurveyForm
from facebookconnect.models import FacebookProfile
from django.conf import settings
from datetime import datetime, timedelta
from django.core.context_processors import csrf
from common.helpers import JSONHttpResponse
import hashlib

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
def home(request, sort=0, page=1):
    """
        Home page showing personal information including
        public feeds, recent updates
    """
    data = {
        'username': request.user.username
    }

    u = request.user
    try:
        fb_profile = u.facebook_profile
        data["fb_profile"] = fb_profile
    except FacebookProfile.DoesNotExist:
        return render_to_response("web2/logout.html",
                                  data,
                                  context_instance=RequestContext(request)) 

    # if my friend list was never created, create one
    my, me_created = Friends.objects.get_or_create(facebook_id = fb_profile.facebook_id)
    if me_created:
        my.image = fb_profile.picture_url
        my.name = fb_profile.full_name
        my.save()

    # if friend list update has been more than two weeks, update friends list
    #if me_created or my.last_update < datetime.today()-timedelta(14):
    if me_created or my.last_update < datetime.today():
          
        # get Facebook friends
        friendList = request.user.facebook_profile.get_friends_profiles()
        logger.debug( "Facebook friends of %d: %s"%(fb_profile.facebook_id,str(friendList)) )
        for friend_info in friendList:
            #print friend_info['name']
            friend, created = Friends.objects.get_or_create(facebook_id = friend_info['uid'])
            #if created:
            friend.image = friend_info['pic_square'] 
            friend.name = friend_info['name']
            friend.save()
            my.friends.add(friend)

    # get friends signed up
    participant_fb_ids = FacebookProfile.objects.all().values("facebook_id")
    friends_list = my.friends.filter(facebook_id__in=participant_fb_ids)

    data["friends_list"] = friends_list

    # get feeds
    #data["num_requests"] = 5
    #data["num_wishes"] = 7
    #data["num_people"] = 10

    #data["feeds"] = Feed.objects.all()[:8]
    #data["personal_feeds"] = Feed.objects.filter(actor=u)[:8]
    #data["public_feeds"] = Feed.objects.exclude(actor=u)[:8]


    #create reviews from new purchases
    for t in TransactionLineItem.objects.filter(transaction__party=u):
        p = t.product
        
        if Review.objects.filter(reviewer=u.party, product=p).exists():
            pass
        else:
            r = Review(reviewer=u.party, product=p, posted=t.transaction.timestamp)
            r.save()

    if int(sort) == 0:
        feeds = Feed.objects.all().order_by("-timestamp")
    elif int(sort) == 1:
        feeds = Feed.objects.filter(actor=u)
    elif int(sort) == 2:
        feeds = Feed.objects.exclude(actor=u)
    

    paginator = Paginator(feeds, 8)

    try:
        page = int(page)
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    try:
        feed_pages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        feed_pages = paginator.page(paginator.num_pages)

    data["feeds"] = feed_pages

    return render_to_response("web2/home.html",
            data,
            context_instance=RequestContext(request))

@login_required
def user(request, user_id, sort='purchases', page=1):
    """
        Shows user information

        :url: /user/(?P<user_id>\d+)/
    """
    
    p = Party.objects.get(id=user_id)

    data = display_user(request, p, sort, page)

    return render_to_response("web2/user.html",
            data,
            context_instance=RequestContext(request))

    
@login_required
def friend(request, friend_id, sort='purchases', page=1):
    """
        Shows friends information (purchases/wishes/reviews)

        :url: /friend/(?P<user_id>\d+)/
    """

    f = Friends.objects.get(id=friend_id)
    
    p = Party.objects.get(facebook_profile__facebook_id=f.facebook_id)

    data = display_user(request, p, sort, page)

    return render_to_response("web2/user.html",
            data,
            context_instance=RequestContext(request))

def display_user(request, p, sort, page):
    """
        Data from user, friend methods
        After getting user/friend, displays transactions, wishlists, and reviews
    """
    data = {}
    u = request.user

    data['p'] = p
    data['sort'] = sort
    
    # get friends
    participant_fb_ids = FacebookProfile.objects.all().values("facebook_id")
    my = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id)
    data['friends_list'] = my.friends.filter(facebook_id__in=participant_fb_ids)

    if sort == 'purchases':
        display = TransactionLineItem.objects.filter(transaction__party=p).order_by("-transaction__timestamp")
        paginator = Paginator(display, 8)
    elif sort == 'wishlist':
        display = Wishlist.objects.filter(party=p).order_by("-added")
        paginator = Paginator(display, 8)
    elif sort == 'reviews':
        display = Review.objects.filter(reviewer=p).order_by("-posted")
        paginator = Paginator(display, 6)

    try:
        page = int(page)
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    try:
        display_pages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        display_pages = paginator.page(paginator.num_pages)

    data['display'] = display_pages

    return data


@login_required
def group(request):
    """
        Shows group purchases, so one can start or join
        It also shows group purchases that one is engaged in
    """
    u = request.user
    data = {}

    return render_to_response("web2/group.html",
            data,
            context_instance=RequestContext(request))

@login_required
def profile(request):
    """
        GET: Shows profile
        POST: Updates PIN and default transaction sociability

        :url: /web2/profile/

    """
    u = request.user
    fb_user = u.facebook_profile

    if request.method=="POST":
        if len(request.POST['reward']) > 0:
            # change reward zone number
            u.reward_zone = hashlib.sha224(request.POST['reward']).hexdigest()
            u.save()

        if len(request.POST['first']) > 0:
            if request.POST['first'] == request.POST['second']:
                # change pin
                u.party.pin = hashlib.sha224(request.POST['first']).hexdigest()
                u.party.save()
            else:
                prompt = 'PIN does not match, please reenter'
                return render_to_response('web2/profile.html', 
                        {'prompt':prompt,
                        'fbuser': fb_user,},
                        context_instance=RequestContext(request))
        # after POST changing PIN
        return HttpResponseRedirect("/home/")
    else:
        return render_to_response(
            "web2/profile.html",
            {
                'fbuser': fb_user,
            },
            context_instance=RequestContext(request)
        )


@login_required
def feeds(request):
    """
        Feeds page showing private Feeds
    """
    data = {}
    u = request.user

    feeds = Feed.objects.filter_by(party=u)
    data["feeds"] = feeds

    return render_to_response("web2/feeds.html",
            data,
            context_instance=RequestContext(request))


@login_required
def product(request, product_id):
    """
        Shows product information

        :url: /product/(?P<product_id>\d+)/
    """
    data = {}
    u = request.user
    p = Product.objects.get(id=product_id)
    data['p'] = p
    
    data['purchased'] = TransactionLineItem.objects.filter(transaction__party=u, product=p).exists()

    if Wishlist.objects.filter(party=u, product=p).exists():
        data['wished'] = Wishlist.objects.get(party=u, product=p)

    if data['purchased']:
        data['review'] = Review.objects.get(reviewer=u.party, product=p)


    return render_to_response("web2/product.html",
            data,
            context_instance=RequestContext(request))


@login_required
def purchases(request, page=1):
    """
        List of my purchases 

        :url: /purchases/(?P<page>\d+)/
    """
    u = request.user
    data = {}

    txns = Transaction.objects.filter(party=u).order_by("-timestamp")
    paginator = Paginator(txns, 3)

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

    return render_to_response("web2/purchases.html",
            data,
            context_instance=RequestContext(request))

@login_required
def wishlist(request, sort=0, page=1):
    """
        List of my wishes    

        :url: /wishlist/(?P<page>\d+)/
    """
    u = request.user
    data = {}

    data['sort'] = sort

    # Update review-response status for icon change
    update_review_status(u)

    if int(sort) == 0:
        wishes = Wishlist.objects.filter(party=u, removed=False).order_by("-added")
    elif int(sort) == 1:
        wishes = Wishlist.objects.filter(party=u, removed=False).order_by("product__name")
    elif int(sort) == 2:
        wishes = Wishlist.objects.filter(party=u, removed=False).order_by("-max_price")
        
    paginator = Paginator(wishes, 4)

    try:
        page = int(page)
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    try:
        wish_pages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        wish_pages = paginator.page(paginator.num_pages)

    data["wishlist"] = wish_pages 

    return render_to_response("web2/wishlist.html",
            data,
            context_instance=RequestContext(request))


def update_review_status(u):

    wishes = Wishlist.objects.filter(party=u, removed=False)

    for w in wishes:
        if w.review == Wishlist.REVIEW_REQUESTED:
            if Review.objects.filter(product=w.product, first_reviewed=True).exists():
                w.review = Wishlist.REVIEW_RESPONDED
                w.save()

        
@login_required
def remove_wish(request, product_id):
    """
        Remove an item from the wishlist 
    """
    u = request.user
    data = {}

    p = Product.objects.get(id=product_id)

    w = Wishlist.objects.get(party=u, product=p)
    w.removed = True
    w.remove_date = datetime.now()
    w.save()

    data['p'] = p
    data['key'] = "remove"
    return render_to_response('web2/confirm.html',
                            data,
                            context_instance=RequestContext(request))


@login_required
def requests(request):
    """
        List of review requests that you have requested to others
    """
    u = request.user
    data = {}

    requests = ReviewRequest.objects.filter(requester=u).order_by("-requested")
    data["requests"] = requests

    responses = []
    for req in requests:
        for r in req.replies.filter(first_reviewed=True):
            responses.append(r)

    data["responses"] = responses
    data["count"] = len(responses)
        
    return render_to_response("web2/requests.html",
            data,
            context_instance=RequestContext(request))


@login_required
def request_review(request, product_id):
    """
        Request review

        :url: /request/review/(?P<product_id>\d+)/
    """
    data = {}
    u = request.user

    p = Product.objects.get(id=product_id)

    r, created = ReviewRequest.objects.get_or_create(requester=u.party, product=p)
    
    # associate with other people's reviews
    reviews = Review.objects.filter(product=p).exclude(reviewer=u.party)

    for review in reviews:
        review.reply_to.add(r)
        review.save()

    # change wishlist key
    w = Wishlist.objects.get(party=u, product=p)

    if reviews.filter(first_reviewed=True).exists():
        w.review = Wishlist.REVIEW_RESPONDED
    else:
        w.review = Wishlist.REVIEW_REQUESTED
    w.save()

    # add a feed
    f = Feed(actor=u.party, action=Feed.REQUESTED, product=p) 
    f.save()

    data['p'] = p
    data['key'] = "request"
    return render_to_response('web2/confirm.html',
                            data,
                            context_instance=RequestContext(request))
    #return JSONHttpResponse({'result':str(r.id)})


@login_required
def reviews(request, sort='posted', page=1):
    data={}
    
    u = request.user
    fb_profile = u.facebook_profile

    # review request alerts
    my_products = TransactionLineItem.objects.filter(transaction__party=u).values_list('product', flat=True).distinct()
    rev_reqs = ReviewRequest.objects.filter(product__in=my_products)

    pending_requests = []
    for req in rev_reqs:
        for r in req.replies.filter(reviewer=u, first_reviewed=False):
            pending_requests.append(r)

    data['pending_requests'] = pending_requests
    data['pending_count'] = len(pending_requests)

    
    # display reviews

    if sort == 'posted':
        reviews = Review.objects.filter(reviewer=u).order_by('-posted')
    elif sort == 'rating':
        reviews = Review.objects.filter(reviewer=u).order_by('-rating')
    elif sort == 'pending':
        reviews = pending_requests

    paginator = Paginator(reviews, 3) # 3 reviews per page

    try:
        page = int(page)
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    # If page is empty or invalid, just go to the last one.
    try:
        reviews = paginator.page(page)
    except (EmptyPage, InvalidPage):
        reviews = paginator.page(paginator.num_pages)

    data['reviews'] = reviews
    data['sort'] = sort
        
    return render_to_response('web2/reviews.html',
                          data,
                          context_instance=RequestContext(request))
        




@login_required
def update_description(request):
    """

        :param POST['review']: the review I am modifying
        :param POST['description']: the detail

        :url: /web2/update/description/

    """
    data = {}
    u = request.user
    
    data['result']='0'

    if request.method == "POST":

        # get the review and description
        review_id = request.POST['review_id'].split('_')[1]
        description = request.POST['description']

        logger.debug("Review %s: %s submitted"%(review_id, description))
        
        review = Review.objects.get(id = int(review_id))

        if not review.first_reviewed:
            review.content = description
            review.first_reviewed = True
            review.save()

            # add a feed
            f = Feed(actor=u.party, action=Feed.REVIEWED, product=review.product) 
            f.save()
    
        else:
            review.content = description
            review.save()

            # add a feed
            f = Feed(actor=u.party, action=Feed.UPDATED_REVIEW, product=review.product) 
            f.save()
            
        data['result'] = review.content

    return HttpResponse(data['result'])


@login_required
def update_rating(request):
    """

        :param POST['review_id']: the transaction I am modifying
        :param POST['rating']: the rating value 

        :url: /web2/update/rating/

    """

    data = {'result':'Not Rated'}
    u = request.user

    if request.method == "POST":

        # get the transaction and description
        review_id = request.POST['review_id']
        logger.debug("review_id:%s"%review_id)
        rating = request.POST['rating']

        review = Review.objects.get(id = int(review_id))

        if not review.first_reviewed:
            review.rating = int(rating)
            review.first_reviewed = True
            review.save()

            # add a feed
            f = Feed(actor=u.party, action=Feed.REVIEWED, product=review.product) 
            f.save()
            
        else:
            review.rating = int(rating)
            review.save()

            # add a feed
            f = Feed(actor=u.party, action=Feed.UPDATED_REVIEW, product=review.product) 
            f.save()
            
        data['result'] = review.RATING_CHOICES[review.rating][1]


    return JSONHttpResponse(data)


def update_sharing(request):
    pass


@login_required
def winners(request):
    """
        Return winners

        :url: /winners/
    """
    data = {}
    u = request.user

    return render_to_response("web2/winners.html",
            data,
            context_instance=RequestContext(request))

def searchpurch(request):
    data = {}
    u = request.user
    
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        product = TransactionLineItem.objects.filter(transaction__party=u, product__name__icontains=q)
        return render_to_response('web2/search_results.html',
                                 {'products': product, 'query': q, 'page': 'purchases'},
                                 context_instance=RequestContext(request))
    else:
        return render_to_response('web2/purchases.html', {'error': True})

def searchwish(request):

    data = {}
    u = request.user
    
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        product = Wishlist.objects.filter(party=u, product__name__icontains=q)
        return render_to_response('web2/search_results.html',
                                 {'products': product, 'query': q, 'page': 'wishlist'},
                                 context_instance=RequestContext(request))
    else:
        return render_to_response('web2/wishlist.html', {'error': True})

def mobile(request):
    data = {}
    u = request.user
    
    if u.is_anonymous():
        data['log'] = False
    else:
        data['log'] = True
        
    return render_to_response('web2/mobile.html', 
            data, context_instance=RequestContext(request))

def about(request):
    data = {}
    u = request.user
    
    if u.is_anonymous():
        data['log'] = False
    else:
        data['log'] = True
        
    return render_to_response('web2/about.html', 
            data, context_instance=RequestContext(request))

def faq(request):
    data = {}
    u = request.user
    
    if u.is_anonymous():
        data['log'] = False
    else:
        data['log'] = True
        
    return render_to_response('web2/faq.html', 
            data, context_instance=RequestContext(request))
