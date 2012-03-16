from legals.models import MenuItem, Category, ChefChoice

try:
    m = MenuItem.objects.get(name="Grilled Halibut Steak Three Course Dinner")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

c, created = Category.objects.get_or_create(name="Features")

try:
    m = MenuItem.objects.get(name="Grilled Swordfish")    
    m.description="Mango-chili butter, grilled corn on the cob, red bliss potato salad"
    m.price=26.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Grilled Swordfish", description="Mango-chili butter, grilled corn on the cob, red bliss potato salad", price=26.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Cherry Tomato Salad")    
    m.description="Summer cherry tomato salad"
    m.price=6.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Cherry Tomato Salad", description="Summer cherry tomato salad", price=6.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

