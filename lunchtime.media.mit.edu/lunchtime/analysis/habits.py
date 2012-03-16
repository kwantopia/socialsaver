import matplotlib
#matplotlib.use("CocoaAgg")
matplotlib.use("MacOSX")

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

from django.db.models import Sum, Avg, Count

from common.models import * 
from techcash.models import TechCashTransaction, TechCashBalance 
from offers.models import *
from bestbuy.models import *
from mobile.models import Event, FeedEvent

import numpy as np
import networkx as nx
import pygraphviz as pgv
from scipy.stats import stats
from os import path
from datetime import datetime, timedelta 
import matplotlib.dates as mdates
import random

from scipy.stats import ttest_ind, ttest_rel

import pickle

DEBUG = False

params = {'backend': 'pdf',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Avant Garde', 'Computer Modern Sans Serif'],
    'text.usetex': True,
    'text.latex.unicode': True}

matplotlib.rcParams.update(params)

img_type = "pdf"

PREFIX_IMG = "/Users/kwan/workspace/OTNWeb/lunchtime/images/"
PREFIX_DAT = "/Users/kwan/workspace/OTNWeb/lunchtime/data/"

EFF_START = "2010-01-29"
EFF_END = "2010-05-21"
EFF_DURATION = datetime(year=2010, month=5, day=21) - datetime(year=2010, month=1, day=29)

# track habits versus impulses
# create diversity index per person, if not diverse then the person is habitual. 

# create vectors for each user over a week and see how that vector changes across days, weeks, months

# observe any changes of users that used the iphone versus those that did not use the iphone

# How do you define similar behavior?
# People who purchase in 
# - same locations, 
# - similar times, 
# - similar average amounts (draw the social network of these people) 
# - and compare the degree of separation and similarity


# How do you compare purchase timeline?  You do a fourier transform on the timeline and compare the spectrum that exist in each timeline.


# Diversity: characterize how much variation exists on one's total num of locations and the different number of transitions (ratio of locations covered by this person).  How many transitions versus how many repeats?

# How would you define the ratio of changes - check by checking daily differences in locations during similar times.

# Check how variable one's lunch time is depending on day of the week
# How do you map location changes? markov chain?

# how many people turned off location tracking?

def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

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

  # save friend_map
  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "w")
  pickle.dump(friend_map, friend_map_file)

def random_friend_network(active_users):
  """
    Create friend network 1st, 2nd, 3rd degree with random number of friends so completely different degree distribution
  """

  friend_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    r_degree = random.randint(1,10)
    filtered_list_1st = set(random.sample(active_users, r_degree))-set([u.id])
    friends_1st_list = list(filtered_list_1st) 
    for v in friends_1st_list: 
      r_degree = random.randint(1,10)
      filtered_list_2nd = set(random.sample(active_users, r_degree))-set([u.id])-filtered_list_1st
      friends_2nd_list = list(filtered_list_2nd)
      for w in friends_2nd_list:
        r_degree = random.randint(1,10)
        filtered_list_3rd = set(random.sample(active_users, r_degree))-set([u.id])-filtered_list_1st-filtered_list_2nd
        friends_3rd_list = list(filtered_list_3rd)

    friend_map[u.id] = {'first': friends_1st_list,
                        'second': friends_2nd_list,
                        'third': friends_3rd_list}

  # save friend_map
  friend_map_file = open(PREFIX_DAT+"random_friend_map.obj", "w")
  pickle.dump(friend_map, friend_map_file)

def modified_friend_network(active_users):
  """
    Create friend network 1st, 2nd, 3rd degree with OTNUser IDs
    but with similar degree as real network
  """

  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
  orig_map = pickle.load(friend_map_file)

  friend_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    num_friends_1st = len(orig_map[u.id]['first'])
    filtered_list_1st = set(random.sample(active_users, num_friends_1st))-set([u.id])
    friends_1st_list = list(filtered_list_1st)
    for v in friends_1st_list: 
      num_friends_2nd = len(orig_map[u.id]['second'])
      filtered_list_2nd = set(random.sample(active_users, num_friends_2nd))-set([u.id])-filtered_list_1st
      friends_2nd_list = list(filtered_list_2nd)
      for w in friends_2nd_list:
        num_friends_3rd = len(orig_map[u.id]['third'])
        filtered_list_3rd = set(random.sample(active_users, num_friends_3rd))-set([u.id])-filtered_list_1st-filtered_list_2nd
        friends_3rd_list = list(filtered_list_3rd)

    friend_map[u.id] = {'first': friends_1st_list,
                        'second': friends_2nd_list,
                        'third': friends_3rd_list}

  # save friend_map
  friend_map_file = open(PREFIX_DAT+"modified_friend_map.obj", "w")
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

def location_stats():
    locations = []
    txns = []
    total = []

    # for all eating locations get basic statistics
    for l in Location.objects.filter(type=Location.EATERY).exclude(id=1): 
        locations.append(l)
        # number of transactions per location
        txns.append(l.techcashtransaction_set.all().count())
        sum = l.techcashtransaction_set.aggregate(sum_txns=Sum('amount'))
        if sum['sum_txns'] is None:
            total.append(0)
        else:
            # total $ amount in each location
            total.append(sum['sum_txns'])
         
    print total
    f = plt.figure()
    f.subplots_adjust(hspace=0.4)
    ax1 = f.add_subplot(211)
    # number of transactions per location
    ax1.bar(range(0, len(locations)), txns)
    #ax1.set_xticks(range(0, len(locations)))
    #ax1.set_xticklabels(locations, rotation=45)
    ax1.set_title("Total number of transactions per location")
    ax2 = f.add_subplot(212)
    # number of transactions per location
    ax2.bar(range(0, len(locations)), total)
    ax2.set_title("Total \$ amount of transactions per location")
    ax2.set_xlabel("Location")

    for i, n in enumerate(locations):
        if txns[i] == 0:
            print "%d (%d) %s"%(i, n.id, n.name), txns[i], 0 
        else:
            print "%d (%d) %s"%(i, n.id, n.name), txns[i], total[i]/float(txns[i])

    f.savefig(PREFIX_IMG+"location_stats.%s"%img_type, bbox_inches="tight")

    f.show()

def meal_time_all(active_users):
  """
    For each individual, map out the location vector based on the frequency and
    amount of transaction
  """

  location_visits_file = open(PREFIX_DAT+"location_visits.obj", "w") 
  location_spending_file = open(PREFIX_DAT+"location_spending.obj", "w")

  # get locations for food
  loc_indices = list(Location.objects.filter(type=Location.EATERY).values_list('id', flat=True).order_by('id'))
  num_locs = len(loc_indices)

  # to map the location id to the index (since not all location id's apply)
  loc_indices_file = open(PREFIX_DAT+"loc_indices.obj", "w")
  pickle.dump(loc_indices, loc_indices_file)
  loc_indices_file.close()

  location_spending = np.zeros((len(active_users), num_locs)) 
  location_visits = np.zeros((len(active_users), num_locs)) 

  for i, uid in enumerate(active_users):
    u = OTNUser.objects.get(id=uid) 
    frequency_per_location = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), location__type=Location.EATERY, amount__gt=0).values('location').annotate(visits=Count('location')).order_by('location')
    amount_per_location = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), location__type=Location.EATERY, amount__gt=0).values('location').annotate(total_amount=Sum('amount')).order_by('location')
    
    f = plt.figure()
    f.subplots_adjust(hspace=0.5)
    ax1 = f.add_subplot(211)
    ax2 = f.add_subplot(212)

    x = []
    y = []
    for l in frequency_per_location:
      x.append(loc_indices.index(l['location']))
      y.append(l['visits'])
      location_visits[i][loc_indices.index(l['location'])] = l['visits']

    # normalize y
    if len(y) > 0:
      y = np.array(y, dtype='float')
      ymax = y.max()
      if ymax > 0:
        y /= float(ymax)

    ax1.bar(x, y)
    ax1.set_xlim([0, 38])
    ax1.set_ylim([0,1])
    ax1.set_xlabel('Locations')
    ax1.set_ylabel('Normalized \# Visits')
    #ax1.set_ybound(lower=0)

    x = []
    y = []
    for l in amount_per_location:
      x.append(loc_indices.index(l['location']))
      y.append(l['total_amount'])
      location_spending[i][loc_indices.index(l['location'])] = l['total_amount']

    # normalize y
    if len(y) > 0:
      y = np.array(y, dtype='float')
      ymax = y.max()
      if ymax > 0:
        y /= float(ymax)

    ax2.bar(x, y)
    ax2.set_xlim([0, 38])
    ax2.set_ylim([0,1])
    ax2.set_xlabel('Locations')
    ax2.set_ylabel('Normalized Spending')
    #ax2.set_ybound(lower=0)

    f.savefig(PREFIX_IMG+"user_visits_spending_%d.%s"%(uid, img_type), bbox_inches="tight")
    plt.close()

  location_visits = location_visits.transpose(1,0)
  location_spending = location_spending.transpose(1,0)
  pickle.dump(location_visits, location_visits_file)
  pickle.dump(location_spending, location_spending_file)
  location_visits_file.close()
  location_spending_file.close()

def person_time_map(active_user):
  """
    For each person map out the activity over time
  """
  time_visits_file = open(PREFIX_DAT+"person_time_visits.obj", "w") 
  time_spending_file = open(PREFIX_DAT+"person_time_spending.obj", "w")

  # to map the location id to the index (since not all location id's apply)
  # get locations for food
  loc_indices_file = open(PREFIX_DAT+"loc_indices.obj", "r")
  loc_indices = pickle.load(loc_indices_file)
  num_locs = len(loc_indices)

  time_spending = np.zeros((len(active_users), 24)) 
  time_visits = np.zeros((len(active_users), 24)) 

  for t in range(0,24):
    frequency_per_time = TechCashTransaction.objects.filter(user__id__in=active_users, timestamp__range=(EFF_START, EFF_END), location__type=Location.EATERY, amount__gt=0).extra(where=['extract(hour from timestamp) in (%d,%d)'%(t,t+1)]).values('user').annotate(visits=Count('user')).order_by('user')

    amount_per_time = TechCashTransaction.objects.filter(user__id__in=active_users, timestamp__range=(EFF_START, EFF_END), location__type=Location.EATERY, amount__gt=0).extra(where=['extract(hour from timestamp) in (%d,%d)'%(t,t+1)]).values('user').annotate(total_amount=Sum('amount')).order_by('user')
    
    for l in frequency_per_time:
      time_visits[active_users.index(l['user'])][t] = l['visits']

    for l in amount_per_time:
      time_spending[active_users.index(l['user'])][t] = l['total_amount']

  pickle.dump(time_visits, time_visits_file)
  pickle.dump(time_spending, time_spending_file)
  time_visits_file.close()
  time_spending_file.close()

def person_time_map_plot():
  time_visits_file = open(PREFIX_DAT+"person_time_visits.obj", "r") 
  time_spending_file = open(PREFIX_DAT+"person_time_spending.obj", "r")

  time_visits = pickle.load(time_visits_file)
  time_spending = pickle.load(time_spending_file)

  f = plt.figure(figsize=(12,8))
  f.suptitle("Activity of different users by time of day")
  f.subplots_adjust(wspace=0.5)
  ax1 = f.add_subplot(121)
  ax2 = f.add_subplot(122)

  im = ax1.imshow(time_visits, origin='lower')
  divider = make_axes_locatable(ax1)
  cax = divider.append_axes("right", size="5%", pad=0.1)
  #axc, kw = matplotlib.colorbar.make_axes(ax1, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Num of visits")

  # Set the colorbar
  cax.colorbar = cb

  ax1.set_ylabel("Participant")
  ax1.set_xlabel("Time of Day")

  im = ax2.imshow(time_spending, origin='lower')
  divider = make_axes_locatable(ax2)
  cax = divider.append_axes("right", size="5%", pad=0.1)
  #axc, kw = matplotlib.colorbar.make_axes(ax2, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("\$ spent")

  # Set the colorbar
  cax.colorbar = cb

  ax2.set_ylabel("Participant")
  ax2.set_xlabel("Time of Day")

  f.savefig(PREFIX_IMG+"person_time_map_24hrs.%s"%(img_type)) #, bbox_inches="tight")

  f = plt.figure(figsize=(16,4))
  f.suptitle("Activity of different users by time of day")
  f.subplots_adjust(wspace=0.5)
  ax1 = f.add_subplot(121, projection='3d')
  ax2 = f.add_subplot(122, projection='3d')

  Y = np.arange(0, len(time_visits), 1)
  X = np.arange(0, len(time_visits[0]), 1)
  X, Y = np.meshgrid(X,Y)
  Z = time_visits

  surf = ax1.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=True)
  #ax1.set_zlim3d(1,10)
  #ax.w_zaxis.set_major_locator(LinearLocator(10))
  #ax.w_zaxis.set_major_formatter(FormatStrFormatter('%.03f'))

  Y = np.arange(0, len(time_spending), 1)
  X = np.arange(0, len(time_spending[0]), 1)
  X, Y = np.meshgrid(X,Y)
  Z = time_spending

  surf = ax2.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=True)

  time_visits_file.close()
  time_spending_file.close()

  f.savefig(PREFIX_IMG+"person_time_3d_map_24hrs.%s"%(img_type)) #, bbox_inches="tight")

  #plt.show()

def person_day_map(active_users):

  day_visits_file = open(PREFIX_DAT+"person_day_visits.obj", "w") 
  day_spending_file = open(PREFIX_DAT+"person_day_spending.obj", "w")

  # to map the location id to the index (since not all location id's apply)
  # get locations for food
  loc_indices_file = open(PREFIX_DAT+"loc_indices.obj", "r")
  loc_indices = pickle.load(loc_indices_file)
  num_locs = len(loc_indices)

  day_spending = np.zeros((len(active_users), 7)) 
  day_visits = np.zeros((len(active_users), 7)) 

  users = set()
  for u in OTNUser.objects.filter(id__in=active_users):
    # go through each day
    for d in range(1,8):
      txns = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, timestamp__week_day=d, location__type=Location.EATERY)
      num_visits = txns.count()
      sum_amount = txns.aggregate(Sum('amount'))
      if sum_amount['amount__sum']:
        day_spending[active_users.index(u.id)][d-1] = sum_amount['amount__sum'] 
      day_visits[active_users.index(u.id)][d-1] = num_visits

  pickle.dump(day_spending, day_spending_file)
  pickle.dump(day_visits, day_visits_file)

  day_spending_file.close()
  day_visits_file.close()
 
def person_day_map_plot(active_users):
  # create a distribution graph
  day_visits_file = open(PREFIX_DAT+"person_day_visits.obj", "r") 
  day_spending_file = open(PREFIX_DAT+"person_day_spending.obj", "r")

  day_visits = pickle.load(day_visits_file)
  day_spending = pickle.load(day_spending_file)

  f = plt.figure(figsize=(6,14))
  f.suptitle("Activity during different day of the week")
  f.subplots_adjust(wspace=0.5)
  ax1 = f.add_subplot(121)
  ax2 = f.add_subplot(122)

  im = ax1.imshow(day_visits, origin='lower')
  divider = make_axes_locatable(ax1)
  cax = divider.append_axes("right", size="10%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax1, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Num of visits")

  # Set the colorbar
  cax.colorbar = cb

  ax1.set_ylabel("User")
  ax1.set_xlabel("Day of the Week")

  im = ax2.imshow(day_spending, origin='lower')
  divider = make_axes_locatable(ax2)
  cax = divider.append_axes("right", size="10%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax2, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("\$ spent")

  # Set the colorbar
  cax.colorbar = cb

  ax2.set_ylabel("User")
  ax2.set_xlabel("Day of the Week")

  f.savefig(PREFIX_IMG+"person_day_map.%s"%(img_type)) #, bbox_inches="tight")


def location_time_map(active_users):
  """
    For each location map out how much activity there is over time
  """
  time_visits_file = open(PREFIX_DAT+"time_visits.obj", "w") 
  time_spending_file = open(PREFIX_DAT+"time_spending.obj", "w")

  # get locations for food
  loc_indices_file = open(PREFIX_DAT+"loc_indices.obj", "r")
  loc_indices = pickle.load(loc_indices_file)
  num_locs = len(loc_indices)

  location_spending = np.zeros((24, num_locs)) 
  location_visits = np.zeros((24, num_locs)) 

  for i in range(0,24):
    frequency_per_location = TechCashTransaction.objects.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY, user__id__in=active_users).extra(where=['extract(hour from timestamp) in (%d,%d)'%(i,i+1)]).values('location').annotate(visits=Count('location')).order_by('location')
    amount_per_location = TechCashTransaction.objects.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY, user__id__in=active_users).extra(where=['extract(hour from timestamp) in (%d,%d)'%(i,i+1)]).values('location').annotate(total_amount=Sum('amount')).order_by('location')

    for l in frequency_per_location:
      location_visits[i][loc_indices.index(l['location'])] = l['visits']

    for l in amount_per_location:
      location_spending[i][loc_indices.index(l['location'])] = l['total_amount']

  location_visits = location_visits.transpose(1,0)
  location_spending = location_spending.transpose(1,0)
  pickle.dump(location_visits, time_visits_file)
  pickle.dump(location_spending, time_spending_file)
  time_visits_file.close()
  time_spending_file.close()

def location_time_map_plot():

  time_visits_file = open(PREFIX_DAT+"time_visits.obj", "r") 
  time_spending_file = open(PREFIX_DAT+"time_spending.obj", "r")

  location_visits = pickle.load(time_visits_file)
  location_spending = pickle.load(time_spending_file)

  f = plt.figure(figsize=(12,8))
  f.suptitle("Activity in different locations by time of day")
  f.subplots_adjust(wspace=0.5)
  ax1 = f.add_subplot(121)
  ax2 = f.add_subplot(122)

  im = ax1.imshow(location_visits, origin='lower')
  divider = make_axes_locatable(ax1)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax1, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Num of visits")

  # Set the colorbar
  cax.colorbar = cb

  ax1.set_ylabel("Locations")
  ax1.set_xlabel("Time of Day")

  im = ax2.imshow(location_spending, origin='lower')
  divider = make_axes_locatable(ax2)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax2, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("\$ spent")

  # Set the colorbar
  cax.colorbar = cb

  ax2.set_ylabel("Locations")
  ax2.set_xlabel("Time of Day")

  f.savefig(PREFIX_IMG+"location_time_map_24hrs.%s"%(img_type)) #, bbox_inches="tight")


  f = plt.figure(figsize=(16,4))
  f.suptitle("Activity in different locations by time of day")
  f.subplots_adjust(wspace=0.5)
  ax1 = f.add_subplot(121, projection='3d')
  ax2 = f.add_subplot(122, projection='3d')

  X = np.arange(0, 24, 1)
  Y = np.arange(0, 38, 1)
  X, Y = np.meshgrid(X,Y)
  Z = location_visits

  surf = ax1.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=True)
  #ax1.set_zlim3d(1,10)
  #ax.w_zaxis.set_major_locator(LinearLocator(10))
  #ax.w_zaxis.set_major_formatter(FormatStrFormatter('%.03f'))

  X = np.arange(0, 24, 1)
  Y = np.arange(0, 38, 1)
  X, Y = np.meshgrid(X,Y)
  Z = location_spending

  surf = ax2.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=True)

  time_visits_file.close()
  time_spending_file.close()

  f.savefig(PREFIX_IMG+"location_time_3d_map_24hrs.%s"%(img_type)) #, bbox_inches="tight")

  #plt.show()

def meal_time(active_users, begin, end):
  """
    For each individual, map out the location vector based on the frequency and
    amount of transaction
  """

  location_visits_file = open(PREFIX_DAT+"location_visits_%d_%d.obj"%(begin, end), "w") 
  location_spending_file = open(PREFIX_DAT+"location_spending_%d_%d.obj"%(begin, end), "w")

  # get locations for food
  loc_indices_file = open(PREFIX_DAT+"loc_indices.obj", "r")
  loc_indices = pickle.load(loc_indices_file)
  num_locs = len(loc_indices)

  location_spending = np.zeros((len(active_users), num_locs)) 
  location_visits = np.zeros((len(active_users), num_locs)) 

  for i, uid in enumerate(active_users):
    u = OTNUser.objects.get(id=uid) 
    frequency_per_location = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY).extra(where=['extract(hour from timestamp) in (%d,%d)'%(begin,end)]).values('location').annotate(visits=Count('location')).order_by('location')
    amount_per_location = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY).extra(where=['extract(hour from timestamp) in (%d,%d)'%(begin,end)]).values('location').annotate(total_amount=Sum('amount')).order_by('location')

    f = plt.figure()
    ax1 = f.add_subplot(211)
    ax2 = f.add_subplot(212)

    x = []
    y = []
    for l in frequency_per_location:
      x.append(loc_indices.index(l['location']))
      y.append(l['visits'])
      location_visits[i][loc_indices.index(l['location'])] = l['visits']

    ax1.bar(x, y)
    ax1.set_xlim([0, 38])
    ax1.set_ybound(lower=0)

    x = []
    y = []
    for l in amount_per_location:
      x.append(loc_indices.index(l['location']))
      y.append(l['total_amount'])
      location_spending[i][loc_indices.index(l['location'])] = l['total_amount']

    ax2.bar(x, y)
    ax2.set_xlim([0, 38])
    ax2.set_ybound(lower=0)

    # TODO: draw out the matrix

    f.savefig(PREFIX_IMG+"hr_%d_visits_spending_%d_%d.%s"%(uid, begin, end, img_type), bbox_inches="tight")
    plt.close()


  location_visits = location_visits.transpose(1,0)
  location_spending = location_spending.transpose(1,0)
  pickle.dump(location_visits, location_visits_file)
  pickle.dump(location_spending, location_spending_file)
  location_visits_file.close()
  location_spending_file.close()

def meal_time_plot(begin=0, end=0):
  """
    Plots activity during lunch time 10-15 hours
  """

  if begin==0 and end==0:
    location_visits_lunch = pickle.load(open(PREFIX_DAT+"location_visits.obj"))
    location_spending_lunch = pickle.load(open(PREFIX_DAT+"location_spending.obj"))
  else:
    location_visits_lunch = pickle.load(open(PREFIX_DAT+"location_visits_%d_%d.obj"%(begin, end)))
    location_spending_lunch = pickle.load(open(PREFIX_DAT+"location_spending_%d_%d.obj"%(begin, end)))

  f = plt.figure(figsize=(16,4))
  f.suptitle("Activity in different locations")
  f.subplots_adjust(wspace=0.5)
  ax1 = f.add_subplot(121)
  ax2 = f.add_subplot(122)

  im = ax1.imshow(location_visits_lunch, origin='lower')
  divider = make_axes_locatable(ax1)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax2, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Num of visits")

  # Set the colorbar
  cax.colorbar = cb

  ax1.set_ylabel("Locations")
  ax1.set_xlabel("Participants")

  im = ax2.imshow(location_spending_lunch, origin='lower')
  divider = make_axes_locatable(ax2)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax2, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("\$ spent")

  # Set the colorbar
  cax.colorbar = cb

  ax2.set_ylabel("Locations")
  ax2.set_xlabel("Participants")

  f.savefig(PREFIX_IMG+"hr_visits_spending_%d_%d.%s"%(begin, end, img_type)) #, bbox_inches="tight")

  #plt.show()

def diversity_plot():
    data_path = PREFIX_DAT+"diversity.npz"

    if path.exists(data_path):
        data_file = open(data_path, "r")
        data_load = np.load(data_file)
        div_mat = data_load["diversity_mat"]

        f = plt.figure(figsize=(8,12))
        f.subplots_adjust(hspace=0.6)
        ax1 = f.add_subplot(311)
        ax2 = f.add_subplot(312)
        ax3 = f.add_subplot(313)

        ax1.hist(div_mat[:,1], 20)
        ax1.set_xlabel("Number of distinct locations")
        ax1.set_ylabel("\# Users")
        ax2.hist(div_mat[:,2], 20)
        ax2.set_xlabel("Frequency of transactions")
        ax2.set_ylabel("\# Users")
        ax3.hist(div_mat[:,4], 20)
        ax3.set_xlabel("Diversity")
        ax3.set_ylabel("\# Users")

        f.savefig(PREFIX_IMG+"diversity_summary.%s"%img_type, bbox_inches="tight")

        f.show()

    else:
        print "Data file needs to be created first by calling habitual_behavior(True)"

def similarity_for_friends(active_users, first_monday, last_monday, socialnet, degree="first", normalize=True ):
  """
      Analyzes the similarity between individuals and their friends

      Create a vector that has time difference distribution of TechCASH usage
      and a vector of locations used and measure similarity.

      Cluster people by similar behavior

      TODO: show mean and std for each plot

      0: dollar amount on average
      1: frequency on average
      2: average dollar amount for each day of week
      3: average frequency for each day of week
      4: average dollar amount for each two hour of a day
      5: average frequency for each two hour of a day
      6: average dollar amount for each hour of a day
      7: average frequency for each hour of a day
  """

  if socialnet=="original":
    friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
    friend_map = pickle.load(friend_map_file)
  elif socialnet=="modified":
    friend_map_file = open(PREFIX_DAT+"modified_friend_map.obj", "r")
    friend_map = pickle.load(friend_map_file)
  elif socialnet=="random":
    friend_map_file = open(PREFIX_DAT+"random_friend_map.obj", "r")
    friend_map = pickle.load(friend_map_file)

  results = []
  
  fig1 = plt.figure(figsize=(8,4))
  fig1.subplots_adjust(hspace=0.5)
  ax1 = fig1.add_subplot(121)
  ax2 = fig1.add_subplot(122)

  fig2 = plt.figure(figsize=(9,6))
  fig2.subplots_adjust(hspace=0.5)
  ax3 = fig2.add_subplot(321)
  ax4 = fig2.add_subplot(322)

  # x-axis is the similarity and y-axis is the number of people in that similarity index
  duration = EFF_DURATION 
  num_days = duration.days 

  # file names to save data
  avg_spending_file = open(PREFIX_DAT+"avg_spending.obj", "w")
  avg_visits_file = open(PREFIX_DAT+"avg_visits.obj", "w")
  avg_spending_dow_file = open(PREFIX_DAT+"avg_spending_dow.obj", "w")
  avg_visits_dow_file = open(PREFIX_DAT+"avg_visits_dow.obj", "w")
  avg_spending_12_hrs_file = open(PREFIX_DAT+"avg_spending_12_hrs.obj", "w")
  avg_visits_12_hrs_file = open(PREFIX_DAT+"avg_visits_12_hrs.obj", "w")
  avg_spending_24_hrs_file = open(PREFIX_DAT+"avg_spending_24_hrs.obj", "w")
  avg_visits_24_hrs_file = open(PREFIX_DAT+"avg_visits_24_hrs.obj", "w")

  # 1. similarity in dollar amount - average per fixed duration 
  # for each user find out the average dollar amount spent each week and normalize
  # compare with friends this vector over the week

  # final results
  sim_amount_map = {}

  # calculate average amount of transactions
  avg_amount_map = {}
  users = set()
  for u in OTNUser.objects.filter(id__in=active_users):
    sum_amount = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY).aggregate(Sum("amount"))
    #print sum_amount
    if sum_amount['amount__sum']:
      avg_amount = float(sum_amount['amount__sum'])/num_days
      if avg_amount > 0:
        users.add(u.id)
        avg_amount_map[u.id] = avg_amount 

  pickle.dump(avg_amount_map, avg_spending_file)
  avg_spending_file.close()
  # find out the avg amount each user's friend spends 
  for u in OTNUser.objects.filter(id__in=list(users)):
    n_friends = 0
    amount_friends = []
    for z in OTNUser.objects.filter(id__in=friend_map[u.id][degree]):
      if z.id in avg_amount_map:
        assert avg_amount_map[z.id] != np.nan 
        n_friends += 1
        amount_friends.append(avg_amount_map[z.id])

    if n_friends > 0:
      # find the average difference with friends
      # amount_friends is a vector with each of friends' average
      # avg_amount_map[u.id] is u's average spending
      # NOTE: greater the value greater the difference
      b = np.sum(np.abs(np.array(amount_friends)-avg_amount_map[u.id]))/n_friends
      sim_amount_map[u.id] = b
  
  # create a distribution graph
  sim_vec = np.array(sim_amount_map.values())/np.max(sim_amount_map.values())
  ax1.hist(sim_vec, label="txnamount")
  ax1.set_title("Transaction amount in social network")
  ax1.set_ylabel("\# of participants")
  ax1.set_xlabel("Similarity measure")
  ax1.axis('tight')
  ax1.set_xlim(0,1)

  results.append(sim_vec)

  # 2. similarity in number of visits averaged over fixed duration
  # final results
  sim_frequency_map = {}

  avg_frequency_map = {}
  users = set()
  for u in OTNUser.objects.filter(id__in=active_users):
    sum_frequency = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY).count()
    avg_frequency = float(sum_frequency)/num_days
    if avg_frequency > 0:
      users.add(u.id)
      avg_frequency_map[u.id] = avg_frequency

  pickle.dump(avg_frequency_map, avg_visits_file)
  avg_visits_file.close()
  # calculate similarity between friends
  for u in OTNUser.objects.filter(id__in=list(users)):
    n_friends = 0
    frequency_friends = []
    for z in OTNUser.objects.filter(id__in=friend_map[u.id][degree]):
      #.exclude(facebook_profile__facebook_id=706848):
      if z.id in avg_frequency_map:
        assert avg_frequency_map[z.id] != np.nan 
        n_friends += 1
        frequency_friends.append(avg_frequency_map[z.id])

    if n_friends > 0:
      # NOTE: greater the value greater the difference
      b = np.sum(np.abs(np.array(amount_friends)-avg_amount_map[u.id]))/n_friends
      sim_frequency_map[u.id] = b
  
  # create a distribution graph
  sim_vec = np.array(sim_frequency_map.values())/np.max(sim_frequency_map.values())
  ax2.hist(sim_vec, label="txnamount")
  ax2.set_title("Transaction frequency in social network")
  ax2.set_ylabel("\# of participants")
  ax2.set_xlabel("Similarity measure")
  ax2.axis('tight')
  ax2.set_xlim(0,1)

  results.append(sim_vec)

  # 3. similarity in dollar amount each week (7 vector with dollar amount for each day averaged)
  sim_per_day_map = {}

  users = set()
  per_day_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    per_day_map[u.id] = np.zeros(7)
    # go through each day
    for d in range(1,8):
      sum_amount = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, timestamp__week_day=d, location__type=Location.EATERY).aggregate(Sum('amount'))
      if sum_amount['amount__sum']:
        per_day_map[u.id][d-1] = sum_amount['amount__sum'] 
    if not np.array_equal(per_day_map[u.id], np.zeros(7)):
      # only look at users that have transactions
      users.add(u.id)

  # normalize per_day_map
  if normalize:
    for uid in users:
      per_day_map[uid] = per_day_map[uid]/float(np.max(per_day_map[uid]))

  pickle.dump(per_day_map, avg_spending_dow_file)
  avg_spending_dow_file.close()
  # calculate similarity between friends
  for u in OTNUser.objects.filter(id__in=list(users)):
    n_friends = 0
    per_day_friends = []
    for z in OTNUser.objects.filter(id__in=friend_map[u.id][degree]):
      #.exclude(facebook_profile__facebook_id=706848):
      if z.id in per_day_map and not np.array_equal(per_day_map[z.id], np.zeros(7)):
        n_friends += 1
        per_day_friends.append(per_day_map[z.id])

    if n_friends > 0:
      #print per_day_friends
      # need to calculate vector distance with friends
      per_day_friends = np.array(per_day_friends)
      numerator = np.dot(per_day_friends, per_day_map[u.id])
      denominator = np.sqrt(np.sum(np.square(per_day_friends), axis=1))*np.sqrt(np.sum(np.square(per_day_map[u.id])))
      b = numerator/denominator      #b = np.sum(np.sqrt(np.sum(np.square(np.array(per_day_friends)-per_day_map[u.id]), axis=1)))/n_friends
      if np.mean(b) == np.nan:
        sim_per_day_map[u.id] = 0  
      else:
        sim_per_day_map[u.id] = np.mean(b) 
  
  # create a distribution graph
  #print sim_per_day_map.values()
  #print np.max(np.array(sim_per_day_map.values()))
  sim_vec = np.array(sim_per_day_map.values())/np.max(np.array(sim_per_day_map.values()))
  ax3.hist(sim_vec, label="txnamountweek")
  ax3.set_title("Transaction amount per day of week")
  ax3.set_ylabel("\# of participants")
  ax3.set_xlabel("Similarity measure")
  ax3.axis('tight')
  ax3.set_xlim(0,1)

  results.append(sim_vec)

  # 4. similarity in frequency of transactions (7 vector with number of transactions per day averaged)
  sim_per_day_map = {}

  users = set()
  per_day_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    per_day_map[u.id] = np.zeros(7)
    for d in range(1,8):
      sum_frequency = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, timestamp__week_day=d, location__type=Location.EATERY).count()
      per_day_map[u.id][d-1] = sum_frequency
    if not np.array_equal(per_day_map[u.id], np.zeros(7)):
      # only look at users that have transactions
      users.add(u.id)

  # normalize per_day_map
  if normalize:
    for u in users:
      per_day_map[u] = per_day_map[u]/float(np.max(per_day_map[u]))

  pickle.dump(per_day_map, avg_visits_dow_file)
  avg_visits_dow_file.close()
  # calculate similarity between friends
  for u in OTNUser.objects.filter(id__in=list(users)):
    n_friends = 0
    per_day_friends = []
    for z in OTNUser.objects.filter(id__in=friend_map[u.id][degree]):
      #.exclude(facebook_profile__facebook_id=706848):
      if z.id in per_day_map and not np.array_equal(per_day_map[z.id], np.zeros(7)):
        n_friends += 1
        per_day_friends.append(per_day_map[z.id])

    if n_friends > 0:
      #print per_day_friends
      # need to calculate vector distance with friends
      #b = np.sum(np.sqrt(np.sum(np.square(np.array(per_day_friends)-per_day_map[u.id]), axis=1)))/n_friends
      b = np.dot(per_day_friends, per_day_map[u.id])/(np.sqrt(np.sum(np.square(per_day_friends), axis=1))*np.sqrt(np.sum(np.square(per_day_map[u.id]))))
      sim_per_day_map[u.id] = np.mean(b)
  
  # create a distribution graph
  sim_vec = np.array(sim_per_day_map.values())/np.max(sim_per_day_map.values())
  ax4.hist(sim_vec, label="txnfreqweek")
  ax4.set_title("Transaction frequency per day of week")
  ax4.set_ylabel("\# of participants")
  ax4.set_xlabel("Similarity measure")
  ax4.axis('tight')
  ax4.set_xlim(0,1)

  results.append(sim_vec)
   

  ax5 = fig2.add_subplot(323)
  ax6 = fig2.add_subplot(324)
  ax7 = fig2.add_subplot(325)
  ax8 = fig2.add_subplot(326)


  # 5. similarity in amount of transactions per time of day (12 vector, with two hour blocks per value)
  sim_per_day_map = {}

  users = set()
  per_day_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    per_day_map[u.id] = np.zeros(12)
    for d in range(1,13):
      sum_amount = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY).extra(where=['extract(hour from timestamp) in (%d,%d)'%((d-1)*2,(d-1)*2+1)]).aggregate(Sum('amount'))
      if sum_amount['amount__sum']:
        per_day_map[u.id][d-1] = sum_amount['amount__sum']
    if not np.array_equal(per_day_map[u.id], np.zeros(12)):
      # only look at users that have transactions
      users.add(u.id)

  # normalize per_day_map
  if normalize:
    for u in users:
      per_day_map[u] = per_day_map[u]/float(np.max(per_day_map[u]))

  pickle.dump(per_day_map, avg_spending_12_hrs_file)
  avg_spending_12_hrs_file.close()
  # calculate similarity between friends
  for u in OTNUser.objects.filter(id__in=list(users)):
    n_friends = 0
    per_day_friends = []
    for z in OTNUser.objects.filter(id__in=friend_map[u.id][degree]):
      #.exclude(facebook_profile__facebook_id=706848):
      if z.id in per_day_map and not np.array_equal(per_day_map[z.id], np.zeros(12)):
        n_friends += 1
        per_day_friends.append(per_day_map[z.id])

    if n_friends > 0:
      #print per_day_friends
      # need to calculate vector distance with friends
      b = np.dot(per_day_friends, per_day_map[u.id])/(np.sqrt(np.sum(np.square(per_day_friends), axis=1))*np.sqrt(np.sum(np.square(per_day_map[u.id]))))
      #b = np.sum(np.sqrt(np.sum(np.square(np.array(per_day_friends)-per_day_map[u.id]), axis=1)))/n_friends
      sim_per_day_map[u.id] = np.mean(b)
  
  # create a distribution graph
  sim_vec = np.array(sim_per_day_map.values())/np.max(sim_per_day_map.values())
  ax5.hist(sim_vec, label="txnamount12hr")
  ax5.set_title("Transaction amount/time of day (12)")
  ax5.set_ylabel("\# of participants")
  ax5.set_xlabel("Similarity measure")
  ax5.axis('tight')
  ax5.set_xlim(0,1)

  results.append(sim_vec)


  # 6. similarity in frequency of transactions per time of day (12 vector, with two hour blocks per value)
  sim_per_day_map = {}

  users = set()
  per_day_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    per_day_map[u.id] = np.zeros(12)
    for d in range(1,13):
      sum_frequency = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY).extra(where=['extract(hour from timestamp) in (%d,%d)'%((d-1)*2,(d-1)*2+1)]).count()
      per_day_map[u.id][d-1] = sum_frequency
    if not np.array_equal(per_day_map[u.id], np.zeros(12)):
      # only look at users that have transactions
      users.add(u.id)

  # normalize per_day_map
  if normalize:
    for u in users:
      per_day_map[u] = per_day_map[u]/float(np.max(per_day_map[u]))

  pickle.dump(per_day_map, avg_visits_12_hrs_file)
  avg_visits_12_hrs_file.close()
  # calculate similarity between friends
  for u in OTNUser.objects.filter(id__in=list(users)):
    n_friends = 0
    per_day_friends = []
    for z in OTNUser.objects.filter(id__in=friend_map[u.id][degree]):
      #.exclude(facebook_profile__facebook_id=706848):
      if z.id in per_day_map and not np.array_equal(per_day_map[z.id], np.zeros(12)):
        n_friends += 1
        per_day_friends.append(per_day_map[z.id])

    if n_friends > 0:
      #print per_day_friends
      # need to calculate vector distance with friends
      b = np.dot(per_day_friends, per_day_map[u.id])/(np.sqrt(np.sum(np.square(per_day_friends), axis=1))*np.sqrt(np.sum(np.square(per_day_map[u.id]))))
      #b = np.sum(np.sqrt(np.sum(np.square(np.array(per_day_friends)-per_day_map[u.id]), axis=1)))/n_friends
      sim_per_day_map[u.id] = np.mean(b)
  
  # create a distribution graph
  sim_vec = np.array(sim_per_day_map.values())/np.max(sim_per_day_map.values())
  ax6.hist(sim_vec, label="txnfreqday")
  ax6.set_title("Transaction frequency/time of day (12)")
  ax6.set_ylabel("\# of participants")
  ax6.set_xlabel("Similarity measure")
  ax6.axis('tight')
  ax6.set_xlim(0,1)

  results.append(sim_vec)


  # 7. similarity in amount of transactions per time of day (24 vector, with one hour blocks per value)
  sim_per_day_map = {}

  users = set()
  per_day_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    per_day_map[u.id] = np.zeros(24)
    for d in range(0,24):
      sum_amount = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY).extra(where=['extract(hour from timestamp)=%d'%d]).aggregate(Sum('amount'))
      if sum_amount['amount__sum']:
        per_day_map[u.id][d-1] = sum_amount['amount__sum']
    if not np.array_equal(per_day_map[u.id], np.zeros(24)):
      # only look at users that have transactions
      users.add(u.id)

  # normalize per_day_map
  if normalize:
    for u in users:
      per_day_map[u] = per_day_map[u]/float(np.max(per_day_map[u]))

  pickle.dump(per_day_map, avg_spending_24_hrs_file)
  avg_spending_24_hrs_file.close()
  # calculate similarity between friends
  for u in OTNUser.objects.filter(id__in=list(users)):
    n_friends = 0
    per_day_friends = []
    for z in OTNUser.objects.filter(id__in=friend_map[u.id][degree]):
      #.exclude(facebook_profile__facebook_id=706848):
      if z.id in per_day_map and not np.array_equal(per_day_map[z.id], np.zeros(24)):
        n_friends += 1
        per_day_friends.append(per_day_map[z.id])

    if n_friends > 0:
      #print per_day_friends
      # need to calculate vector distance with friends
      b = np.dot(per_day_friends, per_day_map[u.id])/(np.sqrt(np.sum(np.square(per_day_friends), axis=1))*np.sqrt(np.sum(np.square(per_day_map[u.id]))))
      #b = np.sum(np.sqrt(np.sum(np.square(np.array(per_day_friends)-per_day_map[u.id]), axis=1)))/n_friends
      sim_per_day_map[u.id] = np.mean(b)
  
  # create a distribution graph
  sim_vec = np.array(sim_per_day_map.values())/np.max(sim_per_day_map.values())
  ax7.hist(sim_vec, label="txnamount24hr")
  ax7.set_title("Transaction amount/time of day (24)")
  ax7.set_ylabel("\# of participants")
  ax7.set_xlabel("Similarity measure")
  ax7.axis('tight')
  ax7.set_xlim(0,1)

  results.append(sim_vec)

  # 8. similarity in frequency of transactions per time of day (24 vector, with one hour blocks per value)
  sim_per_day_map = {}

  users = set()
  per_day_map = {}
  for u in OTNUser.objects.filter(id__in=active_users):
    per_day_map[u.id] = np.zeros(24)
    for d in range(0,24):
      sum_frequency = u.techcashtransaction_set.filter(timestamp__range=(EFF_START, EFF_END), amount__gt=0, location__type=Location.EATERY).extra(where=['extract(hour from timestamp)=%d'%d]).count()
      per_day_map[u.id][d-1] = sum_frequency
    if not np.array_equal(per_day_map[u.id], np.zeros(24)):
      # only look at users that have transactions
      users.add(u.id)

  # normalize per_day_map
  if normalize:
    for u in users:
      per_day_map[u] = per_day_map[u]/float(np.max(per_day_map[u]))

  pickle.dump(per_day_map, avg_visits_24_hrs_file)
  avg_visits_24_hrs_file.close()
  # calculate similarity between friends
  for u in OTNUser.objects.filter(id__in=list(users)):
    n_friends = 0
    per_day_friends = []
    for z in OTNUser.objects.filter(id__in=friend_map[u.id][degree]):
      #.exclude(facebook_profile__facebook_id=706848):
      if z.id in per_day_map and not np.array_equal(per_day_map[z.id], np.zeros(24)):
        n_friends += 1
        per_day_friends.append(per_day_map[z.id])

    if n_friends > 0:
      #print per_day_friends
      # need to calculate vector distance with friends
      b = np.dot(per_day_friends, per_day_map[u.id])/(np.sqrt(np.sum(np.square(per_day_friends), axis=1))*np.sqrt(np.sum(np.square(per_day_map[u.id]))))
      #b = np.sum(np.sqrt(np.sum(np.square(np.array(per_day_friends)-per_day_map[u.id]), axis=1)))/n_friends
      sim_per_day_map[u.id] = np.mean(b)
  
  # create a distribution graph
  sim_vec = np.array(sim_per_day_map.values())/np.max(sim_per_day_map.values())
  ax8.hist(sim_vec, label="txnfreqday")
  ax8.set_title("Transaction frequency/time of day (24)")
  ax8.set_ylabel("\# of participants")
  ax8.set_xlabel("Similarity measure")
  ax8.axis('tight')
  ax8.set_xlim(0,1)

  results.append(sim_vec)

  fig1.savefig(PREFIX_IMG+"similarity_friends_%s_%s.%s"%(socialnet, degree, img_type), bbox_inches="tight")
  fig2.savefig(PREFIX_IMG+"similarity_friends_hrs_%s_%s.%s"%(socialnet, degree, img_type), bbox_inches="tight")
  #plt.show()
  plt.close()
  friend_map_file.close()

  return results

def diversity_mobile_influences(active_users):
    """
        Identify whether weekly diversity was affected by the mobile access 

        The more different locations they went it is higher, the more they went to a single location, it is lower (num of locations/frequency) 
    """

    # go through each user and find distinct locations they have been to
    # and the total frequency of all the locations

    # create a matrix from earliest to latest, insert 0 if no transactions that week
    #latest = TechCashTransaction.objects.all().order_by("-timestamp")[0]
    #first = TechCashTransaction.objects.all().order_by("timestamp")[0]
    latest = TechCashTransaction.objects.filter(timestamp__range=(EFF_START, EFF_END)).order_by("-timestamp")[0]
    first = TechCashTransaction.objects.filter(timestamp__range=(EFF_START, EFF_END)).order_by("timestamp")[0]

    ft = first.timestamp
    first_day = ft.weekday()
    first_mon_delta = 0
    if first_day != 0:
        first_mon_delta = 7 - first_day
    first_monday = datetime(year=ft.year, month=ft.month, day=ft.day)+timedelta(days=first_mon_delta) 

    lt = latest.timestamp
    last_day = lt.weekday()
    last_mon_delta = 0
    if last_day != 0:
        last_mon_delta = last_day 
    last_monday = datetime(year=lt.year, month=lt.month, day=lt.day)-timedelta(days=last_mon_delta)
    # number of weeks of study
    num_weeks, extra_days = divmod((last_monday-first_monday).days, 7)
    print len(active_users),num_weeks, extra_days

    # mat1: look at every week and see how many stores people visit (n_transactions/week)
    # mat2: how many distinct store visits (n_stores/week)
    # mat3: normalize by max store visits that week so you can see the relative ratio
    #       mat2/max_visits_that_week
    n_txns_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    distinct_stores_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    ratio_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    diversity_pwk = np.zeros((len(active_users),num_weeks), dtype=float)

    # create location set tracking map to count distinct locations
    location_map = [ [ set() for j in range(num_weeks) ] for i in range(len(active_users))] 

    for t in TechCashTransaction.objects.filter(location__type=Location.EATERY, timestamp__range=(first_monday, last_monday)):
        # go through each transaction, add a transaction to particular user id and week
        u = t.user
        # calculate the week
        w, d = divmod((t.timestamp - first_monday).days,7)
        i = active_users.index(u.id)
        if t.location is None:
            print "Unknown location txn:",t.amount
        elif t.amount > 0:
            # add location to the weekly set 
            location_map[i][w].add(t.location.id)
            n_txns_pwk[i][w] += 1
          
        # how this index changes over time for different users
        # plot out time series for different people 

    for i, u in enumerate(location_map):
        for j, w in enumerate(u):
            distinct_stores_pwk[i][j] = len(w)

    max_txns_pwk = np.max(n_txns_pwk, axis=0)
            
    # find max store visits, or total store visits that week
    ratio_pwk = n_txns_pwk/max_txns_pwk

    # to avoide divide by 0
    n_txns_pwk_one = np.ones((len(active_users),num_weeks), dtype=float)
    for i, v in enumerate(n_txns_pwk):
        for j, w in enumerate(v):
            if w != 0:
                n_txns_pwk_one[i][j] = w

    diversity_pwk = distinct_stores_pwk/n_txns_pwk_one
    norm_diversity_pwk = distinct_stores_pwk/max_txns_pwk

    # track mobile access
    events_pwk = np.zeros((len(active_users), num_weeks), dtype=int)
    feeds_pwk = np.zeros((len(active_users), num_weeks), dtype=int)

    for e in Event.objects.filter(timestamp__range=(first_monday, last_monday)):
      if e.action in [2,3,7,8]:
        u = e.user
        w, d = divmod((e.timestamp - first_monday).days,7)
        try:
          i = active_users.index(u.id)
          events_pwk[i][w] += 1
        except ValueError:
          pass

    for e in FeedEvent.objects.filter(timestamp__range=(first_monday, last_monday)):
      u = e.user
      w, d = divmod((e.timestamp - first_monday).days,7)
      try:
        i = active_users.index(u.id)
        feeds_pwk[i][w] += 1
      except ValueError:
        pass

    # per week activity
    n_txns_pwk_file = open(PREFIX_DAT+"n_txns_pwk.dat", "w")
    pickle.dump(n_txns_pwk, n_txns_pwk_file)
    distinct_stores_pwk_file = open(PREFIX_DAT+"distinct_stores_pwk.dat", "w")
    pickle.dump(distinct_stores_pwk, distinct_stores_pwk_file)
    ratio_pwk_file = open(PREFIX_DAT+"ratio_pwk.dat", "w")
    pickle.dump(ratio_pwk, ratio_pwk_file)
    diversity_pwk_file = open(PREFIX_DAT+"diversity_pwk.dat", "w")
    pickle.dump(diversity_pwk, diversity_pwk_file)
    feeds_pwk_file = open(PREFIX_DAT+"feeds_pwk.dat", "w")
    pickle.dump(feeds_pwk, feeds_pwk_file)
    events_pwk_file = open(PREFIX_DAT+"events_pwk.dat", "w")
    pickle.dump(events_pwk, events_pwk_file)

    f = plt.figure(figsize=(16,8))
    f.subplots_adjust(hspace=0.5)
    f.subplots_adjust(wspace=0.5)
    ax1 = f.add_subplot(231)
    ax2 = f.add_subplot(232)
    ax3 = f.add_subplot(233)
    ax4 = f.add_subplot(234)
    ax5 = f.add_subplot(235)
    ax6 = f.add_subplot(236)
    
    x = []
    x_nofeeds = []
    x_txns_nofeeds = []
    x_noevt = []
    x_txns = []
    x_txns_noevt = []
    y = []
    for i, v in enumerate(events_pwk):
      for j, e in enumerate(v):
        if n_txns_pwk[i][j] > 0 and e > 0:
          # mobile accessed
          if feeds_pwk[i][j] == 0:
            # no feeds accessed
            x_nofeeds.append(diversity_pwk[i][j])
            x_txns_nofeeds.append(n_txns_pwk[i][j])
          else:
            # feeds accessed
            y.append(e)
            x.append(diversity_pwk[i][j])
            x_txns.append(n_txns_pwk[i][j])
        elif e == 0:
          # no mobile accessed
          x_noevt.append(diversity_pwk[i][j])
          x_txns_noevt.append(n_txns_pwk[i][j])

    D = np.array(x)
    E = np.array(y)
    print "Correlation between events and diversity when feeds accessed\n",np.corrcoef([D, E])
    print "T-Test for diversity of no mobile access vs feeds accessed",stats.ttest_ind(x_noevt, x)
    print "T-Test for transactions of no mobile access vs feeds accessed", stats.ttest_ind(x_txns_noevt, x_txns)
    print "Length of no feeds accessed to no mobile access", len(x), len(x_noevt)

    """
    ax1.plot(D, E, '.')
    ax1.set_title('Mobile Access vs Diversity')
    ax1.set_ylabel('Mobile access frequency')
    ax1.set_xlabel('Diversity')
    """

    ax1.boxplot([x, x_noevt])
    ax1.set_title("Used mobile vs those who didn't")
    ax1.set_ylabel("Diversity")


    ax2.boxplot([x_txns, x_txns_noevt])
    ax2.set_title("Used mobile vs those who didn't")
    ax2.set_ylabel("\# of transactions")

    x = []
    x_noevt = []
    x_txns = []
    x_txns_noevt = []
    y = []
    for i, v in enumerate(feeds_pwk):
      for j, e in enumerate(v):
        if n_txns_pwk[i][j] > 0 and e > 0:
          y.append(e)
          x.append(diversity_pwk[i][j])
          x_txns.append(n_txns_pwk[i][j])
        elif e == 0:
          x_noevt.append(diversity_pwk[i][j])
          x_txns_noevt.append(n_txns_pwk[i][j])

    D = np.array(x)
    E = np.array(y)
    print "Correlation between events and diversity when feeds accessed\n", np.corrcoef([D, E])
    print "T-Test for diversity of just feeds vs no mobile", stats.ttest_ind(x, x_noevt)
    print "T-Test for transactions of just feeds vs no mobile", stats.ttest_ind(x_txns, x_txns_noevt)
    print "Length of no feeds accessed to no mobile access", len(x), len(x_noevt)
    print "Diversity - Mobile vs No Feeds:", len(x), len(x_nofeeds), stats.ttest_ind(x, x_nofeeds)
    print "Transactions - Mobile vs No Feeds:", len(x_txns), len(x_nofeeds), stats.ttest_ind(x_txns, x_txns_nofeeds)

    ax3.boxplot([x, x_nofeeds])
    ax3.set_title("Used feeds vs no feeds")
    ax3.set_ylabel("Diversity")

    ax4.boxplot([x_txns, x_txns_nofeeds])
    ax4.set_title("Used feeds vs no feeds ")
    ax4.set_ylabel("\# of transactions")

    """
    ax4.plot(D, E, '.')
    ax4.set_title('Feed Access vs Diversity')
    ax4.set_ylabel('Feed access frequency')
    ax4.set_xlabel('Diversity')
    """

    ax5.boxplot([x, x_noevt])
    ax5.set_title("Used feeds vs No mobile")
    ax5.set_ylabel("Diversity")

    ax6.boxplot([x_txns, x_txns_noevt])
    ax6.set_title("Used feeds vs No mobile")
    ax6.set_ylabel("\# of transactions")

    f.savefig(PREFIX_IMG+"event_vs_diversity_pwk.%s"%img_type, bbox_inches="tight")
    f.show()

def diversity_mobile_experiments(active_users):
    """
        Identify whether weekly diversity was affected by the mobile access 

        The more different locations they went it is higher, the more they went to a single location, it is lower (num of locations/frequency) 
    """

    # go through each user and find distinct locations they have been to
    # and the total frequency of all the locations

    # create a matrix from earliest to latest, insert 0 if no transactions that week
    #latest = TechCashTransaction.objects.all().order_by("-timestamp")[0]
    #first = TechCashTransaction.objects.all().order_by("timestamp")[0]
    latest = TechCashTransaction.objects.filter(timestamp__range=(EFF_START, EFF_END), location__type=Location.EATERY).order_by("-timestamp")[0]
    first = TechCashTransaction.objects.filter(timestamp__range=(EFF_START, EFF_END), location__type=Location.EATERY).order_by("timestamp")[0]

    ft = first.timestamp
    first_day = ft.weekday()
    first_mon_delta = 0
    if first_day != 0:
        first_mon_delta = 7 - first_day
    first_monday = datetime(year=ft.year, month=ft.month, day=ft.day)+timedelta(days=first_mon_delta) 

    lt = latest.timestamp
    last_day = lt.weekday()
    last_mon_delta = 0
    if last_day != 0:
        last_mon_delta = last_day 
    last_monday = datetime(year=lt.year, month=lt.month, day=lt.day)-timedelta(days=last_mon_delta)
    # number of weeks of study
    num_weeks, extra_days = divmod((last_monday-first_monday).days, 7)
    print "Users, number of weeks, extra days:",len(active_users),num_weeks, extra_days

    # mat1: look at every week and see how many stores people visit (n_transactions/week)
    # mat2: how many distinct store visits (n_stores/week)
    # mat3: normalize by max store visits that week so you can see the relative ratio
    #       mat2/max_visits_that_week
    n_txns_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    distinct_stores_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    ratio_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    diversity_pwk = np.zeros((len(active_users),num_weeks), dtype=float)

    # create location set tracking map to count distinct locations
    location_map = [ [ set() for j in range(num_weeks) ] for i in range(len(active_users))] 

    for t in TechCashTransaction.objects.filter(location__type=Location.EATERY, timestamp__range=(first_monday, last_monday)):
        # go through each transaction, add a transaction to particular user id and week
        u = t.user
        # calculate the week
        w, d = divmod((t.timestamp - first_monday).days,7)
        i = active_users.index(u.id)
        if t.location is None:
            print "Unknown location txn:",t.amount
        elif t.amount > 0:
            # add location to the weekly set 
            location_map[i][w].add(t.location.id)
            n_txns_pwk[i][w] += 1
          
        # how this index changes over time for different users
        # plot out time series for different people 

    for i, u in enumerate(location_map):
        for j, w in enumerate(u):
            distinct_stores_pwk[i][j] = len(w)

    max_txns_pwk = np.max(n_txns_pwk, axis=0)
            
    # find max store visits, or total store visits that week
    ratio_pwk = n_txns_pwk/max_txns_pwk

    # to avoide divide by 0
    n_txns_pwk_one = np.ones((len(active_users),num_weeks), dtype=float)
    for i, v in enumerate(n_txns_pwk):
        for j, w in enumerate(v):
            if w != 0:
                n_txns_pwk_one[i][j] = w

    diversity_pwk = distinct_stores_pwk/n_txns_pwk_one
    norm_diversity_pwk = distinct_stores_pwk/max_txns_pwk

    # friends_date = track after 4/26
    friends_date = datetime(year=ft.year, month=4, day=26)

    # track mobile access
    events_pwk = np.zeros((len(active_users), num_weeks), dtype=int)
    feeds_pwk = np.zeros((len(active_users), num_weeks), dtype=int)

    for e in Event.objects.filter(timestamp__range=(first_monday, last_monday)):
      if e.action in [2,3,7,8]:
        u = e.user
        w, d = divmod((e.timestamp - first_monday).days,7)
        try:
          i = active_users.index(u.id)
          events_pwk[i][w] += 1
        except ValueError:
          pass

    for e in FeedEvent.objects.filter(timestamp__range=(first_monday, last_monday)):
      u = e.user
      w, d = divmod((e.timestamp - first_monday).days,7)
      try:
        i = active_users.index(u.id)
        feeds_pwk[i][w] += 1
      except ValueError:
        pass


    """
      Plot how different
    """
    f = plt.figure(figsize=(16,8))
    f.subplots_adjust(hspace=0.5)
    f.subplots_adjust(wspace=0.5)
    ax1 = f.add_subplot(241)
    ax2 = f.add_subplot(242)
    ax3 = f.add_subplot(243)
    ax4 = f.add_subplot(244)
    ax5 = f.add_subplot(245)
    ax6 = f.add_subplot(246)
    ax7 = f.add_subplot(247)
    ax8 = f.add_subplot(248)


    # capture diversity before and after intervention
    x = [[], []]
    x_noevt = [[], []]
    x_nofeeds = [[], []]

    # count number of transactions before and after interventions
    x_txns = [[], []]
    x_txns_noevt = [[], []]
    x_txns_nofeeds = [[], []]
    y = [[], []]

    w, d = divmod((friends_date - first_monday).days, 7)

    for i, v in enumerate(events_pwk):
      for j, e in enumerate(v):
        # v is the events per week per user
        # e is the number of events for week j for user i
        if j < w:
          # before the interventions
          if n_txns_pwk[i][j] > 0 and e > 0:
            # evevnts accessed from mobile
            if feeds_pwk[i][j] == 0:
              # no feeds
              x_nofeeds[0].append(diversity_pwk[i][j])
              x_txns_nofeeds[0].append(n_txns_pwk[i][j])
            else:
              # there were feeds
              y[0].append(e)
              x[0].append(diversity_pwk[i][j])
              x_txns[0].append(n_txns_pwk[i][j])
          elif e == 0:
            # no events on mobile
            x_noevt[0].append(diversity_pwk[i][j])
            x_txns_noevt[0].append(n_txns_pwk[i][j])
        else:
          # after the interventions
          if n_txns_pwk[i][j] > 0 and e > 0:
            # evevnts accessed from mobile
            if feeds_pwk[i][j] == 0:
              # no feeds
              x_nofeeds[1].append(diversity_pwk[i][j])
              x_txns_nofeeds[1].append(n_txns_pwk[i][j])
            else:
              # there were feeds
              y[1].append(e)
              x[1].append(diversity_pwk[i][j])
              x_txns[1].append(n_txns_pwk[i][j])
          elif e == 0:
            # no events from mobile
            x_noevt[1].append(diversity_pwk[i][j])
            x_txns_noevt[1].append(n_txns_pwk[i][j])


    D = np.array(x[0])
    E = np.array(y[0])
    print "Correlation between diversity and events when feeds are there:",np.corrcoef([D, E])
    print "T-Test of diversity between events and no events:",len(x[0]), len(x_noevt[0]), stats.ttest_ind(x_noevt[0], x[0])
    print "T-Test of num transactions between events and no events:",stats.ttest_ind(x_txns_noevt[0], x_txns[0])
    print "T-Test of diversity between experiment control and friends for all:", len(x[0]), len(x[1]), stats.ttest_ind(x[0]+x_nofeeds[0], x[1]+x_nofeeds[1])
    print "T-Test of diversity between experiement control and friends for no events:",len(x_noevt[0]), len(x_noevt[1]), stats.ttest_ind(x_noevt[0], x_noevt[1])

    ax7.plot(D, E, '.')
    ax7.set_title('Mobile Access vs Diversity')
    ax7.set_ylabel('Mobile access frequency')
    ax7.set_xlabel('Diversity')

    ax1.boxplot([x[0], x_noevt[0]])
    ax1.set_title("Used mobile vs those who didn't")
    ax1.set_ylabel("Diversity")


    ax2.boxplot([x_txns[0], x_txns_noevt[0]])
    ax2.set_title("Used mobile vs those who didn't")
    ax2.set_ylabel("\# of transactions")

    """
      Investigate how feeds affect people's choices
    """
    x = []
    x_noevt = []
    x_txns = []
    x_txns_noevt = []
    y = []
    for i, v in enumerate(feeds_pwk):
      for j, e in enumerate(v):
        # v is the feeds per week
        # e is the number of feeds on week j for user i
        if n_txns_pwk[i][j] > 0 and e > 0:
          # if there are transactions and feeds
          y.append(e)
          x.append(diversity_pwk[i][j])
          x_txns.append(n_txns_pwk[i][j])
        elif e == 0:
          # if there are no feeds accessed
          x_noevt.append(diversity_pwk[i][j])
          x_txns_noevt.append(n_txns_pwk[i][j])

    D = np.array(x)
    E = np.array(y)
    print "Correlation between feeds accessed and diversity:",np.corrcoef([D, E])
    print "T-Test for diversity between feeds accessed and no feeds:",stats.ttest_ind(x, x_noevt)
    print "T-Test for transactions between feeds accessed and no feeds:",stats.ttest_ind(x_txns, x_txns_noevt)
    print "Total events of feeds and no feeds:",len(x), len(x_noevt)

    print "Diversity - Mobile vs No Feeds:", len(x), len(x_nofeeds[0]), stats.ttest_ind(x, x_nofeeds[0])
    print "Transactions - Mobile vs No Feeds:", len(x_txns), len(x_txns_nofeeds[0]), stats.ttest_ind(x_txns, x_txns_nofeeds[0])

    ax3.boxplot([x, x_nofeeds[0]])
    ax3.set_title("Used feeds vs no feeds")
    ax3.set_ylabel("Diversity")

    ax4.boxplot([x_txns, x_txns_nofeeds[0]])
    ax4.set_title("Used feeds vs no feeds ")
    ax4.set_ylabel("\# of transactions")



    ax8.plot(D, E, '.')
    ax8.set_title('Feed Access vs Diversity')
    ax8.set_ylabel('Feed access frequency')
    ax8.set_xlabel('Diversity')

    ax5.boxplot([x, x_noevt])
    ax5.set_title("Used feeds vs No mobile")
    ax5.set_ylabel("Diversity")

    ax6.boxplot([x_txns, x_txns_noevt])
    ax6.set_title("Used feeds vs No mobile")
    ax6.set_ylabel("\# of transactions")

    f.suptitle("Transaction behavior when mobile used and no mobile used")
    f.savefig(PREFIX_IMG+"event_vs_diversity_pwk.%s"%img_type, bbox_inches="tight")
    f.show()

def weekly_activity_plot():

  n_txns_pwk_file = open(PREFIX_DAT+"n_txns_pwk.dat", "r")
  n_txns_pwk = pickle.load(n_txns_pwk_file)
  distinct_stores_pwk_file = open(PREFIX_DAT+"distinct_stores_pwk.dat", "r")
  distinct_stores_pwk = pickle.load(distinct_stores_pwk_file)
  ratio_pwk_file = open(PREFIX_DAT+"ratio_pwk.dat", "r")
  ratio_pwk = pickle.load(ratio_pwk_file)
  diversity_pwk_file = open(PREFIX_DAT+"diversity_pwk.dat", "r")
  diversity_pwk = pickle.load(diversity_pwk_file)
  feeds_pwk_file = open(PREFIX_DAT+"feeds_pwk.dat", "r")
  feeds_pwk = pickle.load(feeds_pwk_file)
  events_pwk_file = open(PREFIX_DAT+"events_pwk.dat", "r")
  events_pwk = pickle.load(events_pwk_file)

  f = plt.figure(figsize=(24,16))
  f.suptitle("Activity of different users by week")
  f.subplots_adjust(wspace=0.7)
  ax1 = f.add_subplot(161)
  ax2 = f.add_subplot(162)
  ax3 = f.add_subplot(163)
  ax4 = f.add_subplot(164)
  ax5 = f.add_subplot(165)
  ax6 = f.add_subplot(166)

  im = ax1.imshow(n_txns_pwk, origin='lower')
  divider = make_axes_locatable(ax1)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax1, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Num of transactions")

  ax1.set_ylabel("User")
  ax1.set_xlabel("Week")

  im = ax2.imshow(distinct_stores_pwk, origin='lower')
  divider = make_axes_locatable(ax2)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax2, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Distinct store visits")

  ax2.set_ylabel("User")
  ax2.set_xlabel("Week")

  im = ax3.imshow(ratio_pwk, origin='lower')
  divider = make_axes_locatable(ax3)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax3, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Normalized by max transactions/week")

  ax3.set_ylabel("User")
  ax3.set_xlabel("Week")

  im = ax4.imshow(diversity_pwk, origin='lower')
  divider = make_axes_locatable(ax4)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax4, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Diversity")

  ax4.set_ylabel("User")
  ax4.set_xlabel("Week")

  im = ax5.imshow(feeds_pwk, origin='lower')
  divider = make_axes_locatable(ax5)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax5, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Num of feeds")

  ax5.set_ylabel("User")
  ax5.set_xlabel("Week")

  im = ax6.imshow(events_pwk, origin='lower')
  divider = make_axes_locatable(ax6)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  #axc, kw = matplotlib.colorbar.make_axes(ax6, shrink=0.8)
  cb = matplotlib.colorbar.Colorbar(cax, im)
  cb.set_label("Num of mobile access")

  ax6.set_ylabel("User")
  ax6.set_xlabel("Week")

  f.savefig(PREFIX_IMG+"weekly_activity.%s"%img_type, bbox_inches="tight")
 
  f = plt.figure(figsize=(12,6))
  f.subplots_adjust(wspace=0.5)
  ax1 = f.add_subplot(121)
  ax2 = f.add_subplot(122)
  
  mean_diversity = np.mean(diversity_pwk, axis=1)
  ax1.hist(mean_diversity, 20)
  ax1.set_xlabel("Diversity")
  ax1.set_ylabel("\# Users")

  f.savefig(PREFIX_IMG+"diversity_mean.%s"%img_type, bbox_inches="tight")


def experiments():
  """
    Shows the distribution of people in each experiment
  """
  active_users = []
  n_user_transactions = []
  exps = []

  # get number of users that have techcash transactions
  q=OTNUser.objects.annotate(transactions=Count('techcashtransaction'))
  for u in q:
    if u.transactions > 0:
      active_users.append(u.id)
      exps.append(u.experiment.id)
      n_user_transactions.append(u.transactions) 

  
  fig = plt.figure()
  fig.subplots_adjust(hspace=0.5)
  ax1 = fig.add_subplot(211)
  ax2 = fig.add_subplot(212)

  print exps
  ax1.hist(exps)
  fig.show()

def initialize():
    # go through each user and find distinct locations they have been to
    # and the total frequency of all the locations

    active_users = []
    n_user_transactions = []

    # get number of users that have techcash transactions
    q=OTNUser.objects.order_by('id').filter(techcashtransaction__timestamp__range=(EFF_START, EFF_END)).annotate(transactions=Count('techcashtransaction'))
    for u in q:
        if u.transactions > 0:
            active_users.append(u.id)
            n_user_transactions.append(u.transactions) 

    f = open(PREFIX_DAT+"active_users.obj", "w")
    pickle.dump(active_users, f)
    f.close()

    # create a matrix from earliest to latest, insert 0 if no transactions that week
    latest = TechCashTransaction.objects.filter(location__type=Location.EATERY, timestamp__range=(EFF_START, EFF_END)).order_by("-timestamp")[0]
    first = TechCashTransaction.objects.filter(location__type=Location.EATERY, timestamp__range=(EFF_START, EFF_END)).order_by("timestamp")[0]

    ft = first.timestamp
    first_day = ft.weekday()
    first_mon_delta = 0
    if first_day != 0:
        first_mon_delta = 7 - first_day
    first_monday = datetime(year=ft.year, month=ft.month, day=ft.day)+timedelta(days=first_mon_delta) 

    lt = latest.timestamp
    last_day = lt.weekday()
    last_mon_delta = 0
    if last_day != 0:
        last_mon_delta = last_day 
    last_monday = datetime(year=lt.year, month=lt.month, day=lt.day)-timedelta(days=last_mon_delta)
    # number of weeks of study
    num_weeks, extra_days = divmod((last_monday-first_monday).days, 7)
    print len(active_users), num_weeks, extra_days

    return active_users, first_monday, last_monday, num_weeks, n_user_transactions

def diversity_index(active_users, first_monday, last_monday, num_weeks):
    """
        Create diversity index per individual per one week, two weeks, month 

        The more different locations they went it is higher, the more they went to a single location, it is lower (num of locations/frequency) 
    """


    # mat1: look at every week and see how many stores people visit (n_transactions/week)
    # mat2: how many distinct store visits (n_stores/week)
    # mat3: normalize by max store visits that week so you can see the relative ratio
    #       mat2/max_visits_that_week
    n_txns_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    distinct_stores_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    ratio_pwk = np.zeros((len(active_users),num_weeks), dtype=float)
    diversity_pwk = np.zeros((len(active_users),num_weeks), dtype=float)

    # create location set tracking map to count distinct locations
    location_map = [ [ set() for j in range(num_weeks) ] for i in range(len(active_users))] 

    for t in TechCashTransaction.objects.filter(timestamp__range=(first_monday, last_monday), location__type=Location.EATERY):
        # go through each transaction, add a transaction to particular user id
        u = t.user
        w, d = divmod((t.timestamp - first_monday).days,7)
        i = active_users.index(u.id)
        if t.location is None:
            print "Unknown location txn:",t.amount
        else:
            # i is the user, w is the week
            location_map[i][w].add(t.location.id)
            n_txns_pwk[i][w] += 1
          
        # how this index changes over time for different users
        # plot out time series for different people 

    for i, u in enumerate(location_map):
        for j, w in enumerate(u):
            distinct_stores_pwk[i][j] = len(w)

    # find max store visits, or total store visits that week
    max_txns_pwk = np.max(n_txns_pwk, axis=0)
            
    # num times one visited versus max visits that week
    ratio_pwk = n_txns_pwk/max_txns_pwk

    # to avoide divide by 0
    n_txns_pwk_one = np.ones((len(active_users),num_weeks), dtype=float)
    for i, v in enumerate(n_txns_pwk):
        for j, w in enumerate(v):
            if w != 0:
                n_txns_pwk_one[i][j] = float(w)

    diversity_pwk = distinct_stores_pwk/n_txns_pwk_one
    norm_diversity_pwk = distinct_stores_pwk/max_txns_pwk

    # generate three plots of each of these matrices
    for i, r in enumerate(diversity_pwk): 
        fig_ind = plt.figure()
        ax1 = fig_ind.add_subplot(111)
        ax1.hist(r,10)  
        ax1.set_xlim([0,1])
        ax1.set_xlabel("Diversity")
        ax1.set_ylabel("\# Weeks")
        fig_ind.savefig(PREFIX_IMG+"diversity%d.%s"%(active_users[i], img_type), bbox_inches="tight")
        plt.close(fig_ind.number)

    fig_diversity = plt.figure(figsize=(12,8))
    ax1 = fig_diversity.add_subplot(111)
    im = ax1.imshow(diversity_pwk, origin='lower')
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cb = matplotlib.colorbar.Colorbar(cax, im)
    cb.set_label("Diversity")
    cax.colorbar = cb
    ax1.set_ylabel("User")
    ax1.set_xlabel("Week")

    fig_diversity.savefig(PREFIX_IMG+"diversity_all_matrix.%s"%img_type, bbox_inches="tight")
    plt.close(fig_diversity.number)
    
    fig = plt.figure(figsize=(10,10))
    fig.subplots_adjust(hspace=0.5)
    ax1 = fig.add_subplot(321)
    ax2 = fig.add_subplot(322)
    ax3 = fig.add_subplot(323)
    ax4 = fig.add_subplot(324)
    ax5 = fig.add_subplot(325)
    ax6 = fig.add_subplot(326)

    #for v in ratio_pwk[:20]:
    #    ax1.plot(range(num_weeks), v)
    ratio_array = np.resize(ratio_pwk, (1, len(active_users)*num_weeks))
    ax1.hist(ratio_array[0], normed=True, cumulative=True)

    #for v in diversity_pwk[:20]:
    #    ax3.plot(range(num_weeks), v, ".")
    diversity_array = np.resize(diversity_pwk, (1, len(active_users)*num_weeks))
    ax3.hist(diversity_array[0], normed=True, cumulative=True)
    ax3.set_ylim([0,1])

    #for v in norm_diversity_pwk[:20]:
    #    ax5.plot(range(num_weeks), v)
    norm_diversity_array = np.resize(norm_diversity_pwk, (1, len(active_users)*num_weeks))
    ax5.hist(norm_diversity_array[0], normed=True, cumulative=True)

    for v in np.fft.fft(ratio_pwk[:20]):
        ax2.plot(range(num_weeks), v)

    for v in np.fft.fft(diversity_pwk[:20]):
        ax4.plot(range(num_weeks), v)

    for v in np.fft.fft(norm_diversity_pwk[:20]):
        ax6.plot(range(num_weeks), v)


    fig.savefig(PREFIX_IMG+"diversity_all_weeks.%s"%img_type, bbox_inches="tight")
    fig.show()

    return ratio_pwk, diversity_pwk, norm_diversity_pwk

def habitual_behavior(active_users, reload=False):
    """
        If one goes to same place within a threshold day window t, 
        one's habitual behavior index goes up

        The ratio of number of habitual day to non habitual is habitual index
    """
    
    print "***** Calculating habitual behaviors *****"

    data_path = PREFIX_DAT+"time_diff.npz"
    time_diff = []

    if not reload and path.exists(data_path):
        data_file = open(data_path, "r")
        data_load = np.load(data_file)
        time_diff = data_load["time_diff"] 

        f = plt.figure(figsize=(8,12))
        ax = f.add_subplot(311)
        ax2 = f.add_subplot(312)
        ax3 = f.add_subplot(313)

        log_time_diff = np.log(np.array(time_diff))

        bin_size = divmod(max(time_diff) - min(time_diff), 24)
        if bin_size[1] > 0:
            n, bins, patches = ax.hist(time_diff, bins=bin_size[0]+1, color='g') #, log=True)
            ax2.hist(log_time_diff, bins=bin_size[0]+1, normed=True, cumulative=True, histtype='step', range=(0,10))
        else:
            n, bins, patches = ax.hist(time_diff, bins=bin_size[0], color='g') #, log=True)
            ax2.hist(log_time_diff, bins=bin_size[0], normed=True, cumulative=True, histtype='step', range=(0,10))
        #x = np.arange(1,8000000, dtype="float")/float(2750)
        #y = (1./x)
        #ax.plot(x, y, 'r--', linewidth=5)

        ax.set_title("Time difference between visits to same location")
        ax.set_xlabel("Hours")
        ax.set_ylabel("Number of transactions")

        ax2.set_xlabel("log(Hours)")
        ax2.set_ylabel("\% of transactions")

        print "Normal test: %f, %E"%stats.normaltest(time_diff)
        print "Skew original: %f"%stats.skew(time_diff)
        print "Normal test: %f, %E"%stats.normaltest(log_time_diff)
        print "Skew log: %f"%stats.skew(log_time_diff)
        mu = np.mean(log_time_diff)
        sigma = np.std(log_time_diff)
        print "Mean:", mu
        print "STD:", sigma 

        if bin_size[1] > 0:
          n, bins, patches = ax3.hist(time_diff, log=True, bins=bin_size[0]) #, range=(0,10))
        else:
          n, bins, patches = ax3.hist(time_diff, log=True, bins=bin_size[0]) #, range=(0,10))

        ax3.set_ybound(lower=1)
        ax3.set_xlabel("Hours")
        ax3.set_ylabel("Number of transactions")

        x = mu + sigma*np.random.randn(10000)
        y = 3735*mlab.normpdf( bins, mu, sigma)
        #l = ax3.plot(bins, y, 'r--', linewidth=2)

        f.savefig(PREFIX_IMG+"habitual_all.%s"%img_type, bbox_inches="tight")

        data_file.close()
    else:
        diversity_mat = np.zeros((len(active_users),5))
        total_locations = Location.objects.filter(type = Location.EATERY).count()
        i = 0  # index for each user
        for u in OTNUser.objects.filter(id__in=active_users):
            location_set = set()
            total_txns = u.techcashtransaction_set.filter(location__type=Location.EATERY).count()
            if total_txns < 1:
                continue 

            if reload or not path.exists(PREFIX_IMG+"habitual%d.%s"%(u.id, img_type)):

                time_diff_per_user = []
                for t1 in u.techcashtransaction_set.filter(location__type=Location.EATERY).order_by('timestamp'):
                    location_set.add(t1.location)
                    for t2 in u.techcashtransaction_set.filter(location__type=Location.EATERY).filter(timestamp__gt=t1.timestamp).order_by("timestamp"): 
                        if t1.location == t2.location:
                            # same location
                            secs = total_seconds(t2.timestamp - t1.timestamp )
                            # time_diff is in hours 
                            time_diff.append( secs/float(3600) )
                            if secs/float(3600) > 168:
                              print u.id, t2.location, t2.timestamp
                            time_diff_per_user.append( secs/float(3600) )
                            break
    
                # per user distribution
                if len(time_diff_per_user) > 1:
                    fig_user = plt.figure()
                    ax_user = fig_user.add_subplot(111)          
                    bin_size = divmod(max(time_diff_per_user) - min(time_diff_per_user), 24)
                    print u.id,bin_size
                    if bin_size[1] > 0:
                        ax_user.hist(time_diff_per_user, bins=bin_size[0]+1, log=True)
                    else:
                        ax_user.hist(time_diff_per_user, bins=bin_size[0], log=True)
                    fig_user.savefig(PREFIX_IMG+"habitual%d.%s"%(u.id, img_type), bbox_inches="tight")
                    plt.close(fig_user.number)
                else:
                    print "%d does not have any common transactions [%d]"%(u.id, len(time_diff_per_user))

            # 1. number of locations one visited
            # 2. number of total transactions 
            # 3. normalized
            # 4. total distinct locations/ total transactions
            diversity_mat[i] = [u.id, len(location_set), total_txns, len(location_set)/float(total_locations), len(location_set)/float(total_txns)] 
            i += 1
        data_path = PREFIX_DAT+"diversity.npz"
        data_file = open(data_path, "wb")
        np.savez(data_file, diversity_mat=diversity_mat)
        data_file.close()

        data_path = PREFIX_DAT+"time_diff.npz"
        data_file = open(data_path, "wb")
        np.savez(data_file, time_diff=time_diff)    
        data_file.close()

def txn_timeline():
    """
        Show time line of the transaction
            - num locations
            - num of transactions
    """
    
    x_data = []
    daily_num_txns = []
    daily_total = []
    dates = TechCashTransaction.objects.filter(location__type=Location.EATERY, timestamp__gt="2010-01-01").dates('timestamp', 'day')
    for d in dates:
        x_data.append(d)
        daily_num_txns.append(TechCashTransaction.objects.filter(location__type=Location.EATERY,timestamp__range=(d, d+timedelta(days=1))).count())
        tot = TechCashTransaction.objects.filter(location__type=Location.EATERY,timestamp__range=(d, d+timedelta(days=1))).aggregate(daily_sum=Sum('amount'))
        daily_total.append(tot['daily_sum'])

    date_array = np.array(x_data)
    #date_array = np.arange(0, len(x_data))
    num_txns_array = np.array(daily_num_txns)
    total_amount_array = np.array(daily_total)

    years = mdates.YearLocator()
    fridays = mdates.WeekdayLocator(byweekday=mdates.FR)
    months   = mdates.MonthLocator()  # every month
    weekFmt = mdates.DateFormatter('%b-%d')
    days = mdates.DayLocator()

    fig = plt.figure(figsize=(15,10))
    fig.subplots_adjust(hspace=0.3)
    ax1 = fig.add_subplot(211)
    ax1.bar(date_array, num_txns_array)
    ax1.set_title("Number of transactions per day")
    # format the ticks
    labels = ax1.get_xticklabels() 
    for label in labels: 
        label.set_rotation(45)  
    ax1.xaxis.set_major_locator(fridays)
    ax1.xaxis.set_major_formatter(weekFmt)
    ax1.xaxis.set_minor_locator(days)
    ax1.autoscale_view()
    # format the coords message box
    #def price(x): return '$%1.2f'%x
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    #ax.fmt_ydata = price
    ax1.grid(True)

    ax2 = fig.add_subplot(212)
    ax2.bar(date_array, daily_total)
    ax2.set_title("\$ amount of transactions per day")
    labels = ax2.get_xticklabels() 
    for label in labels: 
        label.set_rotation(45)  
    # format the ticks
    ax2.xaxis.set_major_locator(fridays)
    ax2.xaxis.set_major_formatter(weekFmt)
    ax2.xaxis.set_minor_locator(days)
    ax2.autoscale_view()

    # format the coords message box
    #def price(x): return '$%1.2f'%x
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    #ax.fmt_ydata = price
    ax2.grid(True)

    #fig.autofmt_xdate()
    fig.savefig(PREFIX_IMG+"txn_timeline.%s"%img_type, bbox_inches="tight")

    fig.show()

def find_influence(active_users, first_monday, last_monday, num_weeks):
  """
    Find the network of influence by mapping out the network that was
    formed over time based on a person's transactions

    Initially, its finding how one person's transactions relate to one's mobile access events
  """

  # influence time threshold
  td = timedelta(hours=1)
  t_viewed = timedelta(days=7)

  # work with only active users
  # look at each users access log
  affected = set() 
  unaffected = set() 

  affected_ev = set() 
  unaffected_ev = set() 

  for t in TechCashTransaction.objects.filter(timestamp__range=(first_monday, last_monday), location__type=Location.EATERY):
    unaffected.add(t.id) 
    unaffected_ev.add(t.id) 

  # total graph
  J = pgv.AGraph(directed=True)
  K = pgv.AGraph(directed=True)

  for u in OTNUser.objects.filter(id__in=active_users):
    # categorize transactions that could have been affected, and those that
    # have not been affected
    # affected are those transactions that happen within 1 hour of looking at the feed

    #G = nx.DiGraph()
    G = pgv.AGraph(directed=True)
    H = pgv.AGraph(directed=True)
    # for each user draw a graph and divide the transactions


    # for feed event
    for e in u.feedevent_set.filter(timestamp__range=(first_monday, last_monday)).order_by("timestamp"):
      inf_time = e.timestamp+td
      for t in u.techcashtransaction_set.filter(location__type=Location.EATERY, timestamp__range=(e.timestamp, inf_time)).order_by("timestamp"): 
        #e.latitude
        #e.longitude
        #e.timestamp
        #e.action 
        G.add_edge(e.id*100000, t.id)
        J.add_edge(e.id*100000, t.id)
        # 3 day window where this transaction can influence future transactions
        view_time = t.timestamp+t_viewed
        for e_after in u.feedevent_set.filter(timestamp__range=(first_monday, last_monday)).filter(timestamp__range=(t.timestamp, view_time)).order_by("timestamp"):
          G.add_edge(t.id, e_after.id*100000)
          J.add_edge(t.id, e_after.id*100000)
        affected.add(t.id)

    unaffected = unaffected - affected

    if len(G.nodes()) > 0:
      # plot graph and save
      f = plt.figure(figsize=(8,8))
      #node_size = [G.degree(v) for v in G]

      for v in G.nodes():
        if int(v) > 100000:
          v.attr['color'] = 'red'
          v.attr['shape'] = 'box'
        else:
          v.attr['color'] = 'blue'
          v.attr['shape'] = 'circle'

      G.draw(PREFIX_IMG+"graph_feed_txn_influence%d.%s"%(u.id, img_type), prog='twopi', args='-Goverlap=scale')
      # prog=['neato'|'dot'|'twopi'|'circo'|'fdp'|'nop', 'tred', 'gvpr', acyclic', 'gvcolor, 'wc', sccmap] 
      # G.draw('test.ps',prog='twopi',args='-Gepsilon=1')
      #nx.draw(A, node_color=node_color) # node_size=node_size, 
      #f.savefig(PREFIX_IMG+"event_transaction_influence%d.%s"%(u.id, img_type), bbox_inches="tight")
      plt.close()

    # for receipts event
    for e in u.event_set.filter(action=Event.RECEIPTS, timestamp__range=(first_monday, last_monday)).order_by("timestamp"):
      inf_time = e.timestamp+td
      for t in u.techcashtransaction_set.filter(location__type=Location.EATERY, timestamp__range=(e.timestamp, inf_time)).order_by("timestamp"): 
        #e.latitude
        #e.longitude
        #e.timestamp
        #e.action 
        H.add_edge(e.id*100000, t.id)
        K.add_edge(e.id*100000, t.id)
        # 3 day window where this transaction can influence future transactions
        view_time = t.timestamp+t_viewed
        for e_after in u.event_set.filter(action=Event.RECEIPTS, timestamp__range=(t.timestamp, view_time)).order_by("timestamp"):
          H.add_edge(t.id, e_after.id*100000)
          K.add_edge(t.id, e_after.id*100000)
        affected_ev.add(t.id)

    unaffected_ev = unaffected_ev - affected_ev

    if len(H.nodes()) > 0:
      # plot graph and save
      f = plt.figure(figsize=(8,8))
      #node_size = [G.degree(v) for v in G]

      for v in H.nodes():
        if int(v) > 100000:
          v.attr['color'] = 'red'
          v.attr['shape'] = 'box'
        else:
          v.attr['color'] = 'blue'
          v.attr['shape'] = 'circle'

      H.draw(PREFIX_IMG+"graph_event_txn_influence%d.%s"%(u.id, img_type), prog='twopi', args='-Goverlap=scale')
      # prog=['neato'|'dot'|'twopi'|'circo'|'fdp'|'nop', 'tred', 'gvpr', acyclic', 'gvcolor, 'wc', sccmap] 
      # G.draw('test.ps',prog='twopi',args='-Gepsilon=1')
      #nx.draw(A, node_color=node_color) # node_size=node_size, 
      #f.savefig(PREFIX_IMG+"event_transaction_influence%d.%s"%(u.id, img_type), bbox_inches="tight")
      plt.close()

  if len(J.nodes()) > 0:
    # plot total graph and save
    f = plt.figure(figsize=(12,12))
    #node_size = [G.degree(v) for v in G]

    for v in J.nodes():
      if int(v) > 100000:
        v.attr['color'] = 'red'
        v.attr['shape'] = 'box'
      else:
        v.attr['color'] = 'blue'
        v.attr['shape'] = 'circle'

    J.draw(PREFIX_IMG+"graph_event_influence_all.%s"%img_type, prog='twopi', args='-Goverlap=scale')
    plt.close()

  if len(K.nodes()) > 0:
    # plot total graph and save
    f = plt.figure(figsize=(12,12))
    #node_size = [G.degree(v) for v in G]

    for v in K.nodes():
      if int(v) > 100000:
        v.attr['color'] = 'red'
        v.attr['shape'] = 'box'
      else:
        v.attr['color'] = 'blue'
        v.attr['shape'] = 'circle'

    K.draw(PREFIX_IMG+"graph_feed_influence_all.%s"%img_type, prog='twopi', args='-Goverlap=scale')
    plt.close()

  # evaluate the affected transactions and unaffected transactions to see how they are different
  data_path = PREFIX_DAT+"affected_unaffected.npz"
  data_file = open(data_path, "wb")
  np.savez(data_file, affected=list(affected), unaffected=list(unaffected))
  data_file.close()

  data_path = PREFIX_DAT+"affected_unaffected_ev.npz"
  data_file = open(data_path, "wb")
  np.savez(data_file, affected=list(affected_ev), unaffected=list(unaffected_ev))
  data_file.close()

def find_influence_network(active_users, first_monday, last_monday, num_weeks):
  """
    Find the network of influence in the social network 

    Formed over time based on a person's transactions and if the friend has seen the feeds
    (that include those transactions - need to filter the params)

    I will draw a large network map that shows how different people's influence network
    looks like.
  """

  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
  friend_map = pickle.load(friend_map_file)

  # influence time threshold
  td = timedelta(hours=1)
  t_viewed = timedelta(days=7)

  # work with only active users
  # look at each users access log
  affected = set() 
  unaffected = set() 

  for t in TechCashTransaction.objects.filter(timestamp__range=(first_monday, last_monday), location__type=Location.EATERY):
    unaffected.add(t.id) 

  H = pgv.AGraph(directed=True)
  L = pgv.AGraph(directed=True)

  for u in OTNUser.objects.filter(id__in=active_users):
    # categorize transactions that could have been affected, and those that
    # have not been affected
    # affected are those transactions that happen within 1 hour of looking at the feed

    #G = nx.DiGraph()
    G = pgv.AGraph(directed=True)
    # for each user draw a graph and divide the transactions

    # for feed event
    for e in u.feedevent_set.filter(timestamp__range=(first_monday, last_monday)).order_by("timestamp"):
      inf_time = e.timestamp+td
      for t in u.techcashtransaction_set.filter(location__type=Location.EATERY, timestamp__range=(e.timestamp, inf_time)).order_by("timestamp"): 
        #e.latitude
        #e.longitude
        #e.timestamp
        #e.action 
        G.add_edge(e.id*100000, t.id)
        H.add_edge(e.id*100000, t.id)
        # 3 day window where this transaction can influence future transactions
        view_time = t.timestamp+t_viewed

        for u_feed in FeedEvent.objects.filter(user__id__in=friend_map[u.id]['first'], timestamp__range=(t.timestamp, view_time)).order_by("timestamp").values_list('user', flat=True).distinct():
          #print "Adding: %d %d"%(u.id, u_feed)
          L.add_edge(u.id, u_feed)

        for e_after in FeedEvent.objects.filter(user__id__in=friend_map[u.id]['first'], timestamp__range=(t.timestamp, view_time)).order_by("timestamp"):
          G.add_edge(t.id, e_after.id*100000)
          H.add_edge(t.id, e_after.id*100000)
        affected.add(t.id)

    unaffected = unaffected - affected

    if len(G.nodes()) > 0:
      # plot graph and save
      f = plt.figure(figsize=(8,8))
      #node_size = [G.degree(v) for v in G]

      for v in G.nodes():
        if int(v) > 100000:
          v.attr['color'] = 'red'
          v.attr['shape'] = 'box'
        else:
          v.attr['color'] = 'blue'
          v.attr['shape'] = 'circle'

      G.draw(PREFIX_IMG+"graph_feed_friend_influence%d.%s"%(u.id, img_type), prog='twopi', args='-Goverlap=scale')
      # prog=['neato'|'dot'|'twopi'|'circo'|'fdp'|'nop', 'tred', 'gvpr', acyclic', 'gvcolor, 'wc', sccmap] 
      # G.draw('test.ps',prog='twopi',args='-Gepsilon=1')
      #nx.draw(A, node_color=node_color) # node_size=node_size, 
      #f.savefig(PREFIX_IMG+"event_transaction_influence%d.%s"%(u.id, img_type), bbox_inches="tight")
      plt.close()


  if len(H.nodes()) > 0:
    # plot graph and save
    f = plt.figure(figsize=(12,12))
    #node_size = [G.degree(v) for v in G]

    for v in H.nodes():
      if int(v) > 100000:
        v.attr['color'] = 'red'
        v.attr['shape'] = 'box'
      else:
        v.attr['color'] = 'blue'
        v.attr['shape'] = 'circle'

    H.draw(PREFIX_IMG+"graph_feed_friend_influence_all.%s"%img_type, prog='twopi', args='-Goverlap=scale')
    plt.close()

  # draw influence social network
  if len(L.nodes()) > 0:
    # plot graph and save
    f = plt.figure()
    #node_size = [G.degree(v) for v in G]

    L.graph_attr["size"] = (8,8)
    L.draw(PREFIX_IMG+"network_feed_friend_influence.%s"%img_type, prog='twopi', args='-Goverlap=scale')
    plt.close()

def find_location_network(active_users, first_monday, last_monday, num_weeks):
  """
    Find the network of influence in the social network based on common locations they go

    Formed over time based on a person's transactions and if the friend has similar transactions 
    (that include those transactions - need to filter the params)

    I will draw a large network map that shows how different people's influence network
    looks like.
  """

  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
  friend_map = pickle.load(friend_map_file)

  # influence time threshold
  td = timedelta(hours=1)
  t_viewed = timedelta(days=3)

  # work with only active users
  # look at each users access log
  affected = set() 
  unaffected = set() 

  for t in TechCashTransaction.objects.filter(timestamp__range=(first_monday, last_monday), location__type=Location.EATERY):
    unaffected.add(t.id) 

  L1 = pgv.AGraph(directed=True)
  L2 = pgv.AGraph(directed=True)
  L3 = pgv.AGraph(directed=True)

  for u in OTNUser.objects.filter(id__in=active_users):
    # categorize transactions that could have been affected, and those that
    # have not been affected
    # affected are those transactions that happen within 1 hour of looking at the feed

    #G = nx.DiGraph()
    G = pgv.AGraph(directed=True)
    # for each user draw a graph and divide the transactions

    # for feed event
    for t in u.techcashtransaction_set.filter(timestamp__range=(first_monday, last_monday), location__type=Location.EATERY).order_by("timestamp"): 
      # 3 day window where this transaction can influence future transactions
      view_time = t.timestamp+t_viewed

      for f_txn in TechCashTransaction.objects.filter(location__id=t.location.id, user__id__in=friend_map[u.id]['first'], timestamp__range=(first_monday, last_monday)).filter(timestamp__range=(t.timestamp, view_time)).order_by("timestamp").values_list('user', flat=True).distinct():
          #print "Adding: %d %d"%(u.id, f_txn)
          L1.add_edge(u.id, f_txn)

      for f_txn in TechCashTransaction.objects.filter(location__id=t.location.id, user__id__in=friend_map[u.id]['second'], timestamp__range=(first_monday, last_monday)).filter(timestamp__range=(t.timestamp, view_time)).order_by("timestamp").values_list('user', flat=True).distinct():
          #print "Adding: %d %d"%(u.id, f_txn)
          L2.add_edge(u.id, f_txn)

      for f_txn in TechCashTransaction.objects.filter(location__id=t.location.id, user__id__in=friend_map[u.id]['third'], timestamp__range=(first_monday, last_monday)).filter(timestamp__range=(t.timestamp, view_time)).order_by("timestamp").values_list('user', flat=True).distinct():
          #print "Adding: %d %d"%(u.id, f_txn)
          L3.add_edge(u.id, f_txn)

  # draw influence social network
  if len(L1.nodes()) > 0:
    # plot graph and save
    f = plt.figure(figsize=(12,12))
    #node_size = [G.degree(v) for v in G]

    L1.draw(PREFIX_IMG+"network_location_friend1_influence.%s"%img_type, prog='twopi', args='-Goverlap=scale')
    plt.close()

  # draw influence social network
  if len(L2.nodes()) > 0:
    # plot graph and save
    f = plt.figure(figsize=(12,12))
    #node_size = [G.degree(v) for v in G]

    L2.draw(PREFIX_IMG+"network_location_friend2_influence.%s"%img_type, prog='twopi', args='-Goverlap=scale')
    plt.close()

  # draw influence social network
  if len(L3.nodes()) > 0:
    # plot graph and save
    f = plt.figure(figsize=(12,12))
    #node_size = [G.degree(v) for v in G]

    L3.draw(PREFIX_IMG+"network_location_friend3_influence.%s"%img_type, prog='twopi', args='-Goverlap=scale')
    plt.close()


def compare_affected_unaffected(fname="affected_unaffected.npz"):
  # compare average price

  data_path = PREFIX_DAT+fname  
  if path.exists(data_path):
    data_file = open(data_path, "r")
    data_load = np.load(data_file)
    affected = data_load["affected"]
    unaffected = data_load["unaffected"]
  else:
    print "First run find_influence()"
    return

  unaffected_txns = TechCashTransaction.objects.filter(id__in=list(unaffected), amount__gt=0)
  unaffected_locs = TechCashTransaction.objects.filter(id__in=list(unaffected), amount__gt=0).values_list('location__id', flat=True).distinct()
  unaffected_names = TechCashTransaction.objects.filter(id__in=list(unaffected), amount__gt=0).order_by("location__name").values_list('location__name', flat=True).distinct()
  unaffected_prices = np.array([t.amount for t in unaffected_txns])

  affected_txns = TechCashTransaction.objects.filter(id__in=list(affected), amount__gt=0)
  affected_locs = TechCashTransaction.objects.filter(id__in=list(affected), amount__gt=0).values_list('location__id', flat=True).distinct()
  affected_names = TechCashTransaction.objects.filter(id__in=list(affected), amount__gt=0).order_by("location__name").values_list('location__name', flat=True).distinct()
  affected_prices = np.array([t.amount for t in affected_txns])

  print len(unaffected_prices), np.mean(unaffected_prices), len(affected_prices), np.mean(affected_prices), stats.ttest_ind(unaffected_prices, affected_prices)  

  # compare diversity
  unaffected_loc = np.array(unaffected_locs)
  affected_loc = np.array(affected_locs)
  print "Number of distinct locations - unaffected: %d, affected: %d"%(len(unaffected_loc), len(affected_loc))
  print len(unaffected_loc), len(affected_loc), stats.ttest_ind(list(unaffected_loc), list(affected_loc))  

  # compare habits
  unaffected_tod = np.array([t.timestamp.hour for t in unaffected_txns])
  affected_tod = np.array([t.timestamp.hour for t in affected_txns])
  print len(unaffected_tod), len(affected_tod), stats.ttest_ind(unaffected_tod, affected_tod)  

  print "Affected\t\tUnaffected"
  i = 0
  for u in unaffected_names:
    if i >= len(affected_names):
      print "\t\t%s"%(unaffected_names[i])
    else:
      print "%s\t%s"%(affected_names[i], unaffected_names[i])
    i += 1

def influence_access_timeline(active_users, first_monday, last_monday):
    """
        Create a timeline of people accessing the mobile application

        It shows the basic events and the feed events
        70 distinct users used the mobile application
        71 distinct users used the feeds

    """

    txns = []
    x_data_txns = []
    events_list = []
    feeds_list = []
    for t in TechCashTransaction.objects.filter(timestamp__range=(first_monday, last_monday), location__type=Location.EATERY, user__in=active_users).order_by("timestamp"):
        x_data_txns.append(t.timestamp)
        txns.append(t)

    x_data_events = []
    for e in Event.objects.filter(timestamp__range=(first_monday, last_monday)).filter(user__in=active_users).order_by("timestamp"):
        # plot all events by color
        x_data_events.append(e.timestamp)
        events_list.append(e.action) 
    
    # find number of unique users that have events
    num_mobile_users = Event.objects.filter(timestamp__range=(first_monday, last_monday)).order_by('user').values('user').distinct().count()
    for u in active_users:
      print "User %d: %d"%(u, Event.objects.filter(timestamp__range=(first_monday, last_monday)).filter(user__id=u).count())
    
    x_data_feeds = []
    for e in FeedEvent.objects.filter(timestamp__range=(first_monday, last_monday)).filter(user__in=active_users).order_by("timestamp"):
        x_data_feeds.append(e.timestamp)
        feeds_list.append(e.action)

    # find number of unique users that looked at feeds 
    num_feed_users = FeedEvent.objects.filter(timestamp__range=(first_monday, last_monday)).order_by('user').values('user').distinct().count()
    for u in active_users:
      print "User %d: %d"%(u, FeedEvent.objects.filter(timestamp__range=(first_monday, last_monday)).filter(user__id=u).count())
 
    print "Num mobile users:", num_mobile_users
    print "Num feed users:", num_feed_users

    years = mdates.YearLocator()
    fridays = mdates.WeekdayLocator(byweekday=mdates.FR)
    months   = mdates.MonthLocator()  # every month
    weekFmt = mdates.DateFormatter('%b-%d')
    days = mdates.DayLocator()

    fig1 = plt.figure(figsize=(15,10))
    fig1.subplots_adjust(hspace=0.3)
    ax1 = fig1.add_subplot(211)
    ax1.plot(x_data_events, events_list, ".")
    ax1.set_title("Access event time line")
    # format the ticks
    labels = ax1.get_xticklabels() 
    for label in labels: 
        label.set_rotation(45)  
    ax1.xaxis.set_major_locator(fridays)
    ax1.xaxis.set_major_formatter(weekFmt)
    ax1.xaxis.set_minor_locator(days)
    ax1.autoscale_view()
    # format the coords message box
    #def price(x): return '$%1.2f'%x
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    #ax.fmt_ydata = price
    ax1.grid(True)

    ax2 = fig1.add_subplot(212)
    ax2.plot(x_data_feeds, feeds_list, ".")
    ax2.set_title("Feed access time line")
    # format the ticks
    labels = ax2.get_xticklabels() 
    for label in labels: 
        label.set_rotation(45)  
    ax2.xaxis.set_major_locator(fridays)
    ax2.xaxis.set_major_formatter(weekFmt)
    ax2.xaxis.set_minor_locator(days)
    ax2.autoscale_view()
    # format the coords message box
    #def price(x): return '$%1.2f'%x
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    #ax.fmt_ydata = price
    ax2.grid(True)

    #fig.autofmt_xdate()
    fig1.savefig(PREFIX_IMG+"influence_timeline.%s"%img_type, bbox_inches="tight")

    fig1.show()

def event_vs_diversity(active_users):
  """
    Track whether there is a correlation between the number of events accessed
    and the diversity index

    There is currently no correlation between the diversity and the number of mobile access
  """
  data_path = PREFIX_DAT+"diversity_pwk.dat"

  if path.exists(data_path):
    data_file = open(data_path, "r")
    div_mat = pickle.load(data_file)

    f = plt.figure()
    f.subplots_adjust(hspace=0.4)

    ax1 = f.add_subplot(211)
    ax2 = f.add_subplot(212)

    x = []
    y = []
    for i, r in enumerate(div_mat):
      n_evt = Event.objects.filter(user__id=active_users[i]).count()
      if n_evt > 0:
        logn_evt = np.log10(n_evt)
        y.append(logn_evt)
        x.append(np.mean(r))

    D = np.array(x)
    E = np.array(y)
    print "Correlation between num of events and diversity index:", np.corrcoef([D,E])

    ax1.plot(x, y, '.')
    ax1.set_title("Mobile Access vs Diversity")
    ax1.set_ylabel("Mobile access frequency")
    ax1.set_xlabel("Diversity")
 
    x = []
    y = []
    for i,r in enumerate(div_mat):
      logn_evt = FeedEvent.objects.filter(user__id=active_users[i]).count()
      y.append(logn_evt)
      x.append(np.mean(r))

    D = np.array(x)
    F = np.array(y)
    print "Correlation between num of feeds and diversity index:", np.corrcoef([D,F])

    ax2.plot(x, y, '.')
    ax2.set_title("Feed Access vs Diversity")
    ax2.set_ylabel("Feed access frequency")
    ax2.set_xlabel("Diversity")

    f.savefig(PREFIX_IMG+"event_vs_diversity.%s"%img_type, bbox_inches="tight")

    f.show()

def find_social_influence(active_users):
    """
        Generate a vector of transaction locations per person and compare it to 
        friends
    """ 
    friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
    friend_map = pickle.load(friend_map_file)

    # work with only active users
    
    activity_vec = {}
    # look at each users access log
    for u in OTNUser.objects.filter(id__in=active_users):

        # calculate each user's activity vector and store it
        activity_vec[u.id] = []

        for z in OTNUser.objects.filter(id__in=friend_map[u.id]['first']):
            #.exclude(facebook_profile__facebook_id=706848):
            # these are the friends
            # see what relation these friends have
            if z.id in activity_vec:
                z_act = activity_vec[z.id]
            else:
                # create z's activity vector
                activity_vec[z.id] = []
            
def find_access_locations():
    """
        See where they opened the application, what they looked and where they transacted in the next hour, day and see if it correlates between what they saw and where they transacted.
    """
    pass

def advertisement_simulations(active_users, first_monday, last_monday):
  """

    Assumptions

    1. Each location is selected to advertise
      a. randomly 
      b. with some priority (based on how often people go to the store?)
      c. those stores people visit less will have higher priority
    2. Their offer gets distributed to 10 people 
      -(each person has a number limit on receiving offer)
      a. random
      b. using history as likelihood
      c. using time of day as likelihood (if this person likely to go somewhere at this time) 
    3. Each person received forwards up to 5 friends
      a. random likelihood to forward (probability to forward is above 50%)
      b. forward to random number of people 1 to 5

    4. See what percentage receives ads, what percentage receives forwarded ads,
      what percentage redeems (if they come to the store within certain time)

    Question:

    How does:
      1. random spam (to whole population) [ra]
      2. random spotty [rs] 
      3. random-social referral [rsr]
      4. targeted by behavior [t] 
      5. targeted-social referral [tr]
      6. social group targeting (separate social groups) [gt]
      7. social group targeting referral [gtr]

    Metrics:
      1. % spams (per person average), in aggregate
      2. % redemptions (per person average), in aggregate
      3. % repeats (being hit by same location again) 
      4. % diversity (number of different locations versus frequency of ads per week)
    
  """
  friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
  friend_map = pickle.load(friend_map_file)

  total_users = len(active_users) 

  # ad params

  # do very basic advertising, randomly select store, 
  locations = Location.objects.filter( type=Location.EATERY )
  loc_ids = [l.id for l in locations]
  total_locs = locations.count()
  # distribution for locations
  mu = total_locs/2
  sigma = total_locs/4 

  # distribution for users
  mu_recv = total_users/2
  sigma_recv = total_users/4

  # randomly send to 5, 10, 15, 20 customers
  num_target = 5
  cost_per_ad = 1
  # Generate advertisements, time step through time every 30 minutes
  timestep = 60

  d = first_monday+timedelta(days=49)
  first_day = first_monday+timedelta(days=49) 
  last_day = first_monday+timedelta(days=56)
  while d < last_day:

    # if between 8 AM and 11:00 PM
    if d.hour < 7 and d.hour > 23:
      d += timedelta(minutes=timestep)
      continue

    # pick a location index num from a distribution
    num_advertisers = np.random.randint(0,10)

    non_overlap_users = list(active_users)

    #rand_ind = np.random.normal(mu, sigma, num_advertisers)
    rand_ind = np.random.uniform(0,total_locs, num_advertisers)
    for loc_ind in rand_ind:
      # for set of randomly selected locations
      i = int(loc_ind)
      if i < 0:
        i = 0
      if i > total_locs - 1:
        i = total_locs - 1
      ad_loc = locations[i] 

      # create offer RANDOM_ALL 50% of users
      o = Offer(location=ad_loc, ad_strategy=Offer.RANDOM_ALL, timestamp=d) 
      o.save()

      # distribution of ads (strategy ra = 50% of population) 
      rand_ind = np.random.normal(mu_recv, sigma_recv, total_users/2)
      rand_ind = np.random.uniform(0,total_users, total_users/2)
      for user_ind in rand_ind:
        j = int(user_ind)
        if j < 0:
          j = 0
        if j > total_users - 1:
          j = total_users - 1

        # distribute
        if DEBUG:
          print "User index: %d"%j
          print "User ID: %d"%active_users[j]
        c = OfferCode(offer=o, user=OTNUser.objects.get(id=active_users[j]), timestamp=d)
        c.save()
    
      # create offer for RANDOM_SPOTTY
      o = Offer(location=ad_loc, ad_strategy=Offer.RANDOM_SPOTTY, timestamp=d) 
      o.save()

      # distribution of ads (strategy rs = fixed number of population) 
      #rand_ind = np.random.normal(mu_recv, sigma_recv/2, num_target)
      rand_ind = np.random.uniform(0,total_users, num_target)
      for user_ind in rand_ind:
        j = int(user_ind)
        if j < 0:
          j = 0
        if j > total_users - 1:
          j = total_users - 1

        # distribute
        if DEBUG:
          print "User index: %d"%j
          print "User ID: %d"%active_users[j]
        c = OfferCode(offer=o, user=OTNUser.objects.get(id=active_users[j]), timestamp=d)
        c.save()
 
      # create offer for RANDOM_NONOVERLAP
      o = Offer(location=ad_loc, ad_strategy=Offer.RANDOM_NONOVERLAP, timestamp=d) 
      o.save()

      # distribution of ads (strategy rn = fixed number of population non-overlapping) 
      num_users = len(non_overlap_users)
      target_users = set() 
      #rand_ind = np.random.normal(mu_recv, sigma_recv/2, num_target)
      rand_ind = np.random.uniform(0,num_users, num_target)
      for user_ind in rand_ind:
        j = int(user_ind)
        if j < 0:
          j = 0
        if j > num_users - 1:
          j = num_users - 1

        target_users.add( non_overlap_users[j] )

      # distribute
      for uid in target_users:
        # remove users so that it does not overlap for next ad
        non_overlap_users.pop(non_overlap_users.index(uid))
        u = OTNUser.objects.get(id=uid)
        c = OfferCode(offer=o, user=u, timestamp=d) 
        c.save()

      # create offer for RANDOM_REFERRAL
      o = Offer(location=ad_loc, ad_strategy=Offer.RANDOM_REFERRAL, timestamp=d) 
      o.save()

      n_friends = 1
      # distribution of ads via social referral
      for uid in target_users:
        u = OTNUser.objects.get(id=uid)
        c = OfferCode(offer=o, user=u, timestamp=d) 
        c.save()

        # choose random number of friends with some probability
        forward = random.randint(0,1)        
        if forward == 1 and len(friend_map[uid]["first"]) > 0:
          fids = random.sample(friend_map[uid]["first"], n_friends)
          for f in fids:
            friend = OTNUser.objects.get(id=f)
            c = OfferCode(offer=o, user=friend, timestamp=d)
            c.save()


      # create offer for TARGET_BEHAVIORAL
      o = Offer(location=ad_loc, ad_strategy=Offer.TARGET_BEHAVIORAL, timestamp=d) 
      o.save()

      # pick some
      target_users = TechCashTransaction.objects.filter(location=ad_loc, timestamp__range=(d-timedelta(days=14),d)).values_list('user', flat=True).distinct()    
      num_users = random.randint(num_target, num_target*2)      
      if len(target_users) > num_users:
        target_users = random.sample(target_users, num_users)
      for uid in target_users:
        u = OTNUser.objects.get(id=uid)
        c = OfferCode(offer=o, user=u, timestamp=d)
        c.save()
      """
      # additional random users
      rand_users = set(active_users)-set(target_users)
      # num_users determines probability of the location
      rand_users = random.sample(list(rand_users), num_users)
      for uid in rand_users:
        u = OTNUser.objects.get(id=uid)
        c = OfferCode(offer=o, user=u, timestamp=d)
        c.save()
      """

      # create offer for TARGET_REFERRAL
      o = Offer(location=ad_loc, ad_strategy=Offer.TARGET_REFERRAL, timestamp=d) 
      o.save()

      # pick some
      n_friends = 1
      for uid in target_users:
        u = OTNUser.objects.get(id=uid)
        c = OfferCode(offer=o, user=u, timestamp=d)
        c.save()

        # choose random number of friends with some probability
        forward = random.randint(0,1)        
        if forward == 1 and len(friend_map[uid]["first"]) > 0:
          fids = random.sample(friend_map[uid]["first"], n_friends)
          for f in fids:
            friend = OTNUser.objects.get(id=f)
            c = OfferCode(offer=o, user=friend, timestamp=d)
            c.save()

    d += timedelta(minutes=timestep)

    # by seeing if any person who received didn't go to store (spam)

    # by seeing if any person who received ad went to another store (timely, but miss)

    # by seeing if any person who received ad went to the location (redemption) 

    # Future: by seeing if any person who received didn't go to store opened app (desired spam)

  friend_map_file.close()

def advertisement_performance(active_users, first_monday, last_monday):
  strategies = [Offer.RANDOM_ALL, Offer.RANDOM_SPOTTY, Offer.RANDOM_NONOVERLAP, Offer.RANDOM_REFERRAL, Offer.TARGET_BEHAVIORAL, Offer.TARGET_REFERRAL]

  first_day = first_monday+timedelta(days=49) 
  last_day = first_monday+timedelta(days=56)

  total_users = len(active_users)

  locations = Location.objects.filter( type=Location.EATERY )
  loc_ids = [l.id for l in locations]
  total_locs = locations.count()


  ###############################################
  # check if any ads can be redeemed from the transactions simulation
  visits_mat = np.zeros((total_locs, total_users))
  for txn in TechCashTransaction.objects.filter(timestamp__range=(first_day, last_day), location__type=Location.EATERY).order_by('timestamp'):

    # create visit matrix
    visits_mat[loc_ids.index(txn.location.id)][active_users.index(txn.user.id)] += 1

    # if there was an offer 90 minutes before the txn from the location of transaction
    # then the offer was redeemed
    offer_time = txn.timestamp - timedelta(minutes=90)
    for c in OfferCode.objects.filter(offer__location=txn.location, user=txn.user, timestamp__range=(offer_time, txn.timestamp)):
      c.redeemed = txn.timestamp
      c.save()

    # if there was an offer 90 minutes before the txn from a different location 
    # than the location of transaction then the offer was missed
    for c in OfferCode.objects.filter(user=txn.user, timestamp__range=(offer_time, txn.timestamp)).exclude(offer__location=txn.location):
      c.missed = txn.timestamp
      c.save()

  # OUTPUT:
  max_algos = max(strategies)+1
  recvd_mat = np.zeros((max_algos, total_locs, total_users))
  redeemed_mat = np.zeros((max_algos, total_locs, total_users))
  missed_mat = np.zeros((max_algos, total_locs, total_users))


  for stgy in strategies: 
  
    # for each strategy
    # ads received per individual
    # ads redeemed per individual
  
    # matrix of locations by users
    # visits
    # ads sent
    # ads redeemed
    # ads missed

    for l in locations:
      for i, uid in enumerate(active_users):
        u = OTNUser.objects.get(id=uid) 
        recvd = OfferCode.objects.filter(user=u, offer__ad_strategy=stgy, offer__location=l).count() 
        redeemed = OfferCode.objects.filter(user=u, offer__ad_strategy=stgy, offer__location=l, redeemed__isnull=False).count() 
        missed = OfferCode.objects.filter(user=u, offer__ad_strategy=stgy, offer__location=l, missed__isnull=False).count() 
        recvd_mat[stgy][loc_ids.index(l.id)][i] = recvd
        redeemed_mat[stgy][loc_ids.index(l.id)][i] = redeemed
        missed_mat[stgy][loc_ids.index(l.id)][i] = missed 

  # TODO: plot heat map for each strategy

  print "Redemption Ratio"
  for i in strategies: 
    print "Strategy %d: %f"%(i, np.sum(redeemed_mat[i])/np.sum(recvd_mat[i])*100)

  print "Miss Ratio"
  for i in strategies: 
    print "Strategy %d: %f"%(i, np.sum(missed_mat[i])/np.sum(recvd_mat[i])*100)

  print "Spam Ratio"
  for i in strategies: 
    print "Strategy %d: %f"%(i, np.sum(missed_mat[i])/np.sum(redeemed_mat[i]))

  print "Total Sent"
  for i in strategies: 
    print "Strategy %d: %f"%(i, np.sum(recvd_mat[i]))

  return visits_mat, recvd_mat, redeemed_mat, missed_mat  
 

def participant_network(active_users):
    """
        Participants and their network of friends

        Color: 
            - people who joined
            - people who participated (shaded by number of times)
            - friends of the participants

    """

    friend_map_file = open(PREFIX_DAT+"friend_map.obj", "r")
    friend_map = pickle.load(friend_map_file)


    fig1 = plt.figure(figsize=(12,10))
    ax1 = fig1.add_subplot(111)


    G = nx.Graph()
    order_map = {}
    first_day = {}
    for u in OTNUser.objects.filter(id__in=active_users): #all().exclude(facebook_profile__facebook_id=706848):

        # get u's friends
        for z in OTNUser.objects.filter(id__in=friend_map[u.id]['first']):
            #.exclude(facebook_profile__facebook_id=706848):
            G.add_edge(z.id, u.id)

    pos = nx.graphviz_layout(G)
    node_colors = []
    node_labels = {}
    for c in G.nodes():
        node_colors.append(nx.degree(G, c))
        node_labels[c] = active_users.index(c)
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.Reds_r)
    labels = nx.draw_networkx_labels(G, pos, labels=node_labels)
    edges = nx.draw_networkx_edges(G, pos)
    #labels = nx.draw_networkx_labels(G, pos, labels=order_map, font_size=10)
    plt.sci(nodes)
    c = plt.colorbar()
    c.set_label("Degrees")

    ax1.axis('tight')
    ax1.set_title("Participant Social Network")
    ax1.set_xticklabels([], visible=False)
    ax1.set_yticklabels([], visible=False)
    #ax1.set_xlabel("Node label = number of visits")

    fig1.savefig(PREFIX_IMG+"participantnet.%s"%img_type, bbox_inches="tight")

    fig3 = plt.figure(figsize=(10,10))
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

def bestbuy_db_populate():

  import csv

  f = open("/Users/kwan/workspace/BestBuy/m_detail.dat", "r")
  txn_reader = csv.reader(f, delimiter='\t')

  # skip first line
  row = txn_reader.next()
  for row in txn_reader:
    print row
    bb = BestBuy(user=row[0], store=row[1], date=datetime.strptime(row[2], "%m/%d/%Y"))   
    bb.save()
  f.close()
    
  f = open("/Users/kwan/workspace/BestBuy/m_header.dat", "r")
  zip_reader = csv.reader(f, delimiter='\t')
  row = zip_reader.next()
  for row in zip_reader:
    bb = BBUserZip(user=row[0], zipcode=row[2])
    bb.save()

  f.close()

def bestbuy_transaction_timeline():

  x_data = []
  daily_num_txns = []
  dates = BestBuy.objects.filter(store=True).order_by("date").dates('date', 'day')
  for d in dates:
      x_data.append(d)
      daily_num_txns.append(BestBuy.objects.filter(store=True,date=d).count())

  date_array = np.array(x_data)
  #date_array = np.arange(0, len(x_data))
  num_txns_array = np.array(daily_num_txns)

  years = mdates.YearLocator()
  fridays = mdates.WeekdayLocator(byweekday=mdates.FR)
  months   = mdates.MonthLocator()  # every month
  weekFmt = mdates.DateFormatter('%b-%d')
  days = mdates.DayLocator()

  fig = plt.figure(figsize=(15,10))
  fig.subplots_adjust(hspace=0.3)
  ax1 = fig.add_subplot(211)
  ax1.bar(date_array, num_txns_array)
  ax1.set_title("Number of transactions per day")
  # format the ticks
  labels = ax1.get_xticklabels() 
  for label in labels: 
      label.set_rotation(45)  
  ax1.xaxis.set_major_locator(fridays)
  ax1.xaxis.set_major_formatter(weekFmt)
  ax1.xaxis.set_minor_locator(days)
  ax1.autoscale_view()
  # format the coords message box
  #def price(x): return '$%1.2f'%x
  #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  #ax.fmt_ydata = price
  ax1.grid(True)

  fig.savefig(PREFIX_IMG+"bestbuy_timeline.%s"%img_type, bbox_inches="tight")
  plt.show()

if __name__ == "__main__":

  active_users, first_monday, last_monday, num_weeks, n_user_transactions = initialize()

  #friend_network(active_users)
  #random_friend_network(active_users)
  #modified_friend_network(active_users)
  #friend_map_to_matrix()

  #a,b,c = diversity_index(active_users, first_monday, last_monday, num_weeks)
  #participant_network(active_users)

  #location_time_map(active_users)
  #location_time_map_plot()
  #txn_timeline() 
  """
  meal_time_all(active_users)
  meal_time_plot()
  meal_time(active_users,6,10)
  meal_time_plot(6,10)
  meal_time(active_users, 11,15)
  meal_time_plot(11,15)
  meal_time(active_users, 17,23)
  meal_time_plot(17,23)
  person_time_map(active_users)
  person_time_map_plot()
  #influence_access_timeline(active_users, first_monday, last_monday)
  """

  #habitual_behavior(active_users)
  #habitual_behavior(active_users, True)
  #diversity_plot()
  #location_stats()
  #person_day_map(active_users)
  #person_day_map_plot(active_users)

  #bestbuy_db_populate()
  #bestbuy_transaction_timeline()
  #results1 = similarity_for_friends(active_users, first_monday, last_monday, socialnet="original")
  #results2 = similarity_for_friends(active_users, first_monday, last_monday, socialnet="random")
  #results3 = similarity_for_friends(active_users, first_monday, last_monday, socialnet="modified")
  #for i in range(0,8):
  #print "Orig to Random %s"%i, ttest_ind(results1[i], results2[i])
  #print "Orig to Modified %s"%i, ttest_ind(results1[i], results3[i])
  #results4 = similarity_second_degree(active_users)

  #results1 = similarity_for_friends(active_users, first_monday, last_monday, socialnet="original", degree="second")
  #results2 = similarity_for_friends(active_users, first_monday, last_monday, socialnet="random", degree="second")
  #results3 = similarity_for_friends(active_users, first_monday, last_monday, socialnet="modified", degree="second")
  #for i in range(0,8):
   #print "Orig to Random %s"%i, ttest_ind(results1[i], results2[i])
   #print "Orig to Modified %s"%i, ttest_ind(results1[i], results3[i])

  #for i, r in enumerate(results1):
  #  print stats.ttest_ind(r, results2[i])
  
	#event_vs_diversity(active_users)
	#diversity_mobile_influences(active_users)
  #experiments()
	#diversity_mobile_experiments(active_users)
  #weekly_activity_plot()
  #find_influence(active_users, first_monday, last_monday, num_weeks)
  #compare_affected_unaffected("affected_unaffected.npz")
  #compare_affected_unaffected("affected_unaffected_ev.npz")

  #find_influence_network(active_users, first_monday, last_monday, num_weeks)
  #find_location_network(active_users, first_monday, last_monday, num_weeks)
  #advertisement_simulations(active_users, first_monday, last_monday)
  #v_mat, s_mat, r_mat, m_mat = advertisement_performance(active_users, first_monday, last_monday)



"""""

Redemption Ratio
Strategy 0: 0.042876
Strategy 1: 0.026385
Strategy 2: 0.000000
Strategy 6: 0.000000
Miss Ratio
Strategy 0: 1.998681
Strategy 1: 1.794195
Strategy 2: 1.904244
Strategy 6: 2.112135
Spam Ratio
Strategy 0: 2.145215
Strategy 1: 1.470588
Strategy 2: 0.000000
Strategy 6: 0.000000

Rank sum

Orig to Random 0 (0.79187102604357751, 0.42843588277452083)
Orig to Modified 0 (0.17977030805190433, 0.85733289456643724)
Orig to Random 1 (4.161833544472068, 3.1570244823019751e-05)
Orig to Modified 1 (0.92388284897560957, 0.35554731365195857)
Orig to Random 2 (2.7925983272878567, 0.0052286573789389213)
Orig to Modified 2 (1.6998534191743357, 0.089158500535348004)
Orig to Random 3 (3.333877256482201, 0.00085644442401774695)
Orig to Modified 3 (2.7147592089357198, 0.0066323974253712469)
Orig to Random 4 (0.94423102092791134, 0.34505160634590637)
Orig to Modified 4 (0.6166804238236212, 0.53744553596125411)
Orig to Random 5 (2.1631109800025827, 0.030532644797220333)
Orig to Modified 5 (0.68494762941295195, 0.49337696891159921)
Orig to Random 6 (2.8928351660275502, 0.0038178160018526516)
Orig to Modified 6 (2.7011057678178534, 0.0069109357110157454)
Orig to Random 7 (3.1494414732011653, 0.0016358287092970683)
Orig to Modified 7 (1.6770976839778922, 0.093523381627907368)


T-test

Orig to Random 0 (0.82959025237282369, 0.40816292372097207)
Orig to Modified 0 (0.18745293187249604, 0.8515977813997333)
Orig to Random 1 (3.018060183388418, 0.0030162758325488841)
Orig to Modified 1 (0.66915458072460643, 0.50458350422836173)
Orig to Random 2 (2.4683763830466905, 0.014759982386638696)
Orig to Modified 2 (1.6106084552528754, 0.10969055734912728)
Orig to Random 3 (2.6978751607847622, 0.0078241657726809844)
Orig to Modified 3 (1.9607348298725433, 0.052048078071260051)
Orig to Random 4 (0.30520561021780512, 0.76065647248745794)
Orig to Modified 4 (0.27512333733483985, 0.78365826960585894)
Orig to Random 5 (1.3125454780503119, 0.19145364601720122)
Orig to Modified 5 (0.50156998736851388, 0.61681838519013088)
Orig to Random 6 (2.2949258237167531, 0.023202989180249694)
Orig to Modified 6 (2.1639101751660879, 0.032299260959037811)
Orig to Random 7 (2.7676503973957072, 0.0063991386915098801)
Orig to Modified 7 (1.4603737227861244, 0.14659994641219215)


Including 2nd degree social network

Orig to Random 0 (0.82959025237282369, 0.40816292372097207)
Orig to Modified 0 (0.18745293187249604, 0.8515977813997333)
Orig to Random 1 (3.018060183388418, 0.0030162758325488841)
Orig to Modified 1 (0.66915458072460643, 0.50458350422836173)
Orig to Random 2 (2.4683763830466905, 0.014759982386638696)
Orig to Modified 2 (1.6106084552528754, 0.10969055734912728)
Orig to Random 3 (2.6978751607847622, 0.0078241657726809844)
Orig to Modified 3 (1.9607348298725433, 0.052048078071260051)
Orig to Random 4 (0.30520561021780512, 0.76065647248745794)
Orig to Modified 4 (0.27512333733483985, 0.78365826960585894)
Orig to Random 5 (1.3125454780503119, 0.19145364601720122)
Orig to Modified 5 (0.50156998736851388, 0.61681838519013088)
Orig to Random 6 (2.2949258237167531, 0.023202989180249694)
Orig to Modified 6 (2.1639101751660879, 0.032299260959037811)
Orig to Random 7 (2.7676503973957072, 0.0063991386915098801)
Orig to Modified 7 (1.4603737227861244, 0.14659994641219215)
Orig to Random 0 (0.1288656035748687, 0.89763547670395938)
Orig to Modified 0 (-0.78798475154647551, 0.43194908973485491)
Orig to Random 1 (-0.63939406497446527, 0.52353542214278026)
Orig to Modified 1 (-2.26252383546344, 0.025101062088914255)
Orig to Random 2 (1.1454186628244323, 0.25384789716814787)
Orig to Modified 2 (0.188117353329155, 0.85103890866393095)
Orig to Random 3 (0.87625460211931805, 0.38228347631660464)
Orig to Modified 3 (0.40887382200856554, 0.68321543058353273)
Orig to Random 4 (2.4110747677692776, 0.017106888107912634)
Orig to Modified 4 (1.4739217005895648, 0.14259823262404639)
Orig to Random 5 (3.3735956955494952, 0.00094283609311610571)
Orig to Modified 5 (1.8332434553945443, 0.06874874855360634)
Orig to Random 6 (0.19549456019297773, 0.84526861374200202)
Orig to Modified 6 (2.3182825907610103, 0.021785042596930919)
Orig to Random 7 (2.1339813578135729, 0.034459404638273267)
Orig to Modified 7 (2.7298259969045149, 0.0070954270150565477)

Another try: worse values
#
Orig to Random 0 (-0.6767412433387866, 0.49967884317163147)
Orig to Modified 0 (-0.29488299625385117, 0.76855366006702963)
Orig to Random 1 (-1.2572204584980282, 0.21075229638933968)
Orig to Modified 1 (-0.12765108361818911, 0.89862235247890232)
Orig to Random 2 (1.1463981893923503, 0.25357219635154826)
Orig to Modified 2 (1.7476588394412591, 0.082884270487758815)
Orig to Random 3 (1.5543629571629847, 0.12233958556535152)
Orig to Modified 3 (2.0283953271298074, 0.044562707887792423)
Orig to Random 4 (-0.29535075356820401, 0.76816042329437195)
Orig to Modified 4 (0.35669625664805543, 0.72189750985525647)
Orig to Random 5 (-1.5484726806484417, 0.12375014308059941)
Orig to Modified 5 (-0.37309908350024845, 0.70968236466768919)
Orig to Random 6 (2.5692903055616112, 0.011229475850987795)
Orig to Modified 6 (2.291058523174152, 0.023569132659303015)
Orig to Random 7 (1.0630712372646143, 0.2895669383264286)
Orig to Modified 7 (2.4420194011307541, 0.01594958152001354)
Orig to Random 0 (-0.85162477501298162, 0.39576211397856353)
Orig to Modified 0 (0.8390616215114548, 0.40276993178313569)
Orig to Random 1 (-4.501939853903524, 1.332311298223888e-05)
Orig to Modified 1 (-2.8428085992253762, 0.0050953209616394811)
Orig to Random 2 (1.7551044088997103, 0.081256164586152146)
Orig to Modified 2 (0.60280667099751917, 0.54754759606140735)
Orig to Random 3 (1.3849446666802665, 0.16809874320485688)
Orig to Modified 3 (0.88358833939001025, 0.37833245082802924)
Orig to Random 4 (0.31383281381919736, 0.75407830537466569)
Orig to Modified 4 (0.33269502495000125, 0.73982901365302556)
Orig to Random 5 (0.10819642551438838, 0.91398257207410816)
Orig to Modified 5 (0.47557308115874125, 0.63507039353441863)
Orig to Random 6 (-0.073962766053938631, 0.94113725796349823)
Orig to Modified 6 (2.3440751495882517, 0.020385959496593151)
Orig to Random 7 (0.1744203482532298, 0.86176722367779468)
Orig to Modified 7 (2.0007674774284188, 0.047221766914737104)

"""


