import copy

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.media.models import ImageInstance
from knotis.contrib.transaction.models import Transaction
from knotis.views import EmailView


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
            related_object_id=transaction.offer.owner.pk,
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
        payment_method = transaction.mode()
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
        price = transaction.offer.price_discount()

        local_context.update({
            'BASE_URL': settings.BASE_URL,
            'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
            'transaction': transaction,
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
            'price': price,
            'offer_title': offer_title
        })

        return local_context


class MerchantReceiptBody(EmailView):
    template_name = 'knotis/transaction/email_receipt_merchant.html'

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

        business_name = transaction.offer.owner.name
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

        customer = None
        participants = transaction.participants()
        for p in participants:
            if p.pk != transaction.owner.pk:
                customer = p
                break

        username = transaction.owner.name
        payment_method = transaction.mode().title()
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
        price = transaction.offer.price_discount()

        local_context.update({
            'transaction': transaction,
            'customer_name': customer.name,
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
            'price': price,
            'offer_title': offer_title
        })

        return local_context
