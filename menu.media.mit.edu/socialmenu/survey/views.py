# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from models import Survey, SurveyStatus, EatingHabitSurvey, MenuInterfaceSurvey, ChoiceToEatSurvey, FriendDistanceSurvey
from forms import EatingHabitSurveyForm, MenuInterfaceSurveyForm, ChoiceToEatSurveyForm
from legals.models import Order
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.conf import settings
import uuid
from django.db.models import Count
from django.views.decorators.cache import cache_control, never_cache
from common.models import OTNUser, Friends
from common.helpers import JSONHttpResponse

logger = settings.LEGALS_LOGGER


@never_cache
@login_required
def surveys(request):
    """
        Return list of surveys
    """

    u = request.user
    output = {}
    output["surveys"] = []
    output["fbuser"] = u.facebook_profile 

    orders = Order.objects.filter(user = u).order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)

    if orders.count() > 0:

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
                # TODO: need to check if the survey has expired
                #if created or not status.completed:
                if s.title == "Friend Relationship Survey":
                    distances = []
                    friend_fb_ids = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id).friends.values("facebook_id")
                    for f in OTNUser.objects.filter(facebook_profile__facebook_id__in=friend_fb_ids):
                        # create FriendDistanceSurvey for each friend
                        fd, created = FriendDistanceSurvey.objects.get_or_create(status=status, friend=f)
                        if created or fd.completed == False:
                            distances.append(fd)
                    if len(distances) > 0:
                        status.completed = False
                        status.save()

                output['surveys'].append(status)
    
    return render_to_response("survey/surveys.html", output, context_instance=RequestContext(request))

@login_required
def friend_survey(request):
    """
        AJAX to post friend distance information 

        :url: /survey/friends/

        :param POST['survey_id']: survey ID
        :param POST['friend_id']: friend_id (OTN ID)
        :param POST['distance']: distance value

    """
    u = request.user
    data = {}

    survey_id = request.POST['survey_id']
    try:
        s = Survey.objects.get(id=survey_id)
        status = SurveyStatus.objects.get(user=u, survey=s)
    except Survey.DoesNotExist:
        data["result"] = -1
    except SurveyStatus.DoesNotExist:
        data["result"] = -2

    friend_id = request.POST['friend_id']
    try:
        f = OTNUser.objects.get(id=friend_id)
        fsurvey = FriendDistanceSurvey.objects.get(friend=f, status=status)
        fsurvey.distance = int(request.POST['distance'])
        fsurvey.completed = True
        fsurvey.save()
        data["result"] = 1
    except OTNUser.DoesNotExist:
        data["result"] = -3
    except FriendDistanceSurvey.DoesNotExist:
        data["result"] = -4

    return JSONHttpResponse(data) 

@never_cache
@login_required
def survey(request, survey_id):
    """
        Return the survey web page when GET and POST to save survey results

        :url: /survey/(?P<survey_id>\d+)/

        :param POST["uuid_token"]: the uuid token of the survey
    """

    u = request.user
    survey_id = int(survey_id)
    if request.method =='POST':
        try:
            s = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            return render_to_response('survey/notexist.html', context_instance=RequestContext(request))

        if s.title == "Friend Relationship Survey":
            status = eval("%s.objects.get(user=u, survey=s, uuid_token=request.POST['uuid_token'])"%s.model_name) 
            status.completed = True
            status.complete_date = datetime.now()
            status.save()
            return render_to_response("survey/completed.html", 
                                    {
                                      'fbuser': u.facebook_profile,
                                    },
                                    context_instance=RequestContext(request))
        else: 
            status = eval("%s.objects.get(user=request.user, survey=s, uuid_token=request.POST['uuid_token'])"%s.model_name)

            form = eval("%sForm( request.POST, instance=status)"%s.model_name)

            if form.is_valid():
                status.completed = True
                status.complete_date = datetime.now()
                status.save()
                form.save()
                #return HttpResponseRedirect(reverse("survey.views.surveys"))
                return render_to_response("survey/completed.html", 
                                        {
                                          'fbuser': u.facebook_profile,
                                        },
                                        context_instance=RequestContext(request))
            else:
                return render_to_response('survey/basic.html',
                                            {'form':form,
                                            'status': status,
                                            'fbuser': u.facebook_profile,
                                            'survey_id': survey_id,
                                            'uuid_token': status.uuid_token,
                                            'errors':form.errors,
                                            },
                                            context_instance=RequestContext(request))
    else:
        uuid = ""
        form = None
        data = {}
        try:
            s = Survey.objects.get(id=survey_id)
            if s.title == "Friend Relationship Survey":
                status = eval("%s.objects.get(user=u, survey=s)"%s.model_name) 
                data["status"] = status 
                data["survey_id"] = survey_id
                data["uuid_token"] = status.uuid_token
                data["fbuser"] = u.facebook_profile
                    
                # get list of friends
                distances = []
                friend_fb_ids = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id).friends.values("facebook_id")
                for f in OTNUser.objects.filter(facebook_profile__facebook_id__in=friend_fb_ids):
                    # create FriendDistanceSurvey for each friend
                    fd, created = FriendDistanceSurvey.objects.get_or_create(status=status, friend=f)
                    if created or fd.completed == False:
                        distances.append(fd)
                    data["distances"] = distances 
                return render_to_response('survey/friend_survey.html',
                                        data,
                                        context_instance=RequestContext(request))
            else:
                status = eval("%s.objects.get(user=u,survey=s)"%s.model_name)
                form = eval("%sForm()"%s.model_name)
        except Survey.DoesNotExist:
            return render_to_response('survey/notexist.html')

        if status.completed:
            return render_to_response('survey/basic_completed.html', {'form':form,
                                        'fbuser': u.facebook_profile,
                                        'status': status,
                            'survey_id': survey_id,
                            'uuid_token': status.uuid_token},
                            context_instance=RequestContext(request))
        else:
            return render_to_response('survey/basic.html', {'form':form,
                                        'fbuser': u.facebook_profile,
                                        'status': status,
                            'survey_id': survey_id,
                            'uuid_token': status.uuid_token},
                            context_instance=RequestContext(request))
