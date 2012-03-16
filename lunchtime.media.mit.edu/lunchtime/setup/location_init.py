from common.models import Location
from techcash.models import TechCashTransaction
import httplib, json

# merge laverde transactions
first_laverde = Location.objects.get(id=11)
for t in TechCashTransaction.objects.filter(location__id = 38):
    t.location = first_laverde
    t.save()

# store location types
locs = Location.objects.filter(name__iregex=r'[\w# ]+(wash|washer|dryer|dyer)[\w# ]*')

for l in locs:
    l.type = 1 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]*(card)[\w# ]+')

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]+(library)[\w# ]+')

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="pocket reader")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="hair")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="meal reset")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="technicuts")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="omega")

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__icontains="awards")

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__icontains="library")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="alumni")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="copier")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="meal reset")

for l in locs:
    l.type = 2 
    l.save()


locs = Location.objects.filter(name__icontains="hardware")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="terminal")

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__icontains="work")

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__icontains="kendall")

for l in locs:
    l.type = 3 
    l.save()



locs = Location.objects.filter(name__icontains="copytech")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="student art")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="museum")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="parking")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="transportation")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="student group")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__icontains="help desk")

for l in locs:
    l.type = 2 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]+(transfer)[\w# ]*')

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__iregex=r'[\w# ]+(payroll)[\w# ]+')

for l in locs:
    l.type = 4 
    l.save()

locs = Location.objects.filter(name__iregex=r'BLDG [\w# ]+')

for l in locs:
    l.type = 5 
    l.save()


def get_latlong(name):
    # special cases
    if name=="Domino":
        lat = 42.369388
        lon = -71.091156 
    elif name=="Quiznos":
        lat = 42.363015
        lon = -71.093216 
    elif name=="Starbucks":
        name='32'
        # retrieve latest transactions
        h = httplib.HTTPConnection('mobile-stage.mit.edu')
        h.request('GET', '/api/map/?command=search&q=%s'%name)
        r = h.getresponse()
        building_info = json.loads(r.read())
        if len(building_info) > 0:
            lat = building_info[0]["lat_wgs84"]
            lon = building_info[0]["long_wgs84"]
        else:
            lat = 42.365361
            lon = -71.098716
    else:
        # retrieve latest transactions
        h = httplib.HTTPConnection('mobile-stage.mit.edu')
        h.request('GET', '/api/map/?command=search&q=%s'%name)
        r = h.getresponse()
        building_info = json.loads(r.read())
        if len(building_info) > 0:
            lat = building_info[0]["lat_wgs84"]
            lon = building_info[0]["long_wgs84"]
        else:
            lat = 42.365361
            lon = -71.098716

    return (lat, lon)

"""
# store image URL's
TECHCASH_MEDIA_URL = "http://mealtime.mit.edu/media/techcash/"

locs = Location.objects.all()
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"default_icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"restaurant_banner.png"
    l.save()

locs = Location.objects.filter(name__icontains="BLDG")
coord = get_latlong("10")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Vending-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Vending-Machines.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()


locs = Location.objects.filter(name__icontains="Anna's")
coord = get_latlong("Anna's")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Annas-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Annas.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Au Bon Pain")
coord = get_latlong("Au Bon Pain")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Au-Bon-Pain-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Au-Bon-Pain.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="AuBonPain")
coord = get_latlong("AuBonPain")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Au-Bon-Pain-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Au-Bon-Pain.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()


locs = Location.objects.filter(name__icontains="Baker Dining")
coord = get_latlong("Baker Dining")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Baker-House-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Baker-House-Plan.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Bio")
coord = get_latlong("Bio Cafe")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Bio-Cafe-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Bio-Cafe.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Bosworths")
coord = get_latlong("Bosworths")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Bosworths-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Bosworths.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Spice")
coord = get_latlong("Cafe Spice")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Cafe-Spice-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Cafe-Spice.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Cambridge")
coord = get_latlong("Cambridge Grill")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Cambridge-Grill-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Cambridge-Grill.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Domino")
coord = get_latlong("Domino")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Dominos-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Dominos.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()


locs = Location.objects.filter(name__icontains="Dunkin")
coord = get_latlong("Dunkin")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Dunkin-Donuts-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Dunkin-Donuts.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Faculty")
coord = get_latlong("Faculty Lunch")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Faculty-Lunch-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Faculty-Lunch.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Forbes")
coord = get_latlong("Forbes Family")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Forbes-Family-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Forbes-Family.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="verde")
coord = get_latlong("La Verdes")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"LaVerdes-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"LaVerdes.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="macgregor")
coord = get_latlong("MacGregor")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"MacGregor-Convenience-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"MacGregor-Convenience.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="convenience")
coord = get_latlong("MacGregor")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"MacGregor-Convenience-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"MacGregor-Convenience.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="mccormick")
coord = get_latlong("McCormick")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"McCormick-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"McCormick.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="next")
coord = get_latlong("Next House Dining")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Next-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Next.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Street")
coord = get_latlong("Pac Street Cafe")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Pac-Street-Cafe-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Pac-Street-Cafe.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Pacific")
coord = get_latlong("Pac Street Cafe")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Pac-Street-Cafe-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Pac-Street-Cafe.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Papa")
coord = get_latlong("Papa Johns")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Papa-Johns-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Papa-Johns.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Quizno")
coord = get_latlong("Quiznos")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Quiznos-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Quiznos.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Pub")
coord = get_latlong("R&D Pub")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"RD-Pub-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"RD-Pub.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Refresher")
coord = get_latlong("Refresher")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Refresher-Course-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Refresher-Course.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Sepal")
coord = get_latlong("Sepal")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Sepal-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Sepal.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Shinkansen")
coord = get_latlong("Shinkansen")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Shinkansen-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Shinkansen.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Simmons")
coord = get_latlong("Simmons Dining")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Simmons-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Simmons-House-Dining.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Starbucks")
coord = get_latlong("Starbucks")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Starbucks-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Starbucks.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Steam")
coord = get_latlong("Steam")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Steam-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Steam.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Subway")
coord = get_latlong("Subway")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Subway-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Subway.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Thirsty")
coord = get_latlong("Thirsty Ear")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Thirsty-Ear-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Thirsty-Ear.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Vending")
coord = get_latlong("Vending Machines")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Vending-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Vending-Machines.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Zigo")
coord = get_latlong("Zigo")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Zigo-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Zigo.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="4 Coffee")
coord = get_latlong("Cafe 4")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Cafe-Four-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Cafe-Four.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

locs = Location.objects.filter(name__icontains="Nightly")
coord = get_latlong("Nightly Meal")
for l in locs:
    l.icon = TECHCASH_MEDIA_URL+"Nightly-Meal-Reset-Icon.png" 
    l.banner = TECHCASH_MEDIA_URL+"Nightly-Meal-Reset.png"
    l.latitude = coord[0] 
    l.longitude = coord[1] 
    l.save()

"""
