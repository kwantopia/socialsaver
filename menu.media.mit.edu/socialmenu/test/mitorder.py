from mitdining.models import Order, MenuItem, MenuItemReview
from django.contrib.auth.models import User

# MIT Menu
michael = User.objects.get(id=2)
o = Order(user=michael, table='f6ger')
o.save()

# these items have a price that is not fixed
for i in [1,2]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=5, comment="This was soo delicious")
    r.save()
    o.items.add(r)
o.save()

o = Order(user=michael, table='f6gef')
o.save()

for i in [5]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=5, comment="This was soo delicious")
    r.save()
    o.items.add(r)
o.save()

o = Order(user=michael, table='2rfsr')
o.save()

for i in [12,14]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=3, comment="This was kind of mediocre")
    r.save()
    o.items.add(r)
o.save()

kwan = User.objects.get(id=2)
o = Order(user=kwan, table='bfrt2')
o.save()

for i in [3,4]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=5, comment="This was soo delicious")
    r.save()
    o.items.add(r)
o.save()

o = Order(user=kwan, table='gsrw7')
o.save()

for i in [9,10]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=1, comment="This was soo crappy")
    r.save()
    o.items.add(r)
o.save()

o = Order(user=kwan, table='8srw7')
o.save()

for i in [16]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=1, comment="This was soo soo")
    r.save()
    o.items.add(r)
o.save()




