from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from forms import LegalsPopulationSurveyForm
from legals.models import Category, MenuItem
from common.models import Friends
from django.conf import settings
import random
from datetime import datetime

# Import the Django helpers
import facebook.djangofb as facebook

# The User model defined in models.py
from models import User, Invited

# We'll require login for our canvas page. This
# isn't necessarily a good idea, as we might want
# to let users see the page without granting our app
# access to their info. See the wiki for details on how
# to do this.

logger = settings.LOGGER

APP_NAME = settings.APP_NAME 

@facebook.require_login()
def dummy_page(request):
    """
        It only makes user login if not logged in and the
        page forwards back to root :meth:`legals_population_survey`

        :url: /pickadish/legals/

    """
    if not request.facebook.check_session(request):
        return direct_to_template(request, 'presurvey/canvas.fbml', extra_context={'appname': APP_NAME})
    else:
        # Get the User object for the currently logged in user
        user = User.objects.get_current()
        logger.debug("Displaying dummy_page with user logged in")

        friends_in_app = request.facebook.friends.getAppUsers()
        logger.debug("Friends that use the app initial: %s"%friends_in_app)
        if len(friends_in_app)>0:
            if len(friends_in_app)>10:
                friends_in_app = random.sample(friends_in_app,10)
            friends = request.facebook.users.getInfo( friends_in_app, ['pic_square'])
        else:
            friends = []
        logger.debug("Friends that use the app after random: %s"%friends)

        # User is guaranteed to be logged in, so pass canvas.fbml
        # an extra 'fbuser' parameter that is the User object for
        # the currently logged in user.
        return direct_to_template(request, 'presurvey/canvas.fbml', extra_context={'fbuser': user, 'friends': friends, 'appname': APP_NAME})

@facebook.require_login()
def legals_population_survey(request):
    """
        The survey is used at the intro of the Facebook survey
        to collect information about the individual's initial taste

        :url: /pickadish/

    """
    if not request.facebook.check_session(request):
        return direct_to_template(request, 'presurvey/canvas.fbml', extra_context={'appname': APP_NAME})
    else:
        # Get the User object for the currently logged in user
        user = User.objects.get_current()
        userinfo = request.facebook.users.getInfo([request.facebook.uid], ['name', 'pic_square', 'last_name', 'first_name', 'current_location', 'proxied_email', 'birthday_date'])


        if 'pic_square' in userinfo[0]:
            logger.debug("Displaying survey with user pic_square  %s"%userinfo[0]['pic_square'])
        if 'name' in userinfo[0]:
            logger.debug("Displaying survey with user name  %s"%userinfo[0]['name'])
        logger.debug("Displaying survey")
        
        try:
            friends_in_app = request.facebook.friends.getAppUsers()
            logger.debug("Friends that use the app initial: %s"%friends_in_app)
            user.friends_at_signup = len(friends_in_app)
            user.save()
            if len(friends_in_app)>0:
                if len(friends_in_app)>10:
                    friends_in_app = random.sample(friends_in_app,10)
                friends = request.facebook.users.getInfo( friends_in_app, ['pic_square'])
            else:
                friends = []
        except:
            friends = []
            logger.debug("Cannot get friends in app")
        logger.debug("Friends that use the app after random: %s"%friends)
 
        # User is guaranteed to be logged in, so pass canvas.fbml
        # an extra 'fbuser' parameter that is the User object for
        # the currently logged in user.

        # Complete is the name of Submit button in the form
        if "Complete" in request.POST:
            # process submission of form
            form = LegalsPopulationSurveyForm(request.POST, request.FILES) 
            if form.is_valid():
                # save the form
                form.save()
                logger.debug("Saved survey")
                # assign user the facebook ID
                #instance = request.user.get_profile().facebook_id

                # Save user's friends to our DB
                my, created = Friends.objects.get_or_create(facebook_id=userinfo[0]['uid'])
                if created:
                    my.image=userinfo[0]['pic_square']
                    my.name=userinfo[0]['name']
                    my.save()

                logger.debug("Getting friends for %s"%str(userinfo[0]['uid']))

                friend_list = request.facebook.users.getInfo( request.facebook.friends.get(), ['name', 'pic_square'])
                user.friends_str = str(friend_list)
                user.completed = True
                user.save()

                logger.debug("Saved friends for %s"%str(userinfo[0]['uid']))

                #HTML escape function for invitation content.
                from cgi import escape

                facebook_uid = request.facebook.uid
                # Convert the array of friends into a comma-delimited string.  
                exclude_ids = ",".join([str(a) for a in request.facebook.friends.getAppUsers()])

                # Prepare the invitation text that all invited users will receive.  
                logger.debug("Excluding %s"%exclude_ids)

                content = """<fb:name uid="%s" firstnameonly="true" shownetwork="false"/>
                    invites you to join a taste in social network research survey for 5 mins.
                         <fb:req-choice url="%s"
                 label="What would you eat at Legal Sea Foods?"/>
                 """ % (facebook_uid, request.facebook.get_add_url())

                invitation_content = escape(content, True)
                logger.debug("Got the friends, and showing invitation form")

                return direct_to_template(request, 'presurvey/invite_friends.fbml',
                        extra_context={'fbuser':user, 
                                    'content': invitation_content, 
                                    'exclude_ids': exclude_ids,
                                    'appname': APP_NAME})
            else:
                # there was an error in the form 
                logger.debug("Redisplay the form due to error %s"%form.errors)

                form = LegalsPopulationSurveyForm(request.POST)
                # Get Legals menu
                categories = Category.objects.all().order_by('name')
                menu = []
                for c in categories:
                    menu.append({'category':c.name, 'dishes':[m.get_json() for m in c.menuitem_set.all()]})

                return direct_to_template(request, 'presurvey/legalspopulation.fbml', 
                                extra_context={'fbuser': user, 
                                                'friends': friends,
                                                'menu': menu, 
                                                'form': form, 
                                                'errors':form.errors,
                                                'appname':APP_NAME})
        else:
            # present the survey form
            #logger.debug("Displaying initial survey form %s"%request.POST.get('fb_sig_friends'))
            logger.debug(userinfo)
            user.first_name = userinfo[0].get('first_name')
            user.last_name = userinfo[0].get('last_name')
            if userinfo[0].get('current_location') is not None:
                user.city = userinfo[0]['current_location'].get('city')
                user.state = userinfo[0]['current_location'].get('state')
            user.proxied_email = userinfo[0].get('proxied_email')
            user.birthday_date = userinfo[0].get('birthday_date')
            user.started = datetime.now()
            user.save()

            form = LegalsPopulationSurveyForm()
            #logger.debug("Displaying initial survey form: %s"%str(form))
            logger.debug("Displaying initial survey form")

            # Get Legals menu
            categories = Category.objects.all().order_by('name')
            menu = [] 
            for c in categories:
                menu.append({'category':c.name, 'dishes':[m.get_json() for m in c.menuitem_set.filter(active=True)]})

            return direct_to_template(request, 'presurvey/legalspopulation.fbml', 
                    extra_context={'fbuser': user, 
                                    'friends': friends,
                                    'menu': menu, 
                                    'form':form, 
                                    'appname':APP_NAME})

@facebook.require_login()
def invite_more(request):
    """
        :url: /pickadish/legals/invite/

    """
    if not request.facebook.check_session(request):
        return direct_to_template(request, 'presurvey/canvas.fbml', extra_context={'appname': APP_NAME})
    else:
        # Get the User object for the currently logged in user
        user = User.objects.get_current()

        # assign user the facebook ID
        #instance = request.user.get_profile().facebook_id

        #HTML escape function for invitation content.
        from cgi import escape

        facebook_uid = request.facebook.uid
        # Convert the array of friends into a comma-delimited string.  
        exclude_ids = ",".join([str(a) for a in request.facebook.friends.getAppUsers()])

        # Prepare the invitation text that all invited users will receive.  
        logger.debug("Excluding %s"%exclude_ids)

        content = """<fb:name uid="%s" firstnameonly="true" shownetwork="false"/>
        invites you to join a research survey on taste in social network for 5 mins.
                 <fb:req-choice url="%s"
         label="What would you eat at Legal Sea Foods?"/>
         """ % (facebook_uid, request.facebook.get_add_url())

        invitation_content = escape(content, True)
        logger.debug("Got the friends, and showing invitation form")

        return direct_to_template(request, 'presurvey/invite_friends.fbml',
                extra_context={'fbuser':user, 
                            'content': invitation_content, 
                            'exclude_ids': exclude_ids,
                            'appname': APP_NAME})

@facebook.require_login()
def completed(request):
    """
        :url: /pickadish/legals/completed/

    """
    if not request.facebook.check_session(request):
        return direct_to_template(request, 'presurvey/completed.fbml', extra_context={'appname': APP_NAME})
    else:
        # Get the User object for the currently logged in user
        user = User.objects.get_current()

        for invited in request.POST.getlist("ids[]"):
            invitation, created = Invited.objects.get_or_create(user=request.facebook.uid, invited=invited)
            if created:
                invitation.save()

    return direct_to_template(request, "presurvey/completed.fbml", {'fbuser':user, 'appname':APP_NAME})

@facebook.require_login()
def ajax(request):
    return HttpResponse('hello world')
