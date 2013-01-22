from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import (
    render,
)
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.utils.view import get_standard_template_parameters
from knotis.apps.transaction.models import (
    Transaction,
    TransactionTypes,
)
from knotis.apps.auth.models import UserProfile

@login_required
def print_transaction(
    request,
    transaction_id
):
    template_parameters = get_standard_template_parameters(request)

    try:
        transaction = Transaction.objects.get(pk=transaction_id)
        template_parameters['purchase'] = transaction

    except:
        logger.exception('could not get offer')
        transaction = None

    if not transaction:
        return HttpResponseNotFound('Could not get offer')

    try:
        transactions = Transaction.objects.filter(
            user=request.user,
            transaction_type=TransactionTypes.PURCHASE
        )
        template_parameters['purchases'] = transactions
        vouchers = []
        for t in transactions:
            for i in range(t.quantity):
                voucher = {
                    'redemption_code': '-'.join([
                        t.redemption_code(),
                        str(i)
                    ]),
                    'offer': t.offer,
                    'business': t.business,
                    'purchase_date': t.pub_date,
                    'value': t.value_formatted()
                }
                vouchers.append(voucher)

        template_parameters['vouchers'] = vouchers

    except:
        logger.exception('failed to render vouchers')
        transactions = None

    return render(
        request,
        'transaction_print.html',
        template_parameters
    )


@login_required
def get_user_transactions(
    request,
    status
):
    template_parameters = {}

    try:
        template_parameters['user_profile'] = UserProfile.objects.get(
            user=request.user
        )

    except:
        pass

    try:
        if status == 'redeemed':
            transaction_type = TransactionTypes.REDEMPTION

        elif status == 'purchased':
            transaction_type = TransactionTypes.PURCHASE

        else:
            transaction_type = None

        transactions = Transaction.objects.filter(
            user=request.user,
            transaction_type=transaction_type
        )
        template_parameters['transactions'] = transactions

    except:
        pass

    return render(
        request,
        'transaction_list_manage.html',
        template_parameters
    )
