@csrf_exempt
@login_required
def item_group_start(request):
    """
        Item view when initiating group purchase

        Does not need Add a review, nor Add to wishlist

        :url: /m/item/start/group/
        
        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::


    """
    result = {}

    # Need to check if already in wish list

    return JSONHttpResponse()

@csrf_exempt
@login_required
def item_group_join(request):
    """
        Item view when participating in group purchase or when
        considering participating in group purchase

        Need to show a table of discount people will get when they 
        participate in the group purchase

        5% if 10 people join

        :url: /m/item/join/group/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::


    """
    result = {}

    # TODO: can also invite friends if you already joined the group purchase 

    # status = not started, initiated, joined
    # in_my_wishlist = true, false
    # can_review = true, false

    return JSONHttpResponse()


@csrf_exempt
@login_required
def group_ongoing_list(request):
    """
        Group purchases that I am participating in

        :url: /m/group/ongoing/list/

        :rtype: JSON

        ::

            {
              "group_purchases": []
            }
    """
    result = {}

    u = request.user

    # group purchase that I am participating
    g_purchases = u.participating_group_purchases.filter(fulfilled=False,expire_date__gt=datetime.now())
   
    result["group_purchases"] = [ g.get_json() for g in g_purchases]

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def group_join_list(request):
    """
        Lists potential group purchases that are ongoing 

        :url: /m/group/join/list/

        :rtype: JSON

        ::

            {
              "group_purchases": []
            }

    """
    result = {}

    u = request.user

    # group purchases that I am not participating
    g_purchases = GroupPurchase.objects.exclude(participants=u).filter(fulfilled=False, expire_date__gt=datetime.now())

    result["group_purchases"] = [ g.get_json() for g in g_purchases]

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def group_start_list(request):
    """
        Lists potential group purchases that have not been started

        :url: /m/group/start/list/

        :rtype: JSON

        ::

            {
              "group_purchase": [
                {
                  "product": {
                    "sku": "Sony Cyber-Shot 14.1-Megapixel Digital Camera - Blue", 
                    "id": 9
                  }, 
                  "wishes": "2"
                }, 
                {
                  "product": {
                    "sku": "Sony bloggie High-Definition Digital Camcorder with 2.4\" LCD Monitor - Pink", 
                    "id": 10
                  }, 
                  "wishes": "1"
                }, 
                {
                  "product": {
                    "sku": "Sony bloggie High-Definition Digital Camcorder with 2.4\" LCD Monitor - Purple", 
                    "id": 11
                  }, 
                  "wishes": "1"
                }
              ]
            }
    """
    result = {}
    result["group_purchase"] = [] 

    u = request.user

    wished_not_group_purchase = u.wishlist.filter(group=None, fulfilled=False)

    # people wishing this product
    for w in wished_not_group_purchase:
        result["group_purchase"].append({
                                        'product': w.product.get_json(),
                                        'wishes': str(w.product.wished_by())
                                        }) 

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def group_ended_list(request):
    """
        Group purchases that I have initiated or participated that ended

        :url: /m/group/ended/list/

        :rtype: JSON

        ::

            {
              "group_purchases": [], 
              "initiated_group": []
            }
    """
    result = {}

    u = request.user

    g_purchases = u.initiated_group_purchases.filter(fulfilled=True)
    result["initiated_group"] = [ g.get_json() for g in g_purchases]

    g_purchases = u.participating_group_purchases.filter(fulfilled=True)
    result["group_purchases"] = [ g.get_json() for g in g_purchases]

    return JSONHttpResponse(result)


@csrf_exempt
@login_required
def group_purchase_start(request):
    """
        Initiate a group purchase
        Let everybody who has the item on the wish list know
        Show a view where one is confirming group purchase and that
        25 people who has the item on wish list will be notified

        Invite friends to group purchase option is available on this view

        :url: /m/group/start/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::



    """
    result = {}

    u = request.user
    # Ongoing (group purchases you already joined)
    # Join (on going group purchases)
    # Start (begin a group purchase)
    # Ended (group purchases that have ended)
    
    p = Product.objects.get(id=int(request.POST['sku']))
    g = GroupPurchase(initiator=u, product=p, expire_date=datetime.now()+timedelta(30))
    g.save()

    # Need to notify those who are participating
    wishers = WishList.objects.filter(product=p,fulfilled=False)
    for w in wishers:
        g.invited.add(w.user)
        # TODO: send iPhone notifications

    result['result'] = '1'

    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def group_purchase_join(request):
    """
        For joining group purchase
        
        :url: /m/group/join/

        :param POST['group_id']: group purchase ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::


    """
    result = {}
    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def group_purchase_invite_friends(request):
    """
        For inviting additional friends to the existing group purchase
        Show list of friends and if any of them have accepted group
        purchase, it should show positive mark

        :url: /m/group/invite/friends/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::



    """
    result = {}

    
    return JSONHttpResponse(result)


@csrf_exempt
@login_required
def group_add_friend(request):
    """
        Add a friend
        An AJAX call to add a friend to group

        :url: /m/group/add/friend/

        :param POST['sku']: Item ID
        :param POST['group_id']: Group ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::


    """
    result = {}

    
    return JSONHttpResponse(result)

@csrf_exempt
@login_required
def group_remove_friend(request):
    """
        Remove a friend
        An AJAX call to remove friend from group

        :url: /m/group/remove/friend/

        :param POST['sku']: Item ID
        :param POST['group_id']: Group ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::



    """
    result = {}

    
    return JSONHttpResponse(result)


@csrf_exempt
@login_required
def group_send_invite(request):
    """
        Send friends invitation to participate in group purchase
        Push notification

        :url: /m/group/send/invite/

        :param POST['sku']: Item ID
        :param POST['group_id']: Group ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::



    """
    result = {}

    
    return JSONHttpResponse(result)


