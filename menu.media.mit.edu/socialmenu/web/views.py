# Create your views here.
"""
    Make it so that one user can participate in both experiments.

    Handles the front page information for Digital Menu's
"""
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template import RequestContext
from common.models import Friends, OTNUser
from common.helpers import JSONHttpResponse
import random
import hashlib
from django.contrib.auth.decorators import login_required
from legals.models import TableCode
from datetime import date

def index(request):
    """
        Displays the root web page
	
        :url: /, /web/

        :return: the front page of the site
    """

    fbuser = None
    u = request.user
    if not u.is_anonymous():
        fbuser = u.facebook_profile
        
    return render_to_response(
        "web/index.html",
        {'fbuser':fbuser},
        context_instance=RequestContext(request)
    )

def launch(request):
    """
        Displays the root web page once the experiment launches
	
        :url: /, /web/

        :return: the front page of the site
    """
    fbuser = None
    u = request.user
    if not u.is_anonymous():
        fbuser = u.facebook_profile
        
    return render_to_response(
        "web/index.html",
        {'fbuser':fbuser},
        context_instance=RequestContext(request)
    )


def login_redirect(request):
    fbuser = None
    u = request.user
    if not u.is_anonymous():
        fbuser = u.facebook_profile

    if request.GET.get("next", None):
        next_url = request.GET['next']
        return render_to_response('legals/index.html', 
                {
                    'next': next_url,
                    'fbuser':fbuser,
                },
                context_instance=RequestContext(request)
            )
    elif '/mit/' in request.GET['next']:
        return render_to_response('mit/index.html', 
                {
                    'next': '/mit/',
                    'fbuser':fbuser,
                },
                context_instance=RequestContext(request)
            )
    else:
        return render_to_response('legals/index.html',
                {
                    'next': '/legals/',
                    'fbuser':fbuser,
                },
                context_instance=RequestContext(request)
            )

def legals(request):
    """
        Displays the front page of legals
        :url: /web/legals/

        :return: the front page of the site
    """
    user_facebook = ''
    friends_list = []
    transactions = []

    if request.user.is_authenticated():
        user_facebook = request.user.facebook_profile
        user_friend = Friends.objects.get(facebook_id = user_facebook.facebook_id)
        user_OTNUser = OTNUser.objects.get(user = request.user)
        random.seed(random.random())
        friends_list = random.sample(user_friend.friends.all(),10)
        

    return render_to_response(
        "web/legals_index.html",
        {
        'fbuser': user_facebook,
        'friends_list': friends_list,
        'transactions': transactions,
        },
        context_instance=RequestContext(request)
    )

def mit(request):
    """
        Displays the front page
        :url: /web/mit/ 

        :return: the front page of the site
    """
    user_facebook = ''
    friends_list = []
    transactions = []

    if request.user.is_authenticated():
        user_facebook = request.user.facebook_profile
        user_friend = Friends.objects.get(facebook_id = user_facebook.facebook_id)
        user_OTNUser = OTNUser.objects.get(user = request.user)
        random.seed(random.random())
        friends_list = random.sample(user_friend.friends.all(),10)
        

    return render_to_response(
        "web/mit_index.html",
        {
        'fbuser': user_facebook,
        'friends_list': friends_list,
        'transactions': transactions,
        },
        context_instance=RequestContext(request)
    )



def download(request):

    return render_to_response('web/download.html')

def after_login(request):
    """
        :url: /web/after/login/
    """

    if request.user.is_authenticated():
        if request.GET['next'] == '/legals/':
            return HttpResponseRedirect("/legals/")
        elif request.GET['next'] == '/mit/':
            return HttpResponseRedirect("/mit/")
    return HttpResponseRedirect("/")

@login_required
def profile(request):
    page = 'profile'

    if request.user.is_authenticated():
        fb_profile = request.user.facebook_profile
        friendList = request.user.facebook_profile.get_friends_profiles()
    else:
        #print "REDIRECTING"
        return HttpResponseRedirect("/")


    return render_to_response(
        "web/profile.html",
        {
            'page': page,
            'fbuser': fb_profile,
            'friendList': friendList,
        },
        context_instance=RequestContext(request)
    )

def techcash_consent(request):

    return render_to_response("web/techcashconsent.html")

def otn_consent(request):

    return render_to_response("web/digitalmenuconsent.html")

@login_required
def pin_manage(request):
    """
        Allows one to enter new pin #
    """
    user_facebook = request.user.facebook_profile
    if request.method=='POST':

        if request.POST['first'] == request.POST['second']:
            u = OTNUser.objects.get(user=request.user)
             # change pin
            u.pin = hashlib.sha224(request.POST['first']).hexdigest(),
            u.save()
            return HttpResponseRedirect("/web") 
        else:
            prompt = 'PIN does not match, please reenter'
            return render_to_response('web/pinchange.html', 
                    {'prompt':prompt,
                    'fbuser': user_facebook},
                    context_instance=RequestContext(request))
    return render_to_response('web/pinchange.html', 
            {
            'fbuser': user_facebook},
            context_instance=RequestContext(request))

def faq(request):
    """
        Returns the faq page

        :url: /web/faq/

    """
    user_facebook = None
    if request.user.is_authenticated():
        user_facebook = request.user.facebook_profile
    return render_to_response('web/faq.html', 
            context_instance=RequestContext(request))

def test_ajax(request):
    """
        :url: /web/test/ajax/
    """
    return render_to_response('web/test_ajax.html', context_instance=RequestContext(request))

def crossdomain(request):
    return render_to_response('web/crossdomain.xml')

@login_required
def table_codes(request):
    data = {}
    data['codes'] = TableCode.objects.filter(date=date.today(), first_used=None)
    return render_to_response("web/tablecodes.html",
                            data,
                            context_instance=RequestContext(request))

