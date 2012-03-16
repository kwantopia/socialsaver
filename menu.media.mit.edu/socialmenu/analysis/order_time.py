#matplotlib.use("CocoaAgg")
import matplotlib
matplotlib.use("MacOSX")


from django.contrib.auth.models import User
from django.utils.encoding import smart_str, smart_unicode
from django.db.models import Count

from legals.models import * 
from presurvey.models import *
from common.models import OTNUser, Friends

import pylab
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from matplotlib.ticker import MaxNLocator
import numpy as np
from datetime import datetime, timedelta
from time import mktime
import networkx as nx
import sys, os, csv
import pygraphviz
import pickle
from scipy.stats import stats
import math


# 'font.family': 'serif',
# 'font.serif': ['Times', 'Palatino', 'New Century Schoolbook', 'Bookman',
#                'Computer Modern Roman']
# 'font.monospace': ['Courier', 'Computer Modern Typewriter']

params = {'backend':'pdf',
        'font.family': 'sans-serif',
        'font.sans-serif': ['Helvetica', 'Avant Garde', 'Computer Modern Sans Serif'],
        'text.usetex':True}
        #'font.size': 10,
pylab.rcParams.update(params)

img_type = "pdf"
# Ubuntu
#PREFIX = "/home/kwan/workspace/results/"
# Mac
PREFIX_IMG = "/Users/kwan/workspace/results/images/"
PREFIX_DAT = "/Users/kwan/workspace/results/data/"

start_date = datetime(2010,3,1)

"""

This module is to investigate the time of ordering and how it relates to other
parameters.

Find distribution of time by:

1. by experimental group
2. by single or multiple people
3. average price in different groups
4. people who clicked friends view
5. among different taste parameters
6. by price ordered

1. First time or repeated Legals customer (Need presurvey)
2. Know the menu or not
3. The total time ordered and its distribution
4. The different # of categories user clicked
5. Number of different menu items they clicked
6. Number of different items
7. Compare with friend's behavior 

8. Map the network of friends and common choices
    - show shade of color by the common choices they have? 

How does ordered item relate to the items on presurvey?
    - does items they ordered appear in presurvey items? what percentage?
    - how about those people who completed presurvey after their order, do they appear 100%?

1. Graph the network of participants
    a. Graph all population
    b. Graph presurvey participants
    c. Graph diners

2. Graph the per menu choice versus participant

3. Graph number of people who dined together

    a. Whether there is difference between individuals dining and dining as a group.

4. Graph price versus taste
    Price optimizer - economical
    Taste optimizer - taste driven
    Impulsive - don't care about price or taste
    Struggler - optimizing on price and taste

5. Measure if there is time difference between people ordering with different types of menu item.  Average time to choosing a particular item.

6. Measure how much people diverge from their original choices when dining with the social menu.

7. Plot these out by demographic characters M vs F, age group, taste groups

8. Plot out how people's choices change over time

9. For those in social group, draw out the casual effects of people's choices

10. Plot out how many categories or items people look at before finalizing on the order.

11. Regress on price, normalize by number of people who want a specific item
    - price on x-axis, number of items on y-axis
    - price on x-axis, the time to order on y-axis

12. Graph of causal influence.  Directed graphs of people who came after another when they are friends.


13. Time and behavior of people who choose cheap items

14. Time and behavior of people who choose not cheap items

15. How do friends affect our choices and when?

"""

def calculate_order_time(o):

    # total number of categories clicked
    cat_click = 0
    dish_click = 0
    friend_clicked = 0
    features_clicked = 0
    allergies_clicked = 0
    # number of times friend category clicked
    friend_freq = 0
    # number of times feature category clicked
    features_freq = 0
    # number of times allergy category clicked
    allergies_freq = 0

    # for events where items have been ordered
    start_time = datetime(2011,7,10) 
    end_time = datetime(2011,7,10)-timedelta(days=1000)
    evtbasic = Event.objects.filter(order=o)
    for e in evtbasic:
        if e.timestamp < start_time:
            start_time = e.timestamp
        if e.timestamp > end_time:
            end_time = e.timestamp
    evtspecial = EventSpecial.objects.filter(order=o)
    for e in evtspecial:
        if e.category == EventSpecial.FRIENDS:
            friend_clicked = 1
            friend_freq += 1
        if e.category == EventSpecial.CHEFS:
            features_clicked = 1
            features_freq += 1
        if e.category == EventSpecial.ALLERGIES:
            allergies_clicked = 1
            allergies_freq += 1
        cat_click += 1
    evtmenu = EventMenuItem.objects.filter(order=o)
    for e in evtmenu:
        dish_click += 1
    evtcategory = EventCategory.objects.filter(order=o)
    for e in evtcategory:
        cat_click += 1
    # collect all timestamps and sort it
    #duration = mktime(end_time.timetuple())-mktime(start_time.timetuple())
    duration = (end_time - start_time).total_seconds()

    # dish clicks are in 8th item
    return duration, cat_click, friend_clicked, friend_freq, features_clicked, features_freq, allergies_clicked, allergies_freq, dish_click

def calculate_order_time_old(o):

    # total number of categories clicked
    cat_click = 0
    dish_click = 0
    friend_clicked = 0
    features_clicked = 0
    allergies_clicked = 0
    # number of times friend category clicked
    friend_freq = 0
    # number of times feature category clicked
    features_freq = 0
    # number of times allergy category clicked
    allergies_freq = 0

    # for events where items have been ordered
    start_time = datetime(2011,7,10) 
    end_time = datetime(2011,7,10)-timedelta(days=1000)

    evtbasic = EventBasic.objects.filter(order=o)
    for e in evtbasic:
        if e.timestamp < start_time:
            start_time = e.timestamp
        if e.timestamp > end_time:
            end_time = e.timestamp
    evtspecial = EventSpecial.objects.filter(order=o)
    for e in evtspecial:
        """
        if e.timestamp < start_time:
            start_time = e.timestamp
        if e.timestamp > end_time:
            end_time = e.timestamp
        """
        if e.category == EventSpecial.FRIENDS:
            friend_clicked = 1
            friend_freq += 1
        if e.category == EventSpecial.CHEFS:
            features_clicked = 1
            features_freq += 1
        if e.category == EventSpecial.ALLERGIES:
            allergies_clicked = 1
            allergies_freq += 1
        cat_click += 1
    evtmenu = EventMenuItem.objects.filter(order=o)
    for e in evtmenu:
        if e.timestamp < start_time:
            start_time = e.timestamp
        if e.timestamp > end_time:
            end_time = e.timestamp
        dish_click += 1
    evtcategory = EventCategory.objects.filter(order=o)
    for e in evtcategory:
        cat_click += 1
        """
        if e.timestamp < start_time:
            start_time = e.timestamp
        if e.timestamp > end_time:
            end_time = e.timestamp
        """
    # collect all timestamps and sort it
    #duration = mktime(end_time.timetuple())-mktime(start_time.timetuple())
    duration = (end_time - start_time).total_seconds()

    # dish clicks are in 8th item
    return duration, cat_click, friend_clicked, friend_freq, features_clicked, features_freq, allergies_clicked, allergies_freq, dish_click

def duration_categorize():

    # for each experiment
    #orders = Order.objects.filter(items__item__category=cat).filter(table__experiment__id=exp_var).annotate(num_items=Count('items')).filter(num_items__gt=0)
    orders = Order.objects.annotate(num_items=Count('items')).filter(num_items__gt=0)

    # matrix of sets of common dishes between orders
    order_matrix = {}
    for o in orders:
        order_matrix[o] = {}
        for p in orders.exclude(id=o.id):
            common_dishes = o.common_orders(p)
            order_matrix[o][p] = common_dishes

    order_durations = {}
    for o in orders:
        d = calculate_order_time(o)
        order_durations[o.id] = d[0]

    time_limits = [300, 700, 1200]

    # work on statistics related to those orders
    # 1. 0~300 seconds
    certain = []
    # 2. 300~700 seconds
    dilemma = []
    # 3. 700~1200 seconds
    uncertain = []

    for key, val in order_durations.items():
        if val < time_limits[0]:
            certain.append(key)
        elif val < time_limits[1]:
            dilemma.append(key)
        else:
            uncertain.append(key)

    # determine the number of orders in each experimental group
    print "Certain (< 300 s)"
    certain_exp_count = Order.objects.filter(id__in=certain).values("table__experiment").annotate(Count("id"))
    print certain_exp_count
    print "Dilemma (< 700 s)"
    dilemma_exp_count = Order.objects.filter(id__in=dilemma).values("table__experiment").annotate(Count("id"))
    print dilemma_exp_count
    print "Uncertain (< 1200 s)"
    uncertain_exp_count = Order.objects.filter(id__in=uncertain).values("table__experiment").annotate(Count("id"))
    print uncertain_exp_count

    y = np.zeros((4,3))
    for e in certain_exp_count:
        y[e['table__experiment']-1,0]=e['id__count']
    for e in dilemma_exp_count:
        y[e['table__experiment']-1,0]=e['id__count']
    for e in uncertain_exp_count:
        y[e['table__experiment']-1,0]=e['id__count']

    for i in xrange(0,4):
        # print out % of people who made certain decisions
        y[i,:]/np.sum(y[i,:], dtype="float")

    # graph the network of influence
    DG1 = pygraphviz.AGraph(directed=True)
    influence_edges1 = set() 

    for exp in range(1,5):

        certain_orders = Order.objects.filter(id__in=certain, table__experiment__id=exp)
        for o in certain_orders:
            # look at other orders by friends that happened before this order
            # and see if it has common order
            for k in orders.filter(timestamp__lt=o.timestamp, table__experiment__id=exp):
                # if order by friends 
                if Friends.objects.get(facebook_id=o.user.facebook_profile.facebook_id).is_friend(k.user.facebook_profile.facebook_id):
                    # check if common orders exist
                    common_dishes = order_matrix[o][k] 
                    if len(common_dishes) > 0:
                        dish = MenuItem.objects.get(id=list(common_dishes)[0])
                        influence_edges1.add((k.user.id, o.user.id))
                        d1 = (k.timestamp-start_date).days
                        c1 = cm.pink(d1*2)
                        DG1.add_node(k.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]), label=dish.name.encode('ascii', 'replace'))
                        d2 = (o.timestamp-start_date).days
                        c2 = cm.pink(d2*2)
                        DG1.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]), label=dish.name.encode('ascii', 'replace'))

        #print influence_edges
        DG1.add_edges_from(list(influence_edges1))

        # dot output
        DG1.draw(PREFIX_IMG+"certain_people_%d.dot"%exp, prog="dot")
        DG1.draw(PREFIX_IMG+"certain_people_%d.%s"%(exp,img_type), prog='dot')
     
        DG2 = pygraphviz.AGraph(directed=True)
        influence_edges2 = set() 

        dilemma_orders = Order.objects.filter(id__in=dilemma, table__experiment__id=exp)
        for o in dilemma_orders:
            # look at other orders by friends that happened before this order
            # and see if it has common order

            for k in orders.filter(timestamp__lt=o.timestamp, table__experiment__id=exp):
                # if order by friends 
                if Friends.objects.get(facebook_id=o.user.facebook_profile.facebook_id).is_friend(k.user.facebook_profile.facebook_id):
                    # check if common orders exist
                    common_dishes = order_matrix[o][k] 
                    if len(common_dishes) > 0:
                        dish = MenuItem.objects.get(id=list(common_dishes)[0])
                        influence_edges2.add((k.user.id, o.user.id))
                        d1 = (k.timestamp-start_date).days
                        c1 = cm.pink(d1*2)
                        DG2.add_node(k.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]), label=dish.name.encode('ascii', 'replace'))
                        d2 = (o.timestamp-start_date).days
                        c2 = cm.pink(d2*2)
                        DG2.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]), label=dish.name.encode('ascii', 'replace'))

        #print influence_edges
        DG2.add_edges_from(list(influence_edges2))

        # dot output
        DG2.draw(PREFIX_IMG+"dilemma_people_%d.dot"%exp, prog="dot")
        DG2.draw(PREFIX_IMG+"dilemma_people_%d.%s"%(exp, img_type), prog='dot')
     
        DG3 = pygraphviz.AGraph(directed=True)
        influence_edges3 = set() 

        uncertain_orders = Order.objects.filter(id__in=uncertain, table__experiment__id=exp)
        for o in uncertain_orders:
            # look at other orders by friends that happened before this order
            # and see if it has common order
            for k in orders.filter(timestamp__lt=o.timestamp, table__experiment__id=exp):
                # if order by friends 
                if Friends.objects.get(facebook_id=o.user.facebook_profile.facebook_id).is_friend(k.user.facebook_profile.facebook_id):
                    # check if common orders exist
                    common_dishes = order_matrix[o][k] 
                    if len(common_dishes) > 0:
                        dish = MenuItem.objects.get(id=list(common_dishes)[0])
                        influence_edges3.add((k.user.id, o.user.id))
                        d1 = (k.timestamp-start_date).days
                        c1 = cm.pink(d1*2)
                        DG3.add_node(k.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]), label=dish.name.encode('ascii', 'replace'))
                        d2 = (o.timestamp-start_date).days
                        c2 = cm.pink(d2*2)
                        DG3.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]), label=dish.name.encode('ascii', 'replace'))

        #print influence_edges
        DG3.add_edges_from(list(influence_edges3))

        # dot output
        DG3.draw(PREFIX_IMG+"uncertain_people_%d.dot"%exp, prog="dot")
        DG3.draw(PREFIX_IMG+"uncertain_people_%d.%s"%(exp, img_type), prog='dot')
 
def graph_order_influence(item_id=0, exp_id=0, label=0):
    """
        Graph the directed graph that influences friends 
        to choose 

        if label = 1 use node id
        if label = 0 use menu name
    """
    
    DG = pygraphviz.AGraph(directed=True)

    influence_edges = set() 

    if item_id == 0:
        for m in MenuItem.objects.all():
            orders = set() 
            # for each menu item get all the people ordered sorted by time and if they are friends
            # create a link from prev to next
            for r in m.menuitemreview_set.all():
                if r.legals_ordered.all().count() > 0:
                    for o in r.legals_ordered.all():
                        if exp_id == 0:
                            orders.add(o)
                        elif o.table.experiment.id==exp_id:
                            orders.add(o)
            for o in list(orders):
                for p in list(orders):
                    if p.timestamp < o.timestamp:
                        # if users are friends
                        if Friends.objects.get(facebook_id=o.user.facebook_profile.facebook_id).is_friend(p.user.facebook_profile.facebook_id):
                            influence_edges.add((p.user.id, o.user.id))
                            d1 = (p.timestamp-start_date).days
                            c1 = cm.pink(d1*2)
                            if label == 1:
                              DG.add_node(p.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]))
                            else:
                              DG.add_node(p.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]), label=m.name.encode('ascii', 'replace'))
                            d2 = (o.timestamp-start_date).days
                            c2 = cm.pink(d2*2)

                            if label == 1:
                              DG.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]))
                            else:
                              DG.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]), label=m.name.encode('ascii', 'replace'))
    else:
        m = MenuItem.objects.get(id=item_id)
        orders = set() 
        # for each menu item get all the people ordered sorted by time and if they are friends
        # create a link from prev to next
        for r in m.menuitemreview_set.all():
            if r.legals_ordered.all().count() > 0:
                for o in r.legals_ordered.all():
                    if exp_id == 0:
                        orders.add(o)
                    elif o.table.experiment.id==exp_id:
                        orders.add(o)
        for o in list(orders):
            for p in list(orders):
                if p.timestamp < o.timestamp:
                    # if users are friends
                    if Friends.objects.get(facebook_id=o.user.facebook_profile.facebook_id).is_friend(p.user.facebook_profile.facebook_id):
                        influence_edges.add((p.user.id, o.user.id))
                        d1 = (p.timestamp-start_date).days
                        c1 = cm.pink(d1*2)
                        DG.add_node(p.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]), label=m.name.encode('ascii', 'replace'))
                        d2 = (o.timestamp-start_date).days
                        c2 =cm.pink(d2*2)
                        DG.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]), label=m.name.encode('ascii', 'replace'))

    #print influence_edges
    DG.add_edges_from(list(influence_edges))

    # dot output
    DG.draw(PREFIX_IMG+"influence_%d_%d.dot"%(item_id, exp_id), prog="dot")
    DG.draw(PREFIX_IMG+"influence_%d_%d.%s"%(item_id, exp_id, img_type), prog='dot')
     
    """
    pos = nx.graphviz_layout(DG)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    print len(DG.edges())
    print len(DG.nodes())
    nx.draw(DG, pos)
    plt.savefig(PREFIX_IMG+"directed_influence.%s"%img_type)
    plt.show()
    """

def graph_consider_influence(item_id=0, exp_id=0, label=0):
    """
        Graph the directed graph that influences friends 
        to consider 
    """
    
    DG = pygraphviz.AGraph(directed=True)

    influence_edges = set() 

    if item_id == 0:
        for m in MenuItem.objects.all():
            orders = set() 
            considered = set()
            # for each menu item get all the people ordered sorted by time and if they are friends
            # create a link from prev to next
            for r in m.menuitemreview_set.all():
                if r.legals_ordered.all().count() > 0:
                    for o in r.legals_ordered.all():
                        if exp_id == 0:
                            orders.add(o)
                        elif o.table.experiment.id==exp_id:
                            orders.add(o)
            for r in m.eventmenuitem_set.filter(action=EventMenuItem.CONSIDER):
                if r.order is not None:
                    if exp_id == 0:
                        considered.add(r.order)
                    elif r.order.table.experiment.id==exp_id:
                        considered.add(r.order)

            for o in list(orders):
                for p in list(considered):
                    if o.timestamp < p.timestamp:
                        # if users are friends
                        if Friends.objects.get(facebook_id=p.user.facebook_profile.facebook_id).is_friend(o.user.facebook_profile.facebook_id):
                            influence_edges.add((o.user.id, p.user.id))
                            d1 = (p.timestamp-start_date).days
                            c1 = cm.pink(d1*2)
                            if label == 1:
                              DG.add_node(p.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]))
                            else:
                              DG.add_node(p.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]), label=m.name.encode('ascii', 'replace'))
                            d2 = (o.timestamp-start_date).days
                            c2 =cm.pink(d2*2)
                            if label == 1:  
                              DG.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]))
                            else:
                              DG.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]), label=m.name.encode('ascii', 'replace'))
    else:
        m = MenuItem.objects.get(id=item_id)
        orders = set() 
        # for each menu item get all the people ordered sorted by time and if they are friends
        # create a link from prev to next
        for r in m.menuitemreview_set.all():
            if r.legals_ordered.all().count() > 0:
                for o in r.legals_ordered.all():
                    if exp_id == 0:
                        orders.add(o)
                    elif o.table.experiment.id==exp_id:
                        orders.add(o)
        for o in list(orders):
            for p in list(orders):
                if p.timestamp < o.timestamp:
                    # if users are friends
                    if Friends.objects.get(facebook_id=o.user.facebook_profile.facebook_id).is_friend(p.user.facebook_profile.facebook_id):
                        influence_edges.add((p.user.id, o.user.id))
                        d1 = (p.timestamp-start_date).days
                        c1 = cm.pink(d1*2)
                        DG.add_node(p.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]), label=m.name.encode('ascii', 'replace'))
                        d2 = (o.timestamp-start_date).days
                        c2 =cm.pink(d2*2)
                        DG.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]), label=m.name.encode('ascii', 'replace'))

    #print influence_edges
    DG.add_edges_from(list(influence_edges))
    degrees_directed = DG.in_degree()#, weighted=False)
    sum_degrees = 0.0
    i = 0
    max_degree = 0.0
    for v in degrees_directed:
      sum_degrees += v 
      i += 1
      if v > max_degree:
        max_degree = v

    print "Avg in degree:", sum_degrees/float(i)
    print "Max in degree:", max_degree

    degrees_directed = DG.out_degree()#, weighted=False)
    sum_degrees = 0.0
    i = 0
    max_degree = 0.0
    for v in degrees_directed:
      sum_degrees += v 
      i += 1
      if v > max_degree:
        max_degree = v

    print "Avg out degree:", sum_degrees/float(i)
    print "Max out degree:", max_degree


    # dot output
    DG.draw(PREFIX_IMG+"consider_influence_%d_%d.dot"%(item_id, exp_id), prog="dot")
    DG.draw(PREFIX_IMG+"consider_influence_%d_%d.%s"%(item_id, exp_id, img_type), prog='dot')
     
    """
    pos = nx.graphviz_layout(DG)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    print len(DG.edges())
    print len(DG.nodes())
    nx.draw(DG, pos)
    plt.savefig(PREFIX_IMG+"directed_influence.%s"%img_type)
    plt.show()
    """

def category_vs_time(cat=1):
    # look at a particular category
    for c in Category.objects.all():
        print c.id, c.name

     
def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def memory_effect():
    """
        compare how long time difference affects choices between presurvey and order
    """

    x = []  # time difference
    y = []  # whether order changed or not
    exp_count = np.zeros((4,2)) # count of people in experiments
    common_array = {} 
    common_count = 0
    no_common_count = 0
    diff_perc = np.zeros(5)

    for u in OTNUser.objects.all():
        orders = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0)
        if orders.count() > 0:
            presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id)
            if presurvey.exists():
                p = presurvey[0]

                # check if order has shifted and then calculate the time difference

                presurvey_dishes = set()
                for d in p.favorite_dishes.all(): 
                    presurvey_dishes.add(d)

                ordered = set()
                t_diff = []
                for order in orders.all():
                    td = order.timestamp - p.timestamp
                    ts = total_seconds(td)
                    if ts > 0:
                        t_diff.append(ts)
                    for i in order.items.all():
                        ordered.add(i.item)

                # get items common in presurvey and order
                common = presurvey_dishes & ordered

                if len(common) > 0:
                    common_count += 1
                    common_array[u.id] = len(common) 
                    exp_count[order.table.experiment.id-1,0] += 1
                else:
                    no_common_count += 1
                    exp_count[order.table.experiment.id-1,1] += 1

                if len(t_diff)>0:
                    y.append(len(common))
                    x.append(np.mean(np.array(t_diff)))

                    diff_perc[len(common)] += 1


    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    print len(x), len(y)
    print diff_perc/float(np.sum(diff_perc))
    x_array = np.array(x)/3600.0/24.0
    ax1.scatter(x_array, y)
    m,b = np.polyfit(x_array, y, 1)
    print "Fit curve:", m, b
    print stats.linregress(x_array, y)

    ax1.set_xlabel( "Days")
    #ax1.set_xticks(np.array([1,2,3])+0.4)
    #ax1.set_xticklabels(['Friends', 'Features', 'Allergy'])
    plt.show()
            
def memory_effect_experiments():
    """
        compare how long time difference affects choices between presurvey and order
        and categorize by experimental group
    """

    x = [[], [], [], [], []]  # time difference
    y = [[], [], [], [], []]  # whether order changed or not
    exp_count = np.zeros((4,2)) # count of people in experiments
    common_array = {} 
    common_count = 0
    no_common_count = 0
    diff_perc = np.zeros(5)

    common_bin = [{}, {}, {}, {}, {}] 

    for o in Order.objects.all().annotate(num_items=Count('items')).filter(num_items__gt=0):
        u = o.user
        presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id)
        if presurvey.exists():
            p = presurvey[0]

            # check if order has shifted and then calculate the time difference
            presurvey_dishes = set()
            for d in p.favorite_dishes.all(): 
                presurvey_dishes.add(d)

            ordered = set()
            for i in o.items.all():
                ordered.add(i.item)

            td = o.timestamp - p.timestamp
            ts = total_seconds(td)
           
            # get items common in presurvey and order
            common = presurvey_dishes & ordered

            if len(common) > 0:
                common_count += 1
                common_array[u.id] = len(common) 
                exp_count[o.table.experiment.id-1,0] += 1
            else:
                no_common_count += 1
                exp_count[o.table.experiment.id-1,1] += 1

            if ts > 0:
                x[0].append(ts)
                y[0].append(len(common))
                x[o.table.experiment.id].append(ts)
                y[o.table.experiment.id].append(len(common))

                diff_perc[len(common)] += 1

                # per experiment
                td = ts/3600.0/24.0
                if len(common) not in common_bin[o.table.experiment.id]:
                    common_bin[o.table.experiment.id][len(common)] = []
                common_bin[o.table.experiment.id][len(common)].append(td) 

                # for all experiments
                if len(common) not in common_bin[0]:
                    common_bin[0][len(common)] = []
                common_bin[0][len(common)].append(td) 

    fig = plt.figure()
    ax1 = fig.add_subplot(411)
    ax2 = fig.add_subplot(412)
    ax3 = fig.add_subplot(413)
    ax4 = fig.add_subplot(414)
    print len(x[0]), len(y)
    print diff_perc/float(np.sum(diff_perc))
    print exp_count

    #x_array = np.array(x[0])/3600.0/24.0
    #ax1.scatter(x_array, y)
    x_array1 = np.array(x[1])/3600.0/24.0
    x_array2 = np.array(x[2])/3600.0/24.0
    x_array3 = np.array(x[3])/3600.0/24.0
    x_array4 = np.array(x[4])/3600.0/24.0

    ax1.scatter(np.array(x_array1), y[1], c='b')
    ax2.scatter(np.array(x_array2), y[2], c='g')
    ax3.scatter(np.array(x_array3), y[3], c='r')
    ax4.scatter(np.array(x_array4), y[4], c='m')

    ax1.set_xlabel( "Days")
    ax2.set_xlabel( "Days")
    ax3.set_xlabel( "Days")
    ax4.set_xlabel( "Days")
    ax3.set_ylabel( "Number of dishes from preselection")
    #ax1.set_xticks(np.array([1,2,3])+0.4)
    #ax1.set_xticklabels(['Friends', 'Features', 'Allergy'])


    fig2 = plt.figure()
    ax1 = fig2.add_subplot(511)
    ax2 = fig2.add_subplot(512)
    ax3 = fig2.add_subplot(513)
    ax4 = fig2.add_subplot(514)
    ax5 = fig2.add_subplot(515)

    ax1.boxplot([common_bin[0][0], common_bin[0][1], common_bin[0][2]])
    ax1.set_ylabel("Days")
    ax1.set_xticklabels([0,1,2])
    ax2.boxplot([common_bin[1][0], common_bin[1][1], common_bin[1][2]])
    ax2.set_ylabel("Days")
    ax2.set_xticklabels([0,1,2])
    ax3.boxplot([common_bin[2][0], common_bin[2][1], common_bin[2][2]])
    ax3.set_ylabel("Days")
    ax3.set_xticklabels([0,1,2])
    ax4.boxplot([common_bin[3][0], common_bin[3][1], common_bin[3][2]])
    ax4.set_ylabel("Days")
    ax4.set_xticklabels([0,1,2])
    ax5.boxplot([common_bin[4][0], common_bin[4][1], common_bin[4][2]])
    ax5.set_ylabel("Days")
    ax5.set_xticklabels([0,1,2])

    print stats.f_oneway(common_bin[0][0], common_bin[0][1], common_bin[0][2])
    print stats.f_oneway(common_bin[1][0], common_bin[1][1], common_bin[1][2])
    print stats.f_oneway(common_bin[2][0], common_bin[2][1], common_bin[2][2])
    print stats.f_oneway(common_bin[3][0], common_bin[3][1], common_bin[3][2])
    print stats.f_oneway(common_bin[4][0], common_bin[4][1], common_bin[4][2])


    print stats.f_oneway(common_bin[1][0], common_bin[2][0], common_bin[3][0], common_bin[4][0])
    print stats.f_oneway(common_bin[1][1], common_bin[2][1], common_bin[3][1], common_bin[4][1])
    print stats.f_oneway(common_bin[1][2], common_bin[2][2], common_bin[3][2], common_bin[4][2])
    
    plt.show()

def items_considered():

    for ev in EventMenuItem.objects.filter(action=EventMenuItem.CONSIDER):
        if ev.experiment.id == 1:
            ev.item

        # divide into each experiments and then see which ones are considered more

        # considering is a proxy to order, can check if it's ordered by checking
        # EventMenuItem.MARK 


def price_effect():
    """
        Measure the effects of price on people's prechoice versus actual choice

        Find the average price of entrees in presurvey

        Compare it to the price they chose at the restaurant (take difference) and
        see what the price looks like for different group sizes

    """
    
    # entree categories
    cat = [3,4,5,6,7,9]
    #cat = [3,5,7,9] - take out lobster and raw bar

    preselect_mu = {}
    for u in OTNUser.objects.all():
        fb_id = u.facebook_profile.facebook_id
        
        # find what a person has chosen during presurvey
        presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=fb_id)
        if not presurvey.exists():
            continue 
        else:
            presurvey = presurvey[0]
         
        preselect_sum = []
        preselect_avg = 0.0
        for k in presurvey.favorite_dishes.filter(category__in=cat):
            preselect_sum.append(k.cost())

        if len(preselect_sum) > 0:
            preselect_avg = np.mean(np.array(preselect_sum))
            preselect_mu[u.id] = preselect_avg

    # get the average price of ordered items
    order_mu = {}
    per_experiment = {}
    per_experiment[0] = []

    common_per_experiment = {}
    common_per_experiment[0] = []

    per_table = {}
    per_table[0] = []

    those_changed = [[], [], [], [], []]

    cheap_count = 0
    not_cheap_count = 0
    exp_cheap = np.zeros(4)
    common_count = 0
    no_common_count = 0

    orders = Order.objects.exclude(table__code='abcd').filter(items__item__category__in=cat).annotate(num_items=Count('items')).filter(num_items__gt=0).order_by("timestamp")
    total_orders = orders.count()
    print "Total orders:", total_orders 
    for o in orders: 

        u = o.user
        presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id)
        if presurvey.exists():
            p = presurvey[0]

            # check if order has shifted and then calculate the time difference
            presurvey_dishes = set()
            for d in p.favorite_dishes.all(): 
                presurvey_dishes.add(d)

            ordered = set()
            for i in o.items.all():
                ordered.add(i.item)

            td = o.timestamp - p.timestamp
            ts = total_seconds(td)
           
            # get items common in presurvey and order
            common = presurvey_dishes & ordered

            if len(common) > 0:
                common_count += 1
            else:
                no_common_count += 1
        
            order_sum = []
            order_avg = 0.0
            
            if o.user.id not in order_mu:
                order_mu[o.user.id] = []
            for r in o.items.filter(item__category__in=cat):
                order_sum.append(r.item.cost())

            order_avg = np.mean(np.array(order_sum))
            # find average price of each order per user
            order_mu[o.user.id].append(order_avg)

            # price difference
            if o.user.id not in preselect_mu:
                continue
            else:
                diff = order_avg - preselect_mu[o.user.id]
                if diff < -4.5:
                    print o.user.id, preselect_mu[o.user.id], order_avg
                    cheap_count += 1
                    exp_cheap[o.table.experiment.id-1] += 1
                elif diff > 5:
                    print o.user.id, preselect_mu[o.user.id], order_avg
                    not_cheap_count += 1
                #    continue

                if math.isnan(diff):
                    print o.user.id, preselect_mu[o.user.id], order_avg

            common_per_experiment[0].append(len(common))
            if o.table.experiment.id not in common_per_experiment:
                common_per_experiment[o.table.experiment.id] = []
            common_per_experiment[o.table.experiment.id].append(len(common))
            
            per_experiment[0].append( diff ) 
            if o.table.experiment.id not in per_experiment:
                per_experiment[o.table.experiment.id] = []
            per_experiment[o.table.experiment.id].append( diff )

            those_changed[len(common)].append(diff)

            # for different table size
            user_set = set()
            for e in o.table.table_orders.all():
                user_set.add( e.user )

            per_table[0].append(diff)
            if len(user_set) not in per_table:
                per_table[len(user_set)] = []
            per_table[len(user_set)].append(diff)
                
    # plot the price difference
    f1 = plt.figure()
    ax1 = f1.add_subplot(211)

    #print len(per_experiment[0])
    #print len(per_experiment[1])
    #print len(per_experiment[2])
    #print len(per_experiment[3])
    #print len(per_experiment[4])
    ax1.boxplot([per_experiment[0], per_experiment[1], per_experiment[2], per_experiment[3], per_experiment[4]])
    print stats.ttest_ind(per_experiment[1], per_experiment[4])
    ax1.set_title("Per Experiment Group")
    ax1.set_ylabel("Price difference")
    print stats.f_oneway(np.array(per_experiment[1]), 
                        np.array(per_experiment[2]), 
                        np.array(per_experiment[3]), 
                        np.array(per_experiment[4]))  

    #print stats.ttest_ind(np.array(per_experiment[1]), np.array(per_experiment[2]))

    ax2 = f1.add_subplot(212)
    ax2.boxplot([per_table[0], per_table[1], per_table[2], per_table[3], per_table[4]])
    ax2.set_title("Per Table Size")
    ax2.set_ylabel("Price difference")
    print stats.f_oneway(np.array(per_table[1]),
                        np.array(per_table[2]),
                        np.array(per_table[3]),
                        np.array(per_table[4]))

    f2 = plt.figure()

    ax1 = f2.add_subplot(511)
    ax2 = f2.add_subplot(512)
    ax3 = f2.add_subplot(513)
    ax4 = f2.add_subplot(514)
    ax5 = f2.add_subplot(515)

    ax1.scatter(per_experiment[0], common_per_experiment[0])
    ax1.set_xlim([-15, 25])
    ax2.scatter(per_experiment[1], common_per_experiment[1])
    ax2.set_xlim([-15, 25])
    ax3.scatter(per_experiment[2], common_per_experiment[2])
    ax3.set_xlim([-15, 25])
    ax4.scatter(per_experiment[3], common_per_experiment[3])
    ax4.set_xlim([-15, 25])
    ax5.scatter(per_experiment[4], common_per_experiment[4])
    ax5.set_xlim([-15, 25])
    
    f3 = plt.figure()

    ax1 = f3.add_subplot(111)

    ax1.boxplot(those_changed[0:3])
    #ax1.set_xticks(np.array([0,1,2])+0.4)
    ax1.set_xticklabels([0, 1, 2])

    ax1.set_title("Distribution of price difference between ordered and preselection")
    ax1.set_xlabel("Common orders from preselection")
    ax1.set_ylabel("Price difference (\$)")
    f3.savefig(PREFIX_IMG+"price_effect_on_order.%s"%img_type, bbox_inches="tight")
    print np.median(those_changed[0]), np.median(those_changed[1]), np.median(those_changed[2])

    print "Price effect on change:", stats.f_oneway(those_changed[0], those_changed[1], those_changed[2])


    print "People who are cheap:", cheap_count/float(total_orders)
    print "People who are not cheap:", not_cheap_count/float(total_orders)
    print "Cheap per experiment:", exp_cheap
    
    print "Number of orders per experiment:"
    print [(key, len(val)) for key,val in common_per_experiment.items()]
    total_per_experiment = np.array([len(val) for key,val in common_per_experiment.items()])

    cheap_diverts = 0
    for t in those_changed[0]:
        if t < -4.5:
            cheap_diverts += 1
    print "People who diverted that are cheap:", cheap_diverts/float(total_orders)
    cheap_converts = 0
    for t in those_changed[1]:
        if t < -4.5:
            cheap_converts += 1
    for t in those_changed[1]:
        if t < -4.5:
            cheap_converts += 1
    print "People who chose common item that are cheap:", cheap_converts/float(total_orders)

    cheap_all = np.zeros(5) 
    for key, val in per_experiment.items():
        for v in val:
            if v < -4.5:
                cheap_all[key] += 1 
    print "People who are cheap:", cheap_all/np.array(total_per_experiment, dtype="float")

    plt.show()


def order_time_vs_price(cat_var=1, exp_var=1):
    """
        See how long it takes vs price
    """

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(311)
    ax2 = fig1.add_subplot(312)
    ax3 = fig1.add_subplot(313)

    x = []
    y = []
    f = []
    c = []

    for cat in Category.objects.all():
        print cat.id, cat.name

    cat = Category.objects.get(id=cat_var)
    print "Observing:",cat.name, "- Experiment:", exp_var
    orders = Order.objects.filter(items__item__category=cat).filter(table__experiment__id=exp_var).annotate(num_items=Count('items')).filter(num_items__gt=0)
    print "Num orders:",orders.count()
    for o in orders:
        d1 = calculate_order_time(o)
        p1 = o.total_price_value() 

        x.append(d1[0])
        y.append(p1)
        f.append(d1[3])
        c.append(d1[1])

    n = len(y)
    # convert time to minus
    x = np.array(x)/60
    lmax = np.max(x)
    l = np.linspace(0,lmax,n)
    y = np.array(y)
    (ar,br) = np.polyfit(x,y,1)
    yr = np.polyval([ar,br],l)
    err = np.sqrt(np.sum((yr-y)**2)/n)
    pearson = np.sum((x-np.mean(x))*(y-np.mean(y)))/(np.std(x)*np.std(y)*(n-1))
    print "Slope: %s, Intercept: %s, Error: %f"%(str(ar), str(br), err)
    print "Correlation:", stats.linregress(x, y)
    print "Pearson:", pearson
    ax1.plot(l, yr, 'g--')
    ax1.plot(np.array(x), y, ".")
    ax1.set_title("Time vs Price")
    ax1.set_xlabel("Time (mins)")
    ax1.set_ylabel("Price")

    n = len(f)
    lmax = np.max(x)
    l = np.linspace(0,lmax,n)
    f = np.array(f)
    (ar,br) = np.polyfit(x,f,1)
    fr = np.polyval([ar, br],l)
    err = np.sqrt(np.sum((fr-c)**2)/n)
    pearson = np.sum((x-np.mean(x))*(f-np.mean(f)))/(np.std(x)*np.std(f)*(n-1))
    print "Slope: %s, Intercept: %s, Error: %f"%(str(ar), str(br), err)
    print "Correlation:", stats.linregress(x, f)
    print "Pearson:", pearson
    ax2.plot(l, fr, 'g--')
    ax2.plot(x, f, ".")
    ax2.set_title("Time vs Friends Clicked")
    ax2.set_xlabel("Time (mins)")
    ax2.set_ylabel("Friends Clicked")

    n = len(c)
    lmax = np.max(x)
    l = np.linspace(0,lmax,n)
    c = np.array(c)
    (ar,br) = np.polyfit(x,c,1)
    cr = np.polyval([ar, br],l)
    err = np.sqrt(np.sum((cr-c)**2)/n)
    pearson = np.sum((x-np.mean(x))*(c-np.mean(c)))/(np.std(x)*np.std(c)*(n-1))
    print "Slope: %s, Intercept: %s, Error: %f"%(str(ar), str(br), err)
    print "Correlation:", stats.linregress(x, c)
    print "Pearson:", pearson
    ax3.plot(l, cr, 'g--')
    ax3.plot(np.array(x), c, ".")
    ax3.set_title("Time vs Categories Clicked")
    ax3.set_xlabel("Time (mins)")
    ax3.set_ylabel("Categories Clicked")

    fig1.show()
        

def compare_first_vs_subsequent():
    """
        Compare <i>time distribution</i> of first time
        that users participated, versus subsequent times
        when users are more familiar with the menu

        Hope to see people order in shorter time.

        Only need to work with people who have ordered multiple times
        on a different day
    """

    num_people = 0
    dur_list1 = []
    dur_list2 = []
    # number of categories clicked distribution (first timer and 2nd timer)
    cat_click_list1 = []
    cat_click_list2 = []
    categories_clicked1 = np.zeros(13) 
    categories_clicked2 = np.zeros(13)
    friend_clicked1 = 0
    friend_clicked2 = 0
    friend_freq1 = []
    friend_freq2 = []
    feature_clicked1 = 0
    feature_clicked2 = 0
    feature_freq1 = []
    feature_freq2 = []
    allergy_clicked1 = 0
    allergy_clicked2 = 0
    allergy_freq1 = []
    allergy_freq2 = []

    dish_click1 = []
    dish_click2 = []
    
    for u in OTNUser.objects.all():
        # for people who have ordered more than 1 order
        orders = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0)
        if orders.count() > 1:
            num_people += 1
            
            # first order
            d1 = calculate_order_time(orders.order_by("timestamp")[0])
            # second order
            d2 = calculate_order_time(orders.order_by("timestamp")[1])

            dur_list1.append( d1[0] )
            dur_list2.append( d2[0] )

            # the number of categories that are clicked before deciding
            cat_click_list1.append(d1[1])
            cat_click_list2.append(d2[1])
            dish_click1.append(d1[8])
            dish_click2.append(d2[8])

            categories_clicked1[d1[1]] += 1
            categories_clicked2[d2[1]] += 1

            friend_clicked1 += d1[2]
            friend_clicked2 += d2[2]
            friend_freq1.append(d1[3])
            friend_freq2.append(d2[3])
            feature_clicked1 += d1[4]
            feature_clicked2 += d2[4]
            feature_freq1.append(d1[5])
            feature_freq2.append(d2[5])
            allergy_clicked1 += d1[6]
            allergy_clicked2 += d2[6]
            allergy_freq1.append(d1[7])
            allergy_freq2.append(d2[7])
            
    # plot the duration distribution graph 
    dur_array1 = np.array(dur_list1)
    dur_array2 = np.array(dur_list2)


    fig2 = plt.figure(figsize=(6,4))
    fig2.subplots_adjust(hspace=0.4)
    ax9 = fig2.add_subplot(111)
    ax9.hist(dur_array1, bins=1600, normed=True, cumulative=True, histtype='step', label="1st time")
    ax9.axis([0, 1600, 0, 1])
    ax9.hist(dur_array2, bins=1600, normed=True, cumulative=True, histtype='step', label="Repeat", ls="dashed")
    ax9.set_title('Order Duration Distribution (cdf)')
    ax9.set_xlabel('Seconds to finish ordering (s)')
    ax9.legend(loc=4)

    fig = plt.figure(figsize=(12,12))
    fig.subplots_adjust(hspace=0.4)
    ax1 = fig.add_subplot(321)
    ax1.hist(dur_array1, bins=1600, normed=True, cumulative=True, histtype='step', label="1st time")
    ax1.axis([0, 1600, 0, 1])
    ax1.hist(dur_array2, bins=1600, normed=True, cumulative=True, histtype='step', label="Repeat", ls="dashed")
    ax1.set_title('Order Duration Distribution (cdf)')
    ax1.set_xlabel('Seconds to finish ordering (s)')
    ax1.legend(loc=4)

    ax2 = fig.add_subplot(322)
    ax2.boxplot([dish_click1, dish_click2])
    ax2.set_title("Mean \# of dishes clicked")
    print "Mean # of dishes clicked by 1st timer:", np.mean(dish_click1)
    print "Mean # of dishes clicked by 2nd timer:", np.mean(dish_click2)
    print stats.ttest_rel(dish_click1, dish_click2)

    # the number of categories clicked before finishing order 
    ax3 = fig.add_subplot(323)
    ax3.boxplot([cat_click_list1, cat_click_list2])
    ax3.set_title("Mean \# of categories clicked")
    print "Mean # of categories clicked by 1st timer:", np.mean(cat_click_list1)
    print "Mean # of categories clicked by 2nd timer:", np.mean(cat_click_list2)
    print stats.ttest_rel(cat_click_list1, cat_click_list2)

    ax4 = fig.add_subplot(324)
    ax4.bar(np.arange(1,len(categories_clicked1)+1)-0.4, categories_clicked1/np.sum(categories_clicked1), label="1st visit", width=0.4)
    ax4.bar(np.arange(1,len(categories_clicked2)+1), categories_clicked2/np.sum(categories_clicked2), color="r", label="2nd visit", width=0.4)
    ax4.set_title('\% of people that clicked \# of categories')
    ax4.axis([0, 13, 0, 0.4])

    # the number of people click on special categories
    ax5 = fig.add_subplot(325)
    a = np.array(friend_freq1)-np.array(feature_freq1)
    b = np.array(friend_freq2)-np.array(feature_freq2)
    ax5.boxplot([a, b])
    print stats.ttest_rel(-a, -b)
    ax5.set_title('Impact of friends versus Chef')

    # the average number or percentage of times people click on special categories
    ax6 = fig.add_subplot(326)
    ax6.bar(np.array([1,2,3])-0.4, [np.mean(np.array(friend_freq1)), np.mean(np.array(feature_freq1)), np.mean(np.array(allergy_freq1))], width=0.4, label="First timers")
    ax6.bar([1,2,3], [np.mean(np.array(friend_freq2)), np.mean(np.array(feature_freq2)), np.mean(np.array(allergy_freq2))], color="r", width=0.4, label="Repeat")
    ax6.set_title('\% of special categories clicked')
    plt.xticks([1,2,3], ['Friends', 'Features', 'Allergy'])
    ax6.legend()

    fig.savefig(PREFIX_IMG+"first_repeat.%s"%img_type, bbox_inches="tight")
    fig2.savefig(PREFIX_IMG+"first_repeat_time.%s"%img_type, bbox_inches="tight")
    fig.show()

def consider_items():
    """
        How many items do they consider before deciding
        on the final order based on the experimental group
    """

    pass

def time_distribution_experiment(exps=[1]):

    fig = plt.figure(figsize=(12,12))
    fig.subplots_adjust(hspace=0.4)

    ax1 = fig.add_subplot(321)
    ax2 = fig.add_subplot(322)
    ax3 = fig.add_subplot(323)
    ax4 = fig.add_subplot(324)

    ax5 = fig.add_subplot(325)
    ax6 = fig.add_subplot(326)

    fig2 = plt.figure(figsize=(12,12))
    fig2.subplots_adjust(hspace=0.4)
    ax7 = fig2.add_subplot(211)
    ax8 = fig2.add_subplot(212)

    fig3 = plt.figure(figsize=(6,4))
    fig3.subplots_adjust(hspace=0.4)
    ax9 = fig3.add_subplot(111)

    fig4 = plt.figure(figsize=(6,4))
    fig4.subplots_adjust(hspace=0.4)
    ax10 = fig4.add_subplot(111)

    dur_array = []
    cat_click_array = []
    item_click_array = []

    dur_split_array = []

    for exp in exps:
        orders = Order.objects.exclude(table__code="abcd").exclude(user__otnuser__my_email="kool@mit.edu").filter(table__experiment__id=exp).order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)

        friend_clicked = 0
        features_clicked = 0
        allergies_clicked = 0
        categories_clicked = np.zeros(20)
        items_clicked = np.zeros(60)

        total = orders.count()

        i = 0
        dur_array.append(np.zeros(orders.count()))
        cat_click_array.append(np.zeros(orders.count()))
        item_click_array.append(np.zeros(orders.count()))

        dur_split_array.append([[],[],[]])

        for o in orders: 
            cat_click = 0
            item_click = 0
            # for events where items have been ordered
            start_time = datetime.now() 
            end_time = datetime.now()-timedelta(days=1000)
            evtbasic = EventBasic.objects.filter(order=o)
            for e in evtbasic:
                if e.timestamp < start_time:
                    start_time = e.timestamp
                if e.timestamp > end_time:
                    end_time = e.timestamp
            evtspecial = EventSpecial.objects.filter(order=o)
            for e in evtspecial:
                """
                if e.timestamp < start_time:
                    start_time = e.timestamp
                if e.timestamp > end_time:
                    end_time = e.timestamp
                """
                if e.category == EventSpecial.FRIENDS:
                    friend_clicked += 1
                if e.category == EventSpecial.CHEFS:
                    features_clicked += 1
                if e.category == EventSpecial.ALLERGIES:
                    allergies_clicked += 1
            evtmenu = EventMenuItem.objects.filter(order=o)
            for e in evtmenu:
                if e.timestamp < start_time:
                    start_time = e.timestamp
                if e.timestamp > end_time:
                    end_time = e.timestamp
                item_click += 1
            #item_click = EventMenuItem.objects.filter(order=o, action=EventMenuItem.CONSIDER).count()
            evtcategory = EventCategory.objects.filter(order=o)
            for e in evtcategory:
                cat_click += 1
                """
                if e.timestamp < start_time:
                    start_time = e.timestamp
                if e.timestamp > end_time:
                    end_time = e.timestamp
                """ 
            # collect all timestamps and sort it
            duration = mktime(end_time.timetuple())-mktime(start_time.timetuple())
            dur_array[exp-1][i] = duration

            if duration < 300:
              dur_split_array[exp-1][0].append(duration)
            elif duration < 700:
              dur_split_array[exp-1][1].append(duration)
            else:
              dur_split_array[exp-1][2].append(duration)

            # the number of categories that are clicked before deciding
            cat_click_array[exp-1][i] = cat_click
            item_click_array[exp-1][i] = item_click

            categories_clicked[cat_click] += 1
            items_clicked[item_click] += 1
            i += 1

        # plot the duration distribution graph 
        exp_color = ["#000000", "#54e373", "#ff380d", "#4855b1", "#c48d4f"] 
        ax1.hist(dur_array[exp-1], bins=1600, normed=True, cumulative=True, histtype='step', label="Exp %d"%exp, color=exp_color[exp])
        #ax9.hist(dur_array[exp-1], bins=1600, normed=True, cumulative=True, histtype='step', label="Exp %d"%exp, color=exp_color[exp])
        linestyles = ['solid', 'solid', 'dashed', 'dashdot', 'dotted']
        ax9.hist(dur_array[exp-1], bins=1600, normed=True, cumulative=True, histtype='step', label="Exp %d"%exp, linestyle=linestyles[exp])
        print "Group %d"%exp, np.mean(dur_array[exp-1]), np.std(dur_array[exp-1])

        # the number of categories clicked before finishing order 
        ax3.bar(np.arange(1,len(items_clicked)+1)-0.6+exp*0.2, items_clicked/float(total), width=0.2, label="Exp %d"%exp, color=exp_color[exp])

        # the number of categories clicked before finishing order 
        ax5.bar(np.arange(1,len(categories_clicked)+1)-0.6+exp*0.2, categories_clicked/float(total), width=0.2, label="Exp %d"%exp, color=exp_color[exp])
        hatches = ['/', '/', '-', 'x', 'o']

        # the number of times people click on special categories
        ax7.bar(np.array([1,2,3])-0.2+exp*0.2, np.array([friend_clicked, features_clicked, allergies_clicked])/float(total), width=0.2, label="Exp %d"%exp, color=exp_color[exp])
        #plt.xticks([1,2,3], ['Friends', 'Features', 'Allergy'])

    ax1.set_title("Order Duration Distribution (cdf)")
    ax1.set_xlabel("Seconds to finish ordering (s)")
    ax1.legend(loc=4)
    ax1.axis([0, 1800, 0, 1])

    ax9.set_title("Order Duration Distribution (cdf)")
    ax9.set_xlabel("Seconds to finish ordering (s)")
    ax9.legend(loc=4)
    ax9.axis([0, 1800, 0, 1])

    ax3.set_title("Number of Items Clicked")
    ax3.legend()

    ax5.set_title("Percentage of Categories Clicked")
    ax5.set_ylabel("Percentage")
    ax5.legend()

    ax6.set_title("Categories Clicked per Experimental Group")
    ax6.set_ylabel("Percentage")

    ax7.set_xticks(np.array([1,2,3])+0.4)
    ax7.set_xticklabels(['Friends', 'Features', 'Allergy'])
    ax7.set_title("Number of Times Special Categories Clicked")
    ax7.set_xlim(1,5)

    ax7.legend()

    ax2.boxplot(dur_array)
    print len(dur_array[0]), len(dur_array[1]), len(dur_array[2]), len(dur_array[3])
    print stats.f_oneway(dur_array[0], dur_array[1]) 
    print stats.f_oneway(dur_array[0], dur_array[2]) 
    print stats.f_oneway(dur_array[0], dur_array[3]) 
    print stats.f_oneway(dur_array[1], dur_array[2])
    print stats.f_oneway(dur_array[1], dur_array[3])
    print stats.f_oneway(dur_array[2], dur_array[3])
    ax6.boxplot(cat_click_array)
    print "Categories clicked"
    print stats.f_oneway(*cat_click_array)
    print stats.f_oneway(cat_click_array[0], cat_click_array[1]) 
    print stats.f_oneway(cat_click_array[0], cat_click_array[2]) 
    print stats.f_oneway(cat_click_array[0], cat_click_array[3]) 
    print stats.f_oneway(cat_click_array[1], cat_click_array[2])
    print stats.f_oneway(cat_click_array[1], cat_click_array[3])
    print stats.f_oneway(cat_click_array[2], cat_click_array[3])
    ax4.boxplot(item_click_array)
    print "Items clicked"
    print stats.f_oneway(*item_click_array)
    print stats.f_oneway(item_click_array[0], item_click_array[1]) 
    print stats.f_oneway(item_click_array[0], item_click_array[2]) 
    print stats.f_oneway(item_click_array[0], item_click_array[3]) 
    print stats.f_oneway(item_click_array[1], item_click_array[2])
    print stats.f_oneway(item_click_array[1], item_click_array[3])
    print stats.f_oneway(item_click_array[2], item_click_array[3])


    fig5 = plt.figure() #figsize=(8,8))
    fig5.subplots_adjust(hspace=0.4)
    ax11 = fig5.add_subplot(111)

    ax11.boxplot(dur_split_array[0]+dur_split_array[1]+dur_split_array[2]+dur_split_array[3], positions=[1,5,9,2,6,10,3,7,11,4,8,12])
    ax11.set_xticklabels(['1','1','1','2','2','2','3','3','3','4','4','4'])
    ax11.set_xlabel("Experimental group in each time segment")
    ax11.set_ylabel("Time (seconds)")

    print "Split duration segments"
    print stats.f_oneway(dur_split_array[0][0], dur_split_array[1][0], dur_split_array[2][0], dur_split_array[3][0])
    print stats.f_oneway(dur_split_array[0][1], dur_split_array[1][1], dur_split_array[2][1], dur_split_array[3][1])
    print stats.f_oneway(dur_split_array[0][2], dur_split_array[1][2], dur_split_array[2][2], dur_split_array[3][2])

    fig.savefig(PREFIX_IMG+"time_distribution.%s"%img_type, bbox_inches="tight")
    fig3.savefig(PREFIX_IMG+"time_distribution_exp.%s"%img_type, bbox_inches="tight")
    fig4.savefig(PREFIX_IMG+"categories_clicked_exp.%s"%img_type, bbox_inches="tight")
    fig5.savefig(PREFIX_IMG+"time_duration_segments.%s"%img_type, bbox_inches="tight")

    fig.show()
    fig2.show()

def time_distribution():
    orders = Order.objects.exclude(table__code="abcd").exclude(user__otnuser__my_email="kool@mit.edu").order_by('-timestamp').annotate(num_items=Count('items')).filter(num_items__gt=0)

    friend_clicked = 0
    features_clicked = 0
    allergies_clicked = 0
    categories_clicked = np.zeros(20)

    print orders.count()

    i = 0
    dur_array = np.zeros(orders.count()) 
    for o in orders: 
        cat_click = 0
        # for events where items have been ordered
        start_time = datetime.now() 
        end_time = datetime.now()-timedelta(days=365)
        evtbasic = EventBasic.objects.filter(order=o)
        for e in evtbasic:
            if e.timestamp < start_time:
                start_time = e.timestamp
            if e.timestamp > end_time:
                end_time = e.timestamp
        evtspecial = EventSpecial.objects.filter(order=o)
        for e in evtspecial:
            if e.timestamp < start_time:
                start_time = e.timestamp
            if e.timestamp > end_time:
                end_time = e.timestamp
            if e.category == EventSpecial.FRIENDS:
                friend_clicked += 1
            if e.category == EventSpecial.CHEFS:
                features_clicked += 1
            if e.category == EventSpecial.ALLERGIES:
                allergies_clicked += 1
        evtmenu = EventMenuItem.objects.filter(order=o)
        for e in evtmenu:
            if e.timestamp < start_time:
                start_time = e.timestamp
            if e.timestamp > end_time:
                end_time = e.timestamp
        evtcategory = EventCategory.objects.filter(order=o)
        for e in evtcategory:
            cat_click += 1
            if e.timestamp < start_time:
                start_time = e.timestamp
            if e.timestamp > end_time:
                end_time = e.timestamp
    
        # collect all timestamps and sort it
        duration = mktime(end_time.timetuple())-mktime(start_time.timetuple())
        dur_array[i] = duration
        # the number of categories that are clicked before deciding
        categories_clicked[cat_click] += 1
        i += 1

    # plot the duration graph and the different categories that are clicked
    fig = plt.figure()
    ax1 = fig.add_subplot(311)

    ax1.hist(dur_array, 30)

    ax2 = fig.add_subplot(312)

    ax2.bar(np.arange(1,len(categories_clicked)+1),categories_clicked)

    ax3 = fig.add_subplot(313)
    ax3.bar([1,2,3], [friend_clicked, features_clicked, allergies_clicked])
    fig.show()

def menu_choice_matrix():
    # an appetizer, soup/salad, side, entree matrix
    surveys = LegalsPopulationSurvey.objects.all().values("facebook_id")
    c = Category.objects.get(id=1)
    items = MenuItem.objects.filter(category=c)
    num_items = items.count()

    i = 0
    choices = {}
    for m in items:
        people = LegalsPopulationSurvey.objects.filter(favorite_dishes=m)
        for p in people:
            if p.facebook_id in choices:
                choices[p.facebook_id][i] = 1
            else:
                choices[p.facebook_id] = np.zeros(num_items)
                choices[p.facebook_id][i] = 1
        i += 1

    # create matrix
    list_of_arrays = []
    index_to_user = [] 
    for key, value in choices.items():
        list_of_arrays.append(value) 
        index_to_user.append(key)

    matrix = np.matrix(list_of_arrays)
    return matrix

def menu_choice_distribution():
    """
        The distribution of menu items for 
        - presurvey participants
        - for diners' (ordered) presurvey 
        - for orders people have ordered at the restaurant
    """

    fig = plt.figure()

    # presurvey of everybody 
    menu_item_list = []
    menu_item_count = []
    legend = []

    ax1 = fig.add_subplot(411)
    for m in MenuItem.objects.all().order_by('price'):
        n = m.pre_favorite_dishes.all().values('facebook_id').distinct().count()
        menu_item_list.append( m.name )
        menu_item_count.append(n)
        if m.price > 0:
            legend.append((m.id, m.name, "%.2f"%m.price))
        elif m.price == -1:
            legend.append((m.id, m.name, "market price"))
        else:
            legend.append((m.id, m.name, "%.2f"%m.optionprice.price_one))

    ind = np.arange(1,len(menu_item_count)+1)
    ax1.bar(ind, menu_item_count )

    ax1.set_xticks(ind)
    graph_xlim = ax1.get_xlim()
    ax1.xaxis.set_major_locator(MaxNLocator(20))
    #ax1.set_xticklabels( menu_item_list, rotation=45 )
    ax1.set_title('Presurvey of All')

    arr1 = np.array(menu_item_count)

    # presurvey of people participated
    menu_item_list = []
    menu_item_count = []

    ax1 = fig.add_subplot(412)

    fb_participants = [] 
    for u in OTNUser.objects.filter(voucher=True):
        fb_participants.append(u.facebook_profile.facebook_id)

    for m in MenuItem.objects.all().order_by('price'):
        n = m.pre_favorite_dishes.filter(facebook_id__in=fb_participants).values('facebook_id').distinct().count()
        menu_item_list.append( m.name )
        menu_item_count.append(n)

    ind = np.arange(1,len(menu_item_count)+1)
    ax1.bar(ind, menu_item_count )

    ax1.set_xticks(ind)
    ax1.xaxis.set_major_locator(MaxNLocator(20))
    #ax1.set_xticklabels( menu_item_list, rotation=45 )
    ax1.set_title('Presurvey of Diners')

    arr2 = np.array(menu_item_count)

    # people actually eaten 
    menu_item_list = []
    menu_item_count = []

    ax1 = fig.add_subplot(413)
    for m in MenuItem.objects.all().order_by('price'):
        n = m.menuitemreview_set.all().count()
        menu_item_list.append( m.name )
        menu_item_count.append(n)

    ind = np.arange(1,len(menu_item_count)+1)
    ax1.bar(ind, menu_item_count )

    ax1.set_xticks(ind)
    ax1.xaxis.set_major_locator(MaxNLocator(20))
    #ax1.set_xticklabels( menu_item_list, rotation=45 )
    ax1.set_title('Actual orders')

    arr3 = np.array(menu_item_count)

    # people actually eaten 
    menu_item_list = []
    menu_item_count = []

    ax1 = fig.add_subplot(414)
    i = 1
    for m in MenuItem.objects.all().order_by('price'):
        n = m.eventmenuitem_set.filter(action=EventMenuItem.CONSIDER).count()
        menu_item_list.append( m.name.encode('ascii', 'ignore' )+"(%d)"%i)
        menu_item_count.append(n)
        i+=1

    ind = np.arange(1,len(menu_item_count)+1)
    ax1.bar(ind, menu_item_count )

    ax1.set_xticks(ind)
    ax1.xaxis.set_major_locator(MaxNLocator(20))
    #ax1.set_xticklabels( menu_item_list, rotation=45 )
    ax1.set_xlim(graph_xlim)
    ax1.set_title('Considered')

    arr4 = np.array(menu_item_count)

    i = 1
    for l in legend:
        print i, l
        i += 1
    fig.show()

    # calculate correlation between two presurvey groups
    sum1 = np.sum(arr1)
    sum2 = np.sum(arr2)
    n = len(arr1)
    num = np.sum(arr1*arr2)-(sum1*sum2/n) 
    x1 = (np.sum(arr1**2)-sum1**2/n)
    x2 = (np.sum(arr2**2)-sum2**2/n)
    y = float(x1)*float(x2)
    den = np.sqrt(y)
    print num, den
    print "Presurvey all vs Presurvey participants:", num/den

    # calculate correlation between presurvey and ordered
    sum2 = np.sum(arr2)
    sum3 = np.sum(arr3)
    n = len(arr3)
    num = np.sum(arr2*arr3)-(sum3*sum2/n) 
    den = np.sqrt((np.sum(arr3**2)-sum3**2/n)*(np.sum(arr2**2)-sum2**2/n))
    print num, den
    print "Presurvey participants vs Participant orders:", num/den

    # calculate correlation between presurvey and ordered
    sum2 = np.sum(arr2)
    print len(arr2), len(arr4)
    sum4 = np.sum(arr4)
    n = len(arr3)
    num = np.sum(arr2*arr4)-(sum4*sum2/n) 
    den = np.sqrt((np.sum(arr4**2)-sum4**2/n)*(np.sum(arr2**2)-sum2**2/n))
    print num, den
    print "Presurvey participants vs Participant considerations:", num/den

    # calculate correlation between presurvey and ordered
    sum3 = np.sum(arr3)
    sum4 = np.sum(arr4)
    n = len(arr3)
    num = np.sum(arr3*arr4)-(sum4*sum3/n) 
    den = np.sqrt((np.sum(arr4**2)-sum4**2/n)*(np.sum(arr3**2)-sum3**2/n))
    print num, den
    print "Participant orders vs Participant considerations:", num/den

def menu_choice_distribution_exp(cat=1, exp=1):
    """
        The distribution of menu items for 
        - presurvey participants
        - for diners' (ordered) presurvey 
        - for orders people have ordered at the restaurant
    """

    fig = plt.figure()

    # presurvey of everybody 
    menu_item_list = []
    menu_item_count = []
    legend = []

    cat_name = Category.objects.get(id=cat).name

    ax1 = fig.add_subplot(411)
    for m in MenuItem.objects.filter(category=cat).exclude(id=56).order_by('price'):
        n = m.pre_favorite_dishes.all().values('facebook_id').distinct().count()
        menu_item_list.append( m.name.encode('ascii', 'ignore' ))
        menu_item_count.append(n)
        if m.price > 0:
            legend.append((m.id, m.name, "%.2f"%m.price))
        elif m.price == -1:
            legend.append((m.id, m.name, "market price"))
        else:
            legend.append((m.id, m.name, "%.2f"%m.optionprice.price_one))

    ind = np.arange(1,len(menu_item_count)+1)
    ax1.bar(ind, menu_item_count )

    ax1.set_xticks(ind)
    #ax1.xaxis.set_major_locator(MaxNLocator(20))
    #ax1.set_xticklabels( menu_item_list, rotation=45 )
    graph_xlim = ax1.get_xlim()
    ax1.set_xlim(graph_xlim)
    ax1.set_title('Presurvey of All for %s'%cat_name)

    arr1 = np.array(menu_item_count)

    # presurvey of people participated
    menu_item_list = []
    menu_item_count = []

    ax1 = fig.add_subplot(412)

    fb_participants = [] 
    for u in OTNUser.objects.filter(voucher=True):
        for o in u.legals_order.all():
            if exp == 0:
                fb_participants.append(u.facebook_profile.facebook_id)
            elif o.table.experiment.id == exp:
                fb_participants.append(u.facebook_profile.facebook_id)

    for m in MenuItem.objects.filter(category__id=cat).exclude(id=56).order_by('price'):
        n = m.pre_favorite_dishes.filter(facebook_id__in=fb_participants).values('facebook_id').distinct().count()
        menu_item_list.append( m.name.encode('ascii', 'ignore' ))
        menu_item_count.append(n)

    ind = np.arange(1,len(menu_item_count)+1)
    ax1.bar(ind, menu_item_count )

    ax1.set_xticks(ind)
    #ax1.xaxis.set_major_locator(MaxNLocator(20))
    #ax1.set_xticklabels( menu_item_list, rotation=45 )
    ax1.set_xlim(graph_xlim)
    ax1.set_title('Presurvey of Diners in Experimental Group')

    arr2 = np.array(menu_item_count)

    # people actually eaten 
    menu_item_list = []
    menu_item_count = []

    ax1 = fig.add_subplot(413)
    for m in MenuItem.objects.filter(category__id=cat).exclude(id=56).order_by('price'):
        if exp == 0:
            n = m.menuitemreview_set.all().count()
        else:
            n = m.menuitemreview_set.filter(legals_ordered__table__experiment__id=exp).count()
        menu_item_list.append( m.name.encode('ascii', 'ignore' ))
        menu_item_count.append(n)

    ind = np.arange(1,len(menu_item_count)+1)
    ax1.bar(ind, menu_item_count )

    ax1.set_xticks(ind)
    #ax1.xaxis.set_major_locator(MaxNLocator(20))
    #ax1.set_xticklabels( menu_item_list, rotation=45 )
    ax1.set_xlim(graph_xlim)
    ax1.set_title('Actual orders (Exp: %d)'%exp)

    arr3 = np.array(menu_item_count)

    menu_item_list = []
    menu_item_count = []

    ax1 = fig.add_subplot(414)
    i = 1
    for m in MenuItem.objects.filter(category__id=cat).exclude(id=56).order_by('price'):
        if exp == 0:
            n = m.eventmenuitem_set.filter(action=EventMenuItem.CONSIDER).count()
        else:
            n = m.eventmenuitem_set.filter(experiment__id=exp, action=EventMenuItem.CONSIDER).count()
        menu_item_list.append( m.name.encode('ascii', 'ignore' )+"(%d)"%i)
        menu_item_count.append(n)
        i+=1

    ind = np.arange(1,len(menu_item_count)+1)
    ax1.bar(ind, menu_item_count )

    ax1.set_xticks(ind)
    #ax1.xaxis.set_major_locator(MaxNLocator(20))
    ax1.set_xticklabels( menu_item_list, rotation=45 )
    ax1.set_xlim(graph_xlim)
    ax1.set_title('Considered (Exp: %d)'%exp)

    arr4 = np.array(menu_item_count)

    print "***** Legend *****"
    i = 1
    for l in legend:
        print i, l
        i += 1
    fig.show()

    # calculate correlation between two presurvey groups
    sum1 = np.sum(arr1)
    sum2 = np.sum(arr2)
    n = len(arr1)
    num = np.sum(arr1*arr2)-(sum1*sum2/n) 
    x1 = (np.sum(arr1**2)-sum1**2/n)
    x2 = (np.sum(arr2**2)-sum2**2/n)
    y = float(x1)*float(x2)
    den = np.sqrt(y)
    print "Pearson correlation:", num, den
    print "Presurvey all vs Presurvey participants:", num/den

    # calculate correlation between presurvey and ordered
    sum2 = np.sum(arr2)
    sum3 = np.sum(arr3)
    n = len(arr3)
    num = np.sum(arr2*arr3)-(sum3*sum2/n) 
    den = np.sqrt((np.sum(arr3**2)-sum3**2/n)*(np.sum(arr2**2)-sum2**2/n))
    print "Pearson correlation:", num, den
    print "Presurvey participants vs Participant orders:", num/den

    # calculate correlation between presurvey and ordered
    sum2 = np.sum(arr2)
    #print len(arr2), len(arr4)
    sum4 = np.sum(arr4)
    n = len(arr3)
    num = np.sum(arr2*arr4)-(sum4*sum2/n) 
    den = np.sqrt((np.sum(arr4**2)-sum4**2/n)*(np.sum(arr2**2)-sum2**2/n))
    print "Pearson correlation:", num, den
    print "Presurvey participants vs Participant considerations:", num/den

    # calculate correlation between presurvey and ordered
    sum3 = np.sum(arr3)
    sum4 = np.sum(arr4)
    n = len(arr3)
    num = np.sum(arr3*arr4)-(sum4*sum3/n) 
    den = np.sqrt((np.sum(arr4**2)-sum4**2/n)*(np.sum(arr3**2)-sum3**2/n))
    print "Pearson correlation:", num, den
    print "Participant orders vs Participant considerations:", num/den

def order_duration_array(order_set):
    """
        helper function to find out the order times of orders
        in the set
    """
    order_durations = np.zeros(len(order_set))
    i = 0
    for o in list(order_set):
        d = calculate_order_time(o)
        order_durations[i] = d[0]
        i += 1

    return order_durations, np.median(order_durations), np.std(order_durations)

def day_difference_between_orders():

    h_diff = timedelta(hours=1)
    for t in TableCode.objects.all():
        l_orders = [o for o in t.table_orders.all()]
        for i, o in enumerate(l_orders): 
            for p in l_orders[i+1:]:
                diff = o.timestamp-p.timestamp
                if diff.days == -1:
                    print (p.timestamp-o.timestamp).days, o.timestamp, p.timestamp
                    if diff > h_diff:
                        print "Different order"
                else:
                    print (o.timestamp-p.timestamp).days,  o.timestamp, p.timestamp
                    if diff > h_diff:
                        print "Different order"

def connectedness():
    """
        number of friends        
    """

    max_table_size = 7
    h_diff = timedelta(hours=1)

    #orders = Order.objects.all().annotate(num_items=Count('items')).filter(num_items__gt=0)
    orders = Order.objects.all()

    # find all the diners
    diners_set = set([o.user for o in orders])
    diners_id_set = set([o.user.id for o in orders])
    fb_diners_set = set([o.user.facebook_profile.facebook_id for o in orders])
    
    diners = list(diners_set)
    print len(diners)
    diners_id = list(diners_id_set)
    fb_diners = list(fb_diners_set)

    # log num of friends
    all_fb_friends = []
    otn_fb_friends = []

    # mean order time
    avg_order_time = [[], [], [], [], []]
    median_order_time = [[], [], [], [], []]
    o_mu_time_friends = [{}, {}, {}, {}, {}]
    o_median_time_friends = [{}, {}, {}, {}, {}]

    # for every diner
    for u in diners:
        # get all the Facebook friends
        uf = Friends.objects.get(facebook_id=u.facebook_profile.facebook_id)
        # store Facebook friend count 
        all_fb_friends.append(uf.friends.all().count())

        # Facebook friends that participated 
        otn_friends = uf.friends.filter(facebook_id__in=fb_diners)

        # TODO: need to filter only friends that came before
        # store OTN friends count
        otn_fb_friends.append(otn_friends.count())

        # for each experiment (0th element is all the durations)
        exp_times = [[], [], [], [], []]
        for o in u.legals_order.all():
            if o.items.count() > 0:
                duration = calculate_order_time(o)[0]
                exp_times[0].append(duration)
                exp_times[o.table.experiment.id].append(duration)


        # for each experiment get mean and median order times 
        mu = np.zeros(5) 
        mdn = np.zeros(5)
        for e in range(5):
            if e==0 or len(exp_times[e])>0:
                mu[e] = np.mean(np.array(exp_times[e]))
                mdn[e] = np.median(exp_times[e])

                avg_order_time[e].append(mu[e])
                median_order_time[e].append(mdn[e])

                if otn_friends.count() in o_mu_time_friends[e]:
                    o_mu_time_friends[e][otn_friends.count()].append(mu[e])
                else:
                    o_mu_time_friends[e][otn_friends.count()] = []
                    o_mu_time_friends[e][otn_friends.count()].append(mu[e])

                if otn_friends.count() in o_median_time_friends[e]:
                    o_median_time_friends[e][otn_friends.count()].append(mdn[e])
                else:
                    o_median_time_friends[e][otn_friends.count()] = []
                    o_median_time_friends[e][otn_friends.count()].append(mdn[e])

    fig1 = plt.figure(figsize=(12,12))
    ax1 = fig1.add_subplot(411)
    ax2 = fig1.add_subplot(412)
    ax3 = fig1.add_subplot(413) 
    ax4 = fig1.add_subplot(414) 

    ax1.plot(otn_fb_friends, avg_order_time[0], "go", otn_fb_friends, median_order_time[0], "ro") 
    ax2.plot(all_fb_friends, avg_order_time[0], "go", all_fb_friends, median_order_time[0], "ro")
    print "Correlation of friends versus ordering time:", stats.linregress(otn_fb_friends, avg_order_time[0])
    print len(otn_fb_friends), len(avg_order_time[0])

    box_data = []
    # box plot of time to order versus friends in OTN
    for n in range(20):
        if n in o_mu_time_friends[0]:
            box_data.append(o_mu_time_friends[0][n])
        else:
            box_data.append([])
    ax3.boxplot(box_data)

    # plot of mean time to order between experimental groups
    box_data = [[], [], [], [], []]
    for e in [0, 1,2,3,4]:
        for n in range(20):
            if n in o_mu_time_friends[e]:
                box_data[e].append(np.mean(np.array(o_mu_time_friends[e][n])))
            else:
                box_data[e].append(0)
    x = range(20)
    ax4.plot(x, box_data[1], label="grp 1") 
    ax4.plot(x, box_data[2], label="grp 2")
    ax4.plot(x, box_data[3], label="grp 3")
    ax4.plot(x, box_data[4], label="grp 4")
    ax4.legend()
    fig1.show()

    # calculate influencers
    exp_id = 0
    influencers = {}    # virtual influencers that influenced user
    influenced = {}     # orders influenced by certain participants 
    local_influence = {}

    # find out if each user had any friend influence in order
    for m in MenuItem.objects.all():
        # 1. Go through each menu item and find all orders with this menu item 
        orders = set() 

        # for each menu item get all the people ordered sorted by time and if they are friends
        # create a link from prev to next
        for r in m.menuitemreview_set.all():
            if r.legals_ordered.all().count() > 0:
                for o in r.legals_ordered.all():
                    if exp_id == 0:
                        orders.add(o)
                    elif o.table.experiment.id==exp_id:
                        orders.add(o)
        
        # for all the orders find all potential influencers
        l_orders = list(orders)
        for i, o in enumerate(l_orders):
            for p in l_orders[i+1:]:
                # if users are friends
                # 2. Create a list of friends that ordered the same item previously
                if Friends.objects.get(facebook_id=o.user.facebook_profile.facebook_id).is_friend(p.user.facebook_profile.facebook_id):
                    if p.timestamp < o.timestamp:
                        diff = o.timestamp-p.timestamp
                        #print diff, o.timestamp, p.timestamp
                        if o.user.id in influencers:
                            influencers[o.user.id].add((p.user.id, diff))
                        else:
                            influencers[o.user.id] = set()
                            influencers[o.user.id].add((p.user.id, diff))
                        if o.id in influenced:
                            influenced[o.id].add((p.user.id, diff))
                        else:
                            influenced[o.id] = set()
                            influenced[o.id].add((p.user.id, diff))
                    else:
                        diff = p.timestamp-o.timestamp
                        #print diff, o.timestamp, p.timestamp
                        if p.user.id in influencers:
                            influencers[p.user.id].add((o.user.id, diff))
                        else:
                            influencers[p.user.id] = set()
                            influencers[p.user.id].add((o.user.id, diff))
                        if p.id in influenced:
                            influenced[p.id].add((o.user.id, diff))
                        else:
                            influenced[p.id] = set()
                            influenced[p.id].add((o.user.id, diff))

    # friends who dined together
    # first find the friends who dined together
    dine_friends_dict = {}
    # supports up to 10 people per table
    time_matrix = np.matrix([np.zeros(max_table_size) for i in range(len(diners))])
    exp_time_matrix = [[[] for i in range(max_table_size)] for i in range(5)]
    convert_matrix = np.matrix([np.zeros(max_table_size) for i in range(len(diners))])
    divert_matrix = np.matrix([np.zeros(max_table_size) for i in range(len(diners))])
    all_orders = np.zeros((4, max_table_size))
    exp_convert = np.zeros((4,max_table_size)) # count of people in experiments
    exp_divert = np.zeros((4,max_table_size)) # count of people in experiments
    local_convert = np.zeros((4,max_table_size)) # count of people in experiments
    local_divert = np.zeros((4,max_table_size)) # count of people in experiments
    local_convert2 = np.zeros((4,max_table_size)) # count of people in experiments
    local_divert2 = np.zeros((4,max_table_size)) # count of people in experiments
    virtual_convert = np.zeros((4,max_table_size)) # count of people in experiments
    virtual_divert = np.zeros((4,max_table_size)) # count of people in experiments
    
    for t in TableCode.objects.exclude(code="abcd"):
        co_diners = set([o.user for o in t.table_orders.all()])
        co_diners_list = list(co_diners)
        for i, v in enumerate(co_diners_list): 
            for w in co_diners_list[i+1:]:
                if v in dine_friends_dict:
                    dine_friends_dict[v].add(w)
                else:
                    dine_friends_dict[v] = set()
                    dine_friends_dict[v].add(w)

                if w in dine_friends_dict:
                    dine_friends_dict[w].add(v)
                else:
                    dine_friends_dict[w] = set()
                    dine_friends_dict[w].add(v)


        # calculate order time
        table_orders = t.table_orders.all()

        # check if orders are same
        for i, o in enumerate(table_orders):
            for p in table_orders[i+1:]:
                # need to eliminate those orders by same people
                if o.user.id != p.user.id:
                    if o.num_common_orders(p) > 0:
                        # if there are common orders
                        if o.timestamp < p.timestamp:
                            diff = p.timestamp-o.timestamp
                            if p.id in local_influence:
                                local_influence[p.id].add((o.user.id, diff))
                            else:
                                local_influence[p.id] = set()
                                local_influence[p.id].add((o.user.id, diff))
                        else:
                            diff = o.timestamp-p.timestamp
                            if o.id in local_influence:
                                local_influence[o.id].add((p.user.id, diff))
                            else:
                                local_influence[o.id] = set()
                                local_influence[o.id].add((p.user.id, diff))
        
        # distinct people in a table
        people = set()
        for o in table_orders:
            people.add(o.user.id)

        # for each order in the table
        for o in table_orders:
            if o.items.count() > 0:
                d = calculate_order_time(o)
                time_matrix[diners.index(o.user), len(people)-1] = d[0] 
                exp_time_matrix[0][len(people)-1].append(d[0])
                exp_time_matrix[o.table.experiment.id][len(people)-1].append(d[0])
                
                # check if ordered same from presurvey or different
                presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=o.user.facebook_profile.facebook_id)
                if presurvey.exists():

                    # dishes selected during presurvey
                    presurvey_dishes = set()
                    for d in presurvey[0].favorite_dishes.all(): 
                        presurvey_dishes.add(d)

                    # dishes ordered
                    ordered = set()
                    for i in o.items.all():
                        ordered.add(i.item)

                    all_orders[o.table.experiment.id-1, len(people)-1] += 1

                    # get items common in presurvey and order
                    common = presurvey_dishes & ordered

                    local_patrons = set()
                    if len(common) > 0:
                        # common orders
                        convert_matrix[diners.index(o.user), len(people)-1] += 1 
                        exp_convert[o.table.experiment.id-1,len(people)-1] += 1

                        if o.id in influenced and len(influenced[o.id]) > 0:
                            for influencer in list(influenced[o.id]):
                                if influencer[1] <  h_diff:
                                    # if time difference is within an hour it's copresent
                                    local_patrons.add(influencer[0])
                                else:
                                    # if time difference is greater than an hour it's virtual
                                    virtual_convert[o.table.experiment.id-1, len(people)-1] += 1
                        if o.id in local_influence and len(local_influence[o.id]) > 0:
                            for influencer in local_influence[o.id]: 
                                local_patrons.add(influencer[0])
                                local_convert2[o.table.experiment.id-1, len(people)-1] += 1

                        local_convert[o.table.experiment.id-1,len(people)-1] += len(local_patrons)  

                    else:
                        # different orders
                        divert_matrix[diners.index(o.user), len(people)-1] += 1 
                        exp_divert[o.table.experiment.id-1,len(people)-1] += 1
                        if o.id in influenced and len(influenced[o.id]) > 0:
                            for influencer in list(influenced[o.id]):
                                if influencer[1] < h_diff:
                                    local_patrons.add(influencer[0])
                                else:
                                    virtual_divert[o.table.experiment.id-1, len(people)-1] += 1
                        if o.id in local_influence and len(local_influence[o.id]) > 0:
                            for influencer in local_influence[o.id]:
                                local_patrons.add(influencer[0])
                                local_divert2[o.table.experiment.id-1, len(people)-1] += 1

                        local_divert[o.table.experiment.id-1,len(people)-1] += len(local_patrons)  

    # put the number of friends into a list indexed by
    # diners list index
    dine_friends = np.zeros(len(diners)) 
    for key, val in dine_friends_dict.items():
        dine_friends[diners.index(key)] = len(val)

    # find out the average time, shortest/longest time they took to ordering
    mu_time = np.zeros(max_table_size)
    median_time = np.zeros(max_table_size)
    std_time = np.zeros(max_table_size)
    n_time = np.zeros(max_table_size)

    for k in range(max_table_size):
        non_zero_vals = [] 
        for j in time_matrix[:,k]:
            if j > 0:
                non_zero_vals.append(j) 
        # average time per group
        mu_time[k] = np.mean(np.array(non_zero_vals))
        median_time[k] = np.median(np.array(non_zero_vals))
        std_time[k] = np.std(np.array(non_zero_vals))
        n_time[k] = len(non_zero_vals)
            
    print "Mean times:",mu_time
    print "Media times:", median_time
    print "Standard Deviation:", std_time
    print "Number of times ordered:", n_time, np.sum(n_time)

    print "All orders\n", all_orders
    print "Same\t\t", np.sum(convert_matrix, axis=0)  
    print "Different\t", np.sum(divert_matrix, axis=0)  
    print "Different ratio\t", np.sum(divert_matrix, axis=0)/(np.sum(convert_matrix, axis=0)+np.sum(divert_matrix, axis=0))
    # find out if each user diverted their preselects 

    print "Converted: %d\n"%np.sum(exp_convert), exp_convert
    print "Diverted: %d\n"%np.sum(exp_divert), exp_divert

    print "Virtual converted: %d\n"%np.sum(virtual_convert), virtual_convert
    print "Local converted: %d\n"%np.sum(local_convert), local_convert
    print "Local converted 2: %d\n"%np.sum(local_convert2), local_convert2
    print "Virtual diverted: %d\n"%np.sum(virtual_divert), virtual_divert
    print "Local diverted: %d\n"%np.sum(local_divert), local_divert
    print "Local diverted 2: %d\n"%np.sum(local_divert2), local_divert2

    exp_mean_time = np.zeros((5,max_table_size))
    for e in range(5):
        for s in range(max_table_size):
            exp_mean_time[e,s] = np.mean(np.array(exp_time_matrix[e][s]))

    fig2 = plt.figure(figsize=(12,12))
    ax1 = fig2.add_subplot(511)
    ax2 = fig2.add_subplot(512)
    ax3 = fig2.add_subplot(513)
    ax4 = fig2.add_subplot(514)
    ax5 = fig2.add_subplot(515)

    ax1.boxplot([exp_time_matrix[0][s] for s in range(max_table_size)])
    ax2.boxplot([exp_time_matrix[1][s] for s in range(max_table_size)])
    ax3.boxplot([exp_time_matrix[2][s] for s in range(max_table_size)])
    ax4.boxplot([exp_time_matrix[3][s] for s in range(max_table_size)])
    ax5.boxplot([exp_time_matrix[4][s] for s in range(max_table_size)])

    """
        Control group and Friend groups with different table sizes have
        p < 0.05 of time difference

        The two people group has difference in different experimental groups
        for p < 0.01
    """
    print "All group table size"
    print stats.f_oneway(exp_time_matrix[0][0], exp_time_matrix[0][1], exp_time_matrix[0][2], exp_time_matrix[0][3])
    print "Control group table size"
    print stats.f_oneway(exp_time_matrix[1][0], exp_time_matrix[1][1], exp_time_matrix[1][2], exp_time_matrix[1][3])
    print "Friend group table size"
    print stats.f_oneway(exp_time_matrix[2][0], exp_time_matrix[2][1], exp_time_matrix[2][2], exp_time_matrix[2][3])
    print "Popularity group table size"
    print stats.f_oneway(exp_time_matrix[3][0], exp_time_matrix[3][1], exp_time_matrix[3][2], exp_time_matrix[3][3])
    print "Group of friends group table size"
    print stats.f_oneway(exp_time_matrix[4][0], exp_time_matrix[4][1], exp_time_matrix[4][2], exp_time_matrix[4][3])

    print "Loners"
    print stats.f_oneway(exp_time_matrix[1][0],exp_time_matrix[2][0],exp_time_matrix[3][0],exp_time_matrix[4][0])
    print "Doubles"
    print stats.f_oneway(exp_time_matrix[1][1],exp_time_matrix[2][1],exp_time_matrix[3][1],exp_time_matrix[4][1])
    print "Triples"
    print stats.f_oneway(exp_time_matrix[1][2],exp_time_matrix[2][2],exp_time_matrix[3][2])
    print "Quads"
    print stats.f_oneway(exp_time_matrix[1][3],exp_time_matrix[2][3],exp_time_matrix[3][3],exp_time_matrix[4][3])
    print "Fives"
    print stats.f_oneway(exp_time_matrix[1][4],exp_time_matrix[2][4],exp_time_matrix[3][4])

    #ax1.plot(np.arange(1, max_table_size+1), exp_mean_time[0,:], label="grp 1")
    #ax1.plot(np.arange(1, max_table_size+1), exp_mean_time[1,:], label="grp 2")
    #ax1.plot(np.arange(1, max_table_size+1), exp_mean_time[2,:], label="grp 3")
    #ax1.plot(np.arange(1, max_table_size+1), exp_mean_time[3,:], label="grp 4")
    #ax1.legend()

    fig2.show()

    common_count = 0    # count of people that have common dishes
    no_common_count = 0 # count of people that have no common dishes 
    exp_count = np.zeros((4,2)) # count of people in experiments

    common_dict = {} 
    common_list = []
    no_common_list = []

    for u in OTNUser.objects.filter(id__in=diners_id):
        valid_orders = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0)
        if valid_orders.count() > 0:
            # whether this person's presurvey orders have also been ordered
            if LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id).exists():
                presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id)[0]

                # dishes selected during presurvey
                presurvey_dishes = set()
                for d in presurvey.favorite_dishes.all(): 
                    presurvey_dishes.add(d)

                # dishes ordered
                ordered = set()
                for order in valid_orders.all():
                    for i in order.items.all():
                        ordered.add(i.item)

                # get items common in presurvey and order
                common = presurvey_dishes & ordered

                common_dict[u.id] = len(common) 

                if len(common) > 0:
                    common_list.append(u.id)
                    common_count += 1
                    exp_count[order.table.experiment.id-1,0] += 1
                else:
                    no_common_list.append(u.id)
                    no_common_count += 1
                    exp_count[order.table.experiment.id-1,1] += 1

    color_map = ["#54e373", "#ff380d", "#4855b1", "#c48d4f"] 

    print "Common dishes:", common_count, " - Different dishes:", no_common_count
    total = common_count+no_common_count
   
    # Per table code:
    # find out if those who ate in groups were affected by local or virtual

    # find out if those who ate alone were affected by local or virtual


    # Calculate probability of ordering a dish


    # Calculate the probability of ordering common dish

    grand_t = np.sum(all_orders)

    t = np.sum(all_orders, axis=1)
    mve = np.sum(virtual_convert, axis=1)
    dve = np.sum(virtual_divert, axis=1)
    mle = np.sum(local_convert, axis=1)
    dle = np.sum(local_divert, axis=1)
    print "Virtual maintain:", mve/t, np.sum(mve[1:4]), np.sum(mve[1:4])/grand_t
    print mve
    print "Virtual divert:", dve/t, np.sum(dve[1:4]), np.sum(dve[1:4])/grand_t
    print dve
    print "Local maintain:", mle/t, np.sum(mle), np.sum(mle)/grand_t
    print mle
    print "Local divert:", dle/t, np.sum(dle), np.sum(dle)/grand_t
    print dle
    print "Independent:", (t-mve-dve-mle-dle)/t, (grand_t-np.sum(t-mve-dve-mle-dle))/grand_t

    u = np.sum(all_orders, axis=0)
    mv = np.sum(virtual_convert[1:4], axis=0)
    dv = np.sum(virtual_divert[1:4], axis=0)
    ml = np.sum(local_convert, axis=0)
    dl = np.sum(local_divert, axis=0)
    print "Virtual maintain:", mv/u, np.sum(mv), np.sum(mv)/grand_t 
    print mv
    print "Virtual divert:", dv/u, np.sum(dv), np.sum(dv)/grand_t
    print dv
    print "Local maintain:", ml/u, np.sum(ml), np.sum(ml)/grand_t
    print ml
    print "Local divert:", dl/u, np.sum(dl), np.sum(dl)/grand_t
    print dl 
    print "Independent:", (u-mv-dv-ml-dl)/u, (grand_t-np.sum(u-mv-dv-ml-dl))/grand_t
    w = np.array([mv, dv, ml, dl])
    wsum = np.sum(w, axis=1)
    print "Summary:", np.sum(w, axis=1), np.sum(w, axis=1)/grand_t, (grand_t-np.sum(w))/grand_t 

    return all_orders, exp_convert, exp_divert, virtual_convert, local_convert, virtual_divert, local_divert


# TODO: Need to look at each table and see what percentage diverted or converted from
#    preselection and whether the diversion was below average price of preselection.


def num_people_per_table():
    """
        Find out the number of people who were eating together
        by checking the number of orders fulfilled per table code
    """

    people_per_table = np.zeros(10)
    exp_per_table = np.zeros((4,10))
    no_order = 0
    group_orders = {}
    group_orders[1] = []
    group_orders[2] = []
    group_orders[3] = []
    group_orders[4] = []
    group_orders[5] = []
    group_orders[6] = []
    group_orders[7] = []
    group_orders[8] = []
    for tc in TableCode.objects.all():
        if tc.first_used is None:
            continue
        patron_set = set()
        people_count = 0
        valid_orders = []
        valid_order_list = []
        for o in tc.table_orders.all():
            # go through all orders
            if tc.code == 'abcd':
                if o.user.otnuser.my_email == 'kool@mit.edu':
                    # ignore these orders
                    pass
                else:
                    # count the order for table code
                    if o.items.all().count() > 0:
                        patron_set.add(o.user.id)
                        valid_orders.append(o.id)
            else:
                # if order has items
                if o.items.all().count() > 0:
                    patron_set.add(o.user.id)
                    valid_orders.append(o.id)
                    valid_order_list.append(o)

        # TODO
        # check if order has same item as other orders
        # check if order has diverted from preselection
        #for i, o in enumerate(valid_order_list):
        #    for p in valid_order_list[i+1:]:
              
        # for each table code
        people_count = len(patron_set)
        if people_count > 0:
            people_per_table[people_count] += 1
            exp_per_table[tc.experiment.id-1,people_count] += 1
            group_orders[people_count] += valid_orders 
        else:
            no_order += 1

    # plot
    fig1 = plt.figure()
    fig1.subplots_adjust(hspace=0.8)

    print "Empty orders: %d out of %d"%(no_order, TableCode.objects.exclude(code="abcd").count())

    ax1 = fig1.add_subplot(511)

    fig2 = plt.figure(figsize=(3,3))
    ax6 = fig2.add_subplot(111)
    w = 0.5
    offset = 0.2
    #ax6.set_title("Distribution of table sizes")
    ax6.set_xlabel("$n$ of people/table")
    ax6.bar(np.arange(0, len(people_per_table))-offset, people_per_table, width=w)
    #ax6.xaxis.set_major_locator(MaxNLocator(8))
    ax6.set_ylabel("$n$ of groups")
    ax6.set_title("Distribution of table sizes")
    fig2.savefig(PREFIX_IMG+"tablesize.%s"%img_type, bbox_inches="tight")

    ax2 = fig1.add_subplot(512)
    ax2.bar(np.arange(0, len(people_per_table))-offset, exp_per_table[0,:], width=w)
    ax2.set_xlim(0,8)
    ax2.set_ylabel("Group 1")

    ax3 = fig1.add_subplot(513)
    ax3.bar(np.arange(0, len(people_per_table))-offset, exp_per_table[1,:], width=w)
    ax3.set_xlim(0,8)
    ax3.set_ylabel("Group 2")

    ax4 = fig1.add_subplot(514)
    ax4.bar(np.arange(0, len(people_per_table))-offset, exp_per_table[2,:], width=w)
    ax4.set_xlim(0,8)
    ax4.set_ylabel("Group 3")

    ax5 = fig1.add_subplot(515)
    ax5.bar(np.arange(0, len(people_per_table))-offset, exp_per_table[3,:], width=w)
    ax5.set_xlim(0,8)
    ax5.set_ylabel("Group 4")

    fig1.show()

    fig2 = plt.figure()
    ax1 = fig2.add_subplot(111)


    order_durations = {}
    loners = set(group_orders[1])
    doubles = set(group_orders[2])
    triples = set(group_orders[3])
    quads = set(group_orders[4])

    print "Loners"
    k = order_duration_array(loners)
    print k
    print "Doubles"
    l = order_duration_array(doubles)
    print l
    print "Triples"
    m = order_duration_array(triples)
    print m
    print "Quads"
    n = order_duration_array(quads)
    print n
    ax1.boxplot([k[0], l[0], m[0], n[0]])
    print "F-statistic"
    print stats.f_oneway(k[0], l[0], m[0], n[0])
    ax1.set_xlabel("People per table")
    ax1.set_ylabel("Ordering time (seconds)")
    ax1.set_title("Distribution of ordering time among different sized groups")
    fig2.savefig(PREFIX_IMG+"order_time_table_size.%s"%img_type, bbox_inches="tight")
    fig2.show()

    """
    orders = Order.objects.annotate(num_items=Count('items')).filter(num_items__gt=0)
    order_matrix = {}
    for o in orders:
        order_matrix[o] = {}
        for p in orders.exclude(id=o.id):
            common_dishes = o.common_orders(p)
            order_matrix[o][p] = common_dishes

    for exp in range(1,5):
        for i in range(1,3):
            # graph the network of influence
            DG1 = pygraphviz.AGraph(directed=True)
            influence_edges1 = set() 

            certain_orders = Order.objects.filter(id__in=group_orders[i], table__experiment__id=exp)
            for o in certain_orders:
                # look at other orders by friends that happened before this order
                # and see if it has common order
                for k in orders.filter(timestamp__lt=o.timestamp, table__experiment__id=exp):
                    # if order by friends 
                    if Friends.objects.get(facebook_id=o.user.facebook_profile.facebook_id).is_friend(k.user.facebook_profile.facebook_id):
                        # check if common orders exist
                        common_dishes = order_matrix[o][k] 
                        if len(common_dishes) > 0:
                            dish = MenuItem.objects.get(id=list(common_dishes)[0])
                            influence_edges1.add((k.user.id, o.user.id))
                            d1 = (k.timestamp-start_date).days
                            c1 = cm.pink(d1*2)
                            DG1.add_node(k.user.id, style='filled', fillcolor="%s %s %s"%(c1[0], c1[1], c1[2]), label=dish.name.encode('ascii', 'replace'))
                            d2 = (o.timestamp-start_date).days
                            c2 = cm.pink(d2*2)
                            DG1.add_node(o.user.id, style='filled', fillcolor="%s %s %s"%(c2[0], c2[1], c2[2]), label=dish.name.encode('ascii', 'replace'))

            #print influence_edges
            DG1.add_edges_from(list(influence_edges1))

            # dot output
            DG1.draw(PREFIX_IMG+"group_size_%d_%d.dot"%(i, exp), prog="dot")
            DG1.draw(PREFIX_IMG+"group_size_%d_%d.%s"%(i, exp,img_type), prog='dot')
    """ 

def order_time_evolution():

    fig = plt.figure()

    # people actually eaten 

    today = datetime.today()

    for i in range(1,13):
        menu_item_list = []
        menu_item_count = []

        last_day = today - timedelta(7*(12-i))
        ax1 = fig.add_subplot(12, 1, i)
        for m in MenuItem.objects.all().order_by('price'):
            n = m.menuitemreview_set.filter(legals_ordered__timestamp__lt=last_day).count()
            menu_item_list.append( m.name )
            menu_item_count.append(n)

        ind = np.arange(1,len(menu_item_count)+1)
        ax1.bar(ind, menu_item_count )

        ax1.set_xticks(ind)
        ax1.xaxis.set_major_locator(MaxNLocator(20))
        #ax1.set_xticklabels( menu_item_list, rotation=45 )
        ax1.set_title('Actual orders')

    fig.show()

def taste_choice_distribution():
    """
        Look at the distribution of taste
    """
    
    senses_list = []
    senses_count = []

    fig = plt.figure()
    fig.subplots_adjust(hspace=0.4)
    ax1 = fig.add_subplot(211)

    # global - all presurvey participants
    for t in TasteChoice.objects.all(): 
        # filter out duplicates
        n = t.legalspopulationsurvey_set.all().order_by("facebook_id").values('facebook_id').distinct().count()
        print "Num distinct:", n
        senses_list.append( t.sense )
        senses_count.append( n)

    ind = np.arange(1,len(senses_count)+1)
    ax1.bar(ind, senses_count)

    ax1.set_xticks(ind)
    ax1.set_xticklabels( senses_list, rotation=45 )
    ax1.set_title('Taste Profile of Survey Participants')

    # participants who dined
    senses_list = []
    senses_count = []

    ax2 = fig.add_subplot(212)

    # diners
    fb_participants = [] 
    for u in OTNUser.objects.filter(voucher=True):
        fb_participants.append(u.facebook_profile.facebook_id)

    # count the taste choices by diners
    for t in TasteChoice.objects.all(): 
        n = t.legalspopulationsurvey_set.filter(facebook_id__in=fb_participants).count()
        print "Num distinct 2:", n
        senses_list.append( t.sense )
        senses_count.append( n)

    ind = np.arange(1,len(senses_count)+1)
    ax2.bar(ind, senses_count)

    ax2.set_xticks(ind)
    ax2.set_xticklabels( senses_list, rotation=45 )
    ax2.set_title('Taste Profile of Diners')

    fig.show()

def total_social_network():
    """
        Displays the network of people who filled out
        presurvey and colors the nodes differently for
        different taste values or menu items
    """

    G = nx.Graph()
    for u in Friends.objects.all():

        for f in u.friends.all().exclude(id=u.id):
            G.add_edge(u.id,f.id)

    nx.draw(G)
    plt.show()

def participant_exp_network():
    """
        Participants and their network of friends colored by
        the experimental group

    """
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    G = nx.Graph()
    order_map = {}
    for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

        o_count = u.legals_order.all().annotate(num_items=Count('items')).filter(num_items__gt=0).count()
        if o_count > 0:
            #G.add_node(u.facebook_profile.facebook_id)
            G.add_node(u.id)
            #order_map[u.facebook_profile.facebook_id] = o_count 
            order_map[u.id] = u.legals_order.all()[0].table.experiment.id 

            # get u's friends
            list_friends = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)

            for z in OTNUser.objects.filter(facebook_profile__facebook_id__in=list_friends).exclude(facebook_profile__facebook_id=706848):
                o_count = z.legals_order.all().annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                if o_count > 0:
                    #G.add_edge(z.facebook_profile.facebook_id, u.facebook_profile.facebook_id)
                    G.add_edge(z.id, u.id)
                    order_map[z.id] = u.legals_order.all()[0].table.experiment.id 

    print len(G.nodes())
    print "=== Betweenness"
    b=nx.betweenness_centrality(G)
    for v in G.nodes():
        print "%0.2d\t%5.3f"%(v,b[v])

    print "=== Degree centrality"
    d=nx.degree_centrality(G)
    for v in G.nodes():
        print "%0.2d\t%5.3f"%(v,d[v])

    print  "=== Closeness centrality"
    c=nx.closeness_centrality(G)
    for v in G.nodes():
        print "%0.2d\t%5.3f"%(v,c[v])

    pos = nx.graphviz_layout(G)
    node_colors = []
    for c in G.nodes():
        node_colors.append(order_map[c])
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.Reds)
    edges = nx.draw_networkx_edges(G, pos)
    labels = nx.draw_networkx_labels(G, pos, font_size=10)

    plt.sci(nodes)
    c = plt.colorbar()
    c.set_label("Experimental Group")

    ax1.axis('tight')
    ax1.set_title("Participant Social Network")
    fig1.savefig(PREFIX_IMG+"participantexp.%s"%img_type)

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    hist = nx.degree_histogram(G)
    ax2.bar(range(0,len(hist)), hist)
    ax2.set_xlabel("Number of Friends")
    ax2.set_ylabel("Number of Participants")
    ax2.set_title("Participant Social Network Degrees")
    plt.show()

def participant_network():
    """
        Participants and their network of friends

        Color: 
            - people who joined
            - people who participated (shaded by number of times)
            - friends of the participants

    """


    fig1 = plt.figure(figsize=(12,12))
    ax1 = fig1.add_subplot(111)


    G = nx.Graph()
    order_map = {}
    first_day = {}
    for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

        o_count = u.legals_order.all().annotate(num_items=Count('items')).filter(num_items__gt=0).count()
        if o_count > 0:
            #G.add_node(u.facebook_profile.facebook_id)
            G.add_node(u.id)
            #order_map[u.facebook_profile.facebook_id] = o_count 
            order_map[u.id] = o_count
            first_day[u.id] = ((u.legals_order.all().order_by('timestamp')[0].timestamp)-start_date).days

            # get u's friends
            list_friends = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)

            for z in OTNUser.objects.filter(facebook_profile__facebook_id__in=list_friends).exclude(facebook_profile__facebook_id=706848):
                o_count = z.legals_order.all().annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                if o_count > 0:
                    #G.add_edge(z.facebook_profile.facebook_id, u.facebook_profile.facebook_id)
                    G.add_edge(z.id, u.id)

                    order_map[z.id] = o_count 
                    first_day[z.id] = (z.legals_order.all().order_by('timestamp')[0].timestamp-start_date).days


    pos = nx.graphviz_layout(G)
    node_colors = []
    for c in G.nodes():
        node_colors.append(first_day[c])
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.Reds_r)
    edges = nx.draw_networkx_edges(G, pos)
    labels = nx.draw_networkx_labels(G, pos, labels=order_map, font_size=10)
    plt.sci(nodes)
    c = plt.colorbar()
    c.set_label("Initial Participation day")

    ax1.axis('tight')
    ax1.set_title("Participant Social Network")
    ax1.set_xticklabels([], visible=False)
    ax1.set_yticklabels([], visible=False)
    ax1.set_xlabel("Node label = number of visits")

    fig1.savefig(PREFIX_IMG+"participantnet.%s"%img_type, bbox_inches="tight")

    fig3 = plt.figure()
    fig3.subplots_adjust(hspace=0.5)
    ax3 = fig3.add_subplot(311)
    ax4 = fig3.add_subplot(312)
    ax5 = fig3.add_subplot(313)

    print len(G.nodes())
    print "=== Betweenness"
    b=nx.betweenness_centrality(G)
    #for v in G.nodes():
    #    print "%0.2d\t%5.3f"%(v,b[v])
    #ax3.hist(list(b), bins=20, normed=True, cumulative=True, histtype='step', label="Betweenness")
    ax3.hist(list(b.values()), bins=20, histtype='step', normed=True, label="Betweenness")
    ax3.set_title("Betweenness Centrality")
    ax3.set_ylabel("\# of nodes")

    print "=== Degree centrality"
    d=nx.degree_centrality(G)
    #for v in G.nodes():
    #    print "%0.2d\t%5.3f"%(v,d[v])
    #ax3.hist(list(d), bins=20, normed=True, cumulative=True, histtype='step', label="Degree")
    ax4.hist(np.array(d.values()), bins=20, histtype='step', normed=True, label="Degree")
    ax4.set_title("Degree Centrality")
    ax4.set_ylabel("\# of nodes")

    print  "=== Closeness centrality"
    c=nx.closeness_centrality(G)
    #for v in G.nodes():
    #    print "%0.2d\t%5.3f"%(v,c[v])
    #ax3.hist(list(c), bins=20, normed=True, cumulative=True, histtype='step', label="Closeness")
    ax5.hist(list(c.values()), bins=20, histtype='step', normed=True, label="Closeness")
    ax5.set_title("Closeness Centrality")
    ax5.set_ylabel("\# of nodes")
    #ax3.legend()

    fig3.savefig(PREFIX_IMG+"centrality.%s"%img_type, bbox_inches="tight")

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    hist = nx.degree_histogram(G)
    ax2.bar(np.arange(0,len(hist))-0.5, hist)
    ax2.axis('tight')
    ax2.set_xlabel("Number of Friends")
    ax2.set_ylabel("Number of Participants")
    ax2.set_title("Participant Social Network Degrees")
    fig2.savefig(PREFIX_IMG+"frienddegrees.%s"%img_type, bbox_inches="tight")
    plt.show()

def num_common_orders( me, you, exp=0 ):
    a = set()
    b = set()
    
    for o in me.legals_order.all():
        if o.table.experiment.id == exp:
            for m in o.items.all():
                a.add(m.item.id) 
        elif exp == 0:
            for m in o.items.all():
                a.add(m.item.id) 
    for o in you.legals_order.all():
        if o.table.experiment.id == exp:
            for m in o.items.all():
                b.add(m.item.id) 
        elif exp == 0:
            for m in o.items.all():
                b.add(m.item.id) 

    return len( a & b )

def menu_choice_network_all():
    """
        Participants and how they relate using menu item chosen
        vs their friends on Facebook

        Color: 
            - people who joined
            - people who participated (shaded by number of times)
            - friends of the participants

    """

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    G = nx.Graph()
    G1 = nx.Graph() # common menu among friends
    G2 = nx.Graph() # common menu among friends of friends
    order_map = {}
    common_map = {}
    common_map_2 = {}

    # Map out friends in first degree that have common dishes
    for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

        o_count = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
        if o_count > 0:
            G.add_node(u.id)
            order_map[u.id] = o_count 

            # get u's friends
            list_friends = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)

            for z in OTNUser.objects.filter(facebook_profile__facebook_id__in=list_friends).exclude(facebook_profile__facebook_id=706848):
                z_count = z.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                if z_count > 0:
                    G.add_edge(z.id, u.id)
                    order_map[z.id] = z_count 
                    # if they have common order
                    n = num_common_orders(u, z) 
                    if n > 0:
                        print "1st Degree Adding:",z.id, u.id
                        G1.add_edge(z.id, u.id)
                        common_map[(z.id, u.id)] = n

    # Map out friends in second degree that have common dishes
    for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

        o_count = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
        if o_count > 0:
            # get u's friends
            list_friends = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)

            for z in OTNUser.objects.filter(facebook_profile__facebook_id__in=list_friends).exclude(facebook_profile__facebook_id=706848):
                z_count = z.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                # get second degree friends that are common dishes
                second_friends = Friends.objects.get(facebook_id = z.facebook_profile.facebook_id).friends.exclude(facebook_id__in=[u.facebook_profile.facebook_id, z.facebook_profile.facebook_id]).values_list('facebook_id', flat=True)
                for y in OTNUser.objects.filter(facebook_profile__facebook_id__in=second_friends).exclude(facebook_profile__facebook_id=706848):
                    y_count = y.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                    if y_count > 0:
                        # if they have common order
                        n = num_common_orders(u, y) 
                        if n > 0:
                            if y.id not in G1.nodes():
                                print "2nd Degree Adding:",y.id, u.id
                                G2.add_edge(y.id, u.id)
                                common_map_2[(y.id, u.id)] = n
            
    print "Num nodes:", len(G.nodes())
    print "Common edges first degree:", len(G1.edges())
    print "Common edges second degree:", len(G2.edges())
    print len(common_map_2.values())

    print nx.degree(G1, G1.nodes())
    print nx.degree(G2, G2.nodes())

    pos = nx.graphviz_layout(G)
    node_colors = []
    edge_colors = []
    edge_colors_2 = []
    for c in G.nodes():
        node_colors.append(order_map[c])
    for h in G1.edges():
        edge_colors.append(common_map[h])
    for k in G2.edges():
        try:
            edge_colors_2.append(common_map_2[k])
        except KeyError:
            edge_colors_2.append(common_map_2[(k[1], k[0])])
            print "Try inverting edge nodes"
    #nodes = nx.draw(G, pos, width=2, node_color=node_colors, edge_color=edge_colors, cmap=plt.cm.Reds, edge_cmap=plt.cm.Blues, with_labels=False)
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.Greens, with_labels=True)
    edges = nx.draw_networkx_edges(G, pos, alpha=0.3)
    edges = nx.draw_networkx_edges(G1, pos, width=2, alpha=0.8, edge_vmin=-1, edge_color=edge_colors, edge_cmap=plt.cm.Blues)
    edges2 = nx.draw_networkx_edges(G2, pos, width=2, alpha=0.8, edge_vmin=-1, edge_color=edge_colors_2, edge_cmap=plt.cm.Reds)
    #labels = nx.draw_networkx_labels(G, pos, font_size=10)

    plt.sci(nodes)
    c = plt.colorbar()
    c.set_label("Number of Orders")
    plt.sci(edges)
    c = plt.colorbar()
    c.set_label("Common Dishes in 1st Degree Friends")
    if edges2 is not None:
        plt.sci(edges2)
        c = plt.colorbar()
        c.set_label("Common Dishes in 2nd Degree Friends")

    plt.title("Common Dishes")
    plt.xticks(visible=False)
    plt.yticks(visible=False)
    plt.savefig(PREFIX_IMG+"menuchoicenet.%s"%img_type)
    plt.show()

def menu_choice_network(exp=[]):
    """
        Participants and how they relate using menu item chosen
        vs their friends on Facebook

        Color: 
            - people who joined
            - people who participated (shaded by number of times)
            - friends of the participants

    """

    if len(exp)==0:
        exp = [1,2,3,4]

    for e in exp:
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        G = nx.Graph()
        G1 = nx.Graph() # common menu among friends
        G2 = nx.Graph() # common menu among friends of friends
        order_map = {}
        common_map = {}
        common_map_2 = {}

        # Map out friends in first degree that have common dishes
        for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

            o_count = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
            if o_count > 0:
                G.add_node(u.id)
                order_map[u.id] = o_count 

                # get u's friends
                list_friends = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)

                for z in OTNUser.objects.filter(facebook_profile__facebook_id__in=list_friends).exclude(facebook_profile__facebook_id=706848):
                    z_count = z.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                    if z_count > 0:
                        G.add_edge(z.id, u.id)
                        order_map[z.id] = z_count 
                        # if they have common order
                        n = num_common_orders(u, z, e) 
                        if n > 0:
                            print "1st Degree Adding:",z.id, u.id
                            G1.add_edge(z.id, u.id)
                            common_map[(z.id, u.id)] = n

        # Map out friends in second degree that have common dishes
        for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

            o_count = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
            if o_count > 0:
                # get u's friends
                list_friends = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)

                for z in OTNUser.objects.filter(facebook_profile__facebook_id__in=list_friends).exclude(facebook_profile__facebook_id=706848):
                    z_count = z.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                    # get second degree friends that are common dishes
                    second_friends = Friends.objects.get(facebook_id = z.facebook_profile.facebook_id).friends.exclude(facebook_id__in=[u.facebook_profile.facebook_id, z.facebook_profile.facebook_id]).values_list('facebook_id', flat=True)
                    for y in OTNUser.objects.filter(facebook_profile__facebook_id__in=second_friends).exclude(facebook_profile__facebook_id=706848):
                        y_count = y.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                        if y_count > 0:
                            # if they have common order
                            n = num_common_orders(u, y, e) 
                            if n > 0:
                                if y.id not in G1.nodes():
                                    print "2nd Degree Adding:",y.id, u.id
                                    G2.add_edge(y.id, u.id)
                                    common_map_2[(y.id, u.id)] = n
                
        print len(G.nodes())
        print len(G1.edges())
        print len(G2.edges())
        print len(common_map_2.values())

        pos = nx.graphviz_layout(G)
        node_colors = []
        edge_colors = []
        edge_colors_2 = []
        for c in G.nodes():
            node_colors.append(order_map[c])
        for h in G1.edges():
            edge_colors.append(common_map[h])
        for k in G2.edges():
            try:
                edge_colors_2.append(common_map_2[k])
            except KeyError:
                edge_colors_2.append(common_map_2[(k[1], k[0])])
                print "Try inverting edge nodes"
        #nodes = nx.draw(G, pos, width=2, node_color=node_colors, edge_color=edge_colors, cmap=plt.cm.Reds, edge_cmap=plt.cm.Blues, with_labels=False)
        nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.Greens, with_labels=True)
        edges = nx.draw_networkx_edges(G, pos, alpha=0.3)
        edges = nx.draw_networkx_edges(G1, pos, width=2, alpha=0.8, edge_vmin=-1, edge_color=edge_colors, edge_cmap=plt.cm.Blues)
        edges2 = nx.draw_networkx_edges(G2, pos, width=2, alpha=0.8, edge_vmin=-1, edge_color=edge_colors_2, edge_cmap=plt.cm.Reds)
        labels = nx.draw_networkx_labels(G, pos, font_size=10)

        plt.sci(nodes)
        c = plt.colorbar()
        c.set_label("Number of Orders")
        plt.sci(edges)
        c = plt.colorbar()
        c.set_label("Common Dishes in 1st Degree Friends")
        if edges2 is not None:
            plt.sci(edges2)
            c = plt.colorbar()
            c.set_label("Common Dishes in 2nd Degree Friends")

        plt.title("Common Dishes in Experiment: %d"%e)
        plt.xticks(visible=False)
        plt.yticks(visible=False)
        plt.savefig(PREFIX_IMG+"menuchoicenet%d.%s"%(e,img_type))
        plt.show()

def menu_influence_graph():
    """
        Directed graph showing influencer because they came
        before in time
    """

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    G = nx.Graph()
    G1 = nx.Graph() # common menu among friends
    G2 = nx.Graph() # common menu among friends of friends
    order_map = {}
    common_map = {}
    common_map_2 = {}

    # Map out friends in first degree that have common dishes
    for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

        o_count = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
        if o_count > 0:
            G.add_node(u.id)
            order_map[u.id] = o_count 

            # get u's friends
            list_friends = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)

            for z in OTNUser.objects.filter(facebook_profile__facebook_id__in=list_friends).exclude(facebook_profile__facebook_id=706848):
                z_count = z.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                if z_count > 0:
                    G.add_edge(z.id, u.id)
                    order_map[z.id] = z_count 
                    # if they have common order
                    n = num_common_orders(u, z) 
                    if n > 0:
                        print "1st Degree Adding:",z.id, u.id
                        G1.add_edge(z.id, u.id)
                        common_map[(z.id, u.id)] = n

    # Map out friends in second degree that have common dishes
    for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

        o_count = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
        if o_count > 0:
            # get u's friends
            list_friends = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)

            for z in OTNUser.objects.filter(facebook_profile__facebook_id__in=list_friends).exclude(facebook_profile__facebook_id=706848):
                z_count = z.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                # get second degree friends that are common dishes
                second_friends = Friends.objects.get(facebook_id = z.facebook_profile.facebook_id).friends.exclude(facebook_id__in=[u.facebook_profile.facebook_id, z.facebook_profile.facebook_id]).values_list('facebook_id', flat=True)
                for y in OTNUser.objects.filter(facebook_profile__facebook_id__in=second_friends).exclude(facebook_profile__facebook_id=706848):
                    y_count = y.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
                    if y_count > 0:
                        # if they have common order
                        n = num_common_orders(u, y) 
                        if n > 0:
                            if y.id not in G1.nodes():
                                print "2nd Degree Adding:",y.id, u.id
                                G2.add_edge(y.id, u.id)
                                common_map_2[(y.id, u.id)] = n
            
    print len(G.nodes())
    print len(G1.edges())
    print len(G2.edges())
    print len(common_map_2.values())

    print nx.degree(G1, G1.nodes())
    print nx.degree(G2, G2.nodes())

    pos = nx.graphviz_layout(G)
    node_colors = []
    edge_colors = []
    edge_colors_2 = []
    for c in G.nodes():
        node_colors.append(order_map[c])
    for h in G1.edges():
        edge_colors.append(common_map[h])
    for k in G2.edges():
        try:
            edge_colors_2.append(common_map_2[k])
        except KeyError:
            edge_colors_2.append(common_map_2[(k[1], k[0])])
            print "Try inverting edge nodes"
    #nodes = nx.draw(G, pos, width=2, node_color=node_colors, edge_color=edge_colors, cmap=plt.cm.Reds, edge_cmap=plt.cm.Blues, with_labels=False)
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.Greens, with_labels=True)
    edges = nx.draw_networkx_edges(G, pos, alpha=0.3)
    edges = nx.draw_networkx_edges(G1, pos, width=2, alpha=0.8, edge_vmin=-1, edge_color=edge_colors, edge_cmap=plt.cm.Blues)
    edges2 = nx.draw_networkx_edges(G2, pos, width=2, alpha=0.8, edge_vmin=-1, edge_color=edge_colors_2, edge_cmap=plt.cm.Reds)
    #labels = nx.draw_networkx_labels(G, pos, font_size=10)

    plt.sci(nodes)
    c = plt.colorbar()
    c.set_label("Number of Orders")
    plt.sci(edges)
    c = plt.colorbar()
    c.set_label("Common Dishes in 1st Degree Friends")
    if edges2 is not None:
        plt.sci(edges2)
        c = plt.colorbar()
        c.set_label("Common Dishes in 2nd Degree Friends")

    plt.title("Common Dishes")
    plt.xticks(visible=False)
    plt.yticks(visible=False)
    plt.savefig(PREFIX_IMG+"menuchoicenet.%s"%img_type)
    plt.show()


def item_network(dish_id):
    """
        Show network of people who have chosen a particular item
        and nodes colored by time sequence
    """

    fig1 = plt.figure()

    a = set()
    order_set = set()
    G = nx.Graph()

    m = MenuItem.objects.get(id=dish_id)
    name = m.name
    
    for d in m.menuitemreview_set.all():
        if d.legals_ordered.all().count() > 0:
            order_set.add(d.legals_ordered.all()[0])

    # get each individual
    node_map = {}
    for o in list(order_set):
        f = o.user.facebook_profile.facebook_id
        a.add(f)
        u1 = OTNUser.objects.get(facebook_profile__facebook_id=f)
        G.add_node(u1.id)
        d = (o.updated - start_date).days
        node_map[u1.id] = d

    # and find if they are friends
    for f in list(a):
        b = set()
        b.add(f)

        u1 = OTNUser.objects.get(facebook_profile__facebook_id=f)
    
        friends = Friends.objects.get(facebook_id=f).friends.filter(facebook_id__in=list(a-b))
        for g in friends:
            # add edge
            u2 = OTNUser.objects.get(facebook_profile__facebook_id=g.facebook_id)
            G.add_edge(u1.id, u2.id)

    pos = nx.graphviz_layout(G)
    nx.draw_networkx_labels( G, pos, font_size=10 )
    node_colors = []
    for g in G.nodes():
        node_colors.append(node_map[g])
    print len(G.nodes()), len(node_colors)
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.Reds)
    edges = nx.draw_networkx_edges(G, pos)
    plt.sci(nodes)
    c = plt.colorbar()
    c.set_label("Days ago")
    plt.title("%s order evolution"%name)
    plt.savefig(PREFIX_IMG+"dish-%d-%s.%s"%(dish_id,name, img_type))
    plt.show()

def presurvey_network(dish_id=None):
    """
        map taste and dish network

        It doesn't make sense since nodes are fully connected
        Even a bipartite graph would not give information on similarity
    """

    fig = plt.figure()
    ax = fig.add_subplot(111)

    G = nx.Graph()

    if dish_id is not None:
        m = MenuItem.objects.get(id=dish_id)
        flikes = m.pre_favorite_dishes.all().values_list("facebook_id", flat=True)
        print len(flikes)
        a = set()
        for u in OTNUser.objects.filter( facebook_profile__facebook_id__in=flikes ):
            # add nodes 
            a.add(u.id)

        # add edges
        for j in list(a):
            b = set()
            b.add(j)
            for k in list(a-b):
                G.add_edge(j, k)
    else:
        for m in MenuItem.objects.all():
            flikes = m.pre_favorite_dishes.all().values_list("facebook_id", flat=True)
            print len(flikes)
            a = set()
            for u in OTNUser.objects.filter( facebook_profile__facebook_id__in=flikes ):
                # add nodes 
                a.add(u.id)

            # add edges
            for j in list(a):
                b = set()
                b.add(j)
                for k in list(a-b):
                    G.add_edge(j, k)

    pos = nx.graphviz_layout(G)
    nodes = nx.draw_networkx_nodes(G, pos)
    edges = nx.draw_networkx_edges(G, pos)
    plt.savefig(PREFIX_IMG+"presurvey_network.%s"%img_type)
    fig.show()        

def groups_vs_individuals():
    """
        Check decision time comparing individual versus people who
        came in groups

    """

    # go through each table code and find valid orders by distinct users
    # and divide into orders that have been made individually or in groups
    pass

def presurvey_cleanup():

    for l in LegalsPopulationSurvey.objects.values("facebook_id").distinct():
        surveys = LegalsPopulationSurvey.objects.filter(facebook_id=l["facebook_id"])
        if surveys.count()> 1:
            for s in surveys[1:]:
                s.delete()
    
def print_list(l):
    for i in l:
        print i    

def presurvey_stats(exp=0):
    """
        Display presurvey results
    """

    fig1 = plt.figure()
    

    boston = BostonZip.objects.all().values("zipcode")

    boston_surveys = LegalsPopulationSurvey.objects.filter(zipcode__in=boston)
    # all presurvey results
    print_list(boston_surveys.values("sex").annotate(Count("id")))

    print_list(boston_surveys.values("age").annotate(Count("id")))
    print_list(boston_surveys.values("like_seafood").annotate(Count("id")))
    print_list(boston_surveys.values("restaurant_visits").annotate(Count("id")))
    print_list(boston_surveys.values("seafood_visits").annotate(Count("id")))
    print_list(boston_surveys.values("legals_visits").annotate(Count("id")))
    print_list(boston_surveys.values("frequency").annotate(Count("id")))
    print_list(boston_surveys.values("vegetarian").annotate(Count("id")))
    print_list(boston_surveys.values("gluten").annotate(Count("id")))
    print_list(boston_surveys.values("phone_type").annotate(Count("id")))

    # participant presurvey results
    for exp in range(0,5):
        fb_participants = [] 
        for u in OTNUser.objects.all().exclude(facebook_profile__facebook_id=706848):

            o_count = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0).count()
            if o_count > 0:

                for o in u.legals_order.all():
                    if o.table.experiment.id == exp:
                        fb_participants.append(u.facebook_profile.facebook_id)
                    elif exp == 0:
                        fb_participants.append(u.facebook_profile.facebook_id)

        participant_surveys = LegalsPopulationSurvey.objects.filter(facebook_id__in= fb_participants)
        print "Experiment",exp
        print_list(participant_surveys.values("sex").annotate(Count("id")))
        print_list(participant_surveys.values("age").annotate(Count("id")))
        print_list(participant_surveys.values("like_seafood").annotate(Count("id")))
        print_list(participant_surveys.values("restaurant_visits").annotate(Count("id")))
        print_list(participant_surveys.values("seafood_visits").annotate(Count("id")))
        print_list(participant_surveys.values("legals_visits").annotate(Count("id")))
        print_list(participant_surveys.values("frequency").annotate(Count("id")))
        print_list(participant_surveys.values("vegetarian").annotate(Count("id")))
        print_list(participant_surveys.values("gluten").annotate(Count("id")))
        print_list(participant_surveys.values("phone_type").annotate(Count("id")))


def presurvey_order_relationship():
    """
        How does people's choices compare to their presurvey choices?

        Compare it from all menu and then each category
    """

    fig = plt.figure(figsize=(15,5))
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)

    common_count = 0
    no_common_count = 0
    exp_count = np.zeros((4,2))

    common_array = {} 
    for u in OTNUser.objects.all():
        valid_orders = u.legals_order.annotate(num_items=Count('items')).filter(num_items__gt=0)
        if valid_orders.count() > 0:
            # whether this person's presurvey orders have also been ordered
            if LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id).exists():
                presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=u.facebook_profile.facebook_id)[0]

                presurvey_dishes = set()
                for d in presurvey.favorite_dishes.all(): 
                    presurvey_dishes.add(d)

                ordered = set()
                for order in valid_orders.all():
                    for i in order.items.all():
                        ordered.add(i.item)

                # get items common in presurvey and order
                common = presurvey_dishes & ordered

                if len(common) > 0:
                    common_count += 1
                    common_array[u.id] = len(common) 
                    exp_count[order.table.experiment.id-1,0] += 1
                else:
                    no_common_count += 1
                    exp_count[order.table.experiment.id-1,1] += 1

    color_map = ["#54e373", "#ff380d", "#4855b1", "#c48d4f"] 

    total = common_count+no_common_count
    data = np.array([common_count, no_common_count])
    print "Participants:", np.sum(data) 
    print "Common:", float(common_count)/np.sum(data)
    print "Different:", float(no_common_count)/np.sum(data)
    #ax1.bar(np.array([1,2])+0.1, [common_count, no_common_count], width=0.3)
    #label1 = 'Common ({0:.2%})'.format(float(common_count)/np.sum(data))
    color_strs = ['#dddddd', '#aaaaaa', '#999999', '#777777']
    label_strs = ['Common (%d)'%common_count,
                    'Different (%d)'%no_common_count]
    ax1.axis([0.2, 0.2, 0.2, 0.2])
    ax1.axis('scaled')
    ax1.pie(data, colors=['#aaaaaa', '#777777'], labels=label_strs, autopct="%.2f\%%")
    ax1.set_xlabel("Ordered common vs different dishes from presurvey")

    total_count = float(np.sum(exp_count[:,0]))
    
    label_strs = ['Control (%d)'%exp_count[0,0],
                'Exp 2 (%d)'%exp_count[1,0],
                'Exp 3 (%d)'%exp_count[2,0],
                'Exp 4 (%d)'%exp_count[3,0]]
    ax2.axis([0.2, 0.2, 0.2, 0.2])
    ax2.axis('scaled')
    ax2.pie(exp_count[:,0], colors=color_strs, labels=label_strs, autopct="%.2f\%%")
    ax2.set_xlabel("Ordered common dishes from presurvey")

    total_count = float(np.sum(exp_count[:,1]))

    label_strs = ['Control (%d)'%exp_count[0,1],
                'Exp 2 (%d)'%exp_count[1,1],
                'Exp 3 (%d)'%exp_count[2,1],
                'Exp 4 (%d)'%exp_count[3,1]]
    ax3.axis([0.2, 0.2, 0.2, 0.2])
    ax3.axis('scaled')
    ax3.pie(exp_count[:,1], colors=color_strs, labels=label_strs, autopct="%.2f\%%")
    ax3.set_xlabel("Ordered different dishes from presurvey")

    total_count = np.sum(exp_count, axis=1)
    perc_count0 = exp_count[:,0]/np.array(total_count, dtype="float")
    perc_count1 = exp_count[:,1]/np.array(total_count, dtype="float")
    print "perc 1:",perc_count0[0],perc_count1[0]
    print "perc 2:",perc_count0[1],perc_count1[1]
    print "perc 3:",perc_count0[2],perc_count1[2]
    print "perc 4:",perc_count0[3],perc_count1[3]

    """
    ax1.bar(np.array([1,2])+0.4, exp_count[0,:], width=0.3, color=color_map[0], label="Control")
    ax1.bar(np.array([1,2])+0.4, exp_count[1,:], bottom=exp_count[0,:], width=0.3, color=color_map[1], label="Exp 1")
    ax1.bar(np.array([1,2])+0.4, exp_count[2,:], bottom=exp_count[1,:]+exp_count[0,:], width=0.3, color=color_map[2], label="Exp 2")
    ax1.bar(np.array([1,2])+0.4, exp_count[3,:], bottom=exp_count[2,:]+exp_count[1,:]+exp_count[0,:], width=0.3, color=color_map[3], label="Exp 3")
    ax1.set_xticks(np.array([1,2, 3])+0.4)
    ax1.set_xticklabels(['Common', 'Different', ''])
    """
    #ax2.bar(common_array.keys(), common_array.values())
    #ax2.set_xlabel("Participant")
    fig.savefig(PREFIX_IMG+"presurvey_vs_order.%s"%img_type, bbox_inches="tight")
    fig.show()

def calculate_probabilities():
    """
        Probability of ordering a dish

        2 Chowders, Soups, and Salads
        3 Surf, Turf and Beyond
        4 Seafood Bar
        5 Legal Classic Dinners
        6 Legal Lobsters
        7 Fish
        8 Appetizers
        9 Completely Legal
        10 Features
        1 Sides

    """

    dat_file = PREFIX_DAT+"taste_map_to_menu_items.pkl"
    dat_file2 = PREFIX_DAT+"taste_network.pkl"

    if os.path.isfile(dat_file):
        f = open(dat_file, "r")
        taste_map = pickle.load(f)

    else:

        people = set()
        taste_choices = TasteChoice.objects.all()
        taste_map = {}
        for t in TasteChoice.objects.all():
            menu_choices = {}
            for presurvey in t.legalspopulationsurvey_set.all():
                # get all the menu items chosen and their frequency
                if presurvey.facebook_id not in people:
                    people.add(presurvey.facebook_id)
                    for m in presurvey.favorite_dishes.all():
                        if m.id in menu_choices: 
                            menu_choices[m.id] += 1
                        else:
                            menu_choices[m.id] = 1
            taste_map[t.sense] = menu_choices

        # save "taste_map" into a file
        f = open(dat_file, "w")
        pickle.dump(taste_map, f)

    # with the taste map, find the vector for each taste


    # plain probability
    # entree's
    main_dishes = MenuItem.objects.filter(category__in=[3,4,5,6,7,9])
    total_count = main_dishes.count()
    print "Total dishes:", total_count

    sides = MenuItem.objects.filter(category=1)
    print "Total sides:", sides.count()

    appetizers = MenuItem.objects.filter(category=9)
    print "Total appetizers:", appetizers.count()

    soup_salads = MenuItem.objects.filter(category=2)
    print "Total soups/salads:", soup_salads.count()


    # with the taste choices see which ones are most related
    taste_choices = TasteChoice.objects.all()

    if os.path.isfile(dat_file2):
        f2 = open(dat_file2, "r")
        taste_mat = np.load(f2)
    else:

        people = set()
        taste_mat = np.zeros((taste_choices.count(), taste_choices.count()))
        for presurvey in LegalsPopulationSurvey.objects.all():
            if presurvey.facebook_id not in people:
                people.add(presurvey.facebook_id)
                tastes = presurvey.tastes.all()
                for i, t1 in enumerate(tastes):
                    for t2 in tastes[i+1:]:
                        taste_mat[t1.id-1, t2.id-1] += 1
                        taste_mat[t2.id-1, t1.id-1] += 1

        f2 = open(dat_file2, "w")
        np.save(f2, taste_mat)

    # taste legend
    for t in taste_choices:
        print t.id, t.sense

    # taste network
    print taste_mat
    
    im_mat = plt.matshow( taste_mat )
    plt.colorbar(im_mat)
    plt.xlabel("Taste Network")
    plt.xticks(np.array(range(taste_choices.count()))+0.2, [t.sense for t in taste_choices], rotation=90)
    plt.yticks(range(taste_choices.count()), [t.sense for t in taste_choices])
    return taste_mat

def population_stats():

    total = 0
    participants = set()
    for exp_var in [1,2,3,4]:
        orders = Order.objects.filter(table__experiment__id=exp_var).annotate(num_items=Count('items')).filter(num_items__gt=0)
        for o in orders:
            participants.add(o.user)
        print "Num orders:",orders.count()
        total += orders.count()
    print total
    print "People:", len(participants)

def calculate_table_size(order):
  participants = order.table.table_orders.annotate(num_items=Count('items')).filter(num_items__gt=0).values_list('user').distinct()
  #print participants
  return participants.count()

def calculate_common_orders(order, m):
  """
    Finds out how many others ordered the same thing
    among those who were together

    :param: m is the matrix containing the information of common orders

  """
  co_orders = set([o for o in order.table.table_orders.all()])-set([order])
  total = 0
  if len(co_orders) > 0:
    co_orders_list = list(co_orders)

    dishes = set([i.item.id for i in order.items.all()])
    for co_order in co_orders_list:
      if m[order.id][co_order.id] > 0:
        total += 1
      elif m[order.id][co_order.id] == -1:
        # go through each order and fill matrix on num of common dishes
        common_dishes = 0
        co_dishes = set([i.item.id for i in co_order.items.all()]) 
        common_dishes =  len(dishes & co_dishes)
        m[order.id][co_order.id] = common_dishes     
        m[co_order.id][order.id] = common_dishes     
        if common_dishes > 0:
          total += 1
  return m, total 

def calculate_virtual_orders(order):
  """
    Finds out how many virtual friends ordered the same thing
  """
  return 4 

def past_orders(row, order, friend_map):
  """
    Used by orders_export_table
    Find what people have ordered in the past and return information based on experiment id
  """
  
  exp = order.table.experiment.id
  uid = order.user.otnuser.id
  friends_list = friend_map[uid]['first'] 

  fb_list = set()
  for otnuser in OTNUser.objects.filter(id__in=friends_list):
    fb_list.add( otnuser.facebook_profile.facebook_id ) 
  fb_list = list(fb_list)

  for item in MenuItem.objects.all():
    row["item%d_o"%item.id] = 0
    row["item%d_w"%item.id] = 0
    row["item%d_c"%item.id] = 0

  other_orders = order.table.table_orders.annotate(num_items=Count('items')).filter(num_items__gt=0).exclude(id=order.id)
  for o in other_orders:
    for i in o.items.all():
      row["item%d_c"%i.item.id] += 1

  if exp == 2:
    past_orders = Order.objects.filter(user__otnuser__in=friends_list, timestamp__lt=order.timestamp) 
    for o in past_orders:
      for i in o.items.all():
        row["item%d_o"%i.item.id] += 1
    past_surveys = LegalsPopulationSurvey.objects.filter(facebook_id__in=fb_list, timestamp__lt=order.timestamp)
    for s in past_surveys:
      for i in s.favorite_dishes.all():  
        row["item%d_w"%i.id] += 1

  elif exp == 3:
    past_orders = Order.objects.filter(timestamp__lt=order.timestamp) 
    for o in past_orders:
      for i in o.items.all():
        row["item%d_o"%i.item.id] += 1 

    past_surveys = LegalsPopulationSurvey.objects.filter(timestamp__lt=order.timestamp)
    for s in past_surveys:
      for i in s.favorite_dishes.all():  
        row["item%d_w"%i.id] += 1

  elif exp == 4:
    past_orders = Order.objects.filter(user__otnuser__in=friends_list, timestamp__lt=order.timestamp) 
    for o in past_orders:
      for i in o.items.all():
        row["item%d_o"%i.item.id] += 1
    past_surveys = LegalsPopulationSurvey.objects.filter(facebook_id__in=fb_list, timestamp__lt=order.timestamp)
    for s in past_surveys:
      for i in s.favorite_dishes.all():  
        row["item%d_w"%i.id] += 1

  # Find what people have favorited in the past and return information based on experiment id
  # Find other items that were ordered from the table simultaneously
  return row

def orders_export_table():
  """
    Create every event into a table

    Every order recorded
  """

  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
  friend_map = pickle.load(friend_map_file)


  csv_file = open(PREFIX_DAT+"order_table.csv", "w")

  fieldnames = ['txnid', 'userid', 'experimentid', 'orderid', 'categoryid', 'itemid', 'ordertime', 'orderduration', 'tablesize', 'tableid', 'commonorders', 'commonvirtual', 'sex', 'age', 'likeseafood', 'restaurantvisits', 'seafoodvisits', 'legalsvisits', 'frequency', 'vegetarian', 'zipcode', 'favorite1', 'favorite2', 'favorite3', 'favorite4', 'favorite5', 'phonetype', 'presurveydate', 'presurveytoorder']

  # those items ordered by others
  for i in MenuItem.objects.all():
    fieldnames.append('item%d_o'%i.id)

  # those items selected during presurvey
  for i in MenuItem.objects.all():
    fieldnames.append('item%d_w'%i.id)

  # those items ordered on the same table
  for i in MenuItem.objects.all():
    fieldnames.append('item%d_c'%i.id)

  data_writer = csv.DictWriter(csv_file, fieldnames, restval='0', quoting=csv.QUOTE_NONNUMERIC, delimiter='\t')  #, quotechar='|', quoting=csv.QUOTE_MINIMAL) 

  data_writer.writeheader()

  # go through each order by time
  orders = Order.objects.all().annotate(num_items=Count('items')).filter(num_items__gt=0).order_by("timestamp")

  order_ids = [o.id for o in orders]
  max_id = np.max(order_ids)

  # Go through each user and create a pairwise matrix of common orders
  common = -np.ones([max_id+1, max_id+1])

  txn_id = 1
  for o in orders: 
    for item in o.items.all():
  
      row = {}  
      row['txnid'] = txn_id
      row['userid'] = o.user.id
      row['experimentid'] = o.table.experiment.id
      row['orderid'] = o.id
      row['categoryid'] = item.item.category.id
      row['itemid'] = item.item.id
      row['ordertime'] = o.timestamp

      row['orderduration'] = calculate_order_time(o)[0]
      row['tablesize'] = calculate_table_size(o) 
      row['tableid'] = o.table.id
      common, row['commonorders'] = calculate_common_orders(o, common)

      # number of common items with people on table
      
      # number of friends who participated

      # demographic information from presurvey
      presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=o.user.facebook_profile.facebook_id)
      if presurvey.exists():
        p = presurvey[0]
        row['sex'] = p.sex
        row['age'] = p.age
        row['likeseafood'] = p.like_seafood
        row['restaurantvisits'] = p.restaurant_visits
        row['seafoodvisits'] = p.seafood_visits
        row['legalsvisits'] = 1 if p.legals_visits else 0
        row['frequency'] = p.frequency
        row['vegetarian'] = 1 if p.vegetarian else 0
        row['zipcode'] = "%s"%p.zipcode

        i = 1
        while i < 6:
          label = 'favorite%d'%i
          row[label] = -1
          i += 1
        i = 1
        for f in p.favorite_dishes.all():
          label = 'favorite%d'%i
          row[label] = f.id
          i += 1
          if i > 5:
            break
        row['phonetype'] = p.phone_type        
        row['presurveydate'] = p.timestamp
        row['presurveytoorder'] = abs((o.timestamp-p.timestamp).total_seconds())
      else:
        row['sex'] = -1
        row['age'] = -1
        row['likeseafood'] = -1 
        row['restaurantvisits'] = -1 
        row['seafoodvisits'] = -1 
        row['legalsvisits'] = -1 
        row['frequency'] = -1
        row['vegetarian'] = -1 
        row['zipcode'] = -1 
        row['favorite1'] = -1
        row['favorite2'] = -1
        row['favorite3'] = -1
        row['favorite4'] = -1
        row['favorite5'] = -1
        row['phonetype'] = -1 
        row['presurveydate'] = -1 
        row['presurveytoorder'] = -1 

      row = past_orders(row, o, friend_map) 

      data_writer.writerow(row)
      txn_id += 1

  csv_file.close() 

def events_export_table():  
  """
    Create every event into a table

    Every event of the user recorded, including which dishes first considered and last
    time user added an item to the order
  """

  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
  friend_map = pickle.load(friend_map_file)

  csv_file = open(PREFIX_DAT+"event_table.csv", "w")

  fieldnames = ['txnid', 'userid', 'experimentid', 'orderid', 'categoryid', 'itemid', 'ordertime', 'orderduration', 'ordered', 'considertime', 'tablesize', 'tableid', 'commonorders', 'commonvirtual', 'sex', 'age', 'likeseafood', 'restaurantvisits', 'seafoodvisits', 'legalsvisits', 'frequency', 'vegetarian', 'zipcode', 'favorite1', 'favorite2', 'favorite3', 'favorite4', 'favorite5', 'phonetype', 'presurveydate', 'presurveytoorder']

  # those items ordered by others
  for i in MenuItem.objects.all():
    fieldnames.append('item%d_o'%i.id)

  # those items selected during presurvey
  for i in MenuItem.objects.all():
    fieldnames.append('item%d_w'%i.id)

  # those items ordered on the same table
  for i in MenuItem.objects.all():
    fieldnames.append('item%d_c'%i.id)

  data_writer = csv.DictWriter(csv_file, fieldnames, restval='0', quoting=csv.QUOTE_NONNUMERIC, delimiter='\t')  #, quotechar='|', quoting=csv.QUOTE_MINIMAL) 

  data_writer.writeheader()

  # go through each order by time
  orders = Order.objects.all().annotate(num_items=Count('items')).filter(num_items__gt=0).order_by("timestamp")

  order_ids = [o.id for o in orders]
  max_id = np.max(order_ids)

  # Go through each user and create a pairwise matrix of common orders
  common = -np.ones([max_id+1, max_id+1])

  txn_id = 1
  for o in orders: 
    menu_browse_events = EventMenuItem.objects.filter(order=o)
    for item_id in menu_browse_events.values_list('item__id', flat=True).distinct():
      item = MenuItem.objects.get(id=item_id) 
 
      row = {}  
      row['txnid'] = txn_id
      row['userid'] = o.user.id
      row['experimentid'] = o.table.experiment.id
      row['orderid'] = o.id
      row['categoryid'] = item.category.id
      row['itemid'] = item.id
      
      if o.items.filter(item__id=item_id).exists():
        row['ordered'] = 1
        last_mark_event = menu_browse_events.filter(item__id=item_id, action=EventMenuItem.MARK).order_by('-timestamp') 
        if last_mark_event:
          # if item in ordered list
          row['ordertime'] = last_mark_event[0].timestamp
        else:
          print "Order %d is inconsistent for item %d"%(o.id, item_id)
      else:
        row['ordered'] = 0
        row['ordertime'] = 0

      first_consider_event = menu_browse_events.filter(item__id=item_id, action=EventMenuItem.CONSIDER).order_by('timestamp') 
      if first_consider_event: 
        # if item in consideration events
        row['considertime'] = first_consider_event[0].timestamp
      else:
        row['considertime'] = 0

      row['orderduration'] = calculate_order_time(o)[0]
      row['tablesize'] = calculate_table_size(o) 
      row['tableid'] = o.table.id
      common, row['commonorders'] = calculate_common_orders(o, common)

      # number of common items with people on table
      
      # number of friends who participated

      # demographic information from presurvey
      presurvey = LegalsPopulationSurvey.objects.filter(facebook_id=o.user.facebook_profile.facebook_id)
      if presurvey.exists():
        p = presurvey[0]
        row['sex'] = p.sex
        row['age'] = p.age
        row['likeseafood'] = p.like_seafood
        row['restaurantvisits'] = p.restaurant_visits
        row['seafoodvisits'] = p.seafood_visits
        row['legalsvisits'] = 1 if p.legals_visits else 0
        row['frequency'] = p.frequency
        row['vegetarian'] = 1 if p.vegetarian else 0
        row['zipcode'] = "%s"%p.zipcode

        i = 1
        while i < 6:
          label = 'favorite%d'%i
          row[label] = -1
          i += 1
        i = 1
        for f in p.favorite_dishes.all():
          label = 'favorite%d'%i
          row[label] = f.id
          i += 1
          if i > 5:
            break
        row['phonetype'] = p.phone_type        
        row['presurveydate'] = p.timestamp
        row['presurveytoorder'] = abs((o.timestamp-p.timestamp).total_seconds())
      else:
        row['sex'] = -1
        row['age'] = -1
        row['likeseafood'] = -1 
        row['restaurantvisits'] = -1 
        row['seafoodvisits'] = -1 
        row['legalsvisits'] = -1 
        row['frequency'] = -1
        row['vegetarian'] = -1 
        row['zipcode'] = -1 
        row['favorite1'] = -1
        row['favorite2'] = -1
        row['favorite3'] = -1
        row['favorite4'] = -1
        row['favorite5'] = -1
        row['phonetype'] = -1 
        row['presurveydate'] = -1 
        row['presurveytoorder'] = -1 

      row = past_orders(row, o, friend_map) 

      data_writer.writerow(row)
      txn_id += 1
      print "Processing transaction: %d"%txn_id

  csv_file.close() 

def export_item_prices():
  csv_file = open(PREFIX_DAT+"item_prices.csv", "w")

  fieldnames = ['itemid', 'price', 'itemname', 'categoryid']

  data_writer = csv.DictWriter(csv_file, fieldnames, restval='0', quoting=csv.QUOTE_NONNUMERIC, delimiter='\t')  #, quotechar='|', quoting=csv.QUOTE_MINIMAL) 

  data_writer.writeheader()

  for m in MenuItem.objects.all():
    row = {}
    row['itemid'] = m.id
    row['price'] = m.cost()
    row['itemname'] = smart_str(m.name)
    row['categoryid'] = m.category.id

    print row
    data_writer.writerow(row)

  csv_file.close() 


def get_active_users():
  """
    List of user ids that have at least one item in the order
  """

  active_users = []
  for u in OTNUser.objects.all():
    orders =  u.legals_order.all().annotate(num_items=Count('items')).filter(num_items__gt=0)  
    if orders.exists():
      active_users.append(u.id)

  return active_users 

def friend_network(active_users):
  """
    Create friend network 1st, 2nd, 3rd degree with OTNUser IDs
  """

  friend_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    friends_1st = Friends.objects.get(facebook_id = u.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True)
    friends_1st_list = []
    for v in OTNUser.objects.exclude(id=u.id).filter(id__in=active_users).filter(facebook_profile__facebook_id__in=friends_1st): 
      friends_1st_list.append(v.id)
      friends_2nd =Friends.objects.get(facebook_id = v.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True) 
      friends_2nd_list = []
      for w in OTNUser.objects.exclude(id__in=[u.id,v.id]).filter(id__in=active_users).filter(facebook_profile__facebook_id__in=friends_2nd): 
        friends_2nd_list.append(w.id)
        friends_3rd = Friends.objects.get(facebook_id = w.facebook_profile.facebook_id).friends.all().values_list('facebook_id', flat=True) 
        friends_3rd_list = []
        for x in OTNUser.objects.exclude(id__in=[u.id,v.id, w.id]).filter(id__in=active_users).filter(facebook_profile__facebook_id__in=friends_3rd): 
          friends_3rd_list.append(x.id)

    friend_map[u.id] = {'first': friends_1st_list,
                        'second': friends_2nd_list,
                        'third': friends_3rd_list}

  assert friend_map.has_key(463)
  # save friend_map
  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "w")
  pickle.dump(friend_map, friend_map_file)


def friend_map_to_matrix():
  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
  friend_map = pickle.load(friend_map_file)

  users = friend_map.keys()

  friend_1st = np.zeros((len(users), len(users)))
  friend_2nd = np.zeros((len(users), len(users)))
  friend_3rd = np.zeros((len(users), len(users)))
  for i, u in enumerate(users):
    for f in friend_map[u]['first']:
      friend_1st[i][users.index(f)] = 1 
    for f in friend_map[u]['second']:
      friend_2nd[i][users.index(f)] = 1 
    for f in friend_map[u]['third']:
      friend_3rd[i][users.index(f)] = 1 

  data_path = PREFIX_DAT+"friend_mat.npz"
  data_file = open(data_path, "wb")
  np.savez(data_file, users=users, friend_1st=friend_1st, friend_2nd=friend_2nd, friend_3rd=friend_3rd) 
  data_file.close()

  data_path = PREFIX_DAT+"friend_mat.npz"
  if path.exists(data_path):
    data_file = open(data_path, "r")
    data_load = np.load(data_file)
    users = data_load["users"]
    friend_1st = data_load["friend_1st"]
    friend_2nd = data_load["friend_2nd"]
    friend_3rd = data_load["friend_3rd"]

  print "First Friends", friend_1st, np.sum(friend_1st)
  print "Second Friends", friend_2nd, np.sum(friend_2nd)
  print "Third Friends", friend_3rd, np.sum(friend_3rd)
  print "Users", users

  return friend_1st, friend_2nd, friend_3rd, users

def export_friend_net():
  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
  friend_map = pickle.load(friend_map_file)

  csv_file = open(PREFIX_DAT+"num_friends.csv", "w")

  fieldnames = ['userid', 'firstfriend', 'secondfriend', 'thirdfriend']

  data_writer = csv.DictWriter(csv_file, fieldnames, restval='0', quoting=csv.QUOTE_NONNUMERIC, delimiter='\t')  #, quotechar='|', quoting=csv.QUOTE_MINIMAL) 

  data_writer.writeheader()

  users = friend_map.keys()
  for k, v in friend_map.items():
    row = {}
    row['userid'] = k 
    row['firstfriend'] = len(v['first'])
    row['secondfriend'] = len(v['second'])
    row['thirdfriend'] = len(v['third'])
    data_writer.writerow(row)

  csv_file.close() 
  friend_map_file.close()

def orders_per_experiment():
  """
    Find how many positive orders have been made for each experiment
  """
  print "Experiment\tOrders"
  for exp in range(1,5):
    num_orders = Order.objects.filter(table__experiment__id=exp).annotate(num_items=Count('items')).filter(num_items__gt=0).count()
    print "%d\t%d"%(exp, num_orders)


if __name__=="__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "basic":
        taste_mat = calculate_probabilities()

    #active_users = get_active_users()
    #friend_network(active_users)

    #taste_choice_distribution()
    
    # the first timers tend to click one additional category
    #compare_first_vs_subsequent()

    #menu_choice_distribution_exp(1)
    #menu_choice_distribution_exp(2)
    #menu_choice_distribution_exp(3)
    """
    if len(sys.argv) > 1:
        menu_choice_distribution_exp(cat=int(sys.argv[1]), exp=int(sys.argv[2]))
    else:
        menu_choice_distribution_exp(1,1)

    """
    #menu_choice_distribution()
    #m = menu_choice_matrix()
    #time_distribution_experiment([1,2,3,4])
    
    #presurvey_network(56)
    #presurvey_order_relationship()

    #participant_network()
    #participant_exp_network()
    #num_people_per_table()

    #day_difference_between_orders()

    #mat = connectedness()
    # TODO: Did order change in different timed groups?

    """
    if len(sys.argv) > 1: 
         order_time_vs_price(cat_var=int(sys.argv[1]), exp_var=int(sys.argv[2]))
    else:
         order_time_vs_price(1, 1)
    """ 

    """
    for i in range(1,5):
        graph_order_influence(exp_id=i)
    graph_order_influence(label=1)

    graph_consider_influence(label=1)
    for i in range(1,5):
        graph_consider_influence(exp_id=i)
    """

    #population_stats()

    #menu_choice_network()
    #menu_choice_network_all()

    #order_time_evolution()

    #item_network(3) # seaweed salad
    #item_network(56) # rainbow trout
    #item_network(14) # clam chowder 

    #presurvey_cleanup()
    #presurvey_stats()
    #duration_categorize()

    #memory_effect()
    #memory_effect_experiments()

    #price_effect()

    #orders_export_table()
    events_export_table()
    #export_item_prices()
    #export_friend_net()

    #orders_per_experiment()

    """
        Seaweed Salad and Rainbow Trout which were not particularly popular
        during presurvey, start to rise with time as people are given feedback
    """



    """
      duration_categories() result

      Certain (< 300 s)
      [{'table__experiment': 4, 'id__count': 28}, {'table__experiment': 2, 'id__count': 43}, {'table__experiment': 1, 'id__count': 57}, {'table__experiment': 3, 'id__count': 38}]
      Dilemma (< 700 s)
      [{'table__experiment': 4, 'id__count': 36}, {'table__experiment': 2, 'id__count': 45}, {'table__experiment': 1, 'id__count': 32}, {'table__experiment': 3, 'id__count': 61}]
      Uncertain (< 1200 s)
      [{'table__experiment': 4, 'id__count': 16}, {'table__experiment': 2, 'id__count': 30}, {'table__experiment': 1, 'id__count': 25}, {'table__experiment': 3, 'id__count': 20}]

    """
