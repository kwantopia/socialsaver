from legals.models import MenuItem, Category, ChefChoice

try:
    m = MenuItem.objects.get(name="Mint Julep")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Chilled Lobster Cocktail")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Grilled Atlantic Salmon II")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Fresh Fruit Parfait")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass


