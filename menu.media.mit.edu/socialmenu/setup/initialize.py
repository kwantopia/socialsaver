from legals.models import TableCode
from common.models import Experiment
from datetime import date, timedelta
import uuid


def experiments():
    e, created = Experiment.objects.get_or_create(name="Control", description="Just bare menu")
    e.save()
    e, created = Experiment.objects.get_or_create(name="Social", description="Social")
    e.save()
    e, created = Experiment.objects.get_or_create(name="Popularity", description="Popularity")
    e.save()
    e, created = Experiment.objects.get_or_create(name="Mixed", description="Mixed")
    e.save()
    e, created = Experiment.objects.get_or_create(name="Intervention", description="Intervention")
    e.active = False
    e.save()

def print_today(diff=0):
    for tc in TableCode.objects.filter(date=date.today()-timedelta(diff),first_used=None):
        print tc.code

def tc_today(n=1):
    """
        generate n table codes for today
    """
    for i in range(0,n):
        tcode = str(uuid.uuid3(uuid.uuid1(), 'digital menu'))[:4]
        if tcode == 'dba5':
            tcode = str(uuid.uuid3(uuid.uuid1(), 'digital menu'))[:4]
        # insert this table code to use
        tc = TableCode(code=tcode, date=date.today())
        tc.save()

def tc_days(n=30,per_day=10):
    # generate table codes per day
    for i in range(0,n):
        valid_day = date.today()+timedelta(i)
        tc = TableCode(code='dba5', date=valid_day)
        tc.save()
        for j in range(0,per_day):
            # 10 table codes per day
            tcode = str(uuid.uuid3(uuid.uuid1(), 'digital menu'))[:4]
            if tcode == 'dba5':
                # regenerate since it collides with default
                tcode = str(uuid.uuid3(uuid.uuid1(), 'digital menu'))[:4]
            # insert this table code to use
            tc = TableCode(code=tcode, date=valid_day)
            tc.save()

from presurvey.models import TasteChoice

def init_tastes():
    t, created = TasteChoice.objects.get_or_create(sense="acidic")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="bitter")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="bland")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="cool")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="creamy")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="gooey")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="hot")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="juicy")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="mild")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="nutty")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="peppery")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="ripe")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="salty")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="savory")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="sour")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="spicy")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="strong")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="sweet")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="tangy")
    t.save()
    t, created = TasteChoice.objects.get_or_create(sense="tart")
    t.save()


def all():
    experiments()
    tc_100_days()
    init_tastes()
