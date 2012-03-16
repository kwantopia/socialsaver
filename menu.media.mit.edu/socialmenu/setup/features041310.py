from legals.models import MenuItem, Category, ChefChoice

try:
    m = MenuItem.objects.get(name="Lobster Arancini")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Grilled Salmon")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="New England 3 Course Lobster Lover")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Strawberry Rhubarb Crumble")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass


c, created = Category.objects.get_or_create(name="Features")

try:
    m = MenuItem.objects.get(name="Chilled Seafood Cocktail")    
    m.description="Appetizer; fresh shrimp, mussels and Jonah; crab tossed with a citrus-chive vinaigrette"
    m.price=12.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Chilled Seafood Cocktail", description="Appetizer; fresh shrimp, mussels and Jonah; crab tossed with a citrus-chive vinaigrette", price=12.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Grilled Atlantic Salmon")    
    m.description="Mint pesto, barley tabbouleh with cucumber, tomato, red onion and chick peas"
    m.price=23.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Grilled Atlantic Salmon", description="Mint pesto, barley tabbouleh with cucumber, tomato, red onion and chick peas", price=23.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Seafood Saute")    
    m.description="Lobster, shrimp, and scallops tossed with fresh vegetables, whole wheat penne and a coconut-curry sauce"
    m.price=26.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Seafood Saute", description="Lobster, shrimp, and scallops tossed with fresh vegetables, whole wheat penne and a coconut-curry sauce", price=26.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Duo of Mousse")    
    m.description="Dessert; raspberry and chocolate mousse served in a chocolate cup with house made whipped cream"
    m.price=4.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Duo of Mousse", description="Dessert; raspberry and chocolate mousse served in a chocolate cup with house made whipped cream", price=4.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()


