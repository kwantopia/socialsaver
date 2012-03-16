from django import forms
from django.forms import ModelForm 
from models import Weather

class WesabeLoginForm(forms.Form):
    
    email = forms.EmailField()
    password = forms.CharField()

class WeatherForm(ModelForm):

    class Meta:
        model = Weather
        exclude = ['update_time', 'sunrise', 'sunset']
