from django.test.client import Client
from legals.models import Category, MenuItem
import random

c = Client()

table_code = "3273"
response = c.post('/legals/m/login/', {'email': 'kool@mit.edu', 
                                    'pin':'5533',
                                    'udid':'fwr42348fwr42348fwr42348fwr42348fwr42348fwr42348fwr42348fwr42348',
                                    'lat':'-42.7823742',
                                    'lon':'74.234141',
                                    'table':table_code}, follow=True)

#response = c.post('/legals/m/login/', {'email': 'dawei@mit.edu', 'pin':'5533',
#                                    'udid':'gwr42348fwr42348fwr42348fwr42348fwr42348fwr42348fwr42348fwr42348',
#                                    'lat':'-42.7823742',
#                                    'lon':'74.234141',
#                                    'table':'abcd'})
print response.redirect_chain
print response

if len(response.redirect_chain) > 0:
    order_id = int(response.redirect_chain[-1][0].split("/")[-2])

    command = '/legals/m/categories/%d/'%order_id
    response = c.post(command, {'e':'e'})
    print command, response

    command = '/legals/m/chef/choices/%d/'%order_id
    response = c.post(command, {'e':'e'})
    print command, response

    for cat in Category.objects.all():
        command = '/legals/m/category/%d/%d/'%(cat.id, order_id)
        response = c.post(command, {'e':'e'})
        print command, response

    # TODO: Test Order page and Order command
    items = MenuItem.objects.all()
    item_list = random.sample(items,10)
    for i in item_list:
        command = '/legals/m/item/%d/%d/'%(i.id, order_id)
        response = c.post(command, {'e':'e'})
        print command, response

"""
#Order for order_id 1

command = '/legals/m/mark/25/%d/'%order_id
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/mark/47/%d/'%order_id
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/mark/3/%d/'%order_id
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/category/6/%d/'%order_id
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/friend/choices/%d/'%order_id
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/myorder/%d/'%order_id
response = c.post(command, {'e':'e'})
print command, response

"""
"""
command = '/legals/m/friend/choices/3/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/categories/28/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/myorder/28/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/categories/28/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/myorder/28/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/mark/47/28/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/unmark/47/28/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/categories/28/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/myorder/28/'
response = c.post(command, {'e':'e'})
print command, response
command = '/legals/m/chef/choices/32/'
response = c.post(command, {'e':'e'})
print command, response

command = '/legals/m/friend/choices/32/'
response = c.post(command, {'e':'e'})
print command, response

"""
"""

response = c.post('/legals/m/order/', {'items':'[25,27,39]', 'table':'abcd'})
print response

from restaurant.models import Order
orders = Order.objects.all()
for o in orders:
    print o

response = c.post('/web/update/comment/', {'review_id':3, 'comment':'This is updated comment'})
print response

response = c.post('/web/update/rating/', {'review_id':3, 'rating':'4'})
print response
"""
