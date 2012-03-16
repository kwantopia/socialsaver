from django.test import TestCase
from django.test.client import Client
from common.models import OTNUser, Friends, Winner
import json
from django.db.models import Count
from legals.models import Order, TableCode, EventBasic, EventMenuItem, EventSpecial, EventCategory
from presurvey.models import BostonZip, LegalsPopulationSurvey
from django.core.mail import send_mail
import textwrap
import hashlib, random
from datetime import datetime, timedelta

c = Client()

def call(command, params={'e':'e'}):
    print 'CALL:', command
    response = c.post(command, params)
    print response

def call_json(command, params={'e':'e'}):
    print 'CALL:', command
    response = c.post(command, params)
    print json.dumps(json.loads(response.content), indent=2)
    return json.loads(response.content)

def latest_joined(n=1):
    """
        print people who joined last few days
    """

    for u in OTNUser.objects.filter(date_joined__gt=datetime.today()-timedelta(n)):
        print u.name, LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id).exists()

def add_winner():
    command = "/a/winner/add/"
    call_json(command, {'code':'ch00seW199Er'})

def get_emails():
    command = '/a/get/emails/'
    call(command)

def make_stats():
    command = '/a/num/participants/'
    call_json(command)

    command = '/a/get/emails/'
    call(command)

    command = '/a/get/emails/iphone/'
    call(command)

    command = '/a/phone/distribution/'
    call_json(command)

    command = '/a/legals/experienced/'
    call_json(command)

    command = '/a/demographic/distribution/'
    call_json(command)

    command = '/a/experiment/distribution/'
    call_json(command)

    command = '/a/friends/atsignup/'
    call_json(command)

    command = '/a/referral/distribution/'
    call_json(command)

    command = '/a/friends/signedup/'
    call_json(command)

def build_friendnet():

    command = '/a/build/friendnet/'
    call_json(command)

def participants():

    command = '/a/participants/'
    a = call_json(command)
    for u in a["participants"]:
        print u[0], u[1]
    for u in a["participants"]:
        print u[0]

def set_voucher_claimed(name):
    """
        Sets the voucher to be claimed
    """
    u = OTNUser.objects.get(name=name)
    u.voucher=True
    u.save()

def check_events(table_code): 
    tc = TableCode.objects.get(code=table_code)
    o = Order.objects.get(table=tc)
    print EventBasic.objects.filter(order=o)
    print EventCategory.objects.filter(order=o)
    print EventSpecial.objects.filter(order=o)
    print EventMenuItem.objects.filter(order=o)

def print_events(u): 
    print EventBasic.objects.filter(user=u)
    print EventCategory.objects.filter(user=u)
    print EventSpecial.objects.filter(user=u)
    print EventMenuItem.objects.filter(user=u)


def reimburse():
    for u in OTNUser.objects.all():
        wesabe_linked = False
        for w in u.wesabeaccount_set.all():
            if w.wesabetransaction_set.all().count()>5:
                print "$30", u.my_email, "Txns: %d"%w.wesabetransaction_set.all().count()
                wesabe_linked = True 

        if u.legals_order:
            orders = u.legals_order.order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)
            if orders.count() > 0:
                if orders.count() > 3:
                    wesabe_linked = False
                for o in orders:
                    try:
                        if not wesabe_linked and o.receipt.url:
                            print "$10", u.my_email, "Purchased:%s"%o.total_price(), o.receipt.url
                    except:
                        pass
            
def receipt_reminder_may27():
    msg = """
Hello,

Just wanted to remind you to review your dining experience at Legals by logging into http://menu.mit.edu/legals/ and fill out the surveys in the Surveys tab for raffle chances.

And please upload your receipts or link wesabe.com account (see FAQ) to receive the Amazon gift certificates.  For those who have done all this, you will receive Amazon gift cards via e-mail by tomorrow.

I would also like to announce that 4 participants have won the $50 Legal's gift certificate this week, for having 3 of their Facebook friends participate.  The winners' names will be kept anonymous from today due to privacy reasons.  You will be able to see from http://menu.mit.edu/legals/ after you login whether you have won. If you had at least 3 friends participate you deserve a $50 Legal's gift certificate.  You may also ask your friends if they have won :)

Happy Memorial Weekend!

-kwan
    """
    for u in OTNUser.objects.all():
        send_mail("Amazon gift certificates", msg, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email
   
def receipt_reminder_may30():
    msg = """
Hello,

Sorry for the delay in getting the certificates.  I had to figure out an easier way than e-mailing every individual and tracking receipt of human subject voucher form for compensation.  The accounting office requires each person to fill out the Human Subject Voucher for auditing purposes.  I created a simple interface for you to enter your required information for compensation after you login.  This is only required once.  Once your information is entered, Amazon claim codes will be available in the same place by tonight.  Future rewards will also be posted here.  Bare with me, since I have to manually type in all the codes, but I will get them done by midnight tonight if you fill out your forms by then.

Several of you have not reviewed your meal nor filled out the surveys in the Surveys tab.   You may do so by logging into http://menu.mit.edu/legals/ 

Happy Memorial Weekend!

-kwan
    """
    for u in OTNUser.objects.filter(voucher=True):
        send_mail("Amazon gift certificate update", msg, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def transfer(table_code, email):
    """
        e-mail is the user e-mail to transfer to 
    """
    u = OTNUser.objects.get(my_email=email)
    tc = TableCode.objects.get(code=table_code)
    orders = Order.objects.filter(table=tc)
    i = 0
    for order in orders:
        if order.items.count()>0:
            i += 1
            print order.id, order.items.count()
            o = order
            
    if i > 1:
        print "There are more than one set of order"
        return
    for e in EventBasic.objects.filter(order=o):
        e.user = u
        e.save()
    for e in EventCategory.objects.filter(order=o):
        e.user = u
        e.save()
    for e in EventSpecial.objects.filter(order=o):
        e.user = u
        e.save()
    for e in EventMenuItem.objects.filter(order=o):
        e.user = u
        e.save()
    o.user = u
    o.save()

def transfer_order(order_id, email):
    """
        e-mail is the user e-mail to transfer to 
    """
    u = OTNUser.objects.get(my_email=email)
    o = Order.objects.get(id=order_id)
    for e in EventBasic.objects.filter(order=o):
        e.user = u
        e.save()
    for e in EventCategory.objects.filter(order=o):
        e.user = u
        e.save()
    for e in EventSpecial.objects.filter(order=o):
        e.user = u
        e.save()
    for e in EventMenuItem.objects.filter(order=o):
        e.user = u
        e.save()
    o.user = u
    o.save()


opt_out = ["mvulana@gmail.com", "shengxingstars@gmail.com", 'akenney@mit.edu', 'theusualanomaly@yahoo.com', 'chengj@mit.edu', "cguan90@gmail.com", "lbarkal@mit.edu", "sara.vanwie@gmail.com", "aanello@gmail.com", "sricoult@mit.edu", "erika.tabacniks@gmail.com", "web@jeffvyduna.com", "i.t.hwang@gmail.com", "bradford.frost@gmail.com", "hhammad111@gmail.com", "narci@mit.edu", "katiemthom@gmail.com", 'rxu@wellesley.edu', 'almoore@mit.edu', 'egkrull@gmail.com', 'o_h@mit.edu', 'alex.zavackis@gmail.com', 'lnmerr@gmail.com', 'andrew@aeestudios.com', 'chelseao@mit.edu', 'tylor@mit.edu']

def change_pin(email, new_pin):
    u = OTNUser.objects.get(my_email=email)
    u.pin = hashlib.sha224(new_pin).hexdigest()
    u.save()

def send_emails():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True))
    exclude_list.append("")
    exclude_list.append("mvulana@gmail.com")
    exclude_list.append("shengxingstars@gmail.com")
    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 
Hi there,

    You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis.

There are two things to do:

1. Create a PIN at http://menu.mit.edu/legals/. You will use this to access the menu at the restaurant.
2. Visit Legal Sea Foods in Kendall Square and have a subsidized meal. (iPhones and vouchers will be waiting there for you!)

Over 20 people participated over the past week and have enjoyed a nice subsidized meal at Legals.

PS: I encourage you to participate in this unique opportunity of experiencing research in the real world.  Your participation is extremely helpful and crucial to my Ph.D. thesis and the results of the trial will be shared with you through a research report.  Feel free to e-mail or call me at 617-909-2101 with any questions.

Sincerely,

Kwan
    ''' 
    for e in p_emails:
        send_mail("It's simple to participate", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e
        #pass
        #send_mail("It's simple to participate", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', ["ukwan@yahoo.com"], fail_silently=False) 


def send_emails_may11():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True))
    exclude_list.append("")
    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 
Hello,

This weekend is the last weekend to dine to participate in the iPhone 3G raffle. 
(There is still time for other rewards: iPad will be raffled on 6/15 and a $200 Apple gift certificate raffle is added for 6/30.)

1. Please create a PIN at http://menu.mit.edu/legals/ before you come to the restaurant.
2. Get a subsidized meal at Legal Sea Foods Kendall Square. (iPhones and vouchers will be waiting there for you.)
3. Upload your receipt and you will receive $10 Amazon gift certificate.

Referral Bonus: After you have participated, if you refer at least 5 of your friends participate in the trial, you will be rewarded $50 Legal's gift certificate with no restrictions.

Also, if you have an iPhone, you may go to other Legal Sea Food locations and participate.  E-mail me to arrange for vouchers and table code.

Sincerely,

Kwan

--------------------------------------------------------------------
You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.  Please let me know if you are no longer interested in receiving this e-mail so I may invite others.



    ''' 

    for e in p_emails:
        send_mail("Digital Menu: One more weekend for iPhone raffle", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

    msgs = ''' 
Hello,

I encourage you to dine at Legal's this week.  You will be entered into iPhone 3G raffle if you visit by this Sunday.  Please visit Legal Sea Foods in Kendall Square and have a subsidized meal. (iPhones and vouchers will be waiting there for you!)

After your meal: If you rate/review and upload your receipts you will get a $10 Amazon gift certificate.  Or if you link your wesabe account (check FAQ) you will receive a $30 Amazon gift certificate.  Unfortunately, it is a little complicated to process cash and I have been advised to reward using gift certificates.  

Also if you visit third time by 6/15, you are eligible for iPad raffle and I have added an additional raffle of $200 Apple gift certificate for 6/30 for those who have visited a third time.

Referral Bonus: After you have participated, if at least 5 of your friends participate in the trial, you will be rewarded $50 Legal's gift certificate with no restrictions.


Sincerely,

Kwan


----------------------------------------------------------------------
You are receiving this e-mail because you have registered at http://menu.mit.edu/legals/ and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.

    ''' 

    r_emails = OTNUser.objects.filter(voucher=False).values_list("my_email", flat=True)
    print "email count:", len(r_emails)
    for e in r_emails:
        send_mail("Digital Menu: One more weekend for iPhone raffle", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

    msgs = ''' 
Hello,

Hope you enjoyed your meal at Legal's.  Please check back at http://menu.mit.edu/legals/ to rate and review your meals.  

After you review and upload your receipts you will get a $10 Amazon gift certificate.  Or if you link your wesabe account (check FAQ) you will receive a $30 Amazon gift certificate.  Unfortunately, it is a little complicated to process cash and I have been advised to reward using gift certificates.  

Also if you visit one more time by this Sunday, you are eligible for iPhone 3G raffle.  If you have visited a third time by 6/15, you are eligible for iPad raffle and I have added an additional raffle of $200 Apple gift certificate for 6/30 for those who have visited a third time.

Referral Bonus: If you can encourage at least 5 of your friends to participate in the trial, you will be rewarded $50 Legal's gift certificate with no restrictions.  Please encourage your friends to participate.

Sincerely,

Kwan

------------------------------------------------------------------------
You are receiving this e-mail because you have registered at http://menu.mit.edu/legals/. Feel free to e-mail or call me at 617-909-2101 with any questions.

    ''' 

    r_emails = OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True)
    print "email count:", len(r_emails)
    for e in r_emails:
        send_mail("Digital Menu: Friendly Reminder", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

def send_emails_may13():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True))
    exclude_list.append("")
    exclude_list += opt_out

    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 

Hello,

First of all, thank you for participating in the trial. I hope you are enjoying the food and a glimpse of digital menu experience.  For those preparing for finals, hope you can come in to feed your brains in preparation for finals.

I just wanted to send a friendly reminder that the vouchers are valid only for entrees and the trial covers dinner only (after 4pm).  Sorry for those who came in to have a soup.  The data collected would be most useful if you engaged in a normal dining experience since one of the goals is to customize menus for individuals with certain taste attributes and goals.  

With a $10 voucher, the Legal's menu is quite a good deal.  And you can use the rest of the vouchers for lunch.

Sincerely,

Kwan

--------------------------------------------------------------------
You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.  Please let me know if you are no longer interested in receiving this e-mail so I may invite others.



    ''' 

    for e in p_emails:
        send_mail("Digital Menu: Vouchers for Entrees", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

    msgs = ''' 

Hello,

First of all, thank you for participating in the trial. I hope you are enjoying the food and a glimpse of digital menu experience.  For those preparing for finals, hope you can come in to feed your brains in preparation for finals.

I just wanted to send a friendly reminder that the vouchers are valid only for entrees and the trial covers dinner only (after 4pm).  Sorry for those who came in to have a soup.  The data collected would be most useful if you engaged in a normal dining experience since one of the goals is to customize menus for individuals with certain taste attributes and goals.  

With a $10 voucher, the Legal's menu is quite a good deal.  And you can use the rest of the vouchers for lunch.

Sincerely,

Kwan


----------------------------------------------------------------------
You are receiving this e-mail because you have registered at http://menu.mit.edu/legals/ and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.

    ''' 

    r_emails = OTNUser.objects.filter(voucher=False).values_list("my_email", flat=True)
    print "email count:", len(r_emails)
    for e in r_emails:
        send_mail("Digital Menu: Vouchers for Entrees", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e


def send_emails_may17():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True))
    exclude_list.append("")
    exclude_list += opt_out

    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 
Hello,

I hope you have all finished your finals if you are a student and if not I hope you are enjoying this great weather!

Here are the winners for this week:

    Jacinda Shelly won an iPhone 3G.
    Youngeun Yang, Tamie Kim have won $50 Legal's gift certificate for three friends participating.

Just reminding you to please come dine at Legal's this weekend and help me graduate :).

1. IMPORTANT: Please create a PIN at http://menu.mit.edu/legals/ before you come to the restaurant.
2. Make a quick call to Legal's (617) 864-3400 to reserve for dinner telling them that you are participating in the Digital Menu trial.  
3. Get a subsidized meal at Legal Sea Foods Kendall Square. (iPhones and vouchers will be waiting there for you.)
4. Upload your receipt and you will receive $10 Amazon gift certificate or link Wesabe and receive $30 Amazon gift certificate.

Referral Award: After you have participated, if 3 of your friends also participate in the trial, you will be rewarded $50 Legal's gift certificate with no restrictions. Yes, just 3 of your friends. 

Also, if you have an iPhone, you may go to other Legal Sea Food locations and participate.  E-mail me to arrange for vouchers and table code.

There is still time for many more rewards: iPad will be raffled on 6/15, $200 Apple Gift Certificate on 6/30 (end of this trial). $50 Apple/Amazon/Legal's gift certificates are raffled each week for filling out surveys after participation. 

Also, after your third visit, you will be invited for a FREE meal at Legal's to evaluate a new menu design.

Sincerely,

Kwan

--------------------------------------------------------------------
You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.  Please let me know if you are no longer interested in receiving this e-mail so I may invite others.



    ''' 

    for e in p_emails:
        send_mail("Digital Menu: Come Come!", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

    msgs = ''' 
Hello,

I hope you have finished your finals if you are a student and if not I hope you are enjoying this great weather!

Here are the winners for this week:

    Jacinda Shelly won an iPhone 3G.
    Youngeun Yang, Tamie Kim have won $50 Legal's gift certificate for three friends participating.

1. IMPORTANT: Remember your PIN you created at http://menu.mit.edu/legals/ or change it before coming. 
2. Make a quick call to Legal's (617) 864-3400 to reserve for dinner telling them that you are participating in Digital Menu trial (due to graduation season traffic).
3. Upload your receipt and you will receive $10 Amazon gift certificate or link Wesabe and receive $30 Amazon gift certificate.
4. There are also few quick surveys (http://menu.mit.edu/survey/ after login) you could fill out after your participation.  For each survey a $50 gift certificate will be raffled.

Referral Award: After you have participated, if just 3 of your friends also participate in the trial, you will be rewarded $50 Legal's gift certificate with no restrictions. (Has become easier, YES!)

Winners will be posted at http://menu.mit.edu/legals/winners/

Also, if you have an iPhone, you may go to other Legal Sea Food locations and participate.  E-mail me to arrange for vouchers and table code.

There is still time for many more rewards: iPad will be raffled on 6/15 and a $200 Apple gift certificate on 6/30. $50 gift certificates are raffled for filling out each survey after participation.

Also, after your third visit, you will be invited for a FREE meal at Legal's to evaluate a new design.

Sincerely,

Kwan


----------------------------------------------------------------------
You are receiving this e-mail because you have registered at http://menu.mit.edu/legals/ and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.

    ''' 

    r_emails = OTNUser.objects.filter(voucher=False).values_list("my_email", flat=True)
    print "email count:", len(r_emails)
    for e in r_emails:
        send_mail("Digital Menu Survey: Your Input is Extremely Valuable", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

    msgs = ''' 
Hello,

I hope you are enjoying the great weather!  Thank you for your participation and please tell your friends to participate.  If 3 friends participate after you, you will win $50 Legal's gift certificate.

Here are the winners for this week:

    Jacinda Shelly won an iPhone 3G
    Youngeun Yang, Tamie Kim have won $50 Legal's gift certificate for three friends participating.

Amazon gift certificates will be processed next week.  Please check back at http://menu.mit.edu/legals/ to rate and review your meals.  After you review and upload your receipts you will get a $10 Amazon gift certificate.  Or if you link your wesabe account (check FAQ) you will receive a $30 Amazon gift certificate.  

There are also few quick surveys you could fill out once you login.  For each survey $50 gift certificates (Legal's/Apple/Amazon of your choice) will be raffled next week.  Your input is extremely valuable.

Winners will be posted at http://menu.mit.edu/legals/winners/

There is still time for many more rewards: iPad will be raffled on 6/15 and a $200 Apple gift certificate on 6/30.

Hope you can visit again.  Also, after your third visit, you will be invited for a FREE meal at Legal's to evaluate a new design.

Sincerely,

Kwan

------------------------------------------------------------------------
You are receiving this e-mail because you have registered at http://menu.mit.edu/legals/. Feel free to e-mail or call me at 617-909-2101 with any questions.

    ''' 

    r_emails = OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True)
    print "email count:", len(r_emails)
    for e in r_emails:
        send_mail("Digital Menu: 5 min survey for $50 raffle", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e


def send_emails_may27():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True))
    exclude_list.append("")
    exclude_list += opt_out

    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 
Hello,

Only a month remain for participating in the trial!

I still need 70 more people to participate so hope you can drop by and have a nice sea food and provide feedback.  Feel free to forward it to your friends and collegues in Boston.

1. IMPORTANT: Please create a PIN at http://menu.mit.edu/legals/ before you come to the restaurant.

2. Make a quick call to Legal's (617) 864-3400 to reserve for dinner telling them that you are participating in the Digital Menu trial.  

3. Get a subsidized meal at Legal Sea Foods Kendall Square. (You will receive $30 worth of vouchers where first $10 can be applied to your first meal.  iPhones and vouchers will be waiting there for you.)

4. Upload your receipt and you will receive $10 Amazon gift certificate or link Wesabe and receive $30 Amazon gift certificate.

Referral Bonus: After you have participated, if 3 of your friends also participate in the trial, you will be rewarded $50 Legal's gift certificate with no restrictions. 

Also, if you have an iPhone, you may go to other Legal Sea Food locations and participate.  E-mail me to arrange for vouchers and table code.

Raffles: iPad will be raffled on 6/15 for third time participants, $200 Apple Gift Certificate on 6/30 for all (end of this trial). $50 Apple/Amazon/Legal's gift certificates are raffled each week for filling out surveys after participation. 

Also, after your third visit, you will be invited for a FREE meal at Legal's to evaluate a new menu design.

Sincerely,

Kwan

--------------------------------------------------------------------
You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.  Please let me know if you are no longer interested in receiving this e-mail so I may invite others.


    ''' 

    for e in p_emails:
        send_mail("Enjoy your last week of May with some sea food!", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e


def amazon_cert_info():

    msgs = ''' 
Hello,

Sorry for the delay in getting the Amazon gift certificates to you.  Mainly, I need to manually check and type the claim code and e-mail, so I am going to make it available through the website when you login.  It should not take too long, but bare with me for few days and I will let you know when it's ready.

Thank you and have a great Memorial Day weekend!

Kwan

------------------------------------------------------------------------
You are receiving this e-mail because you have registered at http://menu.mit.edu/legals/. Feel free to e-mail or call me at 617-909-2101 with any questions.

    ''' 

    r_emails = OTNUser.objects.all().values_list("my_email", flat=True)
    print "email count:", len(r_emails)
    for e in r_emails:
        send_mail("Amazon gift certificate update", msgs, 'Digital Menu <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

def iPad_info():

    msgs = ''' 
Hi %s,

Amazon gift certificates are available online if you have participated, reviewed, uploaded receipt or linked wesabe account.  Just login to http://menu.mit.edu/legals/ and check the link inside the yellow box. If you just cannot find the receipt, it would be great if you could create a wesabe.com account and link your credit/debit card to contribute transaction data for research purposes.

For those who are curious about wesabe.com, it is a free personal financial management site (it will be useful just to try out, you can unsubscribe after the end of the trial and I can send you a reminder).  In the context of this research, it allows API access to download transactions to the menu site in a secure manner for clustering of purchase behavior during analysis phase.  I just want to assure you that the data is only for research purposes and will not be shared with any other parties (i.e. Legal's nor Facebook) as indicated in the consent form.

Regarding the iPad, the raffle is happening in 2 weeks and only 3 people currently qualify for it. There is also an Apple $200 gift certificate raffle at the end of this month where every participant is entered. If you visit at least three times during trial, you will also automatically be invited for a free dinner at Legal's to review a new digital menu in August. 

Finally, please fill out the Surveys in Surveys tab as soon as possible.  I will raffle the gift certificates for the surveys this Friday to celebrate the commencement. 

It would also be extremely appreciated if you could let few of your friends know about the trial.  Forward them this link: http://menu.mit.edu/media/DigitalMenuTrial.png

If each one of you just asked one person to participate this month, I will be able to conclude this study by end of this month!    

Thanks!

Kwan

PS: Friday is MIT commencement day and I have been told that dinner time is completed booked at Legal's so apologies for those who were thinking of visiting on Friday this week.

------------------------------------------------------------------------
You are receiving this e-mail because you have registered at http://menu.mit.edu/legals/. Feel free to e-mail or call me at 617-909-2101 with any questions.

    ''' 

    users = OTNUser.objects.all()
    print "email count:", users.count() 
    for u in users:
        send_mail("iPad update", msgs%u.name.split(" ")[0], 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def new_recruit_june5():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True))
    exclude_list.append("")
    exclude_list += opt_out

    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 

Hi there!

Over 90 people have participated and just need to reach 150 people to reach statistical significance :)

Just wanted to send you a quick reminder to participate and help out by 

    creating a PIN at http://menu.mit.edu/legals/

or if you can't participate please forward this link to your friends to take advantage of this offer to contribute to research and to have a subsidized sea food dinner and more.

    http://menu.mit.edu/media/DigitalMenuTrial.png

Your participation is extremely helpful for my thesis.

Thank you!

-kwan

--------------------------------------------------------------------
You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.  Please let me know if you are no longer interested in receiving this e-mail.

    ''' 

    for e in p_emails:
        send_mail("Digital Menu: Less than a month left!", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

def wesabe_update_june3():

    msgs = ''' 
Hi %s, 

Could you please go to your profile page (link with your Name on upper right corner after you login to http://menu.mit.edu/legals/) to update your wesabe link?  Mainly, the backend was only retrieving 30 transactions previously.  It should take only 3 minutes to complete :)

Thank you very much!

-Kwan

    ''' 

    for u in OTNUser.objects.all():
        if u.wesabeaccount_set.all().count() > 0:
            send_mail("Digital Menu: Come Come!", msgs%u.name.split(" ")[0], 'Digital Menu Invite <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
            print "Sent email to: %s"%u.my_email

def wireless_signal_june4():

    msgs = ''' 
Hi %s, 

If you happen to go again and experience the menu being slow, it's not because of the software but because of the wireless signal.  It would be great if you could move towards Ames St side of the restaurant momentarily to use the digital menu and add to the order, or ask the server to move you to a table closer to Ames St. side and away from Main St. side.  So far, tables on Ames St. side have worked pretty well, but when there are too many people at the restaurant, it is sometimes not possible to get seated on that side.

Hope you can invite more people to join!  I still need 60 more people.  
Less than a month remain for the trial.

Thank you for all your help!

-kwan

PS: Tonight is probably not a good night to participate due to MIT commencement.

    ''' 

    for u in OTNUser.objects.all():
        send_mail("Digital Menu: Wireless Signal", msgs%u.name.split(" ")[0], 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def ipad_raffle_june14():

    msgs = ''' 
Hi %s, 

I just wanted to let you know that tomorrow June 15 at 11:59 pm $550 Apple gift certificate will be raffled among those who have participated three times so you may use it for an iPad or the new iPhone.  Third time participants also qualify for a free meal to evaluate a new digital menu design in August.

Also, great news is that new AT&T tower has been put up and you can sit anywhere to use the digital menu now.

Please invite your friends to participate by forwarding them: 

http://menu.mit.edu/media/DigitalMenuTrial.png

to help with the Digital Menu study from MIT Media Lab.  Your help would be greatly appreciated.  About 35 more people are needed.  $50 referral award is still valid till end of June.

For those who have participated, please log back on to http://menu.mit.edu/legals/ to rate/review and fill out the surveys.

$50 gift certificates for the surveys will also be raffled after we reach 70%% response rate.

Enjoy the world cup games!

-kwan


    ''' 

    for u in OTNUser.objects.all():
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Digital Menu: iPad or iPhone?", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def new_recruit_june15():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.filter(voucher=True).values_list("my_email", flat=True))
    exclude_list.append("")
    exclude_list += opt_out

    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 

Hi there!

Please enjoy this opportunity to come to Legal Sea Food and dine. 35 more people are needed.  Your participation is extremely helpful for my thesis and
you can help out by participating.

    It's very simple.  Create a PIN at http://menu.mit.edu/legals/

and come to Legals.

After your participation, you will receive $10 Amazon gift certificate for uploading, $30 Amazon gift certificate for linking wesabe.com account and contributing data.  Moreover, if three friends participate after you, you will receive $50 Legal's gift certificate.

If you can't participate please forward this link to your friends to take advantage of this offer to contribute to research and to have a subsidized sea food dinner and more!

    http://menu.mit.edu/media/DigitalMenuTrial.png


$550 Apple gift certificate will be raffled today that one could apply to iPad or iPhone purchase.  But there's still opportunity to receive $200 Apple gift certificate which will be raffled end of June when the trial ends.

Thank you and enjoy the World Cup!

-kwan

--------------------------------------------------------------------
You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. The data collected is only for research purposes and is not shared with Legal's, Facebook or any other thir parties.  Feel free to e-mail or call me at 617-909-2101 with any questions.  Please let me know if you are no longer interested in receiving this e-mail.

    ''' 

    for e in p_emails:
        send_mail("Digital Menu: Two Weeks Remain", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e


def ipad_winner():

    winners = []

    for u in OTNUser.objects.all():
        total_price = 0
        if u.legals_order:
            orders = u.legals_order.order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)
    
            if orders.count() > 2:
                first_order = orders[0]

                friends_fb_ids = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id).friends.exclude(facebook_id=706848).values_list('facebook_id', flat=True)
                referrals = Order.objects.exclude(user=u).filter(timestamp__gt=first_order.timestamp).annotate(num_items=Count('items')).filter(num_items__gt=0).filter(user__facebook_profile__facebook_id__in=friends_fb_ids).values('user').distinct()
     
                for r in referrals:
                    winners.append(u)


                print u.my_email, u.name
                for o in orders:
                    print o.timestamp
                    winners.append(u)
                    for i in o.items.all():
                        total_price += i.item.cost()
                print total_price


    random.shuffle(winners)
    for i in range(1000):
        w = random.sample(winners, 1)
    print "Winner:",w[0].my_email, w[0].name

def ipad_raffled_june16():

    msgs = ''' 
Hi %s, 

iPad has been raffled among the 12 people that participated for three times.  The winner has been notified via e-mail.  For those who did not win, you still qualify for a free meal in August to evaluate a new menu design.

The trial will be ending end of this month with a final raffle of $200 Apple gift certificate with higher chance of winning for those who have more friends who participated.

Please invite your friends to participate by forwarding them: 

http://menu.mit.edu/media/DigitalMenuTrial.png

to help with the Digital Menu study from MIT Media Lab.  Your help would be greatly appreciated.  About 35 more people are needed.  $50 referral award is still valid till end of June.

For those who have participated, please log back on to http://menu.mit.edu/legals/ to rate/review and fill out the short surveys.

$50 gift certificates for the surveys will also be raffled as soon as it reaches 70%% response rate.

Enjoy the world cup games!

-kwan


    ''' 

    for u in OTNUser.objects.all():
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Digital Menu: Final Two Weeks", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def amazon_gift_june16():

    msgs = ''' 
Hi %s, 

Amazon gift certificates are delayed a little bit because I had to order a new batch.  I will add the certificates once they arrive next week.

In the mean time, please log back onto http://menu.mit.edu/legals/ and fill out your gift voucher form by clicking the gift link inside yellow box.

-kwan

    ''' 

    for u in OTNUser.objects.all():
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Digital Menu: Amazon Gift Certificates", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def ipad_final_winner():

    msgs = ''' 
Hi %s, 

You have won the iPad!

Please e-mail me to arrange a time to pick up.

-kwan

    ''' 

    u = OTNUser.objects.get(id=25)

    w = Winner(user=u, prize="iPad")
    w.save()

    first_name = u.name.split(" ")[0]
    print "Sending to: %s"%first_name
    send_mail("Digital Menu: iPad Winner!", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
    print "Sent email to: %s"%u.my_email


opt_out_participant=["nanda20s@mtholyoke.edu", "soonminb@gmail.com", "badjujulien@gmail.com"]
# "sansen@media.mit.edu"

def error_order():

    msgs = ''' 
Hello %s,

If you do not see your order on 6/17 on the menu site: http://menu.mit.edu/legals/ after you login, can you e-mail back?

 Your order was recorded in someone else's account because you did not login to the iPhone menu, instead used it directly as the app was open.

I need to transfer the order to you so that you get the credit.  

For next time, please close the app and reopen to login.  Also please rate/review your meals since that information will be shared with your friends on the menu.

Thank you!

-kwan

-------

Sorry for another e-mail

    ''' 

    for u in OTNUser.objects.all().exclude(my_email__in=opt_out_participant):
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Apologies: Reply only if you visited 6/17 Thurs", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email


def inform_dinner_only_jun21():

    msgs = ''' 
Hello %s,

Just wanted to let you know that the study will conclude in a week or two until 40 more people participate.  

Apologies for those who came for lunch, but the trial is only available for dinner and vouchers are only valid for entrees.

After your meal, please rate/review your dishes and upload your receipts to receive Amazon gift certificates. 

Thank you!

-kwan

-------

Bon Appetit!

    ''' 

    for u in OTNUser.objects.filter(voucher=False).exclude(my_email__in=opt_out_participant):
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("After 5 PM", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def no_lunch_takeout_jun23():

    msgs = ''' 
Dear participants,

     I have been informed that few individuals have been using the vouchers for take-out during lunch.   Unfortunately these vouchers were intended for use during participation in the digital menu trial and regular dining at Legal Sea Foods.  Particularly for the trial, the manager has agreed to accept $10 voucher per person when an entree is ordered at dinner time (although usually only one voucher is valid per table).  The trial only runs for dinner (after 5 PM everyday), so please take this into account when utilizing the vouchers that were given out during the trial.

Also, please accept vouchers only on your first participation so that there may be vouchers remaining for future participants.  

If you have any questions, please e-mail or call me at 617-909-2101.  The waiting staff are not fully informed of the study since I am just utilizing the Kendall location and the restaurant is not really involved in the research.

Thank you for loving sea food and loving technology.

-kwan

-------

Bon Appetit!

    ''' 

    for u in OTNUser.objects.filter(voucher=False).exclude(my_email__in=opt_out_participant):
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("No Take-Out Lunch Please", msgs, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email


vouchers_no_data = ["lobovsky@mit.edu", "lithography@hotmail.com", "qlchen@mit.edu", "pphan@mit.edu", "the_j_mo@yahoo.co.uk"]

def no_orders_jun24():

    msgs = '''
Dear %s,

You are receiving this e-mail because you came to the Legal Sea Food past few days 
to participate in the Digital Menu Trial.  However, no order has been recorded and your 
data has been lost.  It is very important that the data on your order be captured 
through the digital menu for the success of my Ph.D. thesis experiment.  Please let me
know whether you had trouble with the menu.

It would be very helpful if you could visit Legal's for dinner at your convenience 
and use the Digital Menu to capture your order.  Also, it would be great if you would 
not claim new vouchers since I only have very limited number and need to be used for future subjects. 
Every participant is entitled to receive $30 worth of vouchers that you receive on your 
FIRST visit and it can be used $10 at a time during subsequent visits.

It is also important that you not use the paper menu in this process.  
Just call me at 617-909-2101 which is also noted on the table code 
if you have trouble with the menu while you are at the restaurant.

Thank you!!

-kwan
    '''

    for u in OTNUser.objects.filter(my_email__in=vouchers_no_data):
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Digital Menu: No Data Recorded", msgs, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def final_week_jun29():

    msgs = '''
Dear %s,

This is the final week of the trial and the last dinner you may have will be on 7/5 (Monday).  

Here's a quick snapshot of the research you are contributing to:

http://menu.mit.edu/media/participantnet.png

It would be great if those of you who are in sparse network could invite some of your
friends to participate :)

Remember your PIN before going to the restaurant.  
You may update your PIN if you don't remember, by logging onto 

http://menu.mit.edu/legals/ 

and clicking on your name on the upper right corner.

When you are at the restaurant, make sure that you add items to your order 
when you use the menu.  You can always cancel an item after you have added 
to the order so no need to be afraid to add different items.  
Just make sure that only your final choices are visible when you 
click the "My Order" button on the Digital Menu.

Please upload your receipts or link wesabe.com accounts to claim your Amazon
gift certificates.

Thank you!

-kwan
    '''

    for u in OTNUser.objects.exclude(my_email__in=opt_out_participant):
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Digital Menu Quick Update", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email


def final_registration_june29():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.all().values_list("my_email", flat=True))
    exclude_list.append("")
    exclude_list += opt_out
    exclude_list += opt_out_participant

    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 

Tomorrow 6/30 is the last day to REGISTER (at http://menu.mit.edu/legals/) yourself 
to participate in the digital menu trial to get discount vouchers at Legal Sea Foods 
and get Amazon gift certificates for participating.

You may have dinner until 7/5.

Start by creating a PIN at http://menu.mit.edu/legals/
and come have a dinner at Legal's.  


OR if you can't participate please forward this link to your friends to take advantage of this offer to contribute to research and to have a subsidized sea food dinner and more.

    http://menu.mit.edu/media/DigitalMenuTrial.png

Your participation is extremely helpful for my thesis.

Thank you!

-kwan

--------------------------------------------------------------------
You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.  Please let me know if you are no longer interested in receiving this e-mail.

    ''' 

    for e in p_emails:
        send_mail("Digital Menu: 6/30 is last registration day!", msgs, 'Digital Menu Invite <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e


def final_week_jul1():

    msgs = '''
Dear %s,

This is the final week of the trial and the last dinner you may have will be on 7/5 (Monday).  

Remember your PIN before going to the restaurant.  
You may update your PIN if you don't remember, by logging onto 

    http://menu.mit.edu/legals/ 

and clicking on your name on the upper right corner.

And here's a quick update on Wesabe.

Some of you might have signed up for wesabe, to allow me to pull the data through their API for research purposes.  They announced today that they will be shutting down the service on July 31 and purging all data.  Until July 5th though you can still sign up, link/update your accounts and link it to the menu site to get the Amazon gift cards.  It would be great if you could do a final refresh and update with the menu site before the study ends.

The reason I was using wesabe was because their API allows you to enter your wesabe username and password to auto access your transactions without having to tap into your real accounts.  If you do not feel comfortable signing up for it, but would not mind contributing transaction data, you may e-mail the csv files of your transactions that you can download from your online banking/credit card accounts (last three months).  The more data you contribute the more helpful it will be for the research.  I assure that your data will be kept strictly private and personal identifiers removed for analysis.  The data is first used to verify Legal's purchase, and secondly used to investigate clustering algorithms.

Thank you for supporting the study and it would be even more grateful if you could fill out the surveys! :)

-kwan
    '''

    for u in OTNUser.objects.exclude(my_email__in=opt_out_participant):
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Wesabe Update", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email


def restart_aug20():
    boston = BostonZip.objects.all().values("zipcode")

    exclude_list = list(OTNUser.objects.all().values_list("my_email", flat=True))
    exclude_list.append("")
    exclude_list += opt_out
    exclude_list += opt_out_participant

    p_emails = LegalsPopulationSurvey.objects.exclude(email__in=exclude_list).filter(zipcode__in=boston,gluten=False).values_list("email", flat=True).distinct()
    print "Email count:",len(p_emails)

    msgs = ''' 

Hello %s,

The digital menu trial is back and you have a chance to eat discounted meals at Legal's again starting tonight.

Create a PIN or update your PIN at http://menu.mit.edu/legals/

and come for dinner at Legals Kendall Square in Cambridge any day of the week. You just have to spend a few minutes during your ordering time to use the digital menu instead of the regular paper menu.

You will get:

    - $10 off your entree order
    - $20 Amazon gift certificate for rating dish and filling out quick surveys back on the website (http://menu.mit.edu/legals/)

Bonus: If you come in a group of 4, e-mail me beforehand so that your group can get a $50 Legal's gift card for the group instead of the $10 vouchers for each person.

OR if you can't participate please forward this link to your friends to take advantage of this offer to contribute to research and to have a subsidized sea food dinner and more.

    http://menu.mit.edu/media/DigitalMenuTrial.png

Your participation will be extremely helpful for my thesis.

Thank you!

-kwan

--------------------------------------------------------------------
You are receiving this e-mail because you have in the past filled out the Pick-A-Dish survey and you are eligible to participate in the "Digital Menu" trial that I am conducting for my PhD thesis. Feel free to e-mail or call me at 617-909-2101 with any questions.  Please let me know if you are no longer interested in receiving this e-mail.

    ''' 

    for e in p_emails:
        first_name = "friend"
        send_mail("Digital Menu: $10 off your meal", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [e], fail_silently=False) 
        print "Sent email to: %s"%e

    for u in OTNUser.objects.exclude(my_email__in=opt_out_participant):
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Digital Menu: $10 off your meal!", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email

def review_aug23():
    msgs = ''' 

Hello %s,

Please contribute back to the menu by rating and reviewing your dishes you ordered at http://menu.mit.edu/legals/

And of course if you finish filling out the surveys you also get $10 Amazon gift certificate.  

-kwan

    ''' 

    for u in OTNUser.objects.exclude(my_email__in=opt_out_participant):
        first_name = u.name.split(" ")[0]
        print "Sending to: %s"%first_name
        send_mail("Rate/Review - Digital Menu", msgs%first_name, 'Digital Menu <kwan@media.mit.edu>', [u.my_email], fail_silently=False) 
        print "Sent email to: %s"%u.my_email


