from common.models import OTNUser, Friends, Winner
from django.db.models import Count 
from random import sample
from django.core.mail import send_mail
from presurvey.models import *

"""
    Notify of presurvey missing
"""

msg = """

Dear %s,

You have participated in the Legal's trial past year but I have no record of your presurvey which is essential for finishing up my dissertation.  You have been rewarded a coupon for participating and the presurvey was part of the study.  Could you please take 3 minutes to fill it out at:

http://menu.mit.edu/legals/

After logging into the site with Facebook Connect, the survey is linked off of the YELLOW BOX towards the top of the page.

While you are at it, could you also review your dishes and fill out the post surveys linked off of the Surveys tab?

Thank you very much for taking the time to help out with the research.

-kwan
"""

delinquent = []

for u in OTNUser.objects.all().annotate(num_items=Count('legals_order__items')).filter(num_items__gt=0):
    if not LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id):
        delinquent.append(u.my_email)

for email in delinquent: 
    u = OTNUser.objects.get(my_email=email)
    send_mail("URGENT: Your presurvey hasn't been filled out before", msg%u.name.split(" ")[0], 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
    print "Sent email to: %s"%u.my_email

# potentially alums
alums = ['c_k@alum.mit.edu', 'jsslee@alum.mit.edu', 'junie@alum.mit.edu']
for email in alums:
    send_mail("URGENT: Your presurvey hasn't been filled out before", msg%"Friend", 'Digital Menu <kwan@media.mit.edu>', [email], fail_silently=False) 
    print "Sent email to: %s"%email
    
