from legals.models import Order, MenuItem, MenuItemReview, TableCode, Experiment
from django.contrib.auth.models import User
import datetime

e = Experiment.objects.get(id=1)
t = TableCode(code='abcd', experiment = e, date=datetime.date.today())
t.save()

t = TableCode.objects.filter(code='abcd')[0]

michael = User.objects.get(id=2)
o = Order(user=michael, table=t)
o.save()

# these items have a price that is not fixed
for i in [59,52]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=5, comment="This was soo delicious")
    r.save()
    o.items.add(r)
o.save()

o = Order(user=michael, table=t)
o.save()

for i in [25,15,45]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=5, comment="This was soo delicious")
    r.save()
    o.items.add(r)
o.save()

o = Order(user=michael, table=t)
o.save()

for i in [26,16,46]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=3, comment="This was kind of mediocre")
    r.save()
    o.items.add(r)
o.save()

kwan = User.objects.get(id=2)
o = Order(user=kwan, table=t)
o.save()

for i in [21,13]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=5, comment="This was soo delicious")
    r.save()
    o.items.add(r)
o.save()

o = Order(user=kwan, table=t)
o.save()

for i in [28,18,43]:
    m = MenuItem.objects.get(id=i)
    r = MenuItemReview(item=m, rating=1, comment="This was soo crappy")
    r.save()
    o.items.add(r)
o.save()


