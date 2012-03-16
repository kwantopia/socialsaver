from legals.models import MenuItem, Category, ChefChoice

try:
    m = MenuItem.objects.get(name="Thai Daiquiri")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Lobster Stuffed Mushroom")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Grilled Tuna and Shrimp")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Haitian Rum Creme Brulee")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass


c, created = Category.objects.get_or_create(name="Features")

try:
    m = MenuItem.objects.get(name="Original Sin")    
    m.description="Cocktail; Absolut Mandrin, botanicals, muddled orange, fresh lemon juice, cinnamon syrup"
    m.price=8.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Original Sin", description="Cocktail; Absolut Mandrin, botanicals, muddled orange, fresh lemon juice, cinnamon syrup", price=8.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Pink Tuna Au Poivre")    
    m.description="Appetizer; Pickled beet, radish and cucumber salad, mango puree"
    m.price=13.50
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Pink Tuna Au Poivre", description="Appetizer; Pickled beet, radish and cucumber salad, mango puree", price=13.50, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Wild Alaskan Copper River Keta Salmon")    
    m.description="Horseradish crusted, apple & fennel potato cake, green beans, sugarcane shrimp skewer"
    m.price=27.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Wild Alaskan Copper River Keta Salmon", description="Horseradish crusted, apple & fennel potato cake, green beans, sugarcane shrimp skewer", price=27.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Peanut Butter Oreo Pie")    
    m.description="Dessert; House made peanut butter mousse in an Oreo pie crust" 
    m.price=6.50
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Peanut Butter Oreo Pie", description="Dessert; House made peanut butter mousse in an Oreo pie crust", price=6.50, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

