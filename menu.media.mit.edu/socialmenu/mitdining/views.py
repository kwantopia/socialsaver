# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from mitdining.models import Order, MenuItemReview
from common.helpers import JSONHttpResponse
from common.models import Friends
import random
from django.contrib.auth.decorators import login_required


@login_required()
def index(request, page=1):
    """
        Display the MIT Digital Menu experiment

        Make people see what they have eaten and rate the item
    """

    order_list = [] 
    user = request.user
    user_facebook = user.facebook_profile
    user_friend = Friends.objects.get(facebook_id = user_facebook.facebook_id)
    orders = Order.objects.filter(user = user).order_by('-timestamp')[:3]

    paginator = Paginator(orders, 10)
    friends_list = random.sample(user_friend.friends.all(),10)

    return render_to_response(
            "mit/home.html",
            {
                'USER_LOGGED_IN': request.user.is_authenticated(),
                'user': user_facebook,
                'friends_list': friends_list,
                'orders': orders,
            }
        )

"""
    TODO:
        OPTIONAL: provide the user with a pin or e-mail

"""

@login_required()
def orders(request, page=1):
    user_facebook = None 
    friends_list = None 
    orders = None
    order_list = [] 
    if request.user.is_authenticated():
        user = request.user
        user_facebook = user.facebook_profile
        orders = Order.objects.filter(user = user).order_by('-timestamp')

        paginator = Paginator(orders, 5)

        try:
            page = int(page)
        except ValueError:
            page = 1

        if page < 1:
            page = 1
        
        try:
            orders = paginator.page(page)
        except (EmptyPage, InvalidPage):
            orders = paginator.page(paginator.num_pages)

    return render_to_response(
            "mit/orders.html",
            {
                'USER_LOGGED_IN': request.user.is_authenticated(),
                'user': user_facebook,
                'orders': orders,
            }
        )

def profile(request):
    page = 'profile'
    user = ''

    if request.user.is_authenticated():
        user = request.user.facebook_profile
        fb = request.user.facebook_profile
        friendList = request.user.facebook_profile.get_friends_profiles()

    else:
        #print "REDIRECTING"
        return HttpResponseRedirect("/")


    return render_to_response(
        "mit/profile.html",
        {
            'page': page,
            'USER_LOGGED_IN': request.user.is_authenticated(),
            'user': user,
            'friendList': friendList,
        },
        context_instance=RequestContext(request)
    )

def faq(request):
    """
        Returns the faq page

        :url: /mit/faq/

    """
    user_facebook = None
    if request.user.is_authenticated():
        user_facebook = request.user.facebook_profile
    return render_to_response('web/faq.html', 
            {'USER_LOGGED_IN': request.user.is_authenticated(),
            'user': user_facebook})

def download(request):

    return render_to_response('mit/download.html')

def test(request):
    return HttpResponse("Test")


@login_required
def update_comment(request):
    """
        :url: /mit/update/comment/
        
        :param POST['review_id']: the review ID of the menu item 
        :param POST['comment']: the comment that the user added


        :rtype: JSON
        ::

            # if successful
            {'result': '1'}
            # else if user is not authenticated
            {'result': '0'}
    """
    result = {'result':'Please add comment...'} 

    if request.user.is_authenticated() and request.method == "POST":

        # get the transaction and description
        review_id = request.POST['review_id'].split('_')[1]
        comment = request.POST['comment']

        # see if the transaction belongs to the user.
        review = MenuItemReview.objects.get(id = int(review_id))
        review.comment = comment 
        review.save()
        result = {'result':review.comment}

    return HttpResponse(result['result'])


@login_required
def update_rating(request):
    """
    
        :url: /mit/update/rating/
        
        :param POST['review_id']: the review ID of the menu item 
        :param POST['rating']: the rating that the user added

        :rtype: JSON
        ::

            # if successful
            {'result': '1'}
            # else if user is not authenticated
            {'result': '0'}
    """
    result = {'result':'Not Rated'} 

    if request.user.is_authenticated() and request.method == "POST":

        # get the transaction and description
        review_id = request.POST['review_id']
        rating = request.POST['rating']

        # see if the transaction belongs to the user.
        review = MenuItemReview.objects.get(id = int(review_id))
        review.rating = int(rating) 
        review.save()
        result['result'] = review.RATING_CHOICES[review.rating][1] 
        
    return JSONHttpResponse(result)



