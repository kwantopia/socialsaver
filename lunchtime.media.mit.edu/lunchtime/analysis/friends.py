from common.models import OTNUser, Winner, Friends
from facebookconnect.models import FacebookProfile
import json

"""
    Script for finding out the number of friends that are signed up
"""

r = {}
fb_ids = FacebookProfile.objects.all().values("facebook_id") 
for u in FacebookProfile.objects.all():
    friends = Friends.objects.filter(facebook_id__in=fb_ids)
    num_friends = Friends.objects.filter(facebook_id=u.facebook_id, friends__in=friends).count()
    participant = OTNUser.objects.get(facebook_profile__facebook_id=u.facebook_id)
    r[u.facebook_id]="%s (%d): %d"%(participant.name, participant.id, num_friends)

print json.dumps(r, indent=2)

