from legals.models import MenuItem, Category, ChefChoice

try:
    m = MenuItem.objects.get(name="Baked NY/NJ Oysters")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Grilled Atlantic Salmon IV")    
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Lobster Saute")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass

try:
    m = MenuItem.objects.get(name="Angel Food Cake")
    m.active=False
    m.save()
except MenuItem.DoesNotExist:
    pass


c, created = Category.objects.get_or_create(name="Features")

try:
    m = MenuItem.objects.get(name="Thai Daiquiri")    
    m.description="Cocktail; Malibu Banana, Domaine de Canton, lime cordial, lemongrass and pasturized egg white"
    m.price=9.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Thai Daiquiri", description="Appetizer; Malibu Banana, Domaine de Canton, lime cordial, lemongrass and pasturized egg white", price=9.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Lobster Stuffed Mushroom")    
    m.description="Appetizer; Fresh shucked lobster meat, goat, cheese, apple-smoked bacon, watercress salad, balsamic reduction"
    m.price=8.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Lobster Stuffed Mushroom", description="Appetizer; Fresh shucked lobster meat, goat, cheese, apple-smoked bacon, watercress salad, balsamic reduction", price=8.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Grilled Tuna and Shrimp")    
    m.description="Jalapeno pepper relish, green beans, cornbread panzanella salad"
    m.price=27.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Grilled Tuna and Shrimp", description="Jalapeno pepper relish, green beans, cornbread panzanella salad", price=27.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Haitian Rum Creme Brulee")    
    m.description="Dessert; Housemade creme brulee infused with Haitian Rum" 
    m.price=4.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Haitian Rum Creme Brulee", description="Dessert; Housemade creme brulee infused with Haitian Rum", price=4.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

