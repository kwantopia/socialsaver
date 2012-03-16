from techcash.models import TechCashTransaction
from common.models import Friends, Location
from django.contrib.auth.models import User

# get transactions that your friends have made
u = User.objects.get(id=3)
# get friends
friend_fb_ids = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id).friends.values('facebook_id')

# get location
l = Location.objects.get(id=16)

# friends that have visited same places
friends = TechCashTransaction.objects.filter(location=l, user__user__facebook_profile__facebook_id__in=friend_fb_ids).values('user__user').distinct()

similar = []
for f in friends:
    g = User.objects.get(id = f['user__user'])
    friend = Friends.objects.get(facebook_id=g.facebook_profile.facebook_id)
    similar.append(friend)


