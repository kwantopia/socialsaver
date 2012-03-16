from bestbuy.models import *
from datetime import datetime

ben = Party.objects.get(email="ben.viralington@gmail.com")

ben_txn1 = Transaction(bb_transaction_id='189',
                party=ben,
                source=Transaction.STORE,
                key='1',
                register=1,
                number=1,
                timestamp=datetime.now())
ben_txn1.save()

p = Product.objects.get_by_sku(9757802)
time.sleep(0.5)
line1 = TransactionLineItem(line_number=2, line_type='SL',
                            sale_price=99.99,
                            product=p,
                            transaction=ben_txn1)
line1.save()
p = Product.objects.get_by_sku(9812863)
time.sleep(0.5)
line1 = TransactionLineItem(line_number=3, line_type='SL',
                            sale_price=19.99,
                            product=p,
                            transaction=ben_txn1)
line1.save()


