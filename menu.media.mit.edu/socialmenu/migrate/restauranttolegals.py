import restaurant
from legals.models import Store, Category, MenuItem, OptionPrice

s = restaurant.models.Store.objects.get(id=1)
s_new = Store(name=s.name, address=s.address, city=s.city, state=s.state, phone=s.phone)
s_new.save()

cats = restaurant.models.Category.objects.filter(store=s)
for c in cats:
    newc = Category(name=c.name, description=c.description)
    newc.save()
    # get old items
    items = c.menuitem_set.all()
    for i in items:
        # create new items
        m = MenuItem(name=i.name, price=i.price, description=i.description,
                    category=newc)
        m.save()
        # if it has multiple price
        if i.price == -2:
            p = i.optionprice_set.all()[0]
            o = OptionPrice(item=m, option_one=p.option_one, 
                    price_one=p.price_one, option_two=p.option_two,
                    price_two=p.price_two)
            o.save()
