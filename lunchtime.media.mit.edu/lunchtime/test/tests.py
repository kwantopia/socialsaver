from django.test.client import Client
c = Client()

user_email='kool@mit.edu'
pin = '5533'
# user_email='yod@mit.edu'
# pin = '123456'

command = '/mobile/login/'
print 'CALL:',command
response = c.post(command, {'email': user_email, 
                                    'pin':pin,
                                    'lat':'-42.7823742',
                                    'lon':'74.234141'})
print response

command = '/mobile/receipts/0/'
print 'CALL:',command
response = c.post(command, {'h':'e'})
print response

command = '/mobile/feeds/0/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response


command = '/mobile/reviews/0/2/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/receipts/month/'
print 'CALL:',command
response = c.post(command, {'hello':'kwan'})
print response


"""
command = '/mobile/friend/trace/3/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/receipts/0/'
print 'CALL:',command
response = c.post(command, {'h':'e'})
print response

command = '/mobile/receipts/5/'
print 'CALL:',command
response = c.post(command, {'h':'e'})
print response

command = '/mobile/location/trace/21/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/location/trace/2/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/receipts/month/'
print 'CALL:',command
response = c.post(command, {'hello':'kwan'})
print response

command = '/mobile/call/3/'
print 'CALL:',command
response = c.post(command, {'type':'call',
                                    'lat':'-42.7823742',
                                    'lon':'74.234141'})
print response

#command = '/mobile/call/4/'
#print 'CALL:',command
#response = c.post(command, {'type':'sms',
#                                    'lat':'-42.7823742',
#                                    'lon':'74.234141'})
#print response
#
#command = '/mobile/call/2/'
#print 'CALL:',command
#response = c.post(command, {'type':'email',
#                                    'lat':'-42.7823742',
#                                    'lon':'74.234141'})
#print response

command = '/mobile/call/log/'
print 'CALL:',command
response = c.post(command, {'otn_user':'3','duration':'1',
                                        'lat':'-42.7823742', 
                                        'lon':'74.234141'})
print response

command = '/mobile/call/3/'
print 'CALL:',command
response = c.post(command, {'type':'sms'})
print response

command = '/mobile/call/3/'
print 'CALL:',command
response = c.post(command, {'type':'call'})
print response

command = '/mobile/register/'
print 'CALL:',command
response = c.post(command, {'udid':'23415141231fdfadf'})
print response

command = '/mobile/surveys/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/register/'
print 'CALL:',command
if user_email == 'kool@mit.edu':
    response = c.post(command, {'udid':'bd868ce1ba22bb1ed1015bcebe6b63c18568e1f6ca4e0c0dc5f0f1e8ee99443d'})
elif user_email == 'yod@mit.edu':
    response = c.post(command, {'udid':'fc8041eff072292345d1985a510adfc61f6090e372e5223c6ee456f042b74573'})
print response

command = '/mobile/feeds/0/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/feeds/3/'
print 'CALL:',command
response = c.post(command, {'location':'feed'})
print response

# Lunch notification test
# command = '/mobile/notify/lunch/'
#response = c.post(command, {'password':'15389099'})
#print response

#command = '/mobile/featured/'
#print 'CALL:',command
#response = c.post(command, {'feature_id':'1', 'lat':'42.342342', 'lon':'-72.23424'})
#print response

command = '/mobile/reviews/2/1/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/reviews/0/1/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/reviews/0/2/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

command = '/mobile/location/trace/4/'
print 'CALL:',command
response = c.post(command, {'e':'e'})
print response

# need to update my receipt
command = '/mobile/update/txn/'
print 'CALL:', command
response = c.post(command, {'txn_id': 26, 'rating':3, 'accompanied':'1'})
print response

# need to get my own receipt
command = '/mobile/receipt/26/'
print 'CALL:', command
response = c.post(command, {'e':'e'})
print response
"""
