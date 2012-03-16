from common.models import Location
import json

"""
    Get all the lat/lon coordinates
"""
import httplib

# retrieve latest transactions
h = httplib.HTTPConnection('mobile-stage.mit.edu')

buildings = ['32', 'E51', 'E52']
for b in buildings:
    h.request('GET', '/api/map/?command=search&q=%s'%b)
    r = h.getresponse()
    building_info = json.loads(r.read())
    lat = building_info[0]["lat_wgs84"]
    lon = building_info[0]["long_wgs84"]
    places = building_info[0]["contents"]
    for p in places:
        category = p.get("category", None)
        if category:
            if "food" in category or "coffee" in category:
                eatery_name = p["name"]
                eatery_split = eatery_name.split(" ")
                # put lat/lon for eatery
                # how do you match?
                locs = Location.objects.filter(name__iregex=r'^%s'%eatery_split[0])
                for l in locs:
                    print "%s matches: %s"%(eatery_name, l.name)



