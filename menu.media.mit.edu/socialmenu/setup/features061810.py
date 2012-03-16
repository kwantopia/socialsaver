from legals.models import MenuItem, Category, ChefChoice

try:
    m = MenuItem.objects.get(name="Original Sin")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Pink Tuna Au Poivre")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Wild Alaskan Copper River Keta Salmon")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Peanut Butter Oreo Pie")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass


c, created = Category.objects.get_or_create(name="Features")

try:
    m = MenuItem.objects.get(name="Grilled Halibut Steak Three Course Dinner")    
    m.description="First course: Shrimp Caprese Salad; Second course: Grilled Halibut Steak; Third Course: Mixed Berry Crepes"
    m.price=33
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Grilled Halibut Steak Three Course Dinner", description="First course: Shrimp Caprese Salad; Second course: Grilled Halibut Steak; Third Course: Mixed Berry Crepes", price=33, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

