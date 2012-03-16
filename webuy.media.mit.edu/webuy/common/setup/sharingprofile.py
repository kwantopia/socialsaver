from common.models import SharingProfile
from common.models import OTNUser

users = OTNUser.objects.all()
for u in users:
    prof, created = SharingProfile.objects.get_or_create(user=u)
