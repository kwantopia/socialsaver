from django import forms
from django.forms import ModelForm
from shoebox.models import Receipt

class ReceiptUploadForm(ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Receipt
        exclude = ['user', 'png_url']

class TestUploadForm(ModelForm):
    
    class Meta:
        model = Receipt
        exclude = ['png_url']
