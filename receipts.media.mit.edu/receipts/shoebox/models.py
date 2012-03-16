from django.db import models
from common.models import OTNUserTemp

# Create your models here.

class Receipt(models.Model):

    user = models.ForeignKey('common.OTNUserTemp')
    purchase_date = models.DateTimeField()
    amount = models.FloatField()
    img = models.FileField(upload_to='receipts/')
    png_url = models.CharField(max_length=100, blank=True)

class DetailReceipt(models.Model):

    basic = models.OneToOneField('Receipt')
    business = models.ForeignKey('Business', null=True)
    tax = models.FloatField(blank=True, null=True)
    tip = models.FloatField(blank=True, null=True)

    CASH = 0
    AMEX = 1
    VISA = 2
    MASTER = 3
    DISCOVER = 4

    PAYMENT_CHOICES = (
        (CASH, 'Cash'),
        (AMEX, 'Amex'),
        (VISA, 'Visa'),
        (MASTER, 'Master'),
        (DISCOVER, 'Discover'),
    )

    payment_method = models.IntegerField(choices=PAYMENT_CHOICES, default=CASH)

    category = models.ForeignKey('Category')

    def _get_tags(self):
        return Tag.objects.get_for_object(self)

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)
    
class Business(models.Model):

    name = models.CharField(max_length=30)
    location = models.CharField(blank=True, max_length=30)
    address = models.CharField(blank=True, max_length=50)
    phone = models.CharField(blank=True, max_length=15)
    city = models.ForeignKey('City')

class City(models.Model):

    name = models.CharField(max_length=30)
    state = models.CharField(max_length=30)

class Category(models.Model):

    name = models.CharField(max_length=30)
