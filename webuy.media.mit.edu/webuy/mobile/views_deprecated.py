@csrf_exempt
@login_required
def feed_friend(request):
    """
        :note: replaced by :meth:`view_party()`

        Clicked a friend from Feeds

        :url: /m/feed/friend/

        :param POST['friend_id']: friend party id
        :param POST['feed_id']: feed id

        :rtype: JSON

        ::

            # for experiment group 1, 3 no first_name, last_name fields

            {
              "wished": [
                {
                  "wish_id": "3", 
                  "comment": "This is awesome", 
                  "added": "1273123730.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "first_name": "Kwan", 
                    "last_name": "Lee", 
                    "name": "Kwan Hong Lee", 
                    "alias": "kool", 
                    "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5", 
                    "phone": "", 
                    "first_joined": "1267990187.0", 
                    "id": "2"
                  }, 
                  "max_price": "100.00"
                }, 
                {
                  "wish_id": "2", 
                  "comment": "", 
                  "added": "1273123729.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "first_name": "Kwan", 
                    "last_name": "Lee", 
                    "name": "Kwan Hong Lee", 
                    "alias": "kool", 
                    "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5", 
                    "phone": "", 
                    "first_joined": "1267990187.0", 
                    "id": "2"
                  }, 
                  "max_price": "100.00"
                }, 
                {
                  "wish_id": "1", 
                  "comment": "This is awesome", 
                  "added": "1273123728.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "first_name": "Kwan", 
                    "last_name": "Lee", 
                    "name": "Kwan Hong Lee", 
                    "alias": "kool", 
                    "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5", 
                    "phone": "", 
                    "first_joined": "1267990187.0", 
                    "id": "2"
                  }, 
                  "max_price": "100.00"
                }
              ], 
              "friend": {
                "first_name": "Kwan", 
                "last_name": "Lee", 
                "name": "Kwan Hong Lee", 
                "alias": "kool", 
                "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5", 
                "phone": "", 
                "first_joined": "1267990187.0", 
                "id": "2"
              }, 
              "bought": [
                {
                  "source": "Store", 
                  "unit_quantity": "1", 
                  "sale_price": "199.99", 
                  "purchase_date": "1273123722.0", 
                  "party": {
                    "alias": "kool", 
                    "first_joined": "1267990187.0", 
                    "id": "2", 
                    "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5"
                  }
                }, 
                {
                  "source": "Store", 
                  "unit_quantity": "1", 
                  "sale_price": "39.99", 
                  "purchase_date": "1273123722.0", 
                  "party": {
                    "alias": "kool", 
                    "first_joined": "1267990187.0", 
                    "id": "2", 
                    "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5"
                  }
                }, 
                {
                  "source": "Store", 
                  "unit_quantity": "1", 
                  "sale_price": "39.99", 
                  "purchase_date": "1273123722.0", 
                  "party": {
                    "alias": "kool", 
                    "first_joined": "1267990187.0", 
                    "id": "2", 
                    "image": "http://external.ak.fbcdn.net/safe_image.php?logo&d=48a656a116ea622bf6e462eae03e9ecd&url=http%3A%2F%2Fprofile.ak.fbcdn.net%2Fv229%2F620%2F9%2Fq706848_1099.jpg&v=5"
                  }
                }
              ]
            }

    """

    result = {}

    u = request.user

    # return friend information
    party_id = int(request.POST['friend_id'])
    f = Party.objects.get(id=party_id)
    result['friend'] = f.get_json(level=1)
    
    # shows what the friend has recently bought or wishes

    if other in u.friends():
        # this other person is a friend so show all details
        bought = TransactionLineItem.objects.filter(transaction__party=other).order_by('-transaction__timestamp')
        wishes = Wishlist.objects.filter(party=other).order_by('-added')

        result['bought'] = [b.details() for b in bought[:10]]
        result['wished'] = [w.details() for w in wishes[:10]]
 
    else:
        # just show some details
        bought = TransactionLineItem.objects.filter(transaction__party=other).order_by('-transaction__timestamp')
        wishes = Wishlist.objects.filter(party=other).order_by('-added')

        result['bought'] = [b.details() for b in bought[:3]]
        result['wished'] = [w.details() for w in wishes[:3]]
 
    
    return JSONHttpResponse(result)


@csrf_exempt
@login_required
def feed_item(request):
    """
        Clicked an item from Feeds

        :url: /m/feed/item/

        :param POST['sku']: item id
        :param POST['feed_id']: feed id

        :rtype: JSON

        ::

            # if product doesn't exist (something wrong if it gets this output)
            {'result':'0'}

            # if it exists
            {
              "regular_price": "39.99", 
              "bought_by": "Bought by Ben", 
              "wished_by": "", 
              "num_requested": "0", 
              "ask_review": "", 
              "sku": "9461076", 
              "num_bought": "1", 
              "add_wish": "", 
              "on_sale": false, 
              "customer_review_count": "20", 
              "num_wished": "0", 
              "add_review": "/m/review/add/", 
              "thumbnail_image": "http://images.bestbuy.com/BestBuy_US/images/products/9461/9461076s.jpg", 
              "new": false, 
              "review_request": "", 
              "category": "Action & Adventure", 
              "artist_name": "", 
              "sale_price": "39.99", 
              "product_id": "1218108383576", 
              "customer_review_average": "5.0", 
              "name": "Ratchet &amp; Clank Future: A Crack in Time - PlayStation 3", 
              "reviews": {
                "count": "0", 
                "reviews": []
              }, 
              "medium_image": "", 
              "album_title": ""
            }
    """
    result = {}
    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])
    if p is not None:
        result = p.details(u)

        # since you already bought, no need to add to wish
        result['add_wish'] = ""
        result['add_review'] = ""
        result['ask_review'] = ""

        bought_count = p.transactionlineitem_set.filter(transaction__party=u).count()
        wished_count = p.in_wishes.filter(party=u).count()
        if wished_count == 0 and bought_count == 0:
            # if not in wish nor bought add to wish list
            result['add_wish'] = "/m/wishlist/add/"
        if bought_count > 0 and Review.objects.filter(product=p, reviewer=u).count() == 0:
            # if bought and no review, add review
            result['add_review'] = "/m/review/add/"
            
        # already in wish list so ask for review 
        if wished_count > 0:
            result['ask_review'] = "/m/review/ask/"

        # TODO: experimental groups get different reviews
        reviews = Review.objects.filter(product=p)
        result['reviews'] = {'count': str(reviews.count()),
                            'reviews': [r.get_json(me=u) for r in reviews]}
    else:
        result['result']='0'


    return JSONHttpResponse(result)


@csrf_exempt
@login_required
def bought_people(request):
    """
        List of people who bought, and their short reviews

        :url: /m/bought/people/

        :param POST['sku']: Item ID
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            {
              "count": "1", 
              "reviews": [
                {
                  "replied": true, 
                  "rating": "0", 
                  "review_id": "2", 
                  "content": "It's not easy to find such a polished product.", 
                  "reviewer": {
                    "alias": "ben.viralington", 
                    "first_joined": "1273123721.0", 
                    "id": "3", 
                    "image": ""
                  }, 
                  "viewed": "1", 
                  "posted": "1273123731.0"
                }
              ]
            }
    """

    result = {}

    u = request.user

    p = Product.objects.get_by_sku(request.POST['sku'])
    if p is not None:
        if u.experiment.id in [2,4]:
            my_friends = u.friends()
            reviews = Review.objects.filter(product=p, reviewer__in=my_friends)
            result['count'] = str(reviews.count())
            result['reviews'] = [r.get_json(me=u) for r in reviews]
        else:
            reviews = Review.objects.filter(product=p)
            result['count'] = str(reviews.count())
            result['reviews'] = [r.get_json(me=u) for r in reviews]
    else:
        result['result'] = '0'

    return JSONHttpResponse(result)


@csrf_exempt
@login_required
def wish_people(request):
    """
        List of people who wish this item

        :url: /m/wish/people/

        :param POST['sku']: product sku
        :param POST['lat']: latitude
        :param POST['lon']: longitude

        :rtype: JSON

        ::

            {
              "wishes": [
                {
                  "wish_id": "5", 
                  "comment": "This is awesome", 
                  "added": "1273123731.0", 
                  "fulfilled": "False", 
                  "new_reviews": "0", 
                  "party": {
                    "first_name": "Ben", 
                    "last_name": "Viralington", 
                    "name": "Ben", 
                    "alias": "ben.viralington", 
                    "image": "", 
                    "phone": "", 
                    "first_joined": "1273123721.0", 
                    "id": "3"
                  }, 
                  "max_price": "100.00"
                }
              ]
            }    

    """
    result = {}

    u = request.user

    if u.experiment.id in [2,4]:
        my_friends = u.friends()
        logger.debug("Finding friends who wish this %s: %s"%(u,my_friends))
        wishes = Wishlist.objects.filter(product__sku=int(request.POST['sku']), party__in=my_friends)
        result['wishes'] = [w.get_json(me=u) for w in wishes]
    else:
        wishes = Wishlist.objects.filter(product__sku=int(request.POST['sku']))
        result['wishes'] = [w.get_json(me=u) for w in wishes]

    return JSONHttpResponse(result)



