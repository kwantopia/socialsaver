from facebookconnect.models import FacebookProfile
from common.models import OTNUser
from django.contrib.auth.models import User

f_id=706848
df = FacebookProfile.objects.get(facebook_id=f_id)
df.delete()
du = OTNUser.objects.get(username=str(f_id))
du.delete()

