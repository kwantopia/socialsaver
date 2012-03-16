from django.db import models
from common.models import OTNUser, Location

# Create your models here.

class Offer(models.Model):
  location = models.ForeignKey(Location)
  # offer name that is not used in simulation
  name = models.CharField(max_length=100, null=True)
  timestamp = models.DateTimeField()

  RANDOM_ALL = 0
  RANDOM_SPOTTY = 1 
  RANDOM_NONOVERLAP = 2
  RANDOM_ALL_UNI = 3
  RANDOM_SPOTTY_UNI = 4
  RANDOM_NONOVERLAP_UNI = 5
  RANDOM_REFERRAL = 6
  RANDOM_SOCIAL_GROUP = 7
  TARGET_BEHAVIORAL = 8
  TARGET_REFERRAL = 9
  SOCIAL_GROUP_TARGETING = 10 
  SOCIAL_GROUP_REFERRAL = 11 

  STRATEGY_CHOICES = (
    (RANDOM_ALL, 'Random to 50~90%'),
    (RANDOM_SPOTTY, 'Random to fixed number (10)'),
    (RANDOM_NONOVERLAP, 'Random to fixed number but non-overlap so some merchants can\'t send'),
    (RANDOM_ALL_UNI, 'Random to 50~90% Uniform'),
    (RANDOM_SPOTTY_UNI, 'Random to fixed number (10) Uniform'),
    (RANDOM_NONOVERLAP_UNI, 'Random to fixed number but non-overlap so some merchants can\'t send Uniform'),
    (RANDOM_REFERRAL, 'Random to fixed and people refer potential friends'),
    (RANDOM_SOCIAL_GROUP, 'Random few people in different clusters of social networks and referral'),
    (TARGET_BEHAVIORAL, 'Targeting based on the frequency of visits'),
    (TARGET_REFERRAL, 'Target based on frequency and social referrals'),
    (SOCIAL_GROUP_TARGETING, 'Target few people in clusters of social networks'),
    (SOCIAL_GROUP_REFERRAL, 'Target social networks and social referrals')
  )

  ad_strategy = models.IntegerField(choices=STRATEGY_CHOICES)

class OfferCode(models.Model):
  """
    offers sent to people
  """
  user = models.ForeignKey(OTNUser, related_name="received_offers")
  offer = models.ForeignKey(Offer)
  timestamp = models.DateTimeField()
  referred = models.ForeignKey(OTNUser, related_name="forwarded_offers", null=True)
  redeemed = models.DateTimeField(default=None, null=True)
  missed = models.DateTimeField(default=None, null=True)  

class OfferCollision(models.Model):
  """
    When an offer has been already received
  """
  user = models.ForeignKey(OTNUser, related_name="duplicate_offers")
  offer = models.ForeignKey(Offer)
  timestamp = models.DateTimeField()
  referred = models.ForeignKey(OTNUser, related_name="collided_offers", null=True)



