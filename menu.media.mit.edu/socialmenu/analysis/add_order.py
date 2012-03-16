from legals.models import Order, Category, MenuItem, MenuItemReview, EventMenuItem 
from common.models import Experiment, OTNUser
from django.conf import settings
from datetime import datetime
import random

logger = settings.LEGALS_LOGGER

def fix_order( u, d, order_id, item_id):
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
        o.updated = d
        o.save()

    # log mark/order event
    people_ordered = item.menuitemreview_set.all().exclude(legals_ordered__user=u)
    event = EventMenuItem(user=u, 
            order=o,
            experiment=Experiment.objects.get(id=exp_id),
            item=item, 
            action=EventMenuItem.MARK,
            num_people=people_ordered.count())
    event.save()
    event.timestamp = d
    event.save()

def add_consider(u, d, order_id, item_id):
    ord = Order.objects.get(id=order_id)
    exp_id = ord.table.experiment.id 

    # log to events
    item = MenuItem.objects.get(id=int(item_id))
    o = Order.objects.get(id=order_id)

    # log consider event
    people_ordered = item.menuitemreview_set.all().exclude(legals_ordered__user=u)
    event = EventMenuItem(user=u, 
            order=o,
            experiment=Experiment.objects.get(id=exp_id),
            item=item, 
            action=EventMenuItem.CONSIDER,
            num_people=people_ordered.count())
    event.save()
    event.timestamp = d
    event.save()

def list_user_events(u):
    for e in EventMenuItem.objects.filter(user=u):
        print e.item, e.item.id, e.order, e.order.id

def fix_stephanie_lam():
    # Stephanie Lam OTNUser ID = 409
    u = OTNUser.objects.get(my_email="theasianhobbit@berkeley.edu")
    # baked stuffed lobster (75)
    # baked potato (2)
    # jalapeno cheddar polenta (11)
    d = datetime(2010, 8, 30, 19, 46, 59)
    fix_order(u, d, 452, 75)

    d = datetime(2010, 8, 30, 19, 47, 11)
    fix_order(u, d, 452, 75)

    d = datetime(2010, 8, 30, 19, 47, 23)
    fix_order(u, d, 452, 11)

def fix_christine_lee():
    # Christine Lee OTNUser ID = 440 
    u = OTNUser.objects.get(my_email="csl@juilliard.edu")
    # order id = 479
    # steamed lobster (51)
    # mashed potato (1)
    # onion strings (7)
    d = datetime(2010, 9, 8, 18, 29, 34)
    fix_order(u, d, 479, 51)

    d = datetime(2010, 9, 8, 18, 30, 5)
    add_consider(u, d, 479, 1)

    d = datetime(2010, 9, 8, 18, 30, 47)
    fix_order(u, d, 479, 1)

    d = datetime(2010, 9, 8, 18, 31, 25)
    add_consider(u, d, 479, 7)

    d = datetime(2010, 9, 8, 18, 31, 57)
    fix_order(u, d, 479, 7)

def fix_zajacs():
    # Kristin Zajac 
    u = OTNUser.objects.get(my_email="kzajac@sloan.mit.edu")
    # order id = 486
    # Goat Cheese Salad (100)
    d = datetime(2010, 9, 10, 18, 07, 13)
    fix_order(u, d, 486, 100)


    # Biran Zajac
    u = OTNUser.objects.get(my_email="bdzajac@gmail.com")
    # order id = 487
    # Atlantic Salmon (59)
    d = datetime(2010, 9, 10, 18, 07, 58)
    fix_order(u, d, 487, 59)

def fix_multiple_orders():
  """
    Poined by Elenna

    Table: 110
    - Remove order 15 which is a repeat of order 12, user 5 (flag Relogin)
    - Adds item for order 13, user 2
    - Remove order 11

    Table: 222
    - Removes order 361, 362 which is repeat of order 359, user 335 (flag Relogin)
    - Adds item for order 360, user 256

    Table: 180
    - Need to add Baked Stuffed Lobsters to order 188, user 200 

    Table: 241
    - Need to add Red Onion Jam Swordfish for order 306, user 93

    Table: 282
    - Need to add Lemon Caper Grey Sole for order 518, user 465
    
    Table: 294
    - Need to add Legal's Signature Crab Cakes for order 520, user 461

    Table: 132
    - Need to remove order 63, user 2
    - Need to add Lobster Roll to order 65, user 2

    Table: 145
    - Need to add an order for order 113, user 119 (no items ever selected, just categories)

    Table: 179
    - Need to add New England Clam Chowder for order 137, user 154
    - Need to add Snap Peas in Oyster Sauce for order 136, user 81
    - Need to add Haddock to order 135, user 30

    Table: 204
    - Need to remove order 262, user 204
    - Need to remove order 264, user 278

    Table: 245
    - Need to add Vegetarian Box with Shrimp or Scallops for order 304, user 235

    Table: 228
    - Need to add Haddock to order 331, user 256
    - Need to add something random to order 329, user 335
    - Need to add Swordfish to order 328, user 334

    Table: 257
    - Need to remove order 435, user 399
    - Need to add something random to order 436, user 47 (no menu item)
    - Need to remove order 438, user 398
    - Need to remove order 439, user 398 (valid browsing)
    - Need to remove order 443, user 398

  """

  # Table 110
  for o in Order.objects.filter(id__in=[15,11]):
    o.delete()
  
  order_id = 13
  item_id = 53  # Swordfish
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 4, 13, 10, 11, 20)
  fix_order(o.user, d, order_id, item_id)

  # Table 222
  for o in Order.objects.filter(id__in=[361, 362]):
    o.delete()

  order_id = 360
  # select a random item from Legal Classic Dinners
  legal_classic_dinner = Category.objects.get(id=5)
  items = MenuItem.objects.filter(category=legal_classic_dinner)
  item = random.sample(items, 1)[0]
  item_id = item.id 
  o = Order.objects.get(id=order_id) 
  d = datetime(2010, 7, 3, 18, 20, 59)
  add_consider(o.user, d, order_id, item_id)

  d = datetime(2010, 7, 3, 18, 21, 15)
  fix_order(o.user, d, order_id, item_id)

  # Table 180
  order_id = 188
  item_id = 75
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 6, 7, 18, 46, 3)
  fix_order(o.user, d, order_id, item_id)

  # Table 241
  order_id = 306
  item_id = 81
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 6, 26, 20, 17, 48)
  fix_order(o.user, d, order_id, item_id)

  # Table 282
  order_id = 518
  item_id = 83
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 9, 14, 19, 3, 49)
  add_consider(o.user, d, order_id, item_id)
  d = datetime(2010, 9, 14, 19, 3, 55)
  fix_order(o.user, d, order_id, item_id)

  # Table 294
  order_id = 520
  item_id = 76
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 9, 15, 21, 0, 20)
  fix_order(o.user, d, order_id, item_id)

  # Table 132
  o = Order.objects.get(id=63)
  o.delete()
  order_id = 65
  item_id = 45
  d = datetime(2010, 5, 7, 20, 39, 1)
  fix_order(o.user, d, order_id, item_id)

  # Table 145
  surf_turf = Category.objects.get(id=3)
  items = MenuItem.objects.filter(category=surf_turf)
  item = random.sample(items, 1)[0]
  item_id = item.id 
  order_id = 113
  o = Order.objects.get(id=order_id) 
  d = datetime(2010, 5, 23, 17, 52, 20)
  add_consider(o.user, d, order_id, item_id)
  d = datetime(2010, 5, 23, 17, 52, 35)
  fix_order(o.user, d, order_id, item_id)

  # Table 179
  order_id = 137
  item_id = 14
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 5, 27, 18, 45, 25)
  fix_order(o.user, d, order_id, item_id)

  order_id = 136
  item_id = 13
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 5, 27, 18, 43, 15)
  fix_order(o.user, d, order_id, item_id)

  order_id = 135
  item_id = 63
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 5, 27, 18, 50, 10)
  fix_order(o.user, d, order_id, item_id)
  
  item_id = 3
  d = datetime(2010, 5, 27, 18, 51, 9)
  fix_order(o.user, d, order_id, item_id)

  item_id = 13
  d = datetime(2010, 5, 27, 18, 51, 29)
  fix_order(o.user, d, order_id, item_id)

  # Table 204
  o = Order.objects.get(id=262)
  o.delete()
  o = Order.objects.get(id=264)
  o.delete()

  # Table 245
  order_id = 304
  item_id = 30
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 6, 25, 19, 23, 23)
  fix_order(o.user, d, order_id, item_id)

  # Table 228
  order_id = 331
  item_id = 63
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 6, 30, 18, 56, 15)
  fix_order(o.user, d, order_id, item_id)

  order_id = 329
  fish = Category.objects.get(id=7)
  items = MenuItem.objects.filter(category=fish)
  item = random.sample(items, 1)[0]
  item_id = item.id 
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 6, 30, 18, 55, 47)
  add_consider(o.user, d, order_id, item_id)
  d = datetime(2010, 6, 30, 18, 55, 52)
  fix_order(o.user, d, order_id, item_id)

  order_id = 328
  item_id = 53
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 6, 30, 18, 54, 48)
  fix_order(o.user, d, order_id, item_id)

  # Table 257
  for o in Order.objects.filter(id__in=[435, 438, 439, 443]):
    o.delete()

  order_id = 436
  item_id = 66
  o = Order.objects.get(id=order_id)
  d = datetime(2010, 8, 29, 19, 40, 44)
  fix_order(o.user, d, order_id, item_id)




