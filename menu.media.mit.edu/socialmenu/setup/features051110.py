from legals.models import MenuItem, Category, ChefChoice

try:
    m = MenuItem.objects.get(name="Baked Cape Cod Oysters")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Grilled Atlantic Salmon III")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Lobster and Crabmeat Saute")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass


c, created = Category.objects.get_or_create(name="Features")

try:
    m = MenuItem.objects.get(name="Baked NY/NJ Oysters")    
    m.description="Appetizer; NY/NJ oysters baked with a savory cornbread and chorizo stuffing"
    m.price=13.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Baked NY/NJ Oysters", description="Appetizer; NY/NJ oysters baked with a savory cornbread and chorizo stuffing", price=13.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Grilled Atlantic Salmon IV")    
    m.description="Bacon wrapped shrimp, mango-chili butter, white rice"
    m.price=27.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Grilled Atlantic Salmon IV", description="Bacon wrapped shrimp, mango-chili butter, white rice", price=27.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Lobster Saute")    
    m.description="Fresh shucked lobster meat, spinach, mushrooms, tomatoes and linguini tossed in a sherry-cream sauce"
    m.price=29.50
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Lobster Saute", description="Fresh shucked lobster meat, spinach, mushrooms, tomatoes and linguini tossed in a sherry-cream sauce", price=29.50, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Angel Food Cake")    
    m.description="Dessert; angel food cake topped with a mixed berry compote and home made whipped cream" 
    m.price=4.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Angel Food Cake", description="Dessert; angel food cake topped with a mixed berry compote and home made whipped cream", price=4.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

