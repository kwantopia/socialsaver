# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext

# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from models import Survey, SurveyStatus, BasicFoodSurvey, EatingOutSurvey, EatingCompanySurvey, DigitalReceiptSurvey
from forms import BasicFoodSurveyForm, EatingOutSurveyForm, EatingCompanySurveyForm, DigitalReceiptSurveyForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.conf import settings
import uuid

logger = settings.LOGGER


@login_required
def surveys(request):
    """
        Return list of surveys
    """

    u = request.user
    output = {}
    output["surveys"] = []
    output["fbuser"] = u.facebook_profile 
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
            #if created or not status.completed:
            output['surveys'].append(status)
    
    return render_to_response("survey/surveys.html", output, context_instance=RequestContext(request))

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
            survey_meta = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            return render_to_response('survey/notexist.html')
        status = eval("%s.objects.get(user=request.user, uuid_token=request.POST['uuid_token'])"%survey_meta.model_name)
        form = eval("%sForm( request.POST, instance=status)"%survey_meta.model_name)

        if form.is_valid():
            status.completed = True
            status.complete_date = datetime.now()
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
                                        'survey': status,
                                        'fbuser': u.facebook_profile,
                                        'survey_id': survey_id,
                                        'uuid_token': status.uuid_token,
                                        'errors':form.errors,
                                        })
    else:
        uuid = ""
        form = None
        try:
            s = Survey.objects.get(id=survey_id)
            status = eval("%s.objects.get(user=u,survey=s)"%s.model_name)
            form = eval("%sForm()"%s.model_name)
        except Survey.DoesNotExist:
            return render_to_response('survey/notexist.html')

        return render_to_response('survey/basic.html', {'form':form,
                                        'fbuser': u.facebook_profile,
                                        'survey': status,
                            'survey_id': survey_id,
                            'uuid_token': status.uuid_token},
                            context_instance=RequestContext(request))      
