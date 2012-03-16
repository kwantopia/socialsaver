import keyword
import re
import unittest
import urllib
try:
    import json #Python >= 2.6
except ImportError:
    try:
        import simplejson as json #Python < 2.6
    except ImportError:
        try:
            from django.utils import simplejson as json #Google App Engine
        except ImportError:
            raise ImportError, "Can't load a json library"


DEFAULT_REMIX_HOST = 'api.remix.bestbuy.com'
DEFAULT_REMIX_VERSION = 'v1'

def camel_to_pep8(camel_str):
    pep8_str = camel_str
    if pep8_str:
        pep8_str = re.sub(
            '(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', pep8_str
        ).lower().strip('_')
        if keyword.iskeyword(pep8_str):
            pep8_str += '_' 
    return pep8_str

def pep8_to_camel(pep8_str):
    sp = pep8_str.split('_')
    new_sp = []
    for i, pep8_str in enumerate(sp):
        if i != 0 and pep8_str:
            pep8_str = pep8_str[0].upper() + pep8_str[1:]
        new_sp.append(pep8_str)
    return ''.join(new_sp)


class RemixQueryResults(object):
    name_map = {}
    
    def __init__(
            self, query, query_url, data, api_key,
            url=DEFAULT_REMIX_HOST, version=DEFAULT_REMIX_VERSION,
            pid=None, retry=1,
            *args, **kwargs
        ):
        super(RemixQueryResults, self).__init__(*args, **kwargs)
        self.query = query
        self.query_url = query_url
        self.data = data
        self.api_key = api_key
        self.url = url
        self.version = version
        self.pid = pid
        self.retry = retry
    
    @classmethod
    def get_query_name_attr(cls, query_name):
        return cls.name_map.get(query_name, camel_to_pep8(query_name))
    
    def requery(self, page_delta):
        new_results = None
        if not self.query.lookup_value:
            new_page = self.current_page + page_delta
            if new_page <= self.total_pages and new_page >= 1:
                new_results = self.query.new_query().fetch(
                    self.api_key, url=self.url, version=self.version,
                    page=new_page, pid=self.pid, retry=self.retry
                )
        return new_results
    
    @property
    def next(self):
        return self.requery(1)
    
    @property
    def previous(self):
        return self.requery(-1)
    
    @property
    def canonical_url(self):
        return self.data.get('canonicalUrl', None)
    
    @property
    def query_time(self):
        return self.data.get('queryTime', None)
    
    @property
    def total_time(self):
        return self.data.get('totalTime', None)
    
    @property
    def total(self):
        return self.data.get('total', None)
    
    @property
    def total_pages(self):
        return self.data.get('totalPages', None)
    
    @property
    def current_page(self):
        return self.data.get('currentPage', None)
    
    @property
    def begin(self):
        return self.data.get('from', None)
    
    @property
    def end(self):
        return self.data.get('to', None)
    
    @property
    def error(self):
        return self.data.get('error', None)
    
    @property
    def error_code(self):
        code = None
        error = self.error
        if error:
            code = error.get('code', None)
        return code
    
    @property
    def error_message(self):
        message = None
        error = self.error
        if error:
            message = error.get('message', None)
        return message
    
    @property
    def error_status(self):
        status = None
        error = self.error
        if error:
            status = error.get('status', None)
        return status
    


class StoreQueryResults(RemixQueryResults):
    def __init__(self, query, query_url, data, *args, **kwargs):
        super(StoreQueryResults, self).__init__(
            query, query_url, data, *args, **kwargs
        )
        self.stores = None
        stores_data = self.data.get('stores', None)
        if stores_data is not None:
            self.stores = self.parse(stores_data)
    
    @classmethod
    def parse(cls, data):
        stores = []
        for store_data in data:
            products = None
            attr_data = {}
            for name, value in store_data.items():
                if name == 'products':
                    attr_data['products'] = ProductQueryResults.parse(value)
                else:
                    attr_data[cls.get_query_name_attr(name)] = value
            stores.append(Store(attr_data))
        return stores
    


class ProductQueryResults(RemixQueryResults):
    def __init__(self, query, query_url, data, *args, **kwargs):
        super(ProductQueryResults, self).__init__(
            query, query_url, data, *args, **kwargs
        )
        self.products = None
        products_data = self.data.get('products', None)
        if products_data is not None:
            self.products = self.parse(products_data)
    
    @classmethod
    def parse(cls, data):
        products = []
        for product_data in data:
            stores = None
            attr_data = {}
            for name, value in product_data.items():
                if name == 'stores':
                    attr_data['stores'] = StoreQueryResults.parse(value)
                else:
                    attr_data[cls.get_query_name_attr(name)] = value
            products.append(Product(attr_data))
        return products
    


class RemixQuery(object):
    query_type = 'none'
    query_results_class = RemixQueryResults
    attr_map = {}
    
    def __init__(self, query=None, lookup_value=None, *args, **kwargs):
        super(RemixQuery, self).__init__(*args, **kwargs)
        self.filters = None
        self.lookup_value = None
        self.order_by = None
        self.show_attrs = None
        self.join_query = None
        if query:
            self.lookup_value = query.lookup_value
            if query.filters is not None:
                self.filters = list(query.filters)
            self.order_by = query.order_by
            if query.show_attrs is not None:
                self.show_attrs = list(query.show_attrs)
            if query.join_query:
                self.join_query = query.join_query
        elif lookup_value:
            self.lookup_value = lookup_value
    
    @classmethod
    def get_attr_query_name(cls, attr):
        return cls.attr_map.get(attr, pep8_to_camel(attr))
    
    @classmethod
    def all(cls):
        return cls()
    
    def url(
            self, api_key,
            url=DEFAULT_REMIX_HOST, version=DEFAULT_REMIX_VERSION,
            page=1, pid=None
        ):
        params = []
        fetch_url = "http://%s/%s/" % (url, version)
        if self.lookup_value:
            fetch_url += '%s/%s.json' % (self.query_type, self.lookup_value)
        else:
            fetch_url += self.filter_string
        show_string = self.build_show_string()
        if show_string:
            params.append(('show', show_string))
        if not self.lookup_value:
            sort_string = self.sort_string
            if sort_string:
                params.append(('sort', sort_string))
            if page > 1:
                params.append(('page', str(page)))
            params.append(('format', 'json'))
        params.append(('apiKey', api_key))
        if pid:
            params.append(('PID', pid))
        fetch_url += '?%s' % urllib.urlencode(params)
        return fetch_url
    
    def fetch(
            self, api_key,
            url=DEFAULT_REMIX_HOST, version=DEFAULT_REMIX_VERSION,
            page=1, pid=None, retry=1
        ):
        fetch_url = self.url(
            api_key, url=url, version=version, page=page, pid=pid
        )
        tries = 0
        while (tries < retry):
            try:
                tries += 1
                f = urllib.urlopen(fetch_url)
                m = f.info()
                if not m:
                    raise IOError("No response from server after %s attempt(s)" % tries)
                if m.get('X-Mashery-Error-Code', None):
                    raise IOError("Error returned from server after %s attempt(s): %s" % (tries, m['X-Mashery-Error-Code']))
                content_type = m.get('Content-Type', None)
                if not content_type or ('application/x-javascript' not in content_type):
                    raise IOError("Got an incorrect response type (%s) after %s attempt(s)" % (content_type, tries))
                raw_data = f.read()
                data = json.loads(raw_data)
                break
            except:
                if tries >= retry:
                    raise
        return self.query_results(
            self, fetch_url, data, api_key,
            url=url, version=version, pid=pid, retry=retry
        )
    
    def new_query(self):
        return self.__class__(query=self)
    
    def extend(self, conditional, value):
        return self.filter(conditional, value, extend=True)
    
    def filter(self, conditional, value, extend=False):
        self.lookup_value = None
        new_query = self.new_query()
        conditional_parts = None
        if conditional:
            conditional_parts = conditional.split()
        if conditional_parts and len(conditional_parts) == 2:
            attr = conditional_parts[0]
            oper = conditional_parts[1]
            new_query.append_filter(
                attr, oper, urllib.quote(str(value)), extend
            )
        else:
            raise ValueError('Bad Conditional: %s' % conditional)
        return new_query
    
    def append_filter(self, attr, oper, value, extend=False):
        if self.filters == None:
            self.filters = []
        self.filters.append((attr, oper, value, extend))
    
    def order(self, order_by):
        new_query = self.new_query()
        new_query.order_by = order_by
        return new_query
    
    def show(self, show_attrs):
        new_query = self.new_query()
        new_query.show_attrs = show_attrs
        return new_query
    
    def show_all(self):
        new_query = self.new_query()
        new_query.show_attrs = ['all',]
        return new_query
    
    def show_default(self):
        new_query = self.new_query()
        new_query.show_attrs = None
        return new_query
    
    def join(self, join_query):
        new_query = self.new_query()
        new_query.join_query = join_query
        return new_query
    
    def query_results(
            self, query, query_url, data, api_key,
            url=DEFAULT_REMIX_HOST, version=DEFAULT_REMIX_VERSION,
            pid=None, retry=1
        ):
        if not self.lookup_value:
            return self.query_results_class(
                query, query_url, data, api_key,
                url=url, version=version, pid=pid, retry=retry
            )
        else:
            result = None
            error = data.get('error', None)
            if not error:
                results = self.query_results_class.parse([data,])
                result = results[0]
            return result
    
    def build_show_string(self, prefix=False):
        show_string = ''
        show_attrs = self.show_attrs
        if show_attrs:
            query_names = []
            for attr in show_attrs:
                query_name = self.get_attr_query_name(attr)
                if prefix:
                    query_name = '%s.%s' % (self.query_type, query_name)
                query_names.append(query_name)
            show_string = ','.join(query_names)
        if self.join_query:
            join_show_string = self.join_query.build_show_string(
                prefix=True
            )
            if join_show_string:
                show_string += ',' + join_show_string
        return show_string
    
    @property
    def sort_string(self):
        sort_string = ''
        if self.order_by:
            if self.order_by[0] != '-':
                sort_string = '%s' % self.get_attr_query_name(self.order_by)
            else:
                sort_string = '%s.desc' % self.get_attr_query_name(
                    self.order_by[1:]
                )
        return sort_string
    
    @property
    def filter_string(self):
        filter_string = self.build_filter_string('')
        if filter_string:
            filter_string = '%s(%s)' % (self.query_type, filter_string)
        else:
            filter_string = self.query_type
        if self.join_query:
            if filter_string:
                filter_string += '+'
            filter_string += self.join_query.filter_string
        return filter_string
    
    def build_filter_string(self, filter_string):
        filters = self.filters
        filter_strings = []
        if self.filters:
            if filter_string:
                filter_string += '&'
            for attr, oper, value, extend in self.filters[0:1]:
                filter_string += '%s%s%s' % (
                    self.get_attr_query_name(attr), oper, value
                )
            for attr, oper, value, extend in self.filters[1:]:
                filter_string += ('|' if extend else '&') + '%s%s%s' % (
                    self.get_attr_query_name(attr), oper, value
                )
        return filter_string
    


class StoreQuery(RemixQuery):
    query_type = 'stores'
    query_results_class = StoreQueryResults
    
    def __init__(self, query=None, *args, **kwargs):
        super(StoreQuery, self).__init__(query=query, *args, **kwargs)
        self.area_tuple = None
        self.product_query = None
        if query:
            self.area_tuple = getattr(query, 'area_tuple', None)
    
    def area(self, zip_code, distance):
        new_query = self.new_query()
        new_query.area_tuple = (zip_code, distance)
        return new_query
    
    def products(self, product_query):
        return self.join(product_query)
    
    def build_filter_string(self, filter_string):
        if self.area_tuple:
            if filter_string:
                filter_string += '&'
            filter_string += 'area(%s,%s)' % (
                self.area_tuple[0], self.area_tuple[1]
            )
        return super(StoreQuery, self).build_filter_string(filter_string)
    
    @classmethod
    def id(cls, store_id):
        return StoreQuery(lookup_value=store_id)
    


class ProductQuery(RemixQuery):
    query_type = 'products'
    query_results_class = ProductQueryResults
    
    def __init__(self, query=None, *args, **kwargs):
        super(ProductQuery, self).__init__(query=query, *args, **kwargs)
        self.store_query = None
    
    def stores(self, store_query):
        return self.join(store_query)
    
    @classmethod
    def sku(cls, sku):
        return ProductQuery(lookup_value=sku)
    


class RemixObject(object):
    def __init__(self, data, *args, **kwargs):
        super(RemixObject, self).__init__(*args, **kwargs)
        self.data = data
    
    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError, name
    
    @property
    def attributes(self):
        keys = self.data.keys()
        keys.sort()
        return keys
    


class Store(RemixObject):
    pass


class Product(RemixObject):
    pass


############################################################################
# TESTS
############################################################################
import time
class StoreTest(unittest.TestCase):
    def setUp(self):
        global test_api_key
        self.api_key = test_api_key
        time.sleep(0.25)
    
    def test_query_all(self):
        store_query = StoreQuery.all()
        self.failUnless(store_query)
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores?format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.failUnless(results)
        self.assertEqual(results.query, store_query)
        self.assertEqual(results.query_url, store_query_url)
        self.assertEqual(
            results.canonical_url,
            "/v1/stores?format=json&apiKey=" + self.api_key
        )
        self.assertEqual(results.error, None)
        self.assertEqual(results.error_code, None)
        self.assertEqual(results.error_status, None)
        self.assertEqual(results.error_message, None)
        self.failUnless(results.query_time)
        self.failUnless(results.total_time)
        self.failUnless(results.total)
        self.failUnless(results.total_pages)
        self.assertEqual(results.current_page, 1)
        self.assertEqual(results.begin, 1)
        self.assertEqual(results.end, 10)
        self.failUnless(results.stores)
        self.failUnless(len(results.stores))
        self.assertEqual(results.api_key, self.api_key)
        self.assertEqual(results.url, DEFAULT_REMIX_HOST)
        self.assertEqual(results.version, DEFAULT_REMIX_VERSION)
        self.failIf(results.pid)
        self.assertEqual(results.retry, 1)
    
    def test_query_next(self):
        store_query = StoreQuery.all()
        initial_results = store_query.fetch(self.api_key, retry=3)
        results = initial_results.next
        self.failUnless(results)
        store_query_url = store_query.url(self.api_key, page=2)
        self.assertEqual(results.query_url, store_query_url)
        self.assertEqual(
            results.canonical_url,
            "/v1/stores?page=2&format=json&apiKey=" + self.api_key
        )
        self.assertEqual(results.retry, 3)
        self.assertEqual(results.error, None)
        self.assertEqual(results.error_code, None)
        self.assertEqual(results.error_status, None)
        self.assertEqual(results.error_message, None)
        self.failUnless(results.query_time)
        self.failUnless(results.total_time)
        self.failUnless(results.total)
        self.failUnless(results.total_pages)
        self.assertEqual(results.current_page, 2)
        self.assertEqual(results.begin, 11)
        self.assertEqual(results.end, 20)
        self.failUnless(results.stores)
        self.failUnless(len(results.stores))
    
    def test_query_no_next(self):
        store_query = StoreQuery.all()
        initial_results = store_query.fetch(self.api_key)
        total_pages = initial_results.total_pages
        last_page_results = store_query.fetch(self.api_key, page=total_pages)
        results = last_page_results.next
        self.failIf(results)
    
    def test_query_previous(self):
        store_query = StoreQuery.all()
        initial_results = store_query.fetch(self.api_key, page=2, retry=3)
        results = initial_results.previous
        self.failUnless(results)
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(results.query_url, store_query_url)
        self.assertEqual(
            results.canonical_url,
            "/v1/stores?format=json&apiKey=" + self.api_key
        )
        self.assertEqual(results.retry, 3)
        self.assertEqual(results.error, None)
        self.assertEqual(results.error_code, None)
        self.assertEqual(results.error_status, None)
        self.assertEqual(results.error_message, None)
        self.failUnless(results.query_time)
        self.failUnless(results.total_time)
        self.failUnless(results.total)
        self.failUnless(results.total_pages)
        self.assertEqual(results.current_page, 1)
        self.assertEqual(results.begin, 1)
        self.assertEqual(results.end, 10)
        self.failUnless(results.stores)
        self.failUnless(len(results.stores))
    
    def test_query_no_previous(self):
        store_query = StoreQuery.all()
        initial_results = store_query.fetch(self.api_key)
        results = initial_results.previous
        self.failIf(results)
    
    def test_retry(self):
        store_query = StoreQuery.all()
        try:
            results = store_query.fetch("NotAValidAPIKey", retry=3)
            self.fail("Retry didn't return an error")
        except Exception, e:
            self.failUnless(str(e).find('3 attempt(s)') > 0)
    
    def test_get_by_id(self):
        store_query = StoreQuery.id(4)
        self.failUnless(store_query)
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores/4.json?apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        store = store_query.fetch(self.api_key)
        self.failUnless(store)
        self.assertEqual(store.store_id, 4)
        self.assertEqual(store.postal_code, '55305')
    
    def test_get_by_invalid_id(self):
        store_query = StoreQuery.id(99999999)
        store = store_query.fetch(self.api_key)
        self.failIf(store)
    
    def test_page(self):
        store_query = StoreQuery.all()
        store_query_url = store_query.url(self.api_key, page=2)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores?page=2&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key, page=2)
        self.failUnless(results)
        self.assertEqual(results.query, store_query)
        self.assertEqual(results.query_url, store_query_url)
        self.assertEqual(
            results.canonical_url,
            "/v1/stores?page=2&format=json&apiKey=" + self.api_key
        )
        self.failUnless(results.query_time)
        self.failUnless(results.total_time)
        self.failUnless(results.total)
        self.failUnless(results.total_pages)
        self.assertEqual(results.current_page, 2)
        self.assertEqual(results.begin, 11)
        self.assertEqual(results.end, 20)
        self.failUnless(results.stores)
    
    def test_show(self):
        store_query = StoreQuery.all().show(
            ['address', 'city', 'postal_code']
        )
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores?show=address%%2Ccity%%2CpostalCode&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            "/v1/stores?show=address,city,postalCode&format=json&apiKey=" + self.api_key
        )
        self.failUnless(results.stores)
        store = results.stores[0]
        self.assertEqual(store.attributes, [
            'address', 'city', 'postal_code'
        ])
        try:
            store_id = store.store_id
            self.fail("Was able to get store_id when not requested")
        except AttributeError:
            pass
        try:
            name = store.name
            self.fail("Was able to get name when not requested")
        except AttributeError:
            pass
    
    def test_show_default(self):
        store_query = StoreQuery.all().show_all().show_default()
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores?format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            "/v1/stores?format=json&apiKey=" + self.api_key
        )
        self.failUnless(results.stores)
        store = results.stores[0]
        self.assertEqual(store.attributes, [
            'address', 'city', 'country', 'full_postal_code', 'hours', 'lat', 'lng', 'long_name', 'name', 'phone', 'postal_code', 'region', 'store_id'
        ])
        self.assertEqual(store.store_id, 1504)
    
    def test_show_all(self):
        store_query = StoreQuery.all().show_all()
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores?show=all&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            "/v1/stores?show=all&format=json&apiKey=" + self.api_key
        )
        self.failUnless(results.stores)
        store = results.stores[0]
        self.assertEqual(store.attributes, [
            'address', 'city', 'country', 'full_postal_code', 'hours', 'lat', 'lng', 'long_name', 'name', 'phone', 'postal_code', 'region', 'store_id'
        ])
        self.assertEqual(store.store_id, 1504)
    
    def test_area(self):
        store_query = StoreQuery.all().area(55405, 10).show(
            ['name', 'distance']
        )
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores(area(55405,10))?show=name%%2Cdistance&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            '/v1/stores(area("55405",10))?show=name,distance&format=json&apiKey=' + self.api_key
        )
        self.failUnless(results.total_pages)
        self.failUnless(results.total)
        store = results.stores[0]
        self.failUnless(store)
        self.failUnless(store.name)
        self.failUnless(store.distance)
    
    def test_extend(self):
        store_query = StoreQuery.all().extend('postal_code =', '787*')
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores(postalCode=787%%2A)?format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            '/v1/stores(postalCode="787*")?format=json&apiKey=' + self.api_key
        )
        self.assertEqual(results.total_pages, 1)
        self.assertEqual(results.total, 6)
        self.assertEqual(results.current_page, 1)
        self.assertEqual(results.begin, 1)
        self.assertEqual(results.end, 6)
    
    def test_filter(self):
        store_query = StoreQuery.all().filter('postal_code =', '787*')
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores(postalCode=787%%2A)?format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            '/v1/stores(postalCode="787*")?format=json&apiKey=' + self.api_key
        )
        self.assertEqual(results.total_pages, 1)
        self.assertEqual(results.total, 6)
        self.assertEqual(results.current_page, 1)
        self.assertEqual(results.begin, 1)
        self.assertEqual(results.end, 6)
    
    def test_area_filter(self):
        store_query = StoreQuery.all().filter('postal_code =', '787*')
        store_query = store_query.area(78723, 2).show(['name', 'distance'])
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores(area(78723,2)&postalCode=787%%2A)?show=name%%2Cdistance&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            '/v1/stores(area("78723",2)&postalCode="787*")?show=name,distance&format=json&apiKey=' + self.api_key
        )
        self.assertEqual(results.total_pages, 1)
        self.assertEqual(results.total, 1)
        self.assertEqual(results.current_page, 1)
        self.assertEqual(results.begin, 1)
        self.assertEqual(results.end, 1)
        store = results.stores[0]
        self.failUnless(store)
        self.assertEqual(store.name, 'Mueller Airport')
        self.assertAlmostEqual(store.distance, 1.3, 1)
        store_query = store_query.filter('name =', 'Mueller Airport')
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores(area(78723,2)&postalCode=787%%2A&name=Mueller%%20Airport)?show=name%%2Cdistance&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(results.total, 1)
        store = results.stores[0]
        self.failUnless(store)
        self.assertEqual(store.name, 'Mueller Airport')
        self.assertAlmostEqual(store.distance, 1.3, 1)
    
    def test_filter_extend(self):
        store_query = StoreQuery.all().filter('postal_code =', '787*')
        store_query = store_query.extend('postal_code =', '55*')
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores(postalCode=787%%2A|postalCode=55%%2A)?format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            '/v1/stores(postalCode="787*"|postalCode="55*")?format=json&apiKey=' + self.api_key
        )
        self.failUnless(results.total_pages)
        self.failUnless(results.total)
        self.assertEqual(results.current_page, 1)
        self.assertEqual(results.begin, 1)
        self.assertEqual(results.end, 10)
    
    def test_sort(self):
        store_query = StoreQuery.all().filter('postal_code =', '787*')
        store_query =  store_query.filter('city =', 'Austin')
        store_query = store_query.order('-postal_code')
        store_query_url = store_query.url(self.api_key)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores(postalCode=787%%2A&city=Austin)?sort=postalCode.desc&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            '/v1/stores(postalCode="787*"&city="Austin")?sort=postalCode.desc&format=json&apiKey=' + self.api_key
        )
        self.assertEqual(results.total, 4)
        store = results.stores[0]
        self.assertEqual(store.name, 'North Austin')
        store_query_url = store_query.url(self.api_key, page=2)
        self.assertEqual(
            store_query_url,
            "http://%s/v1/stores(postalCode=787%%2A&city=Austin)?sort=postalCode.desc&page=2&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_query.fetch(self.api_key, page=2)
        self.assertEqual(results.total_pages, 1)
        self.assertEqual(results.total, 4)
        self.assertEqual(results.current_page, 2)
        self.assertEqual(results.begin, 11)
        self.assertEqual(results.end, 4)
        self.assertEqual(results.stores, [])
    
    def test_bad_filter(self):
        try:
            store_query = StoreQuery.all().filter('postal_code=', '787*')
            self.fail('Able to query with bad filter')
        except ValueError, err:
            self.assertEqual(str(err), 'Bad Conditional: postal_code=')
        try:
            store_query = StoreQuery.all().filter('postal_code', '787*')
            self.fail('Able to query with bad filter')
        except ValueError, err:
            self.assertEqual(str(err), 'Bad Conditional: postal_code')
    
    def test_availability(self):
        store_query = StoreQuery.all().area(10010, 30).show(
            ['name', 'distance']
        )
        product_query = ProductQuery.all().filter('name =', 'ipod* touch*').filter('manufacturer =', 'apple*').show(['name', 'sale_price'])
        store_product_query = store_query.products(product_query)
        store_product_query_url = store_product_query.url(self.api_key)
        self.assertEqual(
            store_product_query_url,
            'http://%s/v1/stores(area(10010,30))+products(name=ipod%%2A%%20touch%%2A&manufacturer=apple%%2A)?show=name%%2Cdistance%%2Cproducts.name%%2Cproducts.salePrice&format=json&apiKey=%s' % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = store_product_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            '/v1/stores(area("10010",30))+products(name="ipod* touch*"&manufacturer="apple*")?show=name,distance,products.name,products.salePrice&format=json&apiKey=' + self.api_key
        )
        self.failUnless(results.total > 0)
        store = results.stores[0]
        self.failUnless(store.name)
        self.failUnless(store.distance)
        self.failUnless(store.products)
        product = store.products[0]
        self.failUnless(product.sale_price)
    


class ProductTest(unittest.TestCase):
    def setUp(self):
        global test_api_key
        self.api_key = test_api_key
        self.pid = 2390208
        time.sleep(0.25)
    
    def test_query_all(self):
        product_query = ProductQuery.all()
        self.failUnless(product_query)
        product_query_url = product_query.url(self.api_key)
        self.assertEqual(
            product_query_url,
            "http://%s/v1/products?format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = product_query.fetch(self.api_key)
        self.failUnless(results)
        self.assertEqual(results.query, product_query)
        self.assertEqual(results.query_url, product_query_url)
        self.assertEqual(
            results.canonical_url,
            "/v1/products?format=json&apiKey=%s" % (self.api_key)
        )
        self.failUnless(results.query_time)
        self.failUnless(results.total_time)
        self.failUnless(results.total >= 1000)
        self.failUnless(results.total_pages >= 100)
        self.assertEqual(results.current_page, 1)
        self.assertEqual(results.begin, 1)
        self.assertEqual(results.end, 10)
        self.failUnless(results.products)
        self.assertEqual(len(results.products), 10)
        product = results.products[0]
        self.failUnless(product.sku)
    
    def test_show_default(self):
        product_query = ProductQuery.all().show_all().show_default()
        product_query_url = product_query.url(self.api_key)
        self.assertEqual(
            product_query_url,
            "http://%s/v1/products?format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = product_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            "/v1/products?format=json&apiKey=%s" % (self.api_key)
        )
        self.failUnless(results.products)
        product = results.products[0]
        expected_attributes = set([
            'accessories_image', 'active', 'active_update_date', 'add_to_cart_url', 'affiliate_add_to_cart_url', 'affiliate_url', 'album_label', 'album_title', 'album_version', 'alternate_views_image', 'amg_id', 'angle_image', 'artist_id', 'artist_name', 'attribute_set_id', 'back_view_image', 'category_path', 'cj_affiliate_add_to_cart_url', 'cj_affiliate_url', 'class_', 'class_id', 'copyright', 'customer_review_average', 'customer_review_count', 'department', 'department_id', 'energy_guide_image', 'format', 'free_shipping', 'frequently_purchased_with', 'genre', 'image', 'in_store_availability', 'in_store_availability_text', 'in_store_availability_update_date', 'item_update_date', 'large_front_image', 'large_image', 'left_view_image', 'manufacturer', 'medium_image', 'mobile_url', 'name', 'napster_album_id', 'national_featured', 'new', 'on_sale', 'online_availability', 'online_availability_text', 'online_availability_update_date', 'original_release_date', 'parental_advisory', 'plan_price', 'price_update_date', 'print_only', 'product_id', 'regular_price', 'release_date', 'remote_control_image', 'right_view_image', 'sale_price', 'sales_rank_long_term', 'sales_rank_medium_term', 'sales_rank_short_term', 'shipping_cost', 'short_description', 'sku', 'source', 'special_order', 'spin360_url', 'start_date', 'subclass', 'subclass_id', 'thumbnail_image', 'tiny_mobile_url', 'top_view_image', 'type', 'upc', 'url'
        ])
        self.assertEqual(set(product.attributes), expected_attributes, "Set difference: %s" % (set(product.attributes) ^ expected_attributes))
    def test_show_all(self):
        product_query = ProductQuery.all().show_all()
        product_query_url = product_query.url(self.api_key)
        self.assertEqual(
            product_query_url,
            "http://%s/v1/products?show=all&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = product_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            "/v1/products?show=all&format=json&apiKey=%s" % self.api_key
        )
        self.failUnless(results.products)
        product = results.products[0]
        expected_attributes = set([
            'accessories_image', 'active', 'active_update_date', 'add_to_cart_url', 'affiliate_add_to_cart_url', 'affiliate_url', 'album_label', 'album_title', 'album_version', 'alternate_views_image', 'amg_id', 'angle_image', 'artist_id', 'artist_name', 'attribute_set_id', 'back_view_image', 'best_buy_item_id', 'category_path', 'cj_affiliate_add_to_cart_url', 'cj_affiliate_url', 'class_', 'class_id', 'copyright', 'customer_review_average', 'customer_review_count', 'department', 'department_id', 'energy_guide_image', 'format', 'free_shipping', 'frequently_purchased_with', 'genre', 'image', 'in_store_availability', 'in_store_availability_text', 'in_store_availability_text_html', 'in_store_availability_update_date', 'item_update_date', 'large_front_image', 'large_image', 'left_view_image', 'manufacturer', 'medium_image', 'mobile_url', 'name', 'napster_album_id', 'national_featured', 'new', 'offers', 'on_sale', 'online_availability', 'online_availability_text', 'online_availability_text_html', 'online_availability_update_date', 'original_release_date', 'plan_price', 'parental_advisory', 'price_update_date', 'print_only', 'product_id', 'regular_price', 'release_date', 'remote_control_image', 'right_view_image', 'sale_price', 'sales_rank_long_term', 'sales_rank_medium_term', 'sales_rank_short_term', 'shipping_cost', 'short_description', 'short_description_html', 'sku', 'source', 'special_order', 'spin360_url', 'start_date', 'subclass', 'subclass_id', 'thumbnail_image', 'tiny_mobile_url', 'top_view_image', 'type', 'upc', 'url'
        ])
        self.assertEqual(set(product.attributes), expected_attributes, "Set difference: %s" % (set(product.attributes) ^ expected_attributes))
    def test_get_by_sku(self):
        product_query = ProductQuery.sku(8880044)
        self.failUnless(product_query)
        product_query_url = product_query.url(self.api_key)
        self.assertEqual(
            product_query_url,
            "http://%s/v1/products/8880044.json?apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        product = product_query.fetch(self.api_key)
        self.failUnless(product)
        self.assertEqual(product.sku, 8880044)
        self.assertEqual(product.name, 'Batman Begins - Blu-ray Disc')
        self.failUnless(product.url.startswith('http://www.bestbuy.com/site/olspage.jsp?skuId=8880044&type=product&id=1484301&cmp=RMX&ky='))
    
    def test_get_by_invalid_sku(self):
        product_query = ProductQuery.sku(999999999)
        product = product_query.fetch(self.api_key)
        self.failIf(product)
    
    def test_affiliate_url(self):
        product_query = ProductQuery.sku(8880044)
        product_query_url = product_query.url(self.api_key, pid=self.pid)
        self.assertEqual(
            product_query_url,
            "http://%s/v1/products/8880044.json?apiKey=%s&PID=%s" % (DEFAULT_REMIX_HOST, self.api_key, self.pid)
        )
        product = product_query.fetch(self.api_key, pid=self.pid)
        self.failUnless(product.affiliate_url)
        self.assertNotEqual(product.affiliate_url, product.url)
        self.failUnless(product.affiliate_add_to_cart_url)
        self.assertNotEqual(product.affiliate_add_to_cart_url, product.add_to_cart_url)
    
    def test_availability(self):
        product_query = ProductQuery.all().filter(
            'name =', 'ipod* touch*'
        ).filter('manufacturer =', 'apple*').show(['name', 'sale_price'])
        store_query = StoreQuery.all().area(10010, 30).show(
            ['name', 'distance']
        )
        product_store_query = product_query.stores(store_query)
        product_store_query_url = product_store_query.url(self.api_key)
        self.assertEqual(
            product_store_query_url,
            "http://%s/v1/products(name=ipod%%2A%%20touch%%2A&manufacturer=apple%%2A)+stores(area(10010,30))?show=name%%2CsalePrice%%2Cstores.name%%2Cstores.distance&format=json&apiKey=%s" % (DEFAULT_REMIX_HOST, self.api_key)
        )
        results = product_store_query.fetch(self.api_key)
        self.assertEqual(
            results.canonical_url,
            '/v1/products(name="ipod* touch*"&manufacturer="apple*")+stores(area("10010",30))?show=name,salePrice,stores.name,stores.distance&format=json&apiKey=' + self.api_key
        )
        self.failUnless(results.total)
    
    def test_error(self):
        product_query = ProductQuery.all()
        store_query = StoreQuery.all().filter('invalid_parameter =', 'INVALID')
        query = product_query.stores(store_query)
        results = query.fetch(self.api_key)
        self.assertEqual(results.total, None)
        self.assertEqual(results.products, None)
        self.failUnless(results.error)
        self.assertEqual(results.error_code, 400)
        self.assertEqual(results.error_status, '400 Bad Request')
        self.assertEqual(results.error_message, "'invalidParameter' is not a valid attribute.")
    


############################################################################
# MAIN
############################################################################
def usage():
    print """Usage: premix.py [options] [test] [...]

Options:
  -h, --help       Show this message
  -v, --verbose    Verbose output
  -q, --quiet      Minimal output
  -k, --key        Best Buy Remix API key to run tests with

Examples:
  premix.py                             - run default set of tests
  premix.py StoreTest                   - run all StoreTest tests
  premix.py ProductTest.test_query_all  - run ProductTest.test_query_all"""

test_api_key = None
def main(argv=[]):
    unittest.main(argv=argv)

if __name__ == "__main__":
    import getopt, sys
    opts = args = None
    unittest_args = [sys.argv[0],]
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hvqk:", ["help", "verbose", "quiet", "key="]
        )
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-k", "--key"):
            test_api_key = arg
        else:
            unittest_args.append(opt)
    unittest_args.extend(args)
    if test_api_key == None:
        test_api_key = raw_input("Enter an API Key: ")
    main(argv=unittest_args)

