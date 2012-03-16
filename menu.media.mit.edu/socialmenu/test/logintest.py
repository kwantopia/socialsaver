from django.test.client import Client

c = Client()

r = c.post('/legals/m/-14.2342342/57.234222/abaser01341fadfaabaser01341fadfabaser01341fadfaabaser01341fadfaad/')
print r
