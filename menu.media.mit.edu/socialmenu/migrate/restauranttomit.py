import restaurant
from mitdining.models import StoreCategory, Store, Category, MenuItem, OptionPrice

sc = restaurant.models.StoreCategory.objects.all()
for c in sc:
    s = StoreCategory(name=c.name)
    s.save()

mit = restaurant.models.Store.objects.get(id=2)
sc = StoreCategory.objects.get(name='House Dining')
c = restaurant.models.Category.objects.filter(store=mit)
for s in c:
    s_new = Store(name=s.name, store_category=sc)
    s_new.save()
    cat = Category(name='Default', description='For all menu', store=s_new)
    cat.save()
    items = s.menuitem_set.all()
    for i in items:
        m = MenuItem(name=i.name, price=i.price, description=i.description,
                    category=cat)
        m.save()
