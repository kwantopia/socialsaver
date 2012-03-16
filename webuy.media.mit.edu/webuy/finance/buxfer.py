import urllib2
import sys
import re
import base64
import json

# XXX WARNING: only a sample; please do NOT hard-code your username 
# or passwords in this manner in your API clients


class BuxferInterface:
    
    def __init__(self):
        
        self.base = "https://www.buxfer.com/api"
    
    def buxfer_login(self, username, password):
        """
          .. function:: buxfer_login()
          
             Logs into the buxfer account and establishes a token for API access
        """
        url = self.base + "/login.json?userid=" + username + "&password=" + password
    
        req = urllib2.Request(url=url)
        try:
            response = self.checkError(urllib2.urlopen(req))
            self.token = response['token']
            return True
        except urllib2.HTTPError:
            self.token = None
            return False
            
    def checkError(self, response):
        result = json.load(response)
        response = result['response']
        if response['status'] != "OK":
            print "An error occured: %s" % response['status'].replace('ERROR: ', '')
            sys.exit(1)
    
        return response
    
    def get_accounts(self):
        url = self.base + "/accounts.json?token=" + self.token
        req = urllib2.Request(url=url)
        response = self.checkError(urllib2.urlopen(req))
        return response['accounts']
    
    def get_transactions(self, account_id, page=1, filter=None):
        url = self.base + "/transactions.json?token=%s&accountId=%s&page=%d" % (self.token, account_id, page)
        req = urllib2.Request(url=url)
        response = self.checkError(urllib2.urlopen(req))
        total = response['numTransactions']
        if filter:
            filtered_txns = []
            for t in response['transactions']:
                if t['type'] == filter:
                    filtered_txns.append(t) 

            return filtered_txns, len(filtered_txns), total
        else:
            for t in response['transactions']:
                self.print_transaction(t)
                
            return response["transactions"], len(response["transactions"]), total

    def get_alltransactions(self, account_id):
        """
            Get all transactions
        """
        final = 1
        p = 1   # page number
        while final != 0: 
            txns, final, total = self.get_transactions( account_id, page=p)
            # TODO: iterate through txns and insert into model
            p += 1
            
    def print_account(self, account):
        print "%12s %12s %8s %10.2f %12s" % (account['id'], account['name'], account['bank'], account['balance'], account['lastSynced'])
    
    def print_transaction(self, txn):
        print txn
        print "%12s %20s %5.2f %s %20s on %s" % ( txn['id'], txn['description'].encode('ascii', 'ignore'), txn['amount'], txn['tags'].encode('ascii', 'ignore'), txn['extraInfo'], txn['date'] ) 
        
    def print_transactions(self, account_id, page=1, filter=None):
        url = self.base + "/transactions.json?token=%s&accountId=%s&page=%d" % (self.token, account_id, page)
        req = urllib2.Request(url=url)
        response = self.checkError(urllib2.urlopen(req))
        print "Total transactions:", response['numTransactions']
        if filter:
            for t in response['transactions']:
                if t['type'] == filter:
                    self.print_transaction(t)
        else:
            for t in response['transactions']:
                self.print_transaction(t)

        return len(response["transactions"])

if __name__ == '__main__':
    b = BuxferInterface()
    success = b.buxfer_login(sys.argv[1], sys.argv[2])

    if success:
        accts = b.get_accounts()
        for a in accts:
            b.print_account( a )
            #b.get_transactions(a['id'])
            b.get_alltransactions(a['id'])
    else:
        print "Invalid login"
