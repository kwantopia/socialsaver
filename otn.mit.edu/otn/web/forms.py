from django import forms
from django.forms import ModelForm 

class BuxferLoginForm(forms.Form):
    
    email = forms.EmailField()
    password = forms.CharField()
