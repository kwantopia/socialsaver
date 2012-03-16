from django import forms
from django.forms import ModelForm
from iphonepush.models import iPhone

class IPhoneRegisterForm(ModelForm):

    class Meta:
        model = iPhone
        fields = ('udid',)

