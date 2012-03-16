from common.models import OTNUser

emails = ""
for u in OTNUser.objects.all():
    emails += u.my_email + ","

print emails
