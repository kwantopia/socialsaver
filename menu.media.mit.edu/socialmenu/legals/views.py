# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from common.helpers import JSONHttpResponse, JSHttpResponse
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import render_to_response
from common.models import Friends, SharingProfile, Winner, OTNUser
import random, hashlib
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Count
from datetime import datetime, date, timedelta
from legals.models import Order, MenuItemReview, Category, MenuItem, HumanSubjectCompensation, TableCode 
from legals.forms import FeedbackForm, ReceiptUploadForm, HumanSubjectForm, GiftCertificateForm 
from django.views.generic.simple import direct_to_template
from django.views.decorators.cache import cache_control, never_cache
import presurvey
from survey.models import SurveyStatus

logger = settings.LEGALS_LOGGER
GOOGLE_API_KEY = settings.GOOGLE_API_KEY

@login_required()
def index(request, page=1):
    """
        Display the Legals Digital Menu experiment

        Make people see what they have eaten and rate the item
    """

    order_list = [] 
    user = request.user
    fb_profile = user.facebook_profile

    # if my friend list was never created, create one
    my, me_created = Friends.objects.get_or_create(facebook_id = fb_profile.facebook_id)
    if me_created:
        my.image = fb_profile.picture_url
        my.name = fb_profile.full_name
        my.save()

    # if friend list update has been more than two weeks, update friends list
    if me_created or my.last_update < datetime.today()-timedelta(7):
          
        # get Facebook friends
        friendList = request.user.facebook_profile.get_friends_profiles()
        #logger.debug( "Facebook friends of %d: %s"%(fb_profile.facebook_id,str(friendList)) )
        for friend_info in friendList:
            friend, created = Friends.objects.get_or_create(facebook_id = friend_info['uid'])
            if created:
                friend.image = friend_info['pic_square'] 
                friend.name = friend_info['name']
                friend.save()
            my.friends.add(friend)

    # number of friends that have completed the survey
    friend_fb_ids = Friends.objects.get(facebook_id=fb_profile.facebook_id).friends.exclude(facebook_id=706848).values_list('facebook_id', flat=True)
    num_friends = presurvey.models.LegalsPopulationSurvey.objects.exclude(facebook_id=fb_profile.facebook_id).exclude(email="").filter(facebook_id__in=friend_fb_ids).count()

    logger.debug("Number of friends that filled out survey:%d"%num_friends)

    # deprecated
    voucher = user.otnuser.voucher

    # orders I ordered
    orders = Order.objects.filter(user = user).order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)

    # referrals
    refs = 0
    if orders.count() > 0:
        voucher = True
        first_order = orders[orders.count()-1]
        referrals = Order.objects.exclude(user=user).filter(timestamp__gt=first_order.timestamp).annotate(num_items=Count('items')).filter(num_items__gt=0).filter(user__facebook_profile__facebook_id__in=friend_fb_ids).values('user').distinct()
        refs = referrals.count()

    # number of visits left
    visits = 3 - orders.count() if orders.count() < 3 else 0

    # survey completed
    try:
        presurvey_status = presurvey.models.User.objects.get(id=fb_profile.facebook_id)
        survey_completed = presurvey_status.completed
    except presurvey.models.User.DoesNotExist:
        survey_completed = False

    for o in orders[:2]:
        logger.debug(o.get_json())
        for i in o.items.all():
            logger.debug("%s %s %s"%(i.item.name, i.rating, MenuItemReview.REASON_CHOICES[i.reason][1]))

    # get number of wesabe transactions
    wesabe_txns = 0
    for acct in user.otnuser.wesabeaccount_set.all():
        wesabe_txns += acct.wesabetransaction_set.all().count()

    return render_to_response(
            "legals/home.html",
            {
                'fbuser': fb_profile,
                'num_friends': refs, 
                'visits': visits,
                'voucher': voucher,
                'wesabe_txns': wesabe_txns,
                'orders': orders[:2],
                'survey_completed': survey_completed,
                'APP_NAME': settings.APP_NAME,
                'GOOGLE_API_KEY': GOOGLE_API_KEY
            },
            context_instance=RequestContext(request)
        )

@login_required()
def orders(request, page=1):
    """
        Make people see what they have eaten and rate the item
    """

    order_list = [] 
    user = request.user
    fb_profile = user.facebook_profile
    user_friend = Friends.objects.get(facebook_id = fb_profile.facebook_id)
    orders = Order.objects.filter(user = user).order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)

    paginator = Paginator(orders, 3)

    try:
        page = int(page)
    except ValueError:
        page = 1
    
    if page < 1:
        page = 1

    try:
        orders = paginator.page(page)
    except (EmptyPage, InvalidPage):
        orders = paginator.page(paginator.num_pages)

    return render_to_response(
            "legals/orders.html",
            {
                'fbuser': fb_profile,
                'orders': orders.object_list,
                'pages': orders
            },
            context_instance=RequestContext(request)
        )


@never_cache
@login_required
def profile(request):
    """
        GET: Shows profile
        POST: Updates PIN and default transaction sociability

        :param POST['first']: first pin
        :param POST['second']: second time entered pin
        :param POST['wesabe_id']: Wesabe username
        :param POST['sharing']: Defaults to 3: public
        :param POST['wesabe_username']: wesabe username/id
        :param POST['wesabe_password']: wesabe password

        :url: /legals/profile/

    """
    u = request.user
    fb_user = u.facebook_profile
    r = {}

    sharing = SharingProfile.objects.get(user=u)

    if request.method=="POST":
        # change default preferences for sharing
        sharing.general = int(request.POST['sharing'])
        sharing.save()
        
        if request.POST.get('wesabe_username', None):
            u.otnuser.wesabe_id = request.POST['wesabe_username']
            # wesabe data is loaded through jquery

        if len(request.POST['first']) > 0:
            if request.POST['first'] == request.POST['second']:
                # change pin
                u.otnuser.pin = hashlib.sha224(request.POST['first']).hexdigest()
                u.otnuser.save()
                # after POST changing sharing and PIN
                r['prompt'] = 'PIN has been updated'
                r['result'] = 1
            else:
                r['prompt'] = 'PIN does not match, please re-enter'
                r['result'] = -1
            return JSONHttpResponse(r)
    else:
        
        return render_to_response(
            "legals/profile.html",
            {
                'fbuser': fb_user,
                'sharing': sharing.general,
                'wesabe_id': u.otnuser.wesabe_id
            },
            context_instance=RequestContext(request)
        )


def faq(request):
    """
        Returns the faq page

        :url: /legals/faq/
    """
    fb_profile = None
    if request.user.is_authenticated():
        fb_profile = request.user.facebook_profile
    return render_to_response('legals/faq.html', 
            {'fbuser': fb_profile}, context_instance=RequestContext(request))


gift_admin_users = [706848, 1257501802]

@login_required
def gift(request):
    """
        Shows user's gift

        :url: /legals/gift/
    """
    data = {}

    u = request.user
    fb_profile = u.facebook_profile
    data['fbuser'] = fb_profile

    comp, created = HumanSubjectCompensation.objects.get_or_create(user=u)
    if request.method == 'POST':
        form = HumanSubjectForm(request.POST, instance=comp)
        if form.is_valid():
            comp = form.save()
            comp.user = u
            comp.verified = True
            comp.save()
    else:
        if created:
            form = HumanSubjectForm()
        else:
            form = HumanSubjectForm(instance=comp)
            
    data['comp'] = comp
    data['form'] = form

    return render_to_response('legals/gift.html',
            data, context_instance=RequestContext(request)) 

@login_required
def gift_admin(request):
    """
        Shows list of gifts to manage

        :url: /legals/gift/admin/
    """
    data = {}

    u = request.user
    fb_profile = u.facebook_profile
    if fb_profile.facebook_id in gift_admin_users:
        data['authorized'] = True
        reimburse = {}
        #for subject in OTNUser.objects.all().order_by('humansubjectcompensation__verified'):
        for subject in OTNUser.objects.exclude(my_email="kool@mit.edu").order_by('humansubjectcompensation__verified'):
            if subject.legals_order.all().count() < 1:
                continue
            reimburse[subject.my_email] = {'email': subject.my_email}
            reimburse[subject.my_email]['first_name'] = subject.first_name
            reimburse[subject.my_email]['user_id'] = subject.id
            reimburse[subject.my_email]['amount'] = 0
            # compensation information
            comp_info, created = HumanSubjectCompensation.objects.get_or_create(user=subject)
            reimburse[subject.my_email]['comp'] = comp_info

            # initialize variables
            wesabe_linked = False
            wesabe_qualified = False
            legals_verified = False
            w_txns = 0
            reimburse[subject.my_email]['num_txns'] = w_txns

            for w in subject.wesabeaccount_set.all():
                w_txns += w.wesabetransaction_set.all().count()
                wesabe_linked = True 
                for t in w.wesabetransaction_set.all():
                    if t.memo.txt.lower().find('legal') != -1:
                        legals_verified = True

            if w_txns > 30:
                wesabe_qualified = True
                reimburse[subject.my_email]['amount'] = 30
                reimburse[subject.my_email]['num_txns'] = w_txns

            receipt_reimbursed = 0
            reimburse[subject.my_email]['receipts'] = []
            reimburse[subject.my_email]['estimate'] = []
            if subject.legals_order:
                orders = subject.legals_order.order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)
                if orders.count() > 0:
                    last_order_time = datetime.now()
                    for o in orders:
                        # check if order is duplicate
                        t_d = last_order_time-o.timestamp
                        if t_d.days >= 1 or t_d.seconds > 2*60*60:
                            reimburse[subject.my_email]['estimate'].append(o.total_price())
                            try:
                                if o.receipt.url:
                                    receipt_reimbursed += 10
                                    reimburse[subject.my_email]['receipts'].append(o.receipt.url)
                            except:
                                pass
                        last_order_time = o.timestamp

            # check survey numbers filled out
            complete_survey_count = 0
            for s in SurveyStatus.objects.filter( user=subject ):
                if s.completed:
                    complete_survey_count += 1
            reimburse[subject.my_email]['surveys'] = complete_survey_count

            # if legals verified through credit card, but many
            # more receipts uploaded
            if reimburse[subject.my_email]['amount'] < receipt_reimbursed:
                reimburse[subject.my_email]['amount'] = receipt_reimbursed

            if complete_survey_count > 3:
                reimburse[subject.my_email]['amount'] += 10 

        data['reimburse'] = reimburse
    else:
        # not authorized
        data['authorized'] = False


    return render_to_response('legals/gift_admin.html',
            data, context_instance=RequestContext(request)) 


out_list = [24, 256, 335]

@login_required
@never_cache
def guest_list(request, signup):
    """
        For printing guest list 

        :url: /legals/guest/list/(?P<signup>\d{1})/
    """
    data = {}


    u = request.user
    fb_profile = u.facebook_profile
    if fb_profile.facebook_id in gift_admin_users:
        data['authorized'] = True

        data['participants'] = [{'name': u.name, 'email': u.my_email, 'voucher': u.voucher, 'presurvey': presurvey.models.LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id).exists() } for u in OTNUser.objects.exclude(id__in=out_list).order_by("name")]

    else:
        data['authorized'] = False

    if signup == '0':
        return render_to_response('legals/guest_list.html',
                data, context_instance=RequestContext(request)) 
    else:
        return render_to_response('legals/guest_list_signup.html',
                data, context_instance=RequestContext(request)) 
    
@never_cache
def guest_mobile(request, code):
    """
        For printing guest list 

        :url: /legals/guest/(?P<code>\d+)/
    """
    data = {}

    if code == '1044': 
        data['authorized'] = True
        data['tablecodes'] = TableCode.objects.filter(date=date.today()-timedelta(0),first_used=None).count()

        data['participants'] = [{'name': u.name, 'email': u.my_email, 'voucher': u.voucher, 'presurvey': presurvey.models.LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id).exists() } for u in OTNUser.objects.exclude(id__in=out_list).order_by("name")]

        orders = Order.objects.all().order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)

        data["latest"] = [o.get_json() for o in orders[:10]]
    else:
        data['authorized'] = False

    return render_to_response('legals/guest_list_signup.html',
                data, context_instance=RequestContext(request)) 
 
@login_required
def gift_certificate_form(request, subject_id):
    """
        Gift certificate update form

        :url: /legals/gift/certificate/(?P<subject_id>\d+)/
    """
    u = request.user
    fb_profile = u.facebook_profile
    data = {}
    data['result'] = -1

    #subject
    subject = OTNUser.objects.get(id=subject_id)

    # if current user is in admin list
    if fb_profile.facebook_id in gift_admin_users:
        data['authorized'] = True
        comp, created = HumanSubjectCompensation.objects.get_or_create(user=subject)
        if request.method == 'POST':
            form = GiftCertificateForm(request.POST, instance=comp)
            if form.is_valid():
                comp = form.save()
                comp.user = subject 
                comp.save()
                data['result'] = 1
                return JSONHttpResponse(data)
            else:
                data["errors"] = str(form.errors)
                return JSONHttpResponse(data)
        else:
            if created:
                form = GiftCertificateForm()
            else:
                form = GiftCertificateForm(instance=comp)
                
        data['comp'] = comp
        data['form'] = form
        data['subject_id'] = subject_id
    else:
        data['authorized'] = False

    return render_to_response('legals/gift_certificate_form.html',
            data, context_instance=RequestContext(request))

@login_required
def gift_update(request):
    """
        AJAX POST: Update gift certificates for particular user

        :url: /legals/gift/update/

        :param POST['user_id']: the user ID
        :param POST['verify']: verification check mark
        :param POST['certificates']: gift certificates
    """
    data = {}
    fb_profile = u.facebook_profile
    if fb_profile.facebook_id in gift_admin_users:
        data['authorized'] = True

        if 'user_id' not in request.POST:
            data['result'] = '-1'
        else:
            u = OTNUser.objects.get(id=request.POST['user_id']) 
            compensation, created = HumanSubjectCompensation.objects.get_or_create(user=u)
            if 'verify' in request.POST:
                compensation.verified = True
                compensation.save()
            if 'certificates' in request.POST:
                compensation.certificates = request.POST['certificates'] 
                compensation.save()
            data['result'] = '1'
    else:
        data['authorized'] = False

    return JSONHttpResponse(data)

@login_required
def download(request):

    return render_to_response('legals/download.html')

@login_required
def order(request):
    """
        Return the order

        :param GET['order_id']: the order ID

        :rtype: JSON
        ::

            # if it's not your order
            {'result':'-1'}

            # if it's your order
            {'result': }

    """
    r = {}
    u = request.user
    orders = Order.objects.filter(id=request.GET['order_id'], user=u)
    if orders.count() > 0:
        # you can view this order
        r['result'] =  orders[0].get_json()
    else:
        r['result'] = '-1'

    return JSONHttpResponse(r)

@login_required
def update_comment(request):
    """
        :url: /legals/update/comment/
        
        :param POST['review_id']: the review ID of the menu item 
        :param POST['comment']: the comment that the user added


        :rtype: JSON
        ::

            # if successful
            {'result': '1'}
            # else if user is not authenticated
            {'result': '0'}
    """
    r = {'result':'Please add comment...'} 

    if request.user.is_authenticated() and request.method == "POST":

        # get the transaction and description
        review_id = request.POST['review_id'].split('_')[1]
        comment = request.POST['comment']

        # see if the transaction belongs to the user.
        review = MenuItemReview.objects.get(id = int(review_id))
        review.comment = comment 
        review.save()
        r = {'result':review.comment}

    return HttpResponse(r['result'])


@login_required
def update_rating(request):
    """
    
        :url: /legals/update/rating/
        
        :param POST['review_id']: the review ID of the menu item 
        :param POST['rating']: the rating that the user added

        :rtype: JSON
        ::

            # if successful
            {'result': '1'}
            # else if user is not authenticated
            {'result': '0'}
    """
    r = {'result':'Not Rated'} 

    if request.user.is_authenticated() and request.method == "POST":

        # get the transaction and description
        review_id = request.POST['review_id']
        rating = request.POST['rating']

        # see if the transaction belongs to the user.
        review = MenuItemReview.objects.get(id = int(review_id))
        review.rating = int(rating) 
        review.save()
        r['result'] = MenuItemReview.RATING_CHOICES[review.rating][1] 
        
    return JSONHttpResponse(r)

@login_required
def update_reason(request):
    """
    
        :url: /legals/update/reason/
        
        :param POST['review_id']: the review ID of the menu item 
        :param POST['reason']: the reason that the user ordered 

        :rtype: JSON
        ::

            # if successful
            {'result': '1'}
            # else if user is not authenticated
            {'result': '0'}
    """
    r = {'result':'Not Rated'} 

    if request.method == "POST":

        # get the transaction and description
        review_id = request.POST['review_id']
        reason = request.POST['reason']

        # see if the transaction belongs to the user.
        review = MenuItemReview.objects.get(id = int(review_id))
        review.reason = int(reason) 
        review.save()
        r['result'] = MenuItemReview.REASON_CHOICES[review.reason][1] 
        
    return JSONHttpResponse(r)

@login_required
def feedback_post(request):
    """
        :url: /legals/feedback/post/

        :param POST['speed']: speed of menu browsing 
        :param POST['size']: size of menu browsing 
        :param POST['comment']: any further comments

        :rtype: JSON
        ::

            # if successful returns the ID of the newly posted Feedback 
            {'result': '7'}

            # else
            {'result': '-1'}

    """
    r = {}
    u = request.user
    fbuser = u.facebook_profile
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = u
            instance.save()
            logger.debug("Saved feedback %d: %s"%(instance.id, request.POST.get('comment',None)))

            r['result'] = str(instance.id)
        else:
            r['result'] = '-1'
        return JSONHttpResponse(r)
    else:
        form = FeedbackForm()
        return direct_to_template( request, 'legals/feedback_form.html',
                                        extra_context={'fbuser': u.facebook_profile, 'form':form})

@login_required
def receipt_upload(request):
    """
        :url: /legals/receipt/upload/

        :param POST['order_id']: the order ID adding the receipt to
        :param FILES['receipt']: the receipt image file

        :rtype: JSON
        ::

            # order id that was modified
            {'result': '5'}

            # if GET request, it's not supported
            {'result': '-1'}
    """
    u = request.user
    r = {}

    logger.debug( "POST: %s"%str(request.POST))
    logger.debug("FILES:%s"%str(request.FILES))
    if request.method == 'POST':
        o = Order.objects.get(id=request.POST['order_id'])
        form = ReceiptUploadForm(files=request.FILES, instance=o)
        if form.is_valid():
            o = form.save()
            r['result'] = {'id':str(o.id), 
                            'url': o.receipt.url,
                            'thumb_url':o.receipt.thumbnail.absolute_url }
        else:
            r['result'] = {'errors':form.errors, 'result':'-2'}
    else:
        r['result'] = '-1'
    return JSHttpResponse(r)

def upload_page(request):

    return render_to_response("legals/test_receipt_upload.html")

def upload_complete(request):
    r = {}

    r['filesUploaded'] = request.POST['filesUploaded']
    r['errors'] = request.POST['errors']
    r['allBytesLoaded'] = request.POST['allBytesLoaded']
    r['speed'] = request.POST['speed']
    return JSONHttpResponse(r)

def winners(request):
    """
        Shows list of winners each day

        :url: /legals/winners/
    """

    data = {}
    data['winners'] = Winner.objects.all().order_by('-timestamp')
    if request.user.is_anonymous():
        fb_profile = None
    else:
        fb_profile = request.user.facebook_profile
    data['fbuser'] = fb_profile

    return render_to_response("legals/winners.html", data,
            context_instance=RequestContext(request))

def migrate_table_codes(request):
    """
        Migrates previously unused table codes to be used
        today

        :url: /legals/tablecodes/migrate/
    """
    r = {}
    
    if request.method=='POST':
        if request.POST.get("code", "000") == "sOc1AlM1gRa2":
            logger.debug("Yesterday's Unused Table Codes")
            for tcs in TableCode.objects.exclude(code="abcd").filter(date=date.today()-timedelta(1), first_used=None):
                logger.debug(tcs.code)
                tcs.date=date.today()
                tcs.save()
            logger.debug("Table Codes Valid for Today:")
            for tcs in TableCode.objects.filter(date=date.today(), first_used=None):
                logger.debug(tcs.code)
            r["result"] = "1"
            return JSONHttpResponse(r)
        else:
            logger.debug("Trying to migrate table code with invalid access code")
        r["result"] = "-2"
        return JSONHttpResponse(r)
    else:
        logger.debug("Trying to migrate table code using GET")
        r["result"] = "-1"
        return JSONHttpResponse(r)

from presurvey.forms import LegalsPopulationSurveyForm

@login_required
def legals_presurvey(request):
    """
        Presurvey inside the site

        :url: /legals/presurvey/
    """

    u = request.user
    fb_profile = u.facebook_profile
    pre_user, created = presurvey.models.User.objects.get_or_create(id=fb_profile.facebook_id)

    friends = fb_profile.get_app_friends_profiles()
    logger.debug(friends)

    sample_friends = []

    if len(friends)>0:
        if len(friends)>10:
            sample_friends = random.sample(friends,10)

    # Complete is the name of Submit button in the form
    if "Complete" in request.POST:
        # process submission of form
        form = LegalsPopulationSurveyForm(request.POST, request.FILES) 
        if form.is_valid():
            # save the form
            form.save()
            logger.debug("Saved survey")
            # assign user the facebook ID
            #instance = request.user.get_profile().facebook_id

            # Create Friends entry to our DB
            my, created = Friends.objects.get_or_create(facebook_id=fb_profile.facebook_id)
            if created:
                my.image=fb_profile.picture_url
                my.name=fb_profile.full_name
                my.save()

            pre_user.completed = True
            pre_user.save()

            logger.debug("Survey completed for %s"%fb_profile.facebook_id)

            return direct_to_template(request, 'legals/invite_friends.html',
                    extra_context={'fbuser':pre_user, 
                                'appname': settings.APP_NAME})
        else:
            # there was an error in the form 
            logger.debug("Redisplay the form due to error %s"%form.errors)

            form = LegalsPopulationSurveyForm(request.POST)
            # Get Legals menu
            categories = Category.objects.all().order_by('name')
            menu = []
            for c in categories:
                menu.append({'category':c.name, 'dishes':[m.get_json() for m in c.menuitem_set.all()]})

            return direct_to_template(request, 'legals/legalspopulation.html', 
                            extra_context={'fbuser': pre_user, 
                                            'friends': sample_friends,
                                            'menu': menu, 
                                            'form': form, 
                                            'errors':form.errors,
                                            'appname':settings.APP_NAME})

    else:
        # present the survey form
        #logger.debug("Displaying initial survey form %s"%request.POST.get('fb_sig_friends'))
        pre_user.first_name = fb_profile.first_name
        pre_user.last_name = fb_profile.last_name
        pre_user.started = datetime.now()
        pre_user.save()

        form = LegalsPopulationSurveyForm()
        #logger.debug("Displaying initial survey form: %s"%str(form))
        logger.debug("Displaying initial survey form")

        # Get Legals menu
        categories = Category.objects.all().order_by('name')
        menu = [] 
        for c in categories:
            menu.append({'category':c.name, 'dishes':[m.get_json() for m in c.menuitem_set.filter(active=True)]})


        return direct_to_template(request, 'legals/legalspopulation.html', 
                extra_context={'fbuser': pre_user, 
                                'friends': sample_friends,
                                'menu': menu, 
                                'form':form, 
                                'appname':settings.APP_NAME})

