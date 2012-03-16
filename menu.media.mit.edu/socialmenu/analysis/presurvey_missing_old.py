from common.models import OTNUser, Friends, Winner
from legals.models import Order
from django.db.models import Count 
from random import sample
from django.core.mail import send_mail
from presurvey.models import *

"""
    Notify of presurvey missing
"""

msg = """

Dear %s,

You have participated in the Legal's trial, but you have not filled out the Pick A Dish survey that needs to be filled out BEFORE going to Legal's.  Could you please take 3 minutes to fill it out at:

http://menu.mit.edu/legals/

After logging into the site with Facebook Connect, the survey is linked off of the YELLOW BOX.

While you are at it, could you also review your dishes and fill out the post surveys linked off of the Surveys tab?

Thank you very much for taking the time to help out with the research.

-kwan
"""

presurvey_notify = set()

num_participants=0
num_missing=0

for u in OTNUser.objects.exclude(my_email="kool@mit.edu"):
    # filter people who have ordered at least one item
    orders = Order.objects.filter(user = u).order_by('timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)
    if orders.count() > 0:
        num_participants += 1
        # filter people who filled out the presurvey
        if LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id).exists():
            presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id)[0]
            print u.my_email, presurvey.referrer 
        else: 
            print u.my_email, "Presurvey Missing" 
            num_missing += 1
            presurvey_notify.add(u.id)

for pid in list(presurvey_notify):
    u = OTNUser.objects.get(id=pid)
    send_mail("URGENT: Your presurvey hasn't been filled out", msg%u.name.split(" ")[0], 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
    print "Sent email to: %s"%u.my_email

print "Num participants:", num_participants
print "Num no presurvey:", num_missing
