# Used to move table codes from one date to another

from datetime import date, timedelta
from legals.models import TableCode

def update_tablecodes():
  for tc in TableCode.objects.filter(date=date.today()-timedelta(2), first_used=None):
    tc.date = date.today()
    tc.save()

def enable_tablecodes():
  for tc in TableCode.objects.filter(first_used=None):
    tc.date = date.today()
    tc.save()
    print tc.code

