# Create your views here.
from datetime import datetime, date, timedelta
from random import randint, sample
from mobile.models import Event, FeedEvent
from common.models import OTNUser, Winner, Friends, Featured, Location
from techcash.models import Receipt
from facebookconnect.models import FacebookProfile
from django.core.mail import send_mail
from common.helpers import JSONHttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

logger = settings.LOGGER

@csrf_exempt
def find_winner(request):
    """
        Finds the winner for the day

        :url: /a/winner/

        :param POST['code']: the pass code to select winner
        :param POST['test']: '1' if testing
    """
    r = {}

    test = False
    if request.POST.get('test','0') == '1':
        test = True 

    if request.POST.get('code','000') == 'ch00seW199Er':
        # check the number of people who transacted today
        d = date.today() #-timedelta(30)
        win_begin = datetime(year=d.year, month=d.month, day=d.day,
                hour=0, minute=0, second=0)
        win_end = datetime(year=d.year, month=d.month, day=d.day,
                hour=23, minute=59, second=59)

        # check the number of people who logged in today
        logged_in = Event.objects.filter(action=Event.LOGIN,timestamp__gt=win_begin, timestamp__lt=win_end).values('user').distinct()
        logger.debug("People that used: %s"%str(logged_in))
        
        # check the number of people who saw the feed today
        feed_viewed = FeedEvent.objects.filter(action=FeedEvent.FEED,timestamp__gt=win_begin, timestamp__lt=win_end).values('user').distinct()
        logger.debug("People that used the feed: %s"%str(feed_viewed))

        # check the number of people who have reviewed
        reviewed = Receipt.objects.filter(last_update__lt=win_end, last_update__gt=win_begin).values_list("txn__user", flat=True).distinct()
        logger.debug("People that reviewed: %s"%str(reviewed))

        # exclude previous winners
        prev_winners = Winner.objects.all().values('user__id')
        #.exclude(id__in=prev_winners)

        r_start = Q(techcashtransaction__receipt__last_update__gt=win_begin)
        r_end = Q(techcashtransaction__receipt__last_update__lt=win_end)
        t_start = Q(techcashtransaction__timestamp__gt=win_begin)
        t_end = Q(techcashtransaction__timestamp__lt=win_end)
        f_viewed = Q(id__in=feed_viewed)

        users_today = OTNUser.objects.filter(f_viewed | (r_start & r_end) | (t_start & t_end)).order_by('id').distinct()
        logger.debug("People that made txns (%d): %s"%(users_today.count(), str(users_today)))

        # randomly select
        winner_id=-1
        if users_today.count() == 0:
            return JSONHttpResponse({'result':'0'})
        elif users_today.count() == 1:
            winner_id = users_today[0].id
            winner = users_today[0]
        else:
            # exclude Kwan, John McDonald, Dawei Shen, Alter Yod
            exclude_list=[-1, 2, 3, 5]
            while winner_id in exclude_list:
                draw = randint(0,users_today.count()-1)
                winner = users_today[draw] 
                winner_id = winner.id
        
        if not test:
            # save to DB
            win_prize = Winner(user=winner, prize="$5 TechCASH")
            win_prize.save()
            
            # if called the day after
            win_prize.timestamp = d 
            win_prize.save()

            # email mitcard to credit from DIGRECPT1 to MIT ID
            msg = "%s is today's OTN/MealTime winner!\n\nPlease transfer $5 from DIGRECPT1 to %s.\n\n-kwan"%(winner.name, winner.mit_id)
            send_mail('OTN Winner', msg, 'kwan@media.mit.edu', ['kwan@media.mit.edu'], fail_silently=False) 

            # email winner
            msg = "You are today's MealTime winner!\n\nYou will receive $5 credit in your TechCASH account.\n\n-kwan"
            send_mail('OTN Winner', msg, 'kwan@media.mit.edu', [winner.my_email, 'kwan@media.mit.edu'], fail_silently=False) 

        r['result'] = {'name':winner.name, 'id':"%d"%winner.id}
    else:
        r['result'] = '-1'

    return JSONHttpResponse(r)

def latest_joined(request):
    """
        Print people that joined recently

        :url: /a/latest/

        :param POST['days']: num days previous
    """
    prev = int(request.POST['days'])
    d = datetime.today()-timedelta(prev)
    users = OTNUser.objects.filter(date_joined__gt=d).order_by("date_joined")
    r = [] 
    # e-mail MIT card office
    for u in users:
        r.append("%s, %s, %s"%(u.mit_id, u.name, u.approved))

    return JSONHttpResponse(r)

def add_to_otn(request):
    """
        Add people to OTN

        :url: /a/add/otn/

        :param POST['code']: code to verify

    """
    r = {}
    if request.POST.get('code','000') == 'ch00seW199Er':
 
        registrants = ""

        latest = OTNUser.objects.filter(approved=0)

        for u in latest:
            registrants += "%s, %s\n"%(u.mit_id, u.name)
            u.approved=1
            u.save()

        r["result"] = registrants

        if latest.count() > 0: 
            # email mitcard to add people to OTN 
            msg = "Please add the following to OTN:\n\n%s\n\n-kwan"%registrants
            send_mail('OTN Winner', msg, 'kwan@media.mit.edu', ['mitcard@mit.edu', 'kwan@media.mit.edu'], fail_silently=False) 

    return JSONHttpResponse(r) 

def friend_stats(request):
    """
        Find out the number of friends each user has that is signed up to
        use the application

        :url: /a/friend/stats/
    """
    
    r = {}
    fb_ids = FacebookProfile.objects.all().values("facebook_id") 
    for u in FacebookProfile.objects.all():
        friends = Friends.objects.filter(facebook_id__in=fb_ids)
        num_friends = Friends.objects.filter(facebook_id=u.facebook_id, friends__in=friends).count()
        participant = OTNUser.objects.get(facebook_profile__facebook_id=u.facebook_id)
        r[u.facebook_id]="%s (%d): %d"%(participant.name, participant.id, num_friends)

    return JSONHttpResponse(r)


def social_winner(request):
    """
        Finds the winner for the day

        :url: /a/winner/social/

        :param POST['code']: the pass code to select winner
        :param POST['winners']: list of people
        :param POST['test']: '1' if testing
    """
    r = {}

    test = False
    if request.POST.get('test','0') == '1':
        test = True 

    if request.POST.get('code','000') == 'ch00seW199Er':
        # check the number of people who transacted today
        d = date.today()
        
        fb_ids = request.POST.getlist('winners')
        winner_str = ""

        if not test:
            for f in fb_ids:
                winner = OTNUser.objects.get(facebook_profile__facebook_id=f)
                # save to DB
                win_prize = Winner(user=winner, prize="$50 TechCASH")
                win_prize.save()
                
                # if called the day after
                win_prize.timestamp = d 
                win_prize.save()
                winner_str += "%s, %s\n"%(winner.name, winner.mit_id) 

                # email winner
                msg = "You are MealTime Social winner!\n\nYou will receive $50 credit in your TechCASH account.\n\n-kwan"
                send_mail('OTN Social Prize Winner', msg, 'kwan@media.mit.edu', [winner.my_email, 'kwan@media.mit.edu'], fail_silently=False) 

            # email mitcard to credit from DIGRECPT1 to MIT ID
            msg = "%s\nare OTN Social Winners!\n\nPlease transfer $50 from DIGRECPT1 to their TechCASH accounts respectively.\n\n-kwan"%winner_str
            send_mail('OTN Social Prize Winner', msg, 'kwan@media.mit.edu', ['mitcard@mit.edu', 'kwan@media.mit.edu'], fail_silently=False) 

        r['result'] = {'winners': winner_str}
    else:
        r['result'] = '-1'

    return JSONHttpResponse(r)

def get_emails(request):
    """
        Return all e-mails
    """

    if request.POST.get('code','000') == 'ch00seW199Er':
        emails = ""
        all_users = OTNUser.objects.all()
        emails = "%s,"%all_users.count()
        for u in all_users:
            emails += u.my_email + ","
    return HttpResponse(emails)

def last_week_winners(request):
    """
        Return winners from last week
    """

    r = {}
    if request.POST.get('code', '000') == 'ch00seW199Er':
        r["result"] = "1"
        r["winners"] = []
        for u in Winner.objects.filter(timestamp__gt=datetime.today()-timedelta(8)):
            r["winners"].append((u.user.mit_id, u.user.name))
    else:
        r["result"] = "-1"
    return JSONHttpResponse(r) 

def past_winners(request, days):
    """
        Return winners from past 
    """

    r = {}
    if request.POST.get('code', '000') == 'ch00seW199Er':
        r["result"] = "1"
        r["winners"] = []
        for u in Winner.objects.filter(timestamp__gt=datetime.today()-timedelta(int(days))):
            r["winners"].append((u.user.mit_id, u.user.name))
    else:
        r["result"] = "-1"
    return JSONHttpResponse(r) 

@csrf_exempt
def add_feature(request):
    """
        Add a feature item for tomorrow

        /a/feature/

    """

    r = {}
    if request.POST.get('code','000') == 'ch00seW199Er':
        # pick a random location
        featured_already = Featured.objects.all().values('location')
        locations = Location.objects.exclude(id=1).exclude(id__in=featured_already).exclude(name__iregex=r'[\w# ]+(wash|washer|dryer|dyer)[\w# ]*').filter(type=Location.EATERY)
        features = sample(locations, 10)
        i = randint(0,9)
        selected = features[i]
        tomorrow = date.today()+timedelta(1)
        
        f = Featured(location=selected, 
                day=tomorrow,
                description="50 cents off if you transact here today",
                amount=0.5,
                expires=datetime(tomorrow.year, tomorrow.month, tomorrow.day, 13,59))
        f.save() 
        r['result'] = {'location': selected.name, 'loc_id': selected.id}
    else:
        r['result'] = '-1'
    return JSONHttpResponse(r)
