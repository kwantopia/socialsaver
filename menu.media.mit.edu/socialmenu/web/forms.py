from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from common.models import OTNUser

class OTNUserCreationForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given email, mit_id, and pin.
    """    
    mit_id = forms.RegexField(label=_("mit_id"), max_length=10, regex=r'^\d{9}$', required=False,
        help_text = _("Enter 10 numbers or fewer."),
        error_message = _("This value must contain only numbers."))
    email = forms.EmailField(label=_("email"), max_length=75,required=True)
    pin = forms.RegexField(label=_("pin"), max_length=6, regex=r'^\d{4,6}$', required=True,
        help_text = _("Enter 4-6 numbers."),
        error_message = _("This value must contain only 4-6 numbers."))


