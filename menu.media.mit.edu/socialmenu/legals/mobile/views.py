# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from legals.models import Category, MenuItem, Store, Order, MenuItemReview, TableCode, ChefChoice, Experiment
from legals.models import EventAccess, Event, EventBasic, EventCategory, EventMenuItem, EventSpecial
from common.helpers import JSONHttpResponse
from common.models import OTNUser, Friends
import hashlib
from iphonepush.models import iPhone, sendMessageToPhoneGroup
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache

from django.contrib.auth.models import User
from django.conf import settings
from datetime import date
import random, json

logger = settings.LEGALS_LOGGER

def index(request, lat, lon, udid):
    """
        The start page of the application.  Show login form.

        :param lat: latitude obtained from phone
        :param lon: longitude
        :param udid: 64 character push notification device id

        :url: /legals/m/login/(?P<lat>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)/(?P<lon>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)/(?P<udid>\d{64})/

    """
    header = "legals"
    restaurant = Store.objects.get(id=1)

    # show e-mail of this phone, if previously logged in
    email = None 
    try:
        phone = iPhone.objects.filter(udid=udid)
        if phone.count() > 0:
            email = phone[0].user.otnuser.my_email
    except iPhone.DoesNotExist:
        pass

    # log any accesses that are made
    e = EventAccess(udid=udid, latitude=lat, longitude=lon)
    e.save()

    return render_to_response( "legals/i/login.html",
                {
                    'header': header,
                    'restaurant': restaurant,
                    'lat': lat,
                    'lon': lon,
                    'udid': udid,
                    'email': email,
                },
                context_instance=RequestContext(request))

def login_mobile(request):
    """
        POST method that is used to login

        :url: /legals/m/login/

        :param POST['lat']: latitude
        :param POST['lon']: longitude 
        :param POST['udid']: udid
        :param POST['email']: email address
        :param POST['pin']: pin number
        :param POST['table']: table code
    """

    # needed to load header icon 
    header = "legals"
    restaurant = Store.objects.get(id=1)

    if request.method == "POST":
        email = request.POST['email']
        pin = hashlib.sha224(request.POST['pin']).hexdigest()
        user = authenticate(email=email, pin=pin)
        lat = float(request.POST.get('lat',"0.0"))
        lon = float(request.POST.get('lon',"0.0"))
    
        if user is not None:
            # valid user
            login(request, user)
            logger.debug( "User %s authenticated and logged in with table code: %s "%(email, request.POST['table']) )

            # check table code
            table = TableCode.objects.check_code(request.POST['table'])
            if table is None:
                # if table code is not usable
                logger.debug( "Table code is not valid: %s"%request.POST['table'] )
                event = EventBasic(user=user, 
                                experiment=user.experiment,
                                action=EventBasic.LOGIN_OUTSIDE, 
                                latitude=lat,
                                longitude=lon,
                                comment="Invalid table code: %s"%request.POST.get('table','no table code entered'))
                event.save()
                #just display plain menu
                #return HttpResponseRedirect("/legals/m/categories/0/")
                return render_to_response( "legals/i/login.html",
                    {
                        'header': header,
                        'error': 'Table Code is Invalid',
                        'restaurant': restaurant,
                        'lat': lat,
                        'lon': lon,
                        'email': email,
                        'pin': request.POST.get("pin",""),
                    },
                    context_instance=RequestContext(request))

            ################################
            # You are logged in successfully
            ################################
            logger.debug( "Using table code %s"%table.code )
            # Create an Order
            order = Order(user=user, table=table)
            order.save()
            event = EventBasic(user=user, 
                            order=order,
                            experiment=table.experiment,
                            table_code=table,
                            action=EventBasic.LOGIN_VALID, 
                            latitude=lat,
                            longitude=lon)
            event.save()
            # register iphone
            if 'udid' in request.POST:
                p, created = iPhone.objects.get_or_create(user=user)
                p.udid = request.POST['udid']
                p.save()
 
            return HttpResponseRedirect("/legals/m/categories/%d/"%order.id)
        else:
            # not a valid user
            event = EventAccess(udid=request.POST['udid'], 
                            bad=True, 
                            latitude=lat,
                            longitude=lon)
            event.save()
            return render_to_response( "legals/i/login.html",
                {
                    'header': header,
                    'error': 'Email or PIN did not validate',
                    'restaurant': restaurant,
                    'lat': lat,
                    'lon': lon,
                    'email': email,
                    'tablecode': request.POST.get('table', "")
                },
                context_instance=RequestContext(request))
    else:
        # not a valid URL
        return render_to_response("legals/i/login.html",
                {
                    'header': header,
                    'error': 'Invalid URL',
                    'restaurant': restaurant,
                    'lat': '',
                    'lon': '',
                    'email': email,
                    'pin': request.POST.get("pin", ""),
                    'tablecode': request.POST.get('table', ""),
                },
                context_instance=RequestContext(request))

@login_required
def categories(request, order_id):
    """
        Display the top level categories

        :url: /legals/m/categories/(?P<order_id>\d+)/$
    """

    if int(order_id) == 0:
        exp_id = 1
    else:
        ord = Order.objects.get(id=order_id)
        exp_id = ord.table.experiment.id 

    header = "legals"
    restaurant = Store.objects.get(id=1)
    categories = list(Category.objects.exclude(name="Features").order_by("name"))

    return render_to_response( "legals/i/categories.html",
        {
            'header': header,
            'restaurant': restaurant,
            'categories': categories,
            'order_id': int(order_id)
        },
        context_instance=RequestContext(request))


def allergies(request, order_id):
    """
        Display allergy information
       
        :url: /legals/m/allergies/{{ order_id }}/
    """
    header = "legals"
    restaurant = Store.objects.get(id=1)

    if int(order_id) == 0:
        exp_id = 1
        event=EventSpecial(user=request.user,
                    experiment=Experiment.objects.get(id=exp_id),
                    category=EventSpecial.ALLERGIES)  
    else:
        ord = Order.objects.get(id=order_id)

        event=EventSpecial(user=request.user,
                    order=ord,
                    experiment=ord.table.experiment,
                    category=EventSpecial.ALLERGIES)  
    event.save()

    return render_to_response( "legals/i/allergies.html",
        {
            'header': header,
            'restaurant': restaurant,
            'order_id': int(order_id)
        },
        context_instance=RequestContext(request))


@login_required
def view_category(request, cat_id, order_id):
    """
        Display the items in the category
        
        :url: /legals/m/category/(?P<cat_id>\d+)/(?P<order_id>\d+)/
    """

    u = request.user

    menu_data = [] 
    header = "legals"
    restaurant = Store.objects.get(id=1)

    if int(order_id) == 0:
        ord = None
        exp_id = 1
    else:
        ord = Order.objects.get(id=order_id)
        exp_id = ord.table.experiment.id 

    category = Category.objects.get(id=cat_id)

    # log category access
    event=EventCategory(user=u,order=ord,
            experiment=Experiment.objects.get(id=exp_id),
            category=category)
    event.save()

    #: i_data stores the label information for each item, indexed by item ID
    i_data = {}

    # build menu items for this category
    # with who else liked it
    items = category.menuitem_set.filter(active=True)
    for i in items:
        #: contains item and other social metadata
        i_data[i.id] = {'item':i.get_json()}
        if exp_id == 3:
            numordered = i.menuitemreview_set.all().exclude(legals_ordered__user=u).count()
            numwanted = i.pre_favorite_dishes.all().count()
            if numordered == 0:
                i_data[i.id]['anonymous'] = ''
            elif numordered == 1: 
                i_data[i.id]['anonymous'] = '1 ordered'
            else:
                i_data[i.id]['anonymous'] = '%d ordered'%numordered
            if numwanted == 1:
                if len(i_data[i.id]['anonymous']) > 0:
                    i_data[i.id]['anonymous'] += ', 1 wants this'
                else:
                    i_data[i.id]['anonymous'] += '1 wants this'
            elif numwanted > 1:
                if len(i_data[i.id]['anonymous']) > 0:
                    i_data[i.id]['anonymous'] += ', %d want this'%numwanted
                else:
                    i_data[i.id]['anonymous'] += '%d want this'%numwanted

        elif exp_id in [2,4,5]:
            i_data[i.id]['friends'] = set() 
            i_data[i.id]['wanted'] = set()
            i_data[i.id]['all'] = set()
        

    if exp_id in [2,4,5]:
        # find numfriends ordered and num friends wanting

        # get all friends of user
        fb_id = u.facebook_profile.facebook_id
        friends = Friends.objects.get(facebook_id=fb_id).friends.values_list('facebook_id', flat=True)
        
        # get those items that friends have ordered for exp 2,3,4,5
        orders = Order.objects.filter(user__facebook_profile__facebook_id__in=friends)
        for o in orders:
            if o.num_items() > 0:
                for r in o.items.all():
                    # 2: friends
                    # 4: friends and popularity mixed
                    # 5: intervention
                    if r.item.id in i_data:
                        # friends that ordered the item
                        i_data[r.item.id]['friends'].add(o.user.first_name)
                        i_data[r.item.id]['all'].add(o.user.first_name)
                        # find friends who want this
                        want_fb_ids = r.item.pre_favorite_dishes.filter(facebook_id__in=friends).values('facebook_id')
                        for u in Friends.objects.filter(facebook_id__in=want_fb_ids):
                            if u.name:
                                i_data[r.item.id]['wanted'].add(u.name.split()[0])
                                i_data[r.item.id]['all'].add(u.name.split()[0])
    
        for key,val in i_data.items(): 
            # arrange labels
            numall = len(val['all'])
            numfriends = len(val['friends'])
            numwanted = len(val['wanted'])
            label = ''

            if exp_id in [2,5]:
                i = 0
                for f in val['all']: 
                    i += 1 
                    if i == 3 and numall > 3:
                        label += f + ', ...'
                        # if there are more than three people, just show
                        # that there are more
                        break
                    elif i == numall:
                        label += f 
                    else:
                        label += f + ', '
            else:
                # just put counts
                if numfriends > 0:
                    label += "%d friend(s) ordered"%numfriends
                    if numwanted > 0:
                        label += ", %d friend(s) want this"%numwanted
                else:
                    if numwanted > 0:
                        label += "%d friend(s) want this"%numwanted

            i_data[key]['friend_label']=label 

    return render_to_response( "legals/i/category.html",
            {
            'header': header,
            'restaurant': restaurant,
            'category': category,
            'menu_data': i_data,
            'exp_id': int(exp_id),
            'friend_experiment':[2,4,5],
            'order_id': int(order_id)
            },
            context_instance=RequestContext(request))

@login_required
def view_chefs_choices(request, order_id):
    """
        Display the Chef's choices

        :url: /legals/m/chef/choices/(?P<order_id>\d+)/
    """
    menu_data = [] 
    header = "legals"
    restaurant = Store.objects.get(id=1)

    if int(order_id) == 0:
        exp_id = 1
        event=EventSpecial(user=request.user,
                    experiment=Experiment.objects.get(id=exp_id),
                    category=EventSpecial.CHEFS)  
    else:
        ord = Order.objects.get(id=order_id)
        exp_id = ord.table.experiment.id 
        event=EventSpecial(user=request.user,
                    order=Order.objects.get(id=order_id),
                    experiment=Experiment.objects.get(id=exp_id),
                    category=EventSpecial.CHEFS)  
    event.save()

    choices = ChefChoice.objects.filter(item__active=True)
    for c in choices:
        i_data = {}
        i_data['item'] = c.item.get_json()

        menu_data.append(i_data)

    return render_to_response( "legals/i/chefchoices.html",
            {
            'header': header,
            'restaurant': restaurant,
            'menu_data': menu_data,
            'order_id': int(order_id)
            },
            context_instance=RequestContext(request))

@login_required
def view_friends_choices(request, order_id):
    """
        Display friend's choices

        :url: /legals/m/friend/choices/(?P<order_id>\d+)/

        :rtype: JSON
        ::

            [
                {
                    'item': item.get_json(),
                    'friends': 'Calvin, Ilya,...',
                    'anonymous': '15 people ordered',
                },
                {
                    'item': item.get_json(),
                    'friends': 'Calvin, Ilya,...',
                    'anonymous': '15 people ordered',
                }

            ]

            
    """

    u = request.user

    if int(order_id) == 0:
        exp_id = 1
        event=EventSpecial(user=u,
                    experiment=Experiment.objects.get(id=exp_id),
                    category=EventSpecial.FRIENDS)  
    else:
        ord = Order.objects.get(id=order_id)
        exp_id = ord.table.experiment.id 
        event=EventSpecial(user=u,
                    order=Order.objects.get(id=order_id),
                    experiment=Experiment.objects.get(id=exp_id),
                    category=EventSpecial.FRIENDS)  
    event.save()

    header = "legals"
    restaurant = Store.objects.get(id=1)
    category = {'name':"Friend's Choices",
                'description': "What your friend's have tried",
                'id': "friends" }

    # get friends of user
    fb_id = u.facebook_profile.facebook_id
    friends = Friends.objects.get(facebook_id=fb_id).friends.values_list('facebook_id', flat=True)
    
    # get those items that friends have ordered
    i_data={}
    orders = Order.objects.filter(user__facebook_profile__facebook_id__in=friends)
    for o in orders:
        if o.num_items() > 0:
            for r in o.items.all():
                if exp_id == 1:
                    if r.item.id not in i_data:
                        i_data[r.item.id] = {'item':r.item.get_json()}
                elif exp_id in [2,4,5]:
                    # 2: friends
                    # 4: friends anonymous 
                    # 5: intervention

                    if r.item.id not in i_data:
                        anonymous_label = ''
                        numordered = r.item.menuitemreview_set.count()
                        if numordered == 1: 
                            anonymous_label = '1 person ordered'
                        elif numordered > 1:
                            anonymous_label = '%d people ordered'%numordered

                        i_data[r.item.id] = {'item':r.item.get_json(), 'friends':set(), 
                                                'anonymous':anonymous_label}
                        i_data[r.item.id]['friends'].add(o.user.first_name)
                    else:
                        # friends that ordered the item
                        i_data[r.item.id]['friends'].add(o.user.first_name)
                elif exp_id == 3:
                    # popularity 
                    if r.item.id not in i_data:
                        anonymous_label = ''

                        numordered = r.item.menuitemreview_set.all().exclude(legals_ordered__user=u).count()
                        if numordered == 1: 
                            anonymous_label = '1 person ordered'
                        elif numordered > 1:
                            anonymous_label = '%d people ordered'%numordered

                        i_data[r.item.id] = {'item':r.item.get_json(), 'friends':set(), 
                                                'anonymous':anonymous_label}

    if exp_id in [2,4,5]:
        for key,val in i_data.items(): 
            # arrange labels
            numfriends = len(val['friends'])
            i = 0
            label = ''
            for f in val['friends']: 
                i += 1 
                if i == 3 and numfriends > 3:
                    label += f + ', ...'
                    # if there are more than three people, just show
                    # that there are more
                    break
                elif i == numfriends:
                    label += f 
                else:
                    label += f + ', '

            i_data[key]['friend_label']=label 

    return render_to_response( "legals/i/category.html",
            {
            'header': header,
            'restaurant': restaurant,
            'category': category,
            'menu_data': i_data,
            'exp_id': int(exp_id),
            'friend_experiment':[2,4,5],
            'order_id': int(order_id)
            },
            context_instance=RequestContext(request))

@never_cache
@login_required
def view_item(request, item_id, order_id):
    """
        View details of an item
        
        :url: /legals/m/item/(?P<item_id>\d+)/(?<order_id>\d+)/
    """
    header = "legals"
    restaurant = Store.objects.get(id=1)

    item = MenuItem.objects.get(id=item_id)
    # has it been ordered yet, if so need to hide order button
    ordered = False

    u = request.user
    if int(order_id) == 0:
        exp_id = 1
    else:
        ord = Order.objects.get(id=order_id)
        exp_id = ord.table.experiment.id 

    try:
        if int(order_id) > 0:
            o = Order.objects.get(id=order_id)
            r = o.items.get(item=item)
            ordered = True
    except MenuItemReview.DoesNotExist:
        # hasn't been ordered yet
        ordered=False

     
    #: initialize
    numordered = 0

    i_data = {}
    i_data['item'] = item.get_json()
    # build social data for this item
    # with who else liked it
    if exp_id == 3:
        numordered = item.menuitemreview_set.all().exclude(legals_ordered__user=u).count()
        numwanted = item.pre_favorite_dishes.all().count()
        if numordered == 0:
            i_data['anonymous'] = ''
        elif numordered == 1: 
            i_data['anonymous'] = '1 person ordered'
        else:
            i_data['anonymous'] = '%d people ordered'%numordered

        numliked = item.menuitemreview_set.all().exclude(legals_ordered__user=u).filter(rating__gte=4).count()
        if numliked == 0:
            i_data['aliked'] = ''
        elif numliked == 1: 
            i_data['aliked'] = '1 person like this'
        else:
            i_data['aliked'] = '%d people like this'%numordered

        if numwanted == 0:
            i_data['awanted'] = ''
        elif numwanted == 1: 
            i_data['awanted'] = '1 person wants this'
        else:
            i_data['awanted'] = '%d people want this'%numwanted

    elif exp_id in [2,4,5]:
        i_data['friends'] = set() 
        i_data['fliked'] = set() 
        i_data['fwanted'] = set()

    # Handle friends orders and reviews
    if exp_id in [2,4,5]:
        # get friends of user
        fb_id = request.user.facebook_profile.facebook_id
        friends = Friends.objects.get(facebook_id=fb_id).friends.values_list('facebook_id', flat=True)
        
        # get those items that friends have ordered 
        reviews = item.menuitemreview_set.filter(legals_ordered__user__facebook_profile__facebook_id__in=friends)
        for r in reviews:
            # 2: friends
            # 4: friends and popularity mixed
            # 5: intervention
            if r.item.id == int(i_data['item']['id']):
                # friends that ordered the item
                i_data['friends'].add(r.legals_ordered.all()[0].user.first_name)
                if r.rating >= MenuItemReview.GOOD:
                    i_data['fliked'].add(r.legals_ordered.all()[0].user.first_name)
                want_fb_ids = r.item.pre_favorite_dishes.filter(facebook_id__in=friends).values('facebook_id')
                for f in Friends.objects.filter(facebook_id__in=want_fb_ids):
                    if f.name:
                        i_data['fwanted'].add(f.name.split()[0])
    if exp_id == 4:
        numordered = len(i_data['friends'])
        numliked = len(i_data['fliked'])
        numwanted = len(i_data['fwanted'])
        if numordered > 0:
            i_data['friends'] = "%d friend(s) ordered"%numordered
        else:
            i_data['friends'] = ''
        if numliked > 0:
            i_data['fliked'] = "%d friend(s) like this"%numliked
        else:
            i_data['fliked'] = ''
        if numwanted > 0:
            i_data['fwanted'] = "%d friend(s) want this"%numwanted
        else:
            i_data['fwanted'] = ''

    if exp_id == 5:
        i_data['alternative'] = []
        # create alternatives
        alt = {}
        alt['influencer'] = 'Ilya'
        alt['action'] = 'ordered'
        alt['alt_id'] = 65
        alt['alt_name'] = 'Crab Cake'
        alt['alt_save'] = 'save $3'
        alt['alt_health'] = '300 calories lower'
        i_data['alternative'].append(alt)

    if int(order_id) > 0:
        # convert set to list
        if exp_id in [2,5]:
            i_data['friends'] = list(i_data['friends'])
            i_data['fliked'] = list(i_data['fliked'])
            i_data['fwanted'] = list(i_data['fwanted'])
        event = EventMenuItem(user=u, 
                order=o,
                experiment=Experiment.objects.get(id=exp_id),
                item=item, 
                action=EventMenuItem.CONSIDER,
                num_people=numordered,
                params=json.dumps(i_data))
    else:
        # user is just considering since cannot order
        event = EventMenuItem(user=u, 
                experiment=Experiment.objects.get(id=exp_id),
                item=item, 
                action=EventMenuItem.CONSIDER)
    event.save()
 
    return render_to_response( "legals/i/item.html",
            {
            'header': header,
            'restaurant': restaurant,
            'cat_id': item.category.id,
            'i': i_data,
            'exp_id': int(exp_id),
            'order_id': int(order_id),
            },
            context_instance=RequestContext(request))

@login_required
def item_reconsider(request, item_id, order_id):
    """
        Reconsider an ordered item, so it allows cancellation
        
        :url: /legals/m/reconsider/(?P<item_id>\d+)/(?<order_id>\d+)/
    """
    header = "legals"
    restaurant = Store.objects.get(id=1)

    ordered = True

    u = request.user
    if int(order_id) == 0:
        exp_id = 1
    else:
        ord = Order.objects.get(id=order_id)
        exp_id = ord.table.experiment.id 

    item = MenuItem.objects.get(id=item_id)
    o = Order.objects.get(id=order_id)

    #: initialize
    numordered = 0

    i_data = {}
    i_data['item'] = item.get_json()
    # build social data for this item
    # with who else liked it
    if exp_id == 3:
        numordered = item.menuitemreview_set.all().exclude(legals_ordered__user=u).count()
        numwanted = item.pre_favorite_dishes.all().count()
        if numordered == 0:
            i_data['anonymous'] = ''
        elif numordered == 1: 
            i_data['anonymous'] = '1 person ordered'
        else:
            i_data['anonymous'] = '%d people ordered'%numordered

        numliked = item.menuitemreview_set.all().exclude(legals_ordered__user=u).filter(rating__gte=4).count()
        if numliked == 0:
            i_data['aliked'] = ''
        elif numliked == 1: 
            i_data['aliked'] = '1 person like this'
        else:
            i_data['aliked'] = '%d people like this'%numordered

        if numwanted == 0:
            i_data['awanted'] = ''
        elif numwanted == 1: 
            i_data['awanted'] = '1 person wants this'
        else:
            i_data['awanted'] = '%d people want this'%numwanted

    elif exp_id in [2,4,5]:
        i_data['friends'] = set() 
        i_data['fliked'] = set() 
        i_data['fwanted'] = set()

    # Handle friends orders and reviews
    if exp_id in [2,4,5]:
        # get friends of user
        fb_id = request.user.facebook_profile.facebook_id
        friends = Friends.objects.get(facebook_id=fb_id).friends.values_list('facebook_id', flat=True)
        
        # get those items that friends have ordered 
        reviews = item.menuitemreview_set.filter(legals_ordered__user__facebook_profile__facebook_id__in=friends)
        for r in reviews:
            # 2: friends
            # 4: friends and popularity mixed
            # 5: intervention
            if r.item.id == int(i_data['item']['id']):
                # friends that ordered the item
                i_data['friends'].add(r.legals_ordered.all()[0].user.first_name)
                if r.rating >= MenuItemReview.GOOD:
                    i_data['fliked'].add(r.legals_ordered.all()[0].user.first_name)
                want_fb_ids = r.item.pre_favorite_dishes.filter(facebook_id__in=friends).values('facebook_id')
                for f in Friends.objects.filter(facebook_id__in=want_fb_ids):
                    if f.name:
                        i_data['fwanted'].add(f.name.split(" ")[0])

    if exp_id == 4:
        numordered = len(i_data['friends'])
        numliked = len(i_data['fliked'])
        numwanted = len(i_data['fwanted'])
        if numordered > 0:
            i_data['friends'] = "%d friend(s) ordered"%numordered
        else:
            i_data['friends'] = ''
        if numliked > 0:
            i_data['fliked'] = "%d friend(s) like this"%numliked
        else:
            i_data['fliked'] = ''
        if numwanted > 0:
            i_data['fwanted'] = "%d friend(s) want this"%numwanted
        else:
            i_data['fwanted'] = ''

    if exp_id == 5:
        i_data['alternative'] = []
        # create alternatives
        alt = {}
        alt['influencer'] = 'Ilya'
        alt['action'] = 'ordered'
        alt['alt_id'] = 65
        alt['alt_name'] = 'Crab Cake'
        alt['alt_save'] = 'save $3'
        alt['alt_health'] = '300 calories lower'
        i_data['alternative'].append(alt)

    if int(order_id) > 0:
        # convert set to list
        if exp_id in [2,5]:
            i_data['friends'] = list(i_data['friends'])
            i_data['fliked'] = list(i_data['fliked'])
            i_data['fwanted'] = list(i_data['fwanted'])

        event = EventMenuItem(user=u, 
                order=o,
                experiment=Experiment.objects.get(id=exp_id),
                item=item, 
                action=EventMenuItem.RECONSIDER,
                num_people=numordered,
                params=json.dumps(i_data))
    else:
        # user is just considering since cannot order
        event = EventMenuItem(user=u, 
                experiment=Experiment.objects.get(id=exp_id),
                item=item, 
                action=EventMenuItem.RECONSIDER)
 
    event.save()

    return render_to_response( "legals/i/reconsider.html",
            {
            'header': header,
            'restaurant': restaurant,
            'cat_id': item.category.id,
            'i': i_data,
            'exp_id': int(exp_id),
            'order_id': int(order_id),
            },
            context_instance=RequestContext(request)
            )

@login_required
def mark_item(request, item_id, order_id):
    """
        Mark an item to order

        :url: /legals/m/mark/(?P<item_id>\d+)/(?<order_id>\d+)/

        :param order_id: cannot be 0 since if 0 it should never show up
                        in the first place
    """
    header = "legals"
    restaurant = Store.objects.get(id=1)

    u = request.user
    ord = Order.objects.get(id=order_id)
    exp_id = ord.table.experiment.id 

    # log to events
    item = MenuItem.objects.get(id=int(item_id))
    o = Order.objects.get(id=order_id)
    try:
        r = o.items.get(item=item)
        logger.debug("Already have %s on the order"%item.name)
        # already had ordered the item
    except MenuItemReview.DoesNotExist:
        logger.debug("Ordering %s"%item.name)
        # create a review
        r = MenuItemReview(item=item, rating=0, comment="Comments: click to edit")
        r.save()
        o.items.add(r)
        o.save()
        o.last_update()

    # log mark/order event
    people_ordered = item.menuitemreview_set.all().exclude(legals_ordered__user=u)
    event = EventMenuItem(user=u, 
            order=o,
            experiment=Experiment.objects.get(id=exp_id),
            item=item, 
            action=EventMenuItem.MARK,
            num_people=people_ordered.count())
    event.save()

    
    i_data = {}
    # build menu items from my orders
    # with who else liked it
    item_reviews = o.items.all()
    for r in item_reviews:
        #: contains item and other social metadata
        i_data[r.item.id] = {'item':r.item.get_json()}
        if exp_id == 3:
            numordered = r.item.menuitemreview_set.all().exclude(legals_ordered__user=u).count()
            if numordered == 0:
                i_data[r.item.id]['anonymous'] = ''
            elif numordered == 1: 
                i_data[r.item.id]['anonymous'] = '1 person ordered'
            else:
                i_data[r.item.id]['anonymous'] = '%d people ordered'%numordered

            numliked = r.item.menuitemreview_set.all().exclude(legals_ordered__user=u).filter(rating__gte=4).count()
            if numliked == 0:
                i_data[r.item.id]['aliked'] = ''
            elif numliked == 1: 
                i_data[r.item.id]['aliked'] = '1 person like this'
            else:
                i_data[r.item.id]['aliked'] = '%d people like this'%numordered

        elif exp_id in [2,4,5]:
            i_data[r.item.id]['friends'] = set() 
            i_data[r.item.id]['fliked'] = set() 
        

    # Handle friends orders and reviews
    if exp_id in [2,4,5]:
        # get friends of user
        fb_id = request.user.facebook_profile.facebook_id
        friends = Friends.objects.get(facebook_id=fb_id).friends.values_list('facebook_id', flat=True)
        
        # get those items that friends have ordered 
        orders = Order.objects.filter(user__facebook_profile__facebook_id__in=friends)
        for o in orders:
            if o.num_items() > 0:
                for r in o.items.all():
                    # 2: friends
                    # 4: friends and popularity mixed
                    # 5: intervention
                    if r.item.id in i_data:
                        # friends that ordered the item
                        i_data[r.item.id]['friends'].add(o.user.first_name)
                        if r.rating >= MenuItemReview.GOOD:
                            i_data[r.item.id]['fliked'].add(o.user.first_name)
    
        for key,val in i_data.items(): 
            # arrange labels
            numfriends = len(val['friends'])
            numliked = len(val['fliked'])

            if exp_id == 4:
                # anonymous friends
                i_data[key]['friend_label']="%d friend(s) ordered"%numfriends
                if numliked > 0:
                    i_data[key]['fliked']="%d friend(s) like this"%numliked
            else:
                # friends names           
                i = 0
                label = ''
                for f in val['friends']: 
                    i += 1 
                    if i == 3 and numfriends > 3:
                        label += f + ', ...'
                        # if there are more than three people, just show
                        # that there are more
                        break
                    elif i == numfriends:
                        label += f 
                    else:
                        label += f + ', '

                i_data[key]['friend_label']=label+" ordered"


    logger.debug("Mark Order: Listing order")

    return render_to_response( "legals/i/order.html",
            {
            'header': header,
            'restaurant': restaurant,
            'order_data': i_data,
            'exp_id': int(exp_id),
            'experiments': [2,5],
            'order_id': int(order_id)
            },
            context_instance=RequestContext(request))

@login_required
def unmark_item(request, item_id, order_id):
    """
        Unmark an item to cancel order 

        :url: /legals/m/unmark/(?P<item_id>\d+)/(?<order_id>\d+)/
    """
    header = "legals"
    restaurant = Store.objects.get(id=1)

    u = request.user
    ord = Order.objects.get(id=order_id)
    exp_id = ord.table.experiment.id 

    # log to events
    item = MenuItem.objects.get(id=int(item_id))

    o = Order.objects.get(id=order_id)
    try:
        r = o.items.get(item=item)
        o.items.remove(r)
        o.save()
        o.last_update()
    except MenuItemReview.DoesNotExist:
        logger.debug("Already removed %s from order"%item.name)
        pass

    # log unmark/cancel event
    people_ordered = item.menuitemreview_set.all().exclude(legals_ordered__user=u)
    event = EventMenuItem(user=u, 
            order=o,
            experiment=Experiment.objects.get(id=exp_id),
            item=item, 
            action=EventMenuItem.UNMARK,
            num_people=people_ordered.count())
    event.save()

    i_data = {}
    # build menu items for this category
    # with who else liked it
    item_reviews = o.items.all()
    for r in item_reviews:
        #: contains item and other social metadata
        i_data[r.item.id] = {'item':r.item.get_json()}
        if exp_id == 3:
            numordered = r.item.menuitemreview_set.all().exclude(legals_ordered__user=u).count()
            if numordered == 0:
                i_data[r.item.id]['anonymous'] = ''
            elif numordered == 1: 
                i_data[r.item.id]['anonymous'] = '1 person ordered'
            else:
                i_data[r.item.id]['anonymous'] = '%d people ordered'%numordered

            numliked = r.item.menuitemreview_set.all().exclude(legals_ordered__user=u).filter(rating__gte=4).count()
            if numliked == 0:
                i_data[r.item.id]['aliked'] = ''
            elif numliked == 1: 
                i_data[r.item.id]['aliked'] = '1 person like this'
            else:
                i_data[r.item.id]['aliked'] = '%d people like this'%numordered

        elif exp_id in [2,4,5]:
            i_data[r.item.id]['friends'] = set()
            i_data[r.item.id]['fliked'] = set() 
        

    # Handle friends orders and reviews
    if exp_id in [2,4,5]:
        # get friends of user
        fb_id = request.user.facebook_profile.facebook_id
        friends = Friends.objects.get(facebook_id=fb_id).friends.values_list('facebook_id', flat=True)
        
        # get those items that friends have ordered 
        orders = Order.objects.filter(user__facebook_profile__facebook_id__in=friends)
        for o in orders:
            if o.num_items() > 0:
                for r in o.items.all():
                    # 2: friends
                    # 4: friends and popularity mixed
                    # 5: intervention
                    if r.item.id in i_data:
                        # friends that ordered the item
                        i_data[r.item.id]['friends'].add(o.user.first_name)
                        if r.rating >= MenuItemReview.GOOD:
                            i_data[r.item.id]['fliked'].add(o.user.first_name)
    
        for key,val in i_data.items(): 
            # arrange labels
            numfriends = len(val['friends'])
            numliked = len(val['fliked'])

            if exp_id == 4:
                # anonymous friends
                i_data[key]['friend_label']="%d friend(s) ordered"%numfriends
                if numliked > 0:
                    i_data[key]['fliked']="%d friend(s) like this"%numliked
            else:
                i = 0
                label = ''
                for f in val['friends']: 
                    i += 1 
                    if i == 3 and numfriends > 3:
                        label += f + ', ...'
                        # if there are more than three people, just show
                        # that there are more
                        break
                    elif i == numfriends:
                        label += f 
                    else:
                        label += f + ', '

                i_data[key]['friend_label']=label+" ordered"

    logger.debug("Unmark Order: Listing order")

    return render_to_response( "legals/i/order.html",
            {
            'header': header,
            'restaurant': restaurant,
            'order_data': i_data,
            'exp_id': int(exp_id),
            'experiments': [2,5],
            'order_id': int(order_id)
            },
            context_instance=RequestContext(request))

@never_cache
def my_order(request, order_id):
    """
        View ordered items

        :url: /legals/m/myorder/(?P<order_id>\d+)/

    """

    header = "legals"
    restaurant = Store.objects.get(id=1)

    u = request.user
    o = Order.objects.get(id=order_id)
    exp_id = o.table.experiment.id 
    item_reviews = o.items.all()
    
    logger.debug("View Orders: Listing order")

    event = EventBasic(user=u, 
                    order=o,
                    experiment=u.experiment,
                    action=EventBasic.MY_ORDER)
    event.save()

    i_data = {}
    # build menu items from my orders
    # with who else liked it
    item_reviews = o.items.all()
    for r in item_reviews:
        #: contains item and other social metadata
        i_data[r.item.id] = {'item':r.item.get_json()}
        if exp_id == 3:
            numordered = r.item.menuitemreview_set.all().exclude(legals_ordered__user=u).count()
            if numordered == 0:
                i_data[r.item.id]['anonymous'] = ''
            elif numordered == 1: 
                i_data[r.item.id]['anonymous'] = '1 person ordered'
            else:
                i_data[r.item.id]['anonymous'] = '%d people ordered'%numordered

            numliked = r.item.menuitemreview_set.all().exclude(legals_ordered__user=u).filter(rating__gte=4).count()
            if numliked == 0:
                i_data[r.item.id]['aliked'] = ''
            elif numliked == 1: 
                i_data[r.item.id]['aliked'] = '1 person like this'
            else:
                i_data[r.item.id]['aliked'] = '%d people like this'%numordered

        elif exp_id in [2,4,5]:
            i_data[r.item.id]['friends'] = set() 
            i_data[r.item.id]['fliked'] = set() 
        

    # Handle friends orders and reviews
    if exp_id in [2,4,5]:
        # get friends of user
        fb_id = request.user.facebook_profile.facebook_id
        friends = Friends.objects.get(facebook_id=fb_id).friends.values_list('facebook_id', flat=True)
        
        # get those items that friends have ordered 
        orders = Order.objects.filter(user__facebook_profile__facebook_id__in=friends)
        for o in orders:
            if o.num_items() > 0:
                for r in o.items.all():
                    # 2: friends
                    # 4: friends and popularity mixed
                    # 5: intervention
                    if r.item.id in i_data:
                        # friends that ordered the item
                        i_data[r.item.id]['friends'].add(o.user.first_name)
                        if r.rating >= MenuItemReview.GOOD:
                            i_data[r.item.id]['fliked'].add(o.user.first_name)
    
        for key,val in i_data.items(): 
            # arrange labels
            numfriends = len(val['friends'])
            numliked = len(val['fliked'])

            if exp_id == 4:
                # anonymous friends
                i_data[key]['friend_label']="%d friend(s) ordered"%numfriends
                if numliked > 0:
                    i_data[key]['fliked']="%d friend(s) like this"%numliked
            else:
                i = 0
                label = ''
                for f in val['friends']: 
                    i += 1 
                    if i == 3 and numfriends > 3:
                        label += f + ', ...'
                        # if there are more than three people, just show
                        # that there are more
                        break
                    elif i == numfriends:
                        label += f 
                    else:
                        label += f + ', '

                i_data[key]['friend_label']=label+" ordered" 

    logger.debug("List My Order: Listing order")

    return render_to_response( "legals/i/order.html",
            {
            'header': header,
            'restaurant': restaurant,
            'order_data': i_data,
            'exp_id': int(exp_id),
            'experiments': [2,5],
            'order_id': int(order_id)
            },
            context_instance=RequestContext(request))

@login_required
def search(request):
    """
        Search for an item or filter

        :url: /legals/m/search/
    """

    pass

def home(request, order_id):
    """
        This would be used for home menu, however, currently not needed.
        Go directly to menu

        :url: /legals/m/home/

    """
    o = Order.objects.get(id=order_id)
    exp_id = o.table.experiment.id

    # call /legals/m/menu/(?P<exp_id>\d+)/ from the template to display menu
    return render_to_response("legals/mobile_home.html",
            {
                'exp_id': int(exp_id),
            },
            context_instace=RequestContext(request) )

def get_menu(request):
    """
        Load JSON of all menu item
        :url: /legals/m/json/menu/
        
        :return: JSON of all menu item
    """
    restaurant = Store.objects.get(id=1)
    # build menu items for each category
    items = MenuItem.objects.filter(category__store=restaurant)
    items_array = []
    for i in items:
        items_array.append(i.get_json())
    return JSONHttpResponse(items_array)

def login_ws(request):
    """
        This method would be used if a native app was built

        :url: /legals/m/login/real/
        
        :param POST['email']: email
        :param POST['pin']: PIN of the user
        :param POST['lat']: latitude of the phone
        :param POST['lon']: longitude of the phone

        :rtype: JSON
        ::

            # `experiment` is the experimental group
            #   0: control group
            #   1: social group
            #   2: anonymous social group

            # `surveys` is the number of surveys that needs to be filled

            # login success
            {'result':'1', 'experiment': '0', 'surveys': '2'}
            # login failure
            {'result':'-1'}

    """

    email = request.POST['email']
    pin = hashlib.sha224(request.POST['pin']).hexdigest()
    user = authenticate(email=email, pin=pin)
    if user is not None:
        login(request, user)
        logger.debug( "User %s authenticated and logged in: "%email )
        exp_group = user.experiment.id
        # TODO: check the number of surveys that needs to be filled out
        
        # log latitude and longitude
        if 'lat' in request.POST:
            event = EventBasic(user=user, experiment=user.experiment, action=EventBasic.LOGIN_TEST, latitude=float(request.POST['lat']), longitude=float(request.POST['lon']))
            event.save()
        return JSONHttpResponse({'result': '1', 'experiment': str(exp_group), 'surveys':'2'})          
    else:
        return JSONHttpResponse({'result': '-1'})

@login_required
def order(request):
    """
        Order items

        :param POST['items']: the item id's of ordered items (list in string format)
        :param POST['table']: the table number where customer sits
    """
    #if request.user.is_authenticated():
    u = request.user
    #u = User.objects.get(id=2)
    tc = TableCode.objects.filter(code=request.POST['table']).latest('date')
    o = Order(user=u, table=tc)    
    o.save()
    #logger.debug("posted items %s"%request.POST['items'])

    for i in eval(request.POST['items']):
        m = MenuItem.objects.get(id=i)
        r = MenuItemReview(item=m, rating=0, comment="Please let us know how you liked this dish.")
        r.save()
        o.items.add(r)
    o.save()
    o.last_update()

    return JSONHttpResponse({'result':'1'})
    #else:
    #    return JSONHttpResponse({'result':'-1'})

@login_required
def register(request):
    """
        Useful if a native app is built
        Registers the token for iPhone

        :url: /mobile/register/

        :param POST['udid']: the token

        :rtype: JSON
        ::

            # successful
            {'result':'1'}
            # failed registration
            {'result':'-1', 'form_errors':form.errors}
            # if not logged in
            {'result':'-3'}
    """
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = IPhoneRegisterForm( request.POST )
            if form.is_valid():
                p, created = iPhone.objects.get_or_create(user=request.user)
                p.udid = form.cleaned_data['udid']
                p.save()
                return JSONHttpResponse({'result': '1'})
            else:
                return JSONHttpResponse({'result': '-1', 'form_errors':form.errors})
        else:
            form = IPhoneRegisterForm()
            # only used when GET request is made through web page
            return render_to_response( 'registerform.html', { 'form': form, },
                    context_instance=RequestContext(request))
    else:
        return JSONHttpResponse({'result': '-3'})


