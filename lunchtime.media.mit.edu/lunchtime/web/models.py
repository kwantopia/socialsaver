from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class HumanSubjectCompensation(models.Model):
    """
        Human subject compensation related information
    """
    user = models.OneToOneField(User)
    address = models.CharField(max_length=200, default="No address")
    city = models.CharField(max_length=50, default="No city")
    state = models.CharField(max_length=30, default="No state")
    zipcode = models.CharField(max_length=10, default="00000", verbose_name="Zip Code") 
    verified = models.BooleanField(default=False)
    certificates = models.TextField(blank=True, verbose_name="Certificates (separate using comma)")
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%d\t%s\t%s\t%s"%(self.verified, self.user.otnuser.my_email, self.address, self.updated.strftime("%m/%d/%y"))


