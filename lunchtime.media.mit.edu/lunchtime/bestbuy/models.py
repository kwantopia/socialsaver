from django.db import models

# Create your models here.

class BestBuy(models.Model):
  user = models.IntegerField()
  store = models.BooleanField(default=1)
  date = models.DateField()

class BBUserZip(models.Model):
  user = models.IntegerField()
  zipcode = models.CharField(max_length=5)

