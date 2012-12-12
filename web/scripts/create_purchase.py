# coding: utf-8

import random
import string

from knotis.apps.auth.models import KnotisUser
from knotis.apps.business.models import Business
from knotis.apps.offer.models import Offer
from knotis.apps.transaction.models import Transaction, TransactionTypes
from knotis.apps.paypal.views import generate_ipn_hash

def create_purchase(
        business_owner='maps@4thavemaps.com',
        offer_number = 0,
        purchase_user = 'jimlay@gmail.com',
        qty = 1,
        value = 10):
    bus_user = KnotisUser.objects.get(username = business_owner)

    bus = Business.objects.get(user=bus_user)

    bus_offers = Offer.objects.filter(business=bus)

    purchaser = KnotisUser.objects.get(username = purchase_user)

    redemption_code = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits
        ) for _ in range(10)
    )

    trans_context = '|'.join([purchaser.id, generate_ipn_hash(purchaser.id), redemption_code])

    return Transaction.objects.create_transaction(purchaser, TransactionTypes.PURCHASE, bus, bus_offers[offer_number],qty,value,trans_context)

#mytrans = Transaction.objects.create_transaction(TransactionTypes.PURCHASE, josie, mybus,myoffers[0],1,10)
#josie = KnotisUser.objects.get(username = 'jimlay@gmail.com')
#
#mytrans = Transaction.objects.create_transaction(josie, TransactionTypes.PURCHASE, mybus,myoffers[0],1,10)
#mytrans.transaction_context='foobar'
#mytrans.save()
#mytrans = Transaction.objects.create_transaction(josie, TransactionTypes.PURCHASE, mybus,myoffers[0],1,10,'baz')
#mytrans = Transaction.objects.create_transaction(josie, TransactionTypes.PURCHASE, mybus,myoffers[0],1,10,'quux')
#mytrans = Transaction.objects.create_transaction(josie, TransactionTypes.PURCHASE, mybus,myoffers[0],1,10,'bingbangboom')
#mytrans = Transaction.objects.create_transaction(josie, TransactionTypes.PURCHASE, mybus,myoffers[0],1,10,'hamburgertime')
#
#trans_context = '|'.join([josie.id, generate_ipn_hash(josie.id), "wonk")
#mytrans = Transaction.objects.create_transaction(josie, TransactionTypes.PURCHASE, mybus,myoffers[0],1,10,trans_context)
