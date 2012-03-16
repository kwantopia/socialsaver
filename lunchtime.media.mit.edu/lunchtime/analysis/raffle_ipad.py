from common.models import OTNUser, Friends
from facebookconnect.models import FacebookProfile
from datetime import date, datetime
from mobile.models import FeedEvent
import random

"""
    Script for finding out the number of friends that are signed up
"""

raffle_list = []
# find the number of friends and add
r = {}
raffle_f = []
fb_ids = FacebookProfile.objects.all().values("facebook_id") 
for u in FacebookProfile.objects.all():
    friends = Friends.objects.filter(facebook_id__in=fb_ids)
    num_friends = Friends.objects.filter(facebook_id=u.facebook_id, friends__in=friends).count()
    participant = OTNUser.objects.get(facebook_profile__facebook_id=u.facebook_id)
    r[u.facebook_id]="%s (%d): %d"%(participant.name, participant.id, num_friends)
    if num_friends > 2:
        raffle_f.append((participant.name, num_friends))
print raffle_f

# find the number of transactions and add
start_date = datetime(2010, 4, 1)
end_date = datetime(2010, 5, 25)

exclude_users = []

raffle_t = []
for u in OTNUser.objects.all():
    num_txns = u.techcashtransaction_set.filter(timestamp__range=(start_date, end_date), amount__gt=3.0).count()
    if num_txns < 30:
        exclude_users.append(u)
    else:
        raffle_t.append((u.name, num_txns))
print raffle_t

# number of reviews added
raffle_r = []
for u in OTNUser.objects.all():
    if u not in exclude_users:
        num_reviews = u.techcashtransaction_set.filter(receipt__detail__iregex=r'^\w+').count()
        raffle_r.append((u.name, num_reviews))
print raffle_r

# number of times app access
raffle_a = []
for u in OTNUser.objects.all():
    if u not in exclude_users:
        num_feeds = FeedEvent.objects.filter(user=u).count()
        raffle_a.append((u.name, num_feeds))
print raffle_a

for m in raffle_f:
    for i in range(m[1]*5):
        raffle_list.append(m[0])
for m in raffle_t:
    for i in range(m[1]):
        raffle_list.append(m[0])
for m in raffle_r:
    for i in range(m[1]):
        raffle_list.append(m[0])
for m in raffle_a:
    for i in range(m[1]):
        raffle_list.append(m[0])

random.shuffle(raffle_list)
j = random.randint(0, len(raffle_list))
print raffle_list[j]

# find number of friends
for m in raffle_f:
    if raffle_list[j] == m[0]:
        print raffle_list[j], m[1]
        break

# raffle for the surveys
from survey.models import BasicFoodSurvey, EatingCompanySurvey, EatingOutSurvey, DigitalReceiptSurvey

raffle_1=[]
raffle_2=[]
raffle_3=[]
raffle_4=[]
for s in BasicFoodSurvey.objects.all():
    if s.completed:
        raffle_1.append(s.user.otnuser.name)
for s in EatingCompanySurvey.objects.all():
    if s.completed:
        raffle_2.append(s.user.otnuser.name)
for s in EatingOutSurvey.objects.all():
    if s.completed:
        raffle_3.append(s.user.otnuser.name)
for s in DigitalReceiptSurvey.objects.all():
    if s.completed:
        raffle_4.append(s.user.otnuser.name)

random.shuffle(raffle_1)
random.shuffle(raffle_2)
random.shuffle(raffle_3)
random.shuffle(raffle_4)
print raffle_1[3], len(raffle_1)
print raffle_2[3], len(raffle_2)
print raffle_3[3], len(raffle_3)
print raffle_4[3], len(raffle_4)
        
