from legals.models import MenuItem, Category, OptionPrice

##########################################
# For updating to latest menu on 2/20/10
##########################################

m = MenuItem.objects.get(name="Legal Experience")
m.price = 25.95
m.save()

c = Category.objects.get(name="Appetizers")
m = MenuItem.objects.filter(name__contains="Signature Crab Cake").filter(category=c)
m[0].description = "jumbo lump crab, mustard sauce, seasonal salad (contains nuts)"
m[0].save()

c = Category.objects.get(name="Appetizers")
m = MenuItem.objects.filter(name="New England Fried Clams").filter(category=c)
m[0].price = 13.95
m[0].save()

m = MenuItem.objects.get(name="Shrimp Wontons")
m.price = 9.50
m.save()

m = MenuItem.objects.get(name="New England Clam Chowder")
o = OptionPrice.objects.get(item=m)
o.price_one = 4.75
o.price_two = 6.75
o.save()

m = MenuItem.objects.get(name="Lite Clam Chowder")
o = OptionPrice.objects.get(item=m)
o.price_one = 4.75
o.price_two = 6.75
o.save()

m = MenuItem.objects.get(name="Fish Chowder")
o = OptionPrice.objects.get(item=m)
o.price_one = 4.75
o.price_two = 6.75
o.save()

m = MenuItem.objects.get(name="Gazpacho")
m.description = ""
m.active = False
m.save()

m = MenuItem.objects.get(name="Atlantic Salmon")
m.description = "choice of two sides"
m.price = 22.50
m.save()

m = MenuItem.objects.get(name="Atlantic Salmon Crispy Fried")
m.description = "choice of two sides"
m.active = False
m.price = 22.50
m.save()

m = MenuItem.objects.get(name="Swordfish")
m.description = "10 oz. center prime cut; tested for purity; choice of two sides"
m.save()

m = MenuItem.objects.get(name="Wild Salmon")
m.description = "choice of two sides"
m.active = False
m.save()

m = MenuItem.objects.get(name="Tuna")
m.description = "cooked medium rare; tested for purity; choice of two sides"
m.price = 25.95 
m.save()

m = MenuItem.objects.get(name="Rainbow Trout")
m.price = 17.95 
m.description = "10 oz.; choice of two sides"
m.save()

m = MenuItem.objects.get(name="Barramundi")
m.active = False
m.save()

c = Category.objects.get(name="Fish")
try:
    MenuItem.objects.get(name="Mahi Mahi")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Mahi Mahi", description="also available crispy fried; choice of two sides", price=22.95, category=c)
    m.save()

m = MenuItem.objects.get(name="Shrimp")
m.description = "choice of two sides"
m.save()

m = MenuItem.objects.get(name="Sea Scallops")
m.description = "choice of two sides"
m.save()

m = MenuItem.objects.get(name="Haddock")
m.description = "choice of two sides"
m.price = 18.95
m.save()

m = MenuItem.objects.get(name="Bluefish")
m.description = "choice of two sides"
m.save()

m = MenuItem.objects.get(name="Arctic Char")
m.description = "10 oz.; choice of two sides"
m.save()

c = Category.objects.get(name="Legal Classic Dinners")
m = MenuItem.objects.filter(name="New England Fried Clams").filter(category=c)
m[0].price = 20.95
m[0].save()

m = MenuItem.objects.get(name="Fish and Chips")
m.price = 16.95
m.save()

m = MenuItem.objects.get(name__contains="Baked Boston Scrod")
m.price = 19.95
m.save()

m = MenuItem.objects.get(name="Jasmine Special")
m.price = 19.95
m.save()

m = MenuItem.objects.get(name="Jasmine Special with Brown Rice")
m.price = 19.95
m.save()

c = Category.objects.get(name="Legal Lobsters")
try:
    MenuItem.objects.get(name="Baked Stuffed Lobsters")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Baked Stuffed Lobsters", description="$5.00 more than regular lobsters; baked and stuffed with a shrimp and scallop buttery cracker stuffing", price=-1, category=c)
    m.save()

try:
    m = MenuItem.objects.get(name="Cherrystone Twelve Raw Clams")
    m.name = "Cherrystone Raw Clams"
    m.price = -2
    m.save()
except MenuItem.DoesNotExist:
    m = MenuItem.objects.get(name="Cherrystone Raw Clams")
    m.price = -2
    m.save()

try:
    OptionPrice.objects.get(item=m)
except OptionPrice.DoesNotExist:
    o = OptionPrice(item=m, option_one="six", price_one=6.95, option_two="twelve", price_two=11.95)
    o.save()


m = MenuItem.objects.get(name="Littleneck Raw Clams")
o = OptionPrice.objects.get(item=m)
o.price_two = 11.95
o.save()

m = MenuItem.objects.get(name="Jumbo Shrimp Cocktail")
m.price = 13.95
m.save()

m = MenuItem.objects.get(name="Smoked Salmon")
m.price = 12.50
m.save()

m = MenuItem.objects.get(name__contains="Fried Fisherman")
m.price = 24.95
m.save()

m = MenuItem.objects.get(name="Cioppino")
m.price = 26.95
m.save()

m = MenuItem.objects.get(name="Filet Mignon 8 oz.")
m.price = 28.95
m.save()

m = MenuItem.objects.get(name="Oven Roasted Herbed Chicken")
m.description = "sweet potato mashed, broccoli and lemon butter sauce"
m.price = 18.95
m.save()

try:
    c = Category.objects.get(name="Completely Legal")
except Category.DoesNotExist:
    c = Category(name="Completely Legal", description="Chef Inspired Dinners")
    c.save()
try:
    MenuItem.objects.get(name="Legal's Signature Crab Cakes (Combo)")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Legal's Signature Crab Cakes (Combo)", description="one crab cake, grilled shrimp and scallops; jumbo lump crab, mustard sauce, seasaonal salad (contains nuts)", price=26.95, category=c)
    m.save()

try:
    MenuItem.objects.get(name="Legal's Signature Crab Cakes (Dinner)")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Legal's Signature Crab Cakes (Dinner)", description="two crab cakes; jumbo lump crab, mustard sauce, seasaonal salad (contains nuts)", price=27.95, category=c)
    m.save()

try:
    MenuItem.objects.get(name="Double Stuffed Baked Shrimp")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Double Stuffed Baked Shrimp", description="jumbo shrimp, buttery crabmeat stuffing, choice of one side", price=24.95, category=c)
    m.save()

try:
    MenuItem.objects.get(name="Steamed Jumbo Snow Crab Legs")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Steamed Jumbo Snow Crab Legs", description="cornbread, cole slaw and melted butter", price=29.95, category=c)
    m.save()

try:
    MenuItem.objects.get(name="Nutty Atlantic Salmon")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Nutty Atlantic Salmon", description="almond encrusted, sauteed in a lemon caper butter sauce, mushroom ravioli and spinach", price=23.95, category=c)
    m.save()

try:
    MenuItem.objects.get(name="Red Onion Jam Swordfish")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Red Onion Jam Swordfish", description="10 oz. center prime cut, rice pilaf, sauteed sherry mushrooms and spinach", price=26.95, category=c)
    m.save()

try:
    MenuItem.objects.get(name="Everything Tuna")
except MenuItem.DoesNotExist:
    m = MenuItem(name="Everything Tuna", description="grilled with everything spice mix, roasted red pepper and cold cucumber sauce, jasmine rice, spinach (cooked medium rare)", price=25.95, category=c)
    m.save()
