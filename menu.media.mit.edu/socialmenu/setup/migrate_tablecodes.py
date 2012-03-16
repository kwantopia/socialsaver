from legals.models import TableCode
from datetime import date, timedelta

"""
    Manual migration of table codes
    legals/migrate_tablecodes.py is used for cron migration
"""

for tcs in TableCode.objects.exclude(code="abcd").filter(date=date.today()-timedelta(1), first_used=None):
    print tcs.code
    tcs.date=date.today()
    tcs.save()

# verify which table codes are valid today
print "Table codes for today:"
for tcs in TableCode.objects.filter(date=date.today(), first_used=None):
    print tcs.code
