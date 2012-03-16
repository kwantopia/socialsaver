import json
from django.http import HttpResponse

class JSONHttpResponse(HttpResponse):
    def __init__(self, content='', status=200):
        content = json.dumps(content)
        HttpResponse.__init__(self, content, status=status, content_type='application/json')

class JSHttpResponse(HttpResponse):
    def __init__(self, content='', status=200):
        content = json.dumps(content)
        HttpResponse.__init__(self, content, status=status, content_type='text/html')
