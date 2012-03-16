
from models import WesabeAccount, WesabeTransaction, Detail, WesabeLocation, SpendingCategory, PostalCode, Memo

class AccountParser:
    
    def __init__(self, user):
        """
            :param user: User object
        """
        self.accounts = []
        self.account = {}
        self.guid_found = False
        self.account_found = False
        self.currentbalance = False
        self.name = False
        self.user = user
    
    def start_element(self, name, attrs):
        if name == 'guid':
            # save the guid of the account
            self.guid_found = True
        if name == 'name':
            self.name = True
        if name == 'account':
            self.account_found = True
        if name == 'current-balance':
            self.currentbalance = True
        #print 'Start element:', name
        
    def end_element(self, name):
        #print 'End element:', name
        if name == 'guid':
            self.guid_found = False
        if name == 'name':
            self.name = False
        if name == 'account':
            self.account_found = False
            # save account if it doesn't exist
            if not WesabeAccount.objects.filter(guid=self.account['guid']).exists():
                acct = WesabeAccount(user=self.user, guid=self.account['guid'], name=self.account['name'], balance=self.account['current_balance'])
                acct.save()

        if name == 'current-balance':
            self.currentbalance = False

    def char_data(self, data):
        if self.guid_found:
            self.accounts.append(data)
            self.account['guid'] = data
            # to do, insert into the database
        if self.name:
            self.account['name'] = data
        if self.currentbalance:
            self.account['current_balance'] = data
        if self.account_found:
            pass
        
        #print 'Character data:', repr(data)
        
class TransactionParser:
    
    def __init__(self, account):
        """
            :param user: User object
        """
        self.transactions = []
        self.txn = {}
        self.txaction = False
        self.merchant = False
        self.name = False
        self.locid = False
        self.newest_date = ""

        self.guid = False
        self.amount = False
        self.displayname = False
        self.originaldate = False
        self.newest_txaction = False

        # number of transactions
        self.count = 0

        self.account = account 
 
    def estimate_location(self):
        """
            Estimates the location based on location database
        """
        if 'location_name' in self.txn:
            # can have multiple names
            cambridge = PostalCode.objects.get(code="02139")
            loc, created = WesabeLocation.objects.get_or_create(name=self.txn['location_name'], wesabe_id=self.txn['location_id'], postal_code=cambridge)
        else:
            # just get default UNKNOWN location for now
            loc = WesabeLocation.objects.get(id=1)

        return loc

    def start_element(self, name, attrs):
        if name == 'txaction':
            self.txaction = True
            self.txn = {}
        elif name == 'guid':
            self.guid = True
        elif name == 'merchant':
            self.merchant = True
        elif name == 'name':
            self.name = True
        elif name == 'id':
            self.locid = True
        elif name == 'amount':
            self.amount = True
        elif name == 'display-name':
            self.displayname = True
        elif name == 'original-date':
            self.originaldate = True
        elif name == 'newest-txaction':
            self.newest_txaction = True
        #print 'Start element:', name
        
    def end_element(self, name):
        if name == 'txaction':
            self.txaction = False
            # save transaction if it doesn't exist
            if not WesabeTransaction.objects.filter(account=self.account, guid=self.txn['guid']).exists():
                location = self.estimate_location()
                m = Memo(txt=self.txn['display_name'], location=location)
                m.save()
                wtxn = WesabeTransaction(account=self.account,
                                  guid=self.txn['guid'],
                                  amount=self.txn['amount'],
                                  date=self.txn['original_date'],
                                  memo=m)
                wtxn.save()
                self.count += 1
                #print "Wesabe transaction saved: %s"%wtxn.guid

                none_cat = SpendingCategory.objects.get(name='None')
                details, created = Detail.objects.get_or_create(txn=wtxn, category=none_cat)
                details.save()
                #print "Wesabe detail saved: %d"%details.id
            else:
                #print "TRANSACTION already exists %s"%self.txn['guid']
                pass
                
        elif name == 'guid':
            self.guid = False
        elif name == 'merchant':
            self.merchant = False
        elif name == 'name':
            self.name = False
        elif name == 'id':
            self.locid = False
        elif name == 'amount':
            self.amount = False
        elif name == 'display-name':
            self.displayname = False
        elif name == 'original-date':
            self.originaldate = False
        elif name == 'newest-txaction':
            self.newest_txaction = False
        #print 'End element:', name

    def char_data(self, data):
        if self.guid:
            self.txn['guid'] = data
        if self.merchant and self.name:
            self.txn['location_name'] = data
        if self.merchant and self.locid:
            self.txn['location_id'] = data
        if self.amount: 
            self.txn['amount'] = data
        if self.displayname:
            self.txn['display_name'] = data
        if self.originaldate:
            self.txn['original_date'] = data
        if self.newest_txaction:
            self.txn['newest_txaction'] = data
            self.newest_date = data
            #print "newest-txaction:%s"%repr(data)
            
        #print 'Character data:', repr(data)
              

                
