from common.models import OTNUser, Friends, Winner
from legals.models import Order
from django.db.models import Count 
from random import sample
from django.core.mail import send_mail
from presurvey.models import *

winners = []
participants = 0
for u in OTNUser.objects.all():
    orders = Order.objects.filter(user = u).order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)
    if orders.count() == 1:
        winners.append((u.name, u.id))
        participants += 1
    elif orders.count() > 1:
        winners.append((u.name, u.id))
        winners.append((u.name, u.id))
        winners.append((u.name, u.id))
        winners.append((u.name, u.id))
        participants += 1

print len(winners), sample(winners,1)
print "Num participants:", participants
# check all the people that came after this user
msg = """

Hello %s,

Just wanted to remind you to review your dining experience at Legals by logging into http://menu.mit.edu/legals/.
And please upload your receipts or link wesabe.com account (see FAQ) to receive the Amazon gift certificates. 

And the good news: You have won $50 Legal's gift certificate since at least three friends have participated.  You need to arrange a time for pick up at the Media Lab.  Feel free to e-mail when it's convenient for you.

Cheers,

-kwan
"""

refs = []
presurvey_notify = set()

num_participants=0

for u in OTNUser.objects.exclude(my_email="kool@mit.edu"):
    orders = Order.objects.filter(user = u).order_by('timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)
    if orders.count() > 0:
        if orders.count() > 2:
            print "iPad",orders.count()
        first_order = orders[0]
        num_participants += 1
        friends_fb_ids = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id).friends.exclude(facebook_id=706848).values_list('facebook_id', flat=True)
        referrals = Order.objects.exclude(user=u).filter(timestamp__gt=first_order.timestamp).annotate(num_items=Count('items')).filter(num_items__gt=0).filter(user__facebook_profile__facebook_id__in=friends_fb_ids).values('user').distinct()
        
        if referrals.count() > 2:
            print referrals.count()
            for r in referrals:
                f = OTNUser.objects.get(id=r['user'])
                if LegalsPopulationSurvey.objects.filter(facebook_id=f.facebook_profile.facebook_id).exists():
                    presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=f.facebook_profile.facebook_id)[0]
                    print r, f.my_email, presurvey.referrer 
                else: 
                    print r, f.my_email, "Presurvey Missing" 
                    presurvey_notify.add(r["user"])
            print "Above referred by:(%d) %s (date:%s)"%(u.id, u.name, u.legals_order.all().order_by('timestamp')[0].timestamp)

            """
            if not Winner.objects.filter(user=u).exists():
                w = Winner(user=u, prize="$50 Legal's Gift Certificate")
                w.save()
                send_mail("Referral Award $50 Legal's gift certificate", msg%u.name.split(" ")[0], 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
                print "Sent email to: %s"%u.my_email
            """
            refs.append((u.name,u.id, referrals.count()))

print refs

#winners = [27, 40, 29, 25, 43, 81, 133]
#winners = [79, 91, 166]
#winners = [92]
#winners = [257]
#winners = [168, 109]
#winners = [148] + Sang Kim + Yod
#winners = [137] Tracey
#winners = [306] Tamiko
#winners = [305] Matt (Need to send out)
winners = []
for wid in winners:
    u = OTNUser.objects.get(id=wid)
    w = Winner(user=u, prize="$50 Legal's Gift Certificate")
    w.save()
    send_mail("Referral Award $50 Legal's gift certificate", msg%u.name.split(" ")[0], 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
    print "Sent email to: %s"%u.my_email


