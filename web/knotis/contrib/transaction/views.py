from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import (
    render,
)
from django.utils.log import logging
logger = logging.getLogger(__name__)

# from knotis.utils.view import get_standard_template_parameters
from knotis.contrib.transaction.models import (
    Transaction,
    TransactionTypes,
)

from knotis.views import EmailView
import copy


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


class CustomerReceiptBody(EmailView):
    template_name = 'knotis/transaction/email_receipt_consumer.html'
    
    def process_context(self):
        local_context = copy.copy(self.context)

        business_name = 'Fine Bitstrings'
        browser_link = 'http://example.com'
        business_cover_url = 'http://dev.knotis.com/media/cache/ef/25/ef2517885c028d7545f13f79e5b7993a.jpg'
        business_logo_url = 'http://dev.knotis.com/media/cache/87/08/87087ae77f4a298e550fc9d255513ad4.jpg'
        username = 'Josh'
        order_number = '9999'
        payment_method = 'Visa ending in 1234'
        billing_name = 'Joshua Moore'
        billing_address = '2226 3rd Ave, Seattle, WA'
        payment_date = '2013-11-19'
        shipping_name = 'Joshua Moore'
        shipping_address = '2226 3rd Ave, Seattle, WA'
        product_img_url = 'http://dev.knotis.com/media/cache/87/08/87087ae77f4a298e550fc9d255513ad4.jpg'
        product_link = 'http://dev.knotis.com'
        product_name = 'Coal'
        business_url = 'http://dev.knotis.com/id/a5864e72-55bc-437f-8afe-3103a6af80a9/'
        transaction_id = '999999'
        quantity = '1'
        price = '$0.99'
        item_total = '$0.99'
        shipping = '$0.00'
        sales_tax = '$0.00'
        total = '$0.99'
        message_seller_link = 'http://dev.knotis.com/id/a5864e72-55bc-437f-8afe-3103a6af80a9/'
        
        local_context.update({
            'business_name': business_name,
            'browser_link': browser_link,
            'business_cover_url': business_cover_url,
            'business_logo_url': business_logo_url,
            'username': username,
            'order_number': order_number,
            'payment_method': payment_method,
            'billing_name': billing_name,
            'billing_address': billing_address,
            'payment_date': payment_date,
            'shipping_name': shipping_name,
            'shipping_address': shipping_address,
            'product_img_url': product_img_url,
            'product_link': product_link,
            'business_url': business_url,
            'transaction_id': transaction_id,
            'quantity': quantity,
            'price': price,
            'item_total': item_total,
            'shipping': shipping,
            'sales_tax': sales_tax,
            'total': total,
            'message_seller_link': message_seller_link,
            'product_name': product_name
        })

        return local_context


class MerchantReceiptBody(EmailView):
    template_name = 'knotis/transaction/email_receipt_merchant.html'

    def process_context(self):
        local_context = copy.copy(self.context)

        customer_name = 'Joshua Moore'
        browser_link = 'http://example.com'
        business_cover_url = 'http://dev.knotis.com/media/cache/ef/25/ef2517885c028d7545f13f79e5b7993a.jpg'
        business_logo_url = 'http://dev.knotis.com/media/cache/87/08/87087ae77f4a298e550fc9d255513ad4.jpg'
        business_name = 'Fine Bitstrings'
        merchant_username = 'Josh'
        order_number = '9999'
        payment_method = 'Visa ending in 1234'
        payment_date = '2013-11-23'
        billing_name = 'Joshua Moore'
        billing_address = '2226 3rd Ave, Seattle, WA'
        shipping_name = 'Joshua Moore'
        shipping_address = '2226 3rd Ave, Seattle, WA'
        product_img_url = 'http://dev.knotis.com/media/cache/87/08/87087ae77f4a298e550fc9d255513ad4.jpg'
        product_link = 'http://dev.knotis.com'
        business_url = 'http://dev.knotis.com/id/a5864e72-55bc-437f-8afe-3103a6af80a9/'
        transaction_id = '999999'
        quantity = '1'
        item_total = '$0.99'
        shipping = '$0.00'
        sales_tax = '$0.00'
        total = '$0.99'
        message_customer_link = 'http://dev.knotis.com/id/a5864e72-55bc-437f-8afe-3103a6af80a9/'
        processing = '$0.10'
        product_name = 'Coal'
        price = '$0.99'
        
        local_context.update({
            'customer_name': customer_name,
            'browser_link': browser_link,
            'business_cover_url': business_cover_url,
            'business_logo_url': business_logo_url,
            'business_name': business_name,
            'merchant_username': merchant_username,
            'order_number': order_number,
            'payment_method': payment_method,
            'payment_date': payment_date,
            'billing_name': billing_name,
            'billing_address': billing_address,
            'shipping_name': shipping_name,
            'shipping_address': shipping_address,
            'product_img_url': product_img_url,
            'product_link': product_link,
            'business_url': business_url,
            'transaction_id': transaction_id,
            'quantity': quantity,
            'item_total': item_total,
            'shipping': shipping,
            'sales_tax': sales_tax,
            'total': total,
            'message_customer_link': message_customer_link,
            'processing': processing,
            'product_name': product_name,
            'price': price
        })

        return local_context
