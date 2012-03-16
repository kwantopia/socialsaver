from django import forms
from django.forms import ModelForm
from legals.models import Feedback, Order, HumanSubjectCompensation

class FeedbackForm(ModelForm):
    """
        A form for getting feedback from users
    """

    class Meta:
        model = Feedback
        exclude = ['user', 'timestamp']

class ReceiptUploadForm(ModelForm):
    """
        A form for uploading receipts
    """

    class Meta:
        model = Order
        fields = ['receipt']

class HumanSubjectForm(ModelForm):
    """
        A form for obtaining user info for
        Human Subject Voucher
    """

    class Meta:
        model = HumanSubjectCompensation
        exclude = ['user', 'verified', 'certificates', 'updated', 'created']
        widgets = {
                  'address': forms.TextInput(attrs={'class':'text simple'}),
                  'city': forms.TextInput(attrs={'class':'text simple'}),
                  'state': forms.TextInput(attrs={'class':'text simple'}),
                  'zipcode': forms.TextInput(attrs={'class':'text simple'})
                  }

class GiftCertificateForm(ModelForm):
    """
        A form for entering gift certificate information
    """

    class Meta:
        model = HumanSubjectCompensation
        exclude = ['user', 'verified', 'updated', 'created']
        widgets = {
                  'address': forms.TextInput(attrs={'class':'text simple'}),
                  'city': forms.TextInput(attrs={'class':'text simple'}),
                  'state': forms.TextInput(attrs={'class':'text simple'}),
                  'zipcode': forms.TextInput(attrs={'class':'text simple'}),
                  'certificates': forms.Textarea(attrs={'class':'textarea-small'})
                  }
