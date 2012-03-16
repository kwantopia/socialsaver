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
    m = MenuItem.objects.get(name="Jack Rose")    
    m.description="Cocktail; Lairds Applejack, fresh lemon juice, housemade grenadine, Peychauds bitters"
    m.price=8.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Jack Rose", description="Cocktail; Lairds Applejack, fresh lemon juice, housemade grenadine, Peychauds bitters", price=8.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Shrimp Caprese Salad")    
    m.description="Appetizer; Prosciutto wrapped shrimp, yellow & red tomatoes, fresh mozzarella cheese, basil oil"
    m.price=13.50
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Shrimp Caprese Salad", description="Appetizer; Prosciutto wrapped shrimp, yellow & red tomatoes, fresh mozzarella cheese, basil oil", price=13.50, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Grilled Halibut Steak")    
    m.description="8 oz. bone-in halibut steak, roasted mushroom and arugula salad, crispy sweet potato shoestrings, scallion buerre blanc"
    m.price=27.95
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Grilled Halibut Steak", description="8 oz. bone-in halibut steak, roasted mushroom and arugula salad, crispy sweet potato shoestrings, scallion buerre blanc", price=27.95, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

try:
    m = MenuItem.objects.get(name="Mixed Berry Crepes")    
    m.description="Dessert; Raspberries, blueberries, strawberries wrapped in a crepe topped with powdered sugar" 
    m.price=6.50
    m.category = c
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem(name="Mixed Berry Crepes", description="Dessert; Raspberries, blueberries, strawberries wrapped in a crepe topped with powdered sugar", price=6.50, category=c)
    m.save()

f, created = ChefChoice.objects.get_or_create(item=m)
f.save()

