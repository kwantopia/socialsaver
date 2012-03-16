from django import forms
from django.forms import ModelForm 
from iphonepush.models import iPhone

class IPhoneRegisterForm(ModelForm):

    class Meta:
        model = iPhone
        fields = ('udid',)

class UpdateTransactionForm(forms.Form):
    txn_id = forms.IntegerField()
    rating = forms.IntegerField(required=False)
    sharing = forms.IntegerField(required=False)
    comment = forms.CharField(max_length=200, required=False)
    accompanied = forms.BooleanField(required=False)
