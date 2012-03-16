from legals.models import MenuItem, Category, ChefChoice

try:
    m = MenuItem.objects.get(name="Chilled Seafood Cocktail")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Grilled Atlantic Salmon")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Seafood Saute")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Duo of Mousse")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass


c, created = Category.objects.get_or_create(name="Features")

try:
    m = MenuItem.objects.get(name="Mint Julep")    
    m.description="Cocktail; Maker's Mark Bourbon, muddled mint, sugar"
    m.price=9.25
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Mint Julep", description="Cocktail; Maker's Mark Bourbon, muddled mint, sugar", price=9.25, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Chilled Lobster Cocktail")    
    m.description="Appetizer; fresh shucked lobster meat, avocado and tomato salsa, tortilla strips"
    m.price=12.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Chilled Lobster Cocktail", description="Appetizer; fresh shucked lobster meat, avocado and tomato salsa, tortilla strips", price=12.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Grilled Atlantic Salmon II")    
    m.description="Pear and raisin compote, crispy wild rice cake, roasted asparagus"
    m.price=23.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Grilled Atlantic Salmon II", description="Pear and raisin compote, crispy wild rice cake, roasted asparagus", price=23.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Fresh Fruit Parfait")    
    m.description="Dessert; raspberries, strawberries and blueberries layered with homemade whipped cream topped with granola"
    m.price=4.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Fresh Fruit Parfait", description="Dessert; raspberries, strawberries and blueberries layered with homemade whipped cream topped with granola", price=4.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

