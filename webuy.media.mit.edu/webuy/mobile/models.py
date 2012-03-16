from django.db import models
from bestbuy.models import Party
from common.models import Featured

# Create your models here.


class FeaturedEvent(models.Model):
    user = models.ForeignKey(Party)
    featured = models.ForeignKey(Featured)

    LOCATION_FEATURED = 1

    ACTIONS = (
            (LOCATION_FEATURED, 'saw location featured'),
        )
    action = models.IntegerField(choices=ACTIONS)
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_json(self):

        detail = {'id': str(self.id),
                  'action': self.ACTIONS[self.action][1],
                  'location': featured.location.name,
                  'user_id': str(self.user.id),
                  'user_name': str(self.user.name),
                  'latitude': str(self.latitude),
                  'longitude': str(self.longitude),
                  'timestamp': str(time.mktime(self.timestamp.timetuple())),
                  }

        return detail

    def __unicode__(self):
        return "%s: %s %s at %s"%(self.user.name, self.ACTIONS[self.action][1], featured.location.name, str(self.timestamp))


class Event(models.Model):
    user = models.ForeignKey(Party)

    LOGIN = 0
    LOGOUT = 1
    RECEIPT = 2
    RECEIPTS = 3
    LOCATION = 4
    USER = 5

    ACTIONS = (
            (LOGIN, '/mobile/login/'),
            (LOGOUT, '/mobile/logout/'),
            (RECEIPT, '/mobile/receipt/(?P<receipt_id>\d+)/'),
            (RECEIPTS, '/mobile/receipts/'),
            (LOCATION, '/mobile/location/(?P<location_id>\d+)/'),
            (USER, '/mobile/user/(?P<user_id>\d+)/'),
        )
    action = models.IntegerField(choices=ACTIONS)
    params = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_json(self):

        detail = {'id': str(self.id),
                  'action': self.ACTIONS[self.action][1],
                  'params': self.params,
                  'user_id': str(self.user.id),
                  'user_name': str(self.user.name),
                  'latitude': str(self.latitude),
                  'longitude': str(self.longitude),
                  'timestamp': str(time.mktime(self.timestamp.timetuple())),
                  }

        return detail

    def __unicode__(self):
        return "%s: %s: %s"%(self.user.name, self.ACTIONS[self.action][1], str(self.timestamp))


class CallEvent(models.Model):
    caller = models.ForeignKey(Party, related_name='caller')
    callee = models.ForeignKey(Party, related_name='callee')
    #: action can be called, talked
    CALLED = 0
    TALKED = 1
    SMSED = 2
    EMAILED = 3
    ACTIONS = (
            (CALLED, 'called'),
            (TALKED, 'talked'),
            (SMSED, 'smsed'),
            (EMAILED, 'emailed'),
        )
    action = models.IntegerField(choices=ACTIONS)
    #: minutes called 
    value = models.IntegerField(default=0)
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        if self.action in [self.CALLED, self.SMSED, self.EMAILED]:
            return "%s %s %s at %s"%(self.caller.name, self.ACTIONS[self.action][1],
                self.callee.name, 
                self.timestamp)
        elif self.action == self.TALKED:
            return "%s %s %s for %d mins at %s"%(self.caller.name, self.ACTIONS[self.action][1],
                self.callee.name, 
                self.value,
                self.timestamp)


class FeedEvent(models.Model):
    user = models.ForeignKey(Party)

    FEED = 0
    LOCATION_TRACE = 1
    FRIEND_TRACE = 2
    REVIEWS = 3
    RECEIPTS_MONTH = 4

    ACTIONS = (
            (FEED, '/mobile/feed/'),
            (LOCATION_TRACE, '/mobile/location/trace/(?P<location_id>\d+)/'),
            (FRIEND_TRACE, '/mobile/friend/trace/(?P<friend_id>\d+)/'),
            (REVIEWS, '/mobile/revies/(?P<user_id>\d+)/(?P<location_id>\d+)/'),
            (RECEIPTS_MONTH, '/mobile/receipts/month/'),
        )
    experiment = models.IntegerField()
    action = models.IntegerField(choices=ACTIONS)
    params = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_json(self):

        detail = {'id': str(self.id),
                  'experiment': str(self.experiment),
                  'action': self.ACTIONS[self.action][1],
                  'params': self.params,
                  'user_id': str(self.user.id),
                  'user_name': str(self.user.name),
                  'latitude': str(self.latitude),
                  'longitude': str(self.longitude),
                  'timestamp': str(time.mktime(self.timestamp.timetuple())),
                  }

        return detail

    def __unicode__(self):
        return "%s: %s: %s"%(self.user.name, self.ACTIONS[self.action][1], str(self.timestamp))



