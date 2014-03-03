from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import (
    render,
    get_object_or_404
)
from django.utils.log import logging
logger = logging.getLogger(__name__)

# from knotis.utils.view import get_standard_template_parameters
from knotis.contrib.transaction.models import (
    Transaction,
    TransactionTypes,
)
from knotis.contrib.media.models import ImageInstance

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

        transaction_id = local_context.get('transaction_id')
        transaction = get_object_or_404(
            Transaction,
            pk=transaction_id
        )

        business_images = ImageInstance.objects.filter(
            owner=transaction.offer.owner,
            related_object_id=transaction.offer.owner,
            primary=True
        )

        business_banner = business_badge = None
        for image in business_images:
            if image.context == 'profile_banner':
                business_banner = image

            elif image.context == 'profile_badge':
                business_badge = image

        business_name = transaction.offer.owner
        browser_link = '/'.join([
            settings.BASE_URL,
            'transaction',
            'customerreceipt',
            transaction_id,
            ''
        ])

        try:
            offer_image = ImageInstance.objects.get(
                related_object_id=transaction.offer.pk,
                primary=True,
                context='offer_banner'
            )

        except:
            offer_image = None

        username = transaction.owner.name
        payment_method = 'Stripe'
        billing_name = transaction.owner.name
        payment_date = transaction.pub_date
        offer_link = '/'.join([
            settings.BASE_URL,
            'offers',
            transaction.offer.pk,
            ''
        ])
        offer_title = transaction.offer.title
        business_url = '/'.join([
            settings.BASE_URL,
            'id',
            transaction.offer.owner.pk,
            ''
        ])
        redemption_code = transaction.redemption_code()
        quantity = transaction.quantity()
        price = transaction.offer.price_discount()
        item_total = price * quantity
        
        local_context.update({
            'business_name': business_name,
            'browser_link': browser_link,
            'business_banner': business_banner,
            'business_badge': business_badge,
            'username': username,
            'redemption_code': redemption_code,
            'payment_method': payment_method,
            'billing_name': billing_name,
            'payment_date': payment_date,
            'offer_image': offer_image,
            'offer_link': offer_link,
            'business_url': business_url,
            'quantity': quantity,
            'price': price,
            'item_total': item_total,
            'offer_title': offer_title
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
