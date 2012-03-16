# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from models import Receipt, DetailReceipt, Business, Category, City
from forms import ReceiptUploadForm
from common.models import OTNUserTemp
from common.helpers import JSONHttpResponse
from tagging.views import tagged_object_list
from django.conf import settings
import os 

# For test purposes
from forms import TestUploadForm

logger = settings.LOGGER

def index(request):
    """
        List all receipts
    """
    receipts = DetailReceipt.objects.all() 
    return render_to_response('shoebox/list.html', {'receipts': receipts})

def receipts(request):
    """
        :url: /shoebox/receipts/

    """
    receipts = DetailReceipt.objects.all() 
    
    return render_to_response('shoebox/receipts.html', {'receipts': receipts})

def upload(request):
    """
        Uploads the receipt
        
        :url: /shoebox/upload/
        :param POST['email']: email identifying user
        :param POST['business_name']: i.e. McDonalds (blank)
        :param POST['address']: business address (blank)
        :param POST['location']: i.e. JFK International (blank)
        :param POST['phone']: phone number (blank)
        :param POST['city']: city (blank)
        :param POST['state']: state (blank)
        :param POST['purchase_date']: purchase date in NeatReceipts format
        :param POST['tax']: tax (blank)
        :param POST['tip']: tip (blank)
        :param POST['amount']: total amount
        :param POST['payment_method']: Visa, Master, Cash etc
        :param POST['category']: NeatReceipts category
        :param FILES['img']: Receipts image

        :rtype: JSON
        
        ::
        
            #: if success in posting returns id of created or update object in string format
            {'result': 'id'}
            #: if failed
            {'result': '-1'}
            #: if request was not POST
            {'result': '0'}
    """
    if request.method == 'POST':
        form = ReceiptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            # assign to the current user uploading data
            instance.user, created = OTNUserTemp.objects.get_or_create(email=request.POST['email']) 
            instance.save()
            
            receipt = DetailReceipt(basic=instance)
            if 'business_name' in request.POST:
                b = Business(name=request.POST['business_name'])
                if 'location' in request.POST:
                    b.location = request.POST['location']
                if 'phone' in request.POST:
                    b.phone = request.POST['phone']
                if 'address' in request.POST:
                    b.address = request.POST['address']
                if 'city' in request.POST:
                    c = City(name=request.POST['city'], state=request.POST['state'])
                    c.save()
                    b.city = c
                b.save()
                receipt.business = b
        
            if 'category' in request.POST:
                cat, created = Category.objects.get_or_create(name=request.POST['category'])
                receipt.category = cat
            if 'tax' in request.POST: 
                receipt.tax = request.POST['tax']
            if 'tip' in request.POST:
                receipt.tip = request.POST['tip']
            if 'payment_method' in request.POST:
                pmethod = request.POST['payment_method'].lower()
                if pmethod.find('cash') != -1:
                    receipt.payment_method = receipt.CASH
                elif pmethod.find('amex') != -1:
                    receipt.payment_method = receipt.AMEX
                elif pmethod.find('visa') != -1:
                    receipt.payment_method = receipt.VISA
                elif pmethod.find('master') != -1:
                    receipt.payment_method = receipt.MASTER
                elif pmethod.find('discover') != -1:
                    receipt.payment_method = receipt.DISCOVER
                else:
                    receipt.payment_method = receipt.CASH

            receipt.save()
            return JSONHttpResponse({'result':str(receipt.id)})
        else:
            return JSONHttpResponse({'result':'-1', 'form_errors':str(form.errors)})
    else:
        return JSONHttpResponse({'result':'0'})

def tagged_receipts(request, tag):
    queryset = Receipt.objects.filter(user=request.user)
    return tagged_object_list(request, queryset, tag, paginate_by=25,
            allow_empty=True, template_object_name='receipt')


def test_upload(request):
    """
        :url: /shoebox/test/upload/

        Tests upload of pdf and converting to image for availability of
        image URL

        :rtype: JSON

        ::
            
            {'result':'1'}
            {'result':'-1'}
            {'result':'0'}
    """
    if request.method == 'POST':
        form = TestUploadForm(request.POST, request.FILES)
        logger.debug(request.POST['img'])
        logger.debug(request.FILES.keys())
        if form.is_valid():
            instance = form.save()
            # convert pdf to img and save
            os.execl('convert', settings.MEDIA_ROOT+instance.img.name, settings.MEDIA_ROOT+instance.img.name[:-3]+'png')
            instance.png_url = instance.img.url[:-3]+'png'
            instance.save()
        else:
            return JSONHttpResponse({'result':'-1', 'form_errors':str(form.errors)})
    else:
        form = TestUploadForm()
        return render_to_response('upload_test_form.html', {'form': form})
        return JSONHttpResponse({'result':'0'})

 
