# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from common.helpers import JSONHttpResponse

import xml.parsers.expat

current_category = None 
current_store = None

def strip_dollar(str):
    if str[0] == '$':
        return str[1:]
    else:
        return str

def option_prices(str):
    prices = str.split(' ')
    return prices

def start_element_legals(name, attrs):
    from legals.models import Category, MenuItem, Store, OptionPrice 
    global current_category, current_store
    print 'Start element:', name, attrs
    if name == 'item':
        # store menu item
        detail = option_prices(attrs['price'])
        if 'market' in attrs['price'].lower(): 
            m = MenuItem(name=attrs['name'], 
                    price=-1,
                    description=attrs['description'], 
                    category=current_category)
            m.save()
        elif len(detail)>1:
            m = MenuItem(name=attrs['name'],
                    price=-2,
                    description=attrs['description'],
                    category=current_category)
            m.save()
            o = OptionPrice(item=m, option_one=detail[0],
                                    price_one=detail[1],
                                    option_two=detail[2],
                                    price_two=detail[3])
            o.save()
        else:
            m = MenuItem(name=attrs['name'], 
                    price=strip_dollar(attrs['price']),
                    description=attrs['description'], 
                    category=current_category)
            m.save()
    elif name == 'category':
        #  category
        # create category
        c = Category(name=attrs['name'])
        if 'description' in attrs:
            c.description=attrs['description']
        c.store = current_store
        c.save() 
        current_category = c
    elif name == 'menu':
        s = Store(name=attrs['store'], store_category=StoreCategory.objects.get(name='Restaurant'))
        s.save()
        current_store = s

def start_element_mit(name, attrs):
    from mitdining.models import Category, MenuItem, Store, OptionPrice, StoreCategory
    global current_category, current_store
    print 'Start element:', name, attrs
    if name == 'item':
        # store menu item
        detail = option_prices(attrs['price'])
        if 'market' in attrs['price'].lower(): 
            m = MenuItem(name=attrs['name'], 
                    price=-1,
                    description=attrs['description'], 
                    category=current_category)
            m.save()
        elif len(detail)>1:
            m = MenuItem(name=attrs['name'],
                    price=-2,
                    description=attrs['description'],
                    category=current_category)
            m.save()
            o = OptionPrice(item=m, option_one=detail[0],
                                    price_one=detail[1],
                                    option_two=detail[2],
                                    price_two=detail[3])
            o.save()
        else:
            m = MenuItem(name=attrs['name'], 
                    price=strip_dollar(attrs['price']),
                    description=attrs['description'], 
                    category=current_category)
            m.save()
    elif name == 'category':
        #  category
        # create category
        c = Category(name=attrs['name'])
        if 'description' in attrs:
            c.description=attrs['description']
        c.store = current_store
        c.save() 
        current_category = c
    elif name == 'menu':
        s = Store(name=attrs['store'], store_category=StoreCategory.objects.get(name='House Dining'))
        s.save()
        current_store = s

def end_element(name):
    print 'End element:', name

def char_data(data):
    print 'Character data:', repr(data)

def init_legals_menu(request):
    """
        Populates database from the XML data
       
        :url: /restaurant/init/legals/
        
    """
    p = xml.parsers.expat.ParserCreate()

    p.StartElementHandler = start_element_legals
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data

    xmlfile = open('/home/kwan/Documents/OTNWeb/socialmenu/data/legals_menu.xml', 'r')
    p.ParseFile(xmlfile)

    result = "The Legal's menu was successfully stored into database"
    return render_to_response('restaurant/status.html', {'status':result})

def init_mit_menu(request):
    """
        Populates database from the XML data
       
        :url: /restaurant/init/mit/
        
    """
    p = xml.parsers.expat.ParserCreate()

    p.StartElementHandler = start_element_mit
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data

    xmlfile = open('/home/kwan/Documents/OTNWeb/socialmenu/data/mit_menu.xml', 'r')
    p.ParseFile(xmlfile)

    result = "The MIT menu was successfully stored into database"
    return render_to_response('restaurant/status.html', {'status':result})

def init_store_categories(request):
    """
        :url: /restaurant/init/store/categories/
    """
    
    from mitdining.models import StoreCategory
    cats = ['Restaurant', 'House Dining', 'Trucks', 'Campus']
    for c in cats:
        s = StoreCategory(name=c)
        s.save()

    result = "Successfully stored categories"
    return render_to_response('restaurant/status.html', {'status':result})

