from legals.models import MenuItem, Category, OptionPrice

##########################################
# For updating to latest menu on 5/20/10
##########################################

m = MenuItem.objects.get(name="Atlantic Salmon")
m.price = 23.50
m.save()

m = MenuItem.objects.get(name="Arctic Char")
m.active = False
m.save()

m = MenuItem.objects.get(name="Rainbow Trout")
m.price = 18.50 
m.save()

m = MenuItem.objects.get(name="Shrimp")
m.price = 20.50
m.save()

m = MenuItem.objects.get(name="Sea Scallops")
m.price = 23.50
m.save()

m = MenuItem.objects.get(name="Haddock")
m.price = 19.95 
m.save()

c = Category.objects.get(name="Legal Classic Dinners")
m = MenuItem.objects.get(name="New England Fried Clams", category=c)
m.price = 21.95 
m.save()

m = MenuItem.objects.get(name="Shrimp and Garlic")
m.price = 20.50 
m.save()

m = MenuItem.objects.get(name="Jasmine Special")
m.price = 20.50 
m.save()

m = MenuItem.objects.get(name="Gazpacho")
m.active = True 
m.save()
o = OptionPrice.objects.get(item=m)
o.price_one = 4.75
o.price_two = 6.75 
o.save()

m = MenuItem.objects.get(name="House Salad")
o = OptionPrice.objects.get(item=m)
o.price_one = 5.95 
o.price_two = 7.95 
o.save()

m = MenuItem.objects.get(name="Classic Caesar Salad")
o = OptionPrice.objects.get(item=m)
o.price_one = 5.95 
o.price_two = 7.95 
o.save()

m = MenuItem.objects.get(name="Chopped Greek Salad")
o = OptionPrice.objects.get(item=m)
o.price_one = 6.95 
o.price_two = 8.95 
o.save()

c = Category.objects.get(name="Chowders, Soups, and Salads")
m, created = MenuItem.objects.get_or_create(name="Tortilla, Apple and Goat Cheese Salad", price=-2, description="chopped avocado, roasted red peppers and chipotle orange dressing", category=c)
o, created = OptionPrice.objects.get_or_create(item=m, option_one="half", price_one=6.95, option_two="full", price_two=8.95)

#m = MenuItem.objects.get(name="Legal's Signature Crab Cake")
m = MenuItem.objects.get(id=65)
m.price = 14.95
m.save()

m = MenuItem.objects.get(name="Shrimp Wontons")
m.price = 9.95
m.save()

c = Category.objects.get(name="Surf, Turf and Beyond")
m, created = MenuItem.objects.get_or_create(name = "Surf and Turf", description="8 oz. filet, bearnaise butter and choice of two sides, three double stuffed baked shrimp", price=37.95, category=c)

m = MenuItem.objects.get(name="Filet Mignon 8 oz.")
m.price = 29.95
m.save()

m = MenuItem.objects.get(name="Oven Roasted Herbed Chicken")
m.price = 19.50
m.category = c 
m.save()

c = Category.objects.get(name="Completely Legal")
m, created = MenuItem.objects.get_or_create(name = "Crispy Tempura Soft Shell Crabs", description="sticky rice, edamame carrot salad and mango chili dipping sauce", price=24.95, category=c)

m = MenuItem.objects.get(name="Oven Roasted Herbed Chicken")
m.category = c 
m.save()

m, created = MenuItem.objects.get_or_create(name = "Crispy Tempura Soft Shell Crabs", description="sticky rice, edamame carrot salad and mango chili dipping sauce", price=24.95, category=c)

m = MenuItem.objects.get(name="Steamed Jumbo Snow Crab Legs")
m.active = True 
m.save()

m = MenuItem.objects.get(name="Nutty Atlantic Salmon")
m.price = 24.50
m.save()

m = MenuItem.objects.get(name="Lemon Caper Grey Sole")
m.price = 21.95 
m.save()


