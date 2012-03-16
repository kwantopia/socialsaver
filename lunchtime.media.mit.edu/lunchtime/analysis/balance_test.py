from common.models import OTNUser
from techcash.models import TechCashBalance

for u in OTNUser.objects.all():

    if TechCashBalance.objects.filter(user=u).count()>1:
        for t in TechCashBalance.objects.filter(user=u):
            print t.balance, t.timestamp, u.name


