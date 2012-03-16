# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
    return

def login_ws(request):
    return

def view_dining(request):
    """
        :url: /mit/m/dining/
    """
    return 

def view_item(request, item_id):
    return

def view_category(request, category_id):
    return

def view_friend_choices(request):
    return

def mark_item(request, item_id):
    return

def unmark_item(request, item_id):
    return

def order(request):
    return

def myorders(request):
    return
