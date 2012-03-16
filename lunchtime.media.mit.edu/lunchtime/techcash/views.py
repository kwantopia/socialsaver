# Create your views here.
import urllib, httplib
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from common.helpers import JSONHttpResponse
from tagging.views import tagged_object_list
from common.models import Location, OTNUser
from models import * 
from django.conf import settings
from iphonepush.models import iPhone, sendMessageToPhoneGroup
import datetime
from django.views.decorators.csrf import csrf_exempt

logger = settings.TECHCASH_LOGGER

def index(request):
    """
        List the transactions
    """
    #datetime.timestamp(unixtime from techcash)
    return

@csrf_exempt
def latest_txns(request):
    """
        Uploads transactions from the TechCash database, called from cron job

        :url: /techcash/latest/

        :param POST['txns']: the transactions
        :param POST['load']: '1' for preloading transaction so alerting the phone is avoided
    """

    if request.method == 'POST':
        txns = json.loads(request.POST['txns'])
        for balance in txns['balances']:
            try:
                u = OTNUser.objects.get(mit_id=balance['CURRENTPRIMARYKEY'])
            except OTNUser.DoesNotExist:
                continue
            if u is not None:
                # existing user
                if request.POST.get('load','0')=='1':
                    u.approved=1
                    u.save()
                bal, created = TechCashBalance.objects.get_or_create(user=u)
                bal.balance = balance['BALVALUEAFTERTRAN'] 
                bal.save()
        for txn in txns['transactions']:
            try:
                u = OTNUser.objects.get(mit_id=txn['CURRENTPRIMARYKEY'])
            except OTNUser.DoesNotExist:
                continue
            t, created = TechCashTransaction.objects.get_or_create(user=u, trans_id=int(txn['TRANSID']))
            if created:
                # create an empty receipt object
                r = Receipt(txn=t)
                r.save()
                # create a location object
                b, created = Location.objects.get_or_create(name=txn['LOCATION'])
                t.user=u
                t.timestamp=datetime.datetime.fromtimestamp(int(txn['UNIX_TRANDATE']))
                t.day = t.timestamp.weekday()
                t.time = t.timestamp.time()
                t.amount=txn['APPRVALUEOFTRAN']
                t.location=b
                t.save()
                if 'load' not in request.POST:
                    # alert user about new transaction
                    try:
                        phone = iPhone.objects.get( user = u )
                        phone.send_message("%s: $%.2f. Please share your experience."%(txn['LOCATION'], float(txn['APPRVALUEOFTRAN'])), sound="default", custom_params={'msg_type':'receipt', 'receipt_id': r.id})
                    except iPhone.DoesNotExist:
                        logger.warning("User %s has not registered their iPhone"%u.username)
            else:
                logger.info('Transaction already exists: %s'%str(txn))
    return JSONHttpResponse({'result':'1'})


def old_latest_txns(request):
    """
        Uploads transactions from the TechCash database, called from cron job

        :url: /techcash/latest/

        :param POST['txns']: the transactions
        :param POST['load']: '1' for preloading transaction so alerting the phone is avoided
    """
    if request.method == 'POST':
        txns = json.loads(request.POST['txns'])
        for k,v in txns['balances'].items():
            try:
                u = OTNUser.objects.get(mit_id=k)
            except OTNUser.DoesNotExist:
                continue
            if u is not None:
                # existing user
                bal, created = TechCashBalance.objects.get_or_create(user=u)
                bal.balance = v 
                bal.save()
        for txn in txns['transactions']:
            try:
                u = OTNUser.objects.get(mit_id=txn['CURRENTPRIMARYKEY'])
            except OTNUser.DoesNotExist:
                continue
            t, created = TechCashTransaction.objects.get_or_create(user=u, trans_id=int(txn['TRANSID']))
            if created:
                # create an empty receipt object
                r = Receipt(txn=t)
                r.save()
                # create a location object
                b, created = Location.objects.get_or_create(name=txn['LOCATION'])
                t.user=u
                t.timestamp=datetime.datetime.fromtimestamp(int(txn['UNIX_TRANDATE']))
                t.day = t.timestamp.weekday()
                t.time = t.timestamp.time()
                t.amount=txn['APPRVALUEOFTRAN']
                t.location=b
                t.save()
                if 'load' not in request.POST:
                    # alert user about new transaction
                    try:
                        phone = iPhone.objects.get( user = u )
                        phone.send_message("%s: $%.2f. Please share your experience."%(txn['LOCATION'], float(txn['APPRVALUEOFTRAN'])), sound="default", custom_params={'msg_type':'receipt', 'receipt_id': r.id})
                    except iPhone.DoesNotExist:
                        logger.warning("User %s has not registered their iPhone"%u.username)
            else:
                logger.info('Transaction already exists: %s'%str(txn))
    return JSONHttpResponse({'result':'1'})

def initialize_txns(request):
    """
        Uploads past historical transactions from the TechCash database
        Called from the web

        :url: /techcash/initialize/
        
        :rtype: JSON
        ::
            
            # already initialized
            {'result': '0'}
            # if successfully initialized
            {'result': '1'}

    """

    otnuser = request.user.get_profile() 
    mit_id = otnuser.mit_id
    try:
        bal = TechCashBalance.objects.get(user=otnuser)
        if bal.initialized:
            # already initialized
            return JSONHttpResponse({'result':'0'})
        else:
            # you should load up the transaction
            pass
    except TechCashBalance.DoesNotExist:
        # you should load up the transaction
        pass

    # poll for initial data
    h = httplib.HTTPSConnection('mobi2.mit.edu', key_file=settings.TECHCASH_KEY, cert_file=settings.TECHCASH_CERT)
    h.request('GET', '/~kool/techcash/loadUser.php?id=1&mit=%s'%mit_id)
    r = h.getresponse()
    data = r.read()
    h.close()
    
    txns = json.loads(data)
    for k,v in txns['balances'].items():
        try:
            u = OTNUser.objects.get(mit_id=k)
        except OTNUser.DoesNotExist:
            continue
        if u is not None:
            # existing user
            bal, created = TechCashBalance.objects.get_or_create(user=u)
            bal.balance = v 
            # very first initialization
            bal.initialized = True
            bal.save()
    for txn in txns['transactions']:
        try:
            u = OTNUser.objects.get(mit_id=txn['CURRENTPRIMARYKEY'])
        except OTNUser.DoesNotExist:
            continue
        t, created = TechCashTransaction.objects.get_or_create(user=u, trans_id=int(txn['TRANSID']))
        if created:
            # create an empty receipt object
            r = Receipt(txn=t)
            r.save()
            # create a location object
            b, created = Location.objects.get_or_create(name=txn['LOCATION'])
            t.user=u
            t.timestamp=datetime.datetime.fromtimestamp(int(txn['UNIX_TRANDATE']))

            t.day = t.timestamp.weekday()
            t.time = t.timestamp.time()
            t.amount=txn['APPRVALUEOFTRAN']
            t.location=b
            t.save()
        else:
            logger.debug('Transaction already exists: %s'%str(txn))
    return JSONHttpResponse({'result':'1'})

def update_txns(request):
    """
        Get latest transactions, called from the web

        :url: /techcash/update/
        
        :rtype: JSON
        ::
            
            # already initialized
            {'result': '0'}
            # if successfully initialized
            {'result': '1'}

    """

    otnuser = request.user.get_profile() 
    mit_id = otnuser.mit_id
    try:
        bal = TechCashBalance.objects.get(user=otnuser)
        if not bal.initialized:
            # Need to load up the transactions first
            return JSONHttpResponse({'result':'0'})
    except TechCashBalance.DoesNotExist:
        # you should load up the transaction
        return JSONHttpResponse({'result':'0'})

    # poll for latest data
    h = httplib.HTTPSConnection('mobi2.mit.edu', key_file=settings.TECHCASH_KEY, cert_file=settings.TECHCASH_CERT)
    h.request('GET', '/~kool/techcash/poll.php?id=1')
    r = h.getresponse()
    data = r.read()
    h.close()
    
    txns = json.loads(data)
    for k,v in txns['balances'].items():
        try:
            u = OTNUser.objects.get(mit_id=k)
        except OTNUser.DoesNotExist:
            continue
        if u is not None:
            # existing user
            bal, created = TechCashBalance.objects.get_or_create(user=u)
            bal.balance = v 
            # very first initialization
            bal.initialized = True
            bal.save()
    for txn in txns['transactions']:
        try:
            u = OTNUser.objects.get(mit_id=txn['CURRENTPRIMARYKEY'])
        except OTNUser.DoesNotExist:
            continue
        t, created = TechCashTransaction.objects.get_or_create(user=u, trans_id=int(txn['TRANSID']))
        if created:
            # create an empty receipt object
            r = Receipt(txn=t)
            r.save()
            # create a location object
            b, created = Location.objects.get_or_create(name=txn['LOCATION'])
            t.user=u
            t.timestamp=datetime.datetime.fromtimestamp(int(txn['UNIX_TRANDATE']))

            t.day = t.timestamp.weekday()
            t.time = t.timestamp.time()
            t.amount=txn['APPRVALUEOFTRAN']
            t.location=b
            t.save()
        else:
            logger.debug('Transaction already exists: %s'%str(txn))
    return JSONHttpResponse({'result':'1'})

def initialize_iphone(request):
    """
        Initializes some data that is needed in the database

        :url: /techcash/initialize/iphone/

    """
    # create the user
    u = OTNUser.objects.get(mit_id='926634034')
    # create an iPhone for the user
    p, created = iPhone.objects.get_or_create(user=u.user,udid='bd868ce1ba22bb1ed1015bcebe6b63c18568e1f6ca4e0c0dc5f0f1e8ee99443d')
            
    if created:
        return HttpResponse('iPhone DB initalized with my ID')
    else:
        return HttpResponse('iPhone DB already initialized')

@csrf_exempt
def lunch_alert(request):
    """
        Triggered near lunch time
        :url: /techcash/lunch/alert/

        :param POST['code']: the code that needs to match to send notifications

        :rtype: JSON

        ::

            # successful alert
            {'result':'k'} where k is the number of phones
            # no passcode
            {'result':'-1'}
            # wrong passcode
            {'result':'-2'}
    """

    if request.POST.get('code', None) is None:
        return JSONHttpResponse({'result': '-1'})
    elif request.POST['code']=='sendpeople2lunch':
        logger.debug("calculating lunchtime")
        day_num = datetime.datetime.today().weekday()
        for u in OTNUser.objects.all():
            # need to find a way to estimate lunch time of individual
            # students
            latest = TechCashTransaction.objects.filter(user=u, day=day_num, time__lt=datetime.time(15,0), time__gt=datetime.time(10,0))[:7]
            
            # calculate average
            k = latest.count()
            if k > 0:
                sum = 0
                for l in latest:
                    sum += l.time.hour*60
                    sum += l.time.minute
                avg = sum/k
                # logging changes
                lunch_time = LunchTimeLog(user=u, day_of_week=day_num, avg_time=datetime.time(avg/60, avg%60))
                lunch_time.save()
                # logging to use
                lunch_time, created = LunchTime.objects.get_or_create(user=u, day_of_week=day_num)
                lunch_time.avg_time=datetime.time(avg/60, avg%60)
                lunch_time.save()
                logger.debug("Lunch Time for %s: %s"%(u.name, str(lunch_time.avg_time)))
            else:
                # logging changes
                lunch_time = LunchTimeLog(user=u, day_of_week=day_num, avg_time=datetime.time(12))
                lunch_time.save()
                # logging to use
                lunch_time, created = LunchTime.objects.get_or_create(user=u, day_of_week=day_num)
                lunch_time.avg_time=datetime.time(12)
                lunch_time.save()
                logger.debug("Lunch Time for %s: %s"%(u.name, str(lunch_time.avg_time)))


        lunch_times = LunchTime.objects.filter(day_of_week=day_num,avg_time__gt=datetime.datetime.today().time(), avg_time__lt=(datetime.datetime.today()+datetime.timedelta(minutes=60)).time())
        phones = []
        for l in lunch_times:
            try:
                phone = iPhone.objects.get( user = l.user )
                phones.append(phone)
            except iPhone.DoesNotExist:
                pass
        if len(phones)>0:
            sendMessageToPhoneGroup(phones, "Where do you want to go today?", sound="default", custom_params={'msg_type':'lunch'}, sandbox=False)

        return JSONHttpResponse({'result':str(len(phones))})
    else:
        return JSONHttpResponse({'result':'-2'})

def test_receipt_alert(request, mit_id):
    """
        Triggered receipt 
        :url: /techcash/test/receipt/alert/(?P<mit_id>\d+)/

        :rtype: JSON

        ::

            {'result':'1'}
    """
    # TODO: need to find a way to estimate lunch time of individual
    # students
    otnuser = OTNUser.objects.get(mit_id = mit_id)
    phone = iPhone.objects.get( user__otnuser = otnuser )
    latest_txn = TechCashTransaction.objects.filter(user = otnuser).latest()
    phone.send_message("Anna's Taqueria: $8.75",
            custom_params={'msg_type':'receipt', 'receipt_id': latest_txn.receipt.id })
    return JSONHttpResponse({'result':str(latest_txn.receipt.id)})

@csrf_exempt
def bought(request):
    """
        Checks if something has been purchased through TechCash
        and alerts those phones of MIT ID users

        :url: /techcash/bought/

        :param POST['txns']: the json transactions from TechCash server
        ::

            [
                {"mit_id":"924523420", "current_balance": "$36.02",
                    'transactions': [{'UNIX_TRANDATE':1255070307,
                                        'APPRVALUEOFTRAN':"-3.92",
                                        'LOCATION':"Laverde's Market",
                                    },
                                    ]
                }
            ]

        :rtype: JSON
        ::

            #: success
            {'result': 1}
            #: fail
            {'result': -1} 
            
    """
     
    return

def txns(request):
    """
        Show list of recent transactions
    """
    return

def add_tag(request):
    """
        Add tag to a transaction
    """
    return

def rate(request):
    """
        Rate a purchase
    """
    return

def comment(request):
    """
        Used for adding detail about a transaction
    """
    return
