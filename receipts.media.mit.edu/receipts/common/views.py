# Create your views here.
from common.models import OTNUser, Location, Experiment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

import facebook.djangofb as facebook

def login_ws(request):

    token = request.POST['token']
    user = authenticate(token=token)
    if user is not None:
        print login(request, user)            
        return HttpResponse(simplejson.dumps("Success"))          
    else:
        return HttpResponse(simplejson.dumps("Failure"))


def register(request):

    user = ''
    

    if request.user.is_authenticated():
        finalize(request)



    return render_to_response(
        "common/base.html",
        {
        'USER_LOGGED_IN': request.user.is_authenticated(),
        'user': user,
        })

def finalize(request):

    if request.user.is_authenticated():
        otn = OTNUser()    
        user = request.user
        otn.user = user
        fb = user.facebook_profile
        otn.facebook_profile = fb
        otn.name = fb.full_name
        user.username = otn.name
        user.save()
        otn.experiment = Experiment.objects.get(id = request.user.id % int(settings.NUM_EXPERIMENTS))
        otn.image = fb.picture_url
        otn.mit_id = request.POST['mit_id']
        otn.pin = request.POST['pin']
        otn.save()

 
