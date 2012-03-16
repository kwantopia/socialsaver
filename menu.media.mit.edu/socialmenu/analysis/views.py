from presurvey.models import *
from django.http import HttpResponse
from django.db.models import Count
from common.helpers import JSONHttpResponse
from facebook.djangofb import get_facebook_client
from facebookconnect.models import FacebookProfile
from common.models import Friends, Winner, OTNUser
import json
from datetime import datetime, date, timedelta

def winner_add(request):
    """
        Adds winner to Winner table

        :url: /a/winner/add/
    """
    r = {}

    if request.POST.get('code','000') == 'ch00seW199Er':
        u = OTNUser.objects.get(facebook_profile__facebook_id=517379465)
        w = Winner(user=u, prize="$100 Legal's Gift Certificate")
        w.save()
        # update to old time
        w.timestamp=datetime(year=2010, month=3, day=21, hour=0, minute=0, second=0)
        w.save()
        r['result'] = {'name':w.user.name, 'id': "%d"%w.user.id}
    else:
        r['result'] = '-1'
    return JSONHttpResponse(r)

def num_participants(request):
    """
        Calculate the number of people with e-mail addresses
        recorded and have a zip code in Boston area 

        :url: /a/num/participants/    

    """
    boston = BostonZip.objects.all().values("zipcode")

    m_num = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston).values('email').distinct().count()
    s_num = User.objects.all().count() 
    c_num = User.objects.filter(completed=True).count()
    g_num = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston,gluten=False).values('email').distinct().count()
    r = {}

    r['survey_participants'] = s_num
    r['menu_participants'] = m_num
    r['completed'] = c_num 
    r['gluten'] = g_num 
    return JSONHttpResponse(r)

def get_emails(request):
    """
        Return e-mails of participants

        :url: /a/get/emails/
    """
    boston = BostonZip.objects.all().values("zipcode")

    p_emails = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)
    
    addresses = ""
    for e in p_emails:
        addresses += e+","
    return HttpResponse( addresses )

def get_emails_iphone(request):
    """
        Return e-mails of iPhone participants

        :url: /a/get/emails/iphone/
    """
    boston = BostonZip.objects.all().values("zipcode")

    p_emails = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston,gluten=False,phone_type=0).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)
    
    addresses = ""
    for e in p_emails:
        addresses += e+","
    return HttpResponse( addresses )

def phone_distribution(request):
    """
        Return the distribution of different phones people have

        :url: /a/phone/distribution/
    """
    r = {}

    boston = BostonZip.objects.all().values("zipcode")

    phone_types_survey = LegalsPopulationSurvey.objects.values('phone_type').annotate(type_count=Count('phone_type')).order_by('phone_type')
    phone_types_participants = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston).values('phone_type').annotate(type_count=Count('phone_type')).order_by('phone_type')
    
    r["survey_participants"] = [p for p in phone_types_survey]
    r["menu_participants"] = [p for p in phone_types_participants]

    return JSONHttpResponse(r)

def legals_experienced(request):
    """
        People who have been to Legal Sea Foods

        :url: /a/legals/experienced/
    """
    r = {}

    boston = BostonZip.objects.all().values("zipcode")

    survey_participants = LegalsPopulationSurvey.objects.values('legals_visits').annotate(type_count=Count('legals_visits')).order_by('legals_visits') 
    menu_participants = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston).values('legals_visits').annotate(type_count=Count('legals_visits')).order_by('legals_visits') 
    r['survey_participants'] = [s for s in survey_participants]
    r['menu_participants'] = [s for s in menu_participants]

    return JSONHttpResponse(r)

def demographic_distribution(request):
    """
        Demographic distribution of participants 

        :url: /a/demographic/distribution
    """
    r = {}

    boston = BostonZip.objects.all().values("zipcode")

    survey_sex = LegalsPopulationSurvey.objects.values('sex').annotate(type_count=Count('sex')).order_by('sex') 
    menu_sex = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston).values('sex').annotate(type_count=Count('sex')).order_by('sex') 
    survey_participants = LegalsPopulationSurvey.objects.values('age').annotate(type_count=Count('age')).order_by('age') 
    menu_participants = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston).values('age').annotate(type_count=Count('age')).order_by('age') 
    r['survey_participants'] = [s for s in survey_participants]
    r['menu_participants'] = [s for s in menu_participants]
    r['survey_sex'] = [s for s in survey_sex]
    r['menu_sex'] = [s for s in menu_sex]

    return JSONHttpResponse(r)

def experiment_distribution(request):
    """
        Show how many participated in different experiments

        :url: /a/experiment/distribution/
    """

    r = {}

    boston = BostonZip.objects.all().values("zipcode")

    survey_exp = User.objects.values('experiment').annotate(exp_count=Count('experiment')).order_by('experiment')

    menu_participant_ids = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston).values_list('facebook_id', flat=True)
    menu_exp = User.objects.filter(id__in=menu_participant_ids).values('experiment').annotate(exp_count=Count('experiment')).order_by('experiment')

    incompletes = User.objects.filter(completed=False).values('experiment').annotate(exp_count=Count('experiment')).order_by('experiment')

    r['incomplete'] = [i for i in incompletes]
    r['survey_experiments'] = [s for s in survey_exp]
    r['menu_experiments'] = [s for s in menu_exp]

    return JSONHttpResponse(r)

def friends_at_signup(request):
    """
        Shows distribution of friends at sign up

        :url: /a/friends/atsignup/
    """
    r = {}

    boston = BostonZip.objects.all().values("zipcode")

    non_participant_ids = LegalsPopulationSurvey.objects.filter(email="").values_list('facebook_id', flat=True)
    non_participant_friends = User.objects.filter(id__in=non_participant_ids).values('friends_at_signup').annotate(f_count=Count('friends_at_signup')).order_by('friends_at_signup')

    participant_ids = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston).values_list('facebook_id', flat=True)
    participant_friends = User.objects.filter(id__in=participant_ids).values('friends_at_signup').annotate(f_count=Count('friends_at_signup')).order_by('friends_at_signup')

    r['fs_at_signup_participants'] = [f for f in participant_friends]
    r['fs_at_signup_nonparticipants'] = [f for f in non_participant_friends]

    return JSONHttpResponse(r)

def referral_distribution(request):
    """
        Shows number of friends invited and referred

        :url: /a/referral/distribution/
    """
    r = {}

    boston = BostonZip.objects.all().values("zipcode")

    referrers = LegalsPopulationSurvey.objects.filter(email="").filter(zipcode__in=boston).values('referrer').annotate(r_count=Count('referrer')).order_by('r_count')

    r['referrals'] = [ref for ref in referrers]

    invites = Invited.objects.values('user').annotate(r_count=Count('user')).order_by('-r_count')

    r['invites'] = [i for i in invites]

    # find invites that joined
    participants = User.objects.all().values("id")
    invite_accepted = Invited.objects.filter(invited__in=participants).values('user').annotate(j_count=Count('user')).order_by('-j_count')
    
    total_accepted = Invited.objects.filter(invited__in=participants).count()

    r['invite_accepted'] = [i for i in invite_accepted]
    r['total_accepted'] = total_accepted 

    return JSONHttpResponse(r)

def build_friend_net(request):
    """
        Builds the friend map from participants

        :url: /a/build/friendnet/
    """
    r = {}
    
    # read friend_str and build the Friend table
    users = User.objects.all()

    for u in users:
        try:
            m = FriendMapped.objects.get(user=u)
            if m.mapped:
                # skip to next user
                continue
        except FriendMapped.DoesNotExist:
            # it has never been mapped, continue
            pass

        try:
            friends = eval(str(u.friends_str))
            my, created = Friends.objects.get_or_create(facebook_id=u.id)
            my.save()
            for f in friends:
                a_friend, created = Friends.objects.get_or_create(facebook_id=f["uid"])
                a_friend.image=f["pic_square"]
                a_friend.name=f["name"]
                a_friend.save()
                if not my.friends.filter(facebook_id=a_friend.facebook_id).exists():
                    my.friends.add(a_friend)
        except TypeError:
            print u.friends_str
        map, created = FriendMapped.objects.get_or_create(user=u)
        map.mapped = True
        map.save()
    
    r["result"] = "done"
    return JSONHttpResponse(r)

def count_friends(request):
    """
        Check how many friends have signed up for each user

        :url: /a/friends/signedup/   
    """

    r = {}
    r["friend_count"] = []

    # friends signed up sorted by number of friends

    boston = BostonZip.objects.all().values("zipcode")
    participant_ids = LegalsPopulationSurvey.objects.exclude(email="").filter(zipcode__in=boston).values_list('facebook_id', flat=True)
    users = User.objects.filter(id__in=participant_ids, completed=True)

    i = 0
    for u in users:
        friend_fb_ids = Friends.objects.get(facebook_id=u.id).friends.all().values_list('facebook_id', flat=True)
        print friend_fb_ids.count()
        num_friends = User.objects.exclude(id=u.id).filter(id__in=friend_fb_ids).count()
        r["friend_count"].append( {"id":u.id, "num_friends":num_friends} )
        if num_friends > 10:
            i += 1
    r["have_friends"] = i

    return JSONHttpResponse(r)

def participants(request):
    r = {}
    r["participants"] = []
    for u in OTNUser.objects.filter(voucher=False).order_by('name'):
        r["participants"].append((u.name, u.my_email))

    return JSONHttpResponse(r)


