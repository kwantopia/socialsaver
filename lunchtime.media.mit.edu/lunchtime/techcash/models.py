from django.db import models
from common.models import OTNUser, Location
import time
import datetime
from django.conf import settings

# Create your models here.

class TechCashTransaction(models.Model):
    trans_id = models.IntegerField(unique=True)
    user = models.ForeignKey(OTNUser)
    location = models.ForeignKey(Location, null=True)
    amount = models.FloatField(default=0.0)
    timestamp = models.DateTimeField('purchase_date', auto_now_add=True)
    time = models.TimeField('purchase_time', auto_now_add=True)

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6
    DAY_CHOICES = (
            (MON, 'Monday'),
            (TUE, 'Tuesday'),
            (WED, 'Wednesday'),
            (THU, 'Thursday'),
            (FRI, 'Friday'),
            (SAT, 'Saturday'),
            (SUN, 'Sunday'),
        )

    day = models.IntegerField(choices=DAY_CHOICES, default=MON)
    #: indicates whether this transaction is alerted or not
    alerted = models.BooleanField(default=False)

    class Meta:
         get_latest_by = 'timestamp'

    def set_day_time(self):
        self.day = self.timestamp.weekday()
        self.time = self.timestamp.time()
        self.save()

    def get_json(self, public=False):
        
        if public:
            # content displayed to public
            detail = {'id': str(self.id),
                        'location': self.location.get_json(level=1),
                        'user': self.user.get_json(level=1),
                        'amount': "%.2f"%self.amount,
                        'timestamp': str(time.mktime(self.timestamp.timetuple())),

                        'date': self.timestamp.strftime("%b %d, %Y - %I:%M:%S %p"),
                    }
        else:
            detail = {'id': str(self.id),
                        'location': self.location.get_json(level=1),
                        'amount': "%.2f"%self.amount,
                        'timestamp': str(time.mktime(self.timestamp.timetuple())),
                        'date': self.timestamp.strftime("%b %d, %Y - %I:%M:%S %p"),
                    }
        return detail

    def feed(self, experiment=1, android=False):
        if android:
            if experiment == 1:
                return {"location": self.location.id,
                        "feed_str": "Someone visited <font color='%s'><b>%s</b></font>"%(settings.FEED_COLOR, self.location.name)
                        }
            elif experiment == 2:
                return {"actor": self.user.id,
                        "location": self.location.id,
                        "feed_str": "<font color='%s'><b>%s</b></font> visited <font color='%s'><b>%s</b></font>"%(settings.FEED_COLOR, self.user.first_name, settings.FEED_COLOR, self.location.name)
                        }
        else:

            if experiment == 1:
                return "Someone visited <a href='tt://location/%d'>%s</a>"%(self.location.id, self.location.name)
            elif experiment == 2:
                return "<a href='tt://user/%d'>%s</a> visited <a href='tt://location/%d'>%s</a>"%(self.user.id, self.user.first_name, self.location.id, self.location.name)

    def __unicode__(self):
        return str(self.location) + " at " + str(self.timestamp)
    
class TechCashBalance(models.Model):
    user = models.ForeignKey(OTNUser)
    balance = models.FloatField(default=0.0)
    initialized = models.BooleanField(default=False)
    timestamp = models.DateTimeField('last update', auto_now=True)

    def get_json(self):
        detail = {'user': self.user.name,
                'balance': "%.2f"%self.balance,
                'timestamp': str(time.mktime(self.timestamp.timetuple()))
                }
        return detail


from common.models import OTNUserTemp

class TechCashTransactionTest(models.Model):
    trans_id = models.IntegerField()
    user = models.ForeignKey(OTNUserTemp)
    location = models.ForeignKey(Location, null=True)
    amount = models.FloatField(default=0.0)
    timestamp = models.DateTimeField('purchase date', auto_now_add=True)
    #: indicates whether this transaction is alerted or not
    alerted = models.BooleanField(default=False)

    def get_json(self, public=False):
        
        if(public):
            detail = {'id': str(self.id),
                        'location': self.location.get_json(level=1),
                        'user': self.user.get_json(),
                        'amount': "%.2f"%self.amount,
                        'timestamp': str(time.mktime(self.timestamp.timetuple())),
                    }
        else:
            detail = {'id': str(self.id),
                        'location': self.location.get_json(level=1),
                        'amount': "%.2f"%self.amount,
                        'timestamp': str(time.mktime(self.timestamp.timetuple())),
                    }
        return detail

class TechCashBalanceTest(models.Model):
    user = models.ForeignKey(OTNUserTemp)
    balance = models.FloatField(default=0.0)
    timestamp = models.DateTimeField('last update', auto_now=True)

    def get_json(self):
        detail = {'user': user.first_name,
                'balance': "%.2f"%self.balance,
                'timestamp': str(time.mktime(self.timestamp.timetuple()))
                }

        return detail

class LunchTime(models.Model):
    """
        Every week it updates, one record per user
    """
    user = models.ForeignKey(OTNUser)
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6
    DAY_CHOICES = (
            (MON, 'Monday'),
            (TUE, 'Tuesday'),
            (WED, 'Wednesday'),
            (THU, 'Thursday'),
            (FRI, 'Friday'),
            (SAT, 'Saturday'),
            (SUN, 'Sunday'),
        )
    day_of_week = models.IntegerField(choices=DAY_CHOICES, default=MON)
    avg_time = models.TimeField(default=datetime.time(12))
    updated = models.DateTimeField(auto_now=True)

class LunchTimeLog(models.Model):
    """
        Model to keep a log of how lunch time changes over time
    """
    user = models.ForeignKey(OTNUser)
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6
    DAY_CHOICES = (
            (MON, 'Monday'),
            (TUE, 'Tuesday'),
            (WED, 'Wednesday'),
            (THU, 'Thursday'),
            (FRI, 'Friday'),
            (SAT, 'Saturday'),
            (SUN, 'Sunday'),
        )
    day_of_week = models.IntegerField(choices=DAY_CHOICES, default=MON)
    avg_time = models.TimeField(default=datetime.time(12))
    updated = models.DateTimeField(auto_now=True)


class Receipt(models.Model):
    txn = models.OneToOneField(TechCashTransaction)
    detail = models.TextField(blank=True)

    NOT_RATED = 0
    POOR = 1
    FAIR = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5

    RATING_CHOICES = (
        (NOT_RATED, 'Not Rated'),
        (POOR, 'Poor'),
        (FAIR, 'Fair'),
        (AVERAGE, 'Average'),
        (GOOD, 'Good'),
        (EXCELLENT, 'Excellent'),
    )

    rating = models.IntegerField(choices=RATING_CHOICES, default=NOT_RATED)

    PRIVATE = 0
    FRIENDS = 1
    COMMUNITY = 2
    PUBLIC = 3

    SHARING_CHOICES = (
        (PRIVATE, 'Private'),
        (FRIENDS, 'Friends'),
        (COMMUNITY, 'Community'),
        (PUBLIC, 'Public'),
    )

    sharing = models.IntegerField(choices=SHARING_CHOICES, default=PUBLIC)
    image = models.CharField(max_length=200, null=True)
    accompanied = models.BooleanField(default=False)
    # indicates whether this receipt has been viewed or not
    new = models.BooleanField(default=True)
    last_update = models.DateTimeField(auto_now=True)

    def get_json(self, public=False):
        detail = {'id': str(self.id),
                'techcash': self.txn.get_json(),
                'rating': str(self.rating),
                'sharing': str(self.sharing),
                'detail': self.detail,
                'accompanied': str(self.accompanied),
                'new': str(self.new)
        }
        if public:
            detail = {'id': str(self.id),
                'techcash': self.txn.get_json(public=True),
                'accompanied': str(self.accompanied),
                'rating': str(self.rating),
        }
 
        return detail
 
    def review_len(self):
        return len(self.detail)

    def get_review(self):
        """
            Used for displaying just reviews and comments

        """
        detail = {'id': str(self.id),
                  'timestamp': str(time.mktime(self.txn.timestamp.timetuple())),
                  'rating': str(self.rating),
                  'comment': self.detail
                }

        return detail

    def __unicode__(self):
        return str(self.txn)
