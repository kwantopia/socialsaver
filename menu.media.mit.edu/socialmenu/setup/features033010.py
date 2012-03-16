from legals.models import MenuItem, Category, ChefChoice

c, created = Category.objects.get_or_create(name="Features")
try:
    m = MenuItem.objects.get(name="Lobster Arancini")    
    m.description="with vanilla truffle vinaigrette"
    m.price=10.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Lobster Arancini", description="with vanilla truffle vinaigrette", price=10.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Grilled Salmon")    
    m.description="Sauteed gnocchi with olives, asparagus, roasted tomato and shallot reduction, shaved Romano"
    m.price=23.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Grilled Salmon", description="Sauteed gnocchi with olives, asparagus, roasted tomato and shallot reduction, shaved Romano", price=23.95, category=c)
    m.save()


f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="New England 3 Course Lobster Lover")
    m.description = "Cup of clam chowder; 1.5# lobster and 2 sides; Haitian bread pudding"
    m.price = 39.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="New England 3 Course Lobster Lover", description = "Cup of clam chowder; 1.5# lobster and 2 sides; Haitian bread pudding", price = 39.95, category = c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Strawberry Rhubarb Crumble")
    m.price = 4.95
    m.description = "Dessert"
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Strawberry Rhubarb Crumble", price=4.95, category=c)
    m.description = "Dessert"
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

