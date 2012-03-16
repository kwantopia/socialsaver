from common.models import OTNUser, Friends
from presurvey.models import LegalsPopulationSurvey

u = OTNUser.objects.get(id=4)
friends = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id).friends.values("facebook_id")
print friends.count()
print LegalsPopulationSurvey.objects.filter(facebook_id__in=friends).count()

for s in LegalsPopulationSurvey.objects.filter(facebook_id__in=friends):
    n = Friends.objects.get(facebook_id=s.facebook_id)
    print "%s: %s"%(s.email, n.name)
    for m in s.favorite_dishes.all():
        print "\t%s"%m.name
