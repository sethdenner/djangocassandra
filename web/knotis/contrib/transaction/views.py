import copy

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.media.models import ImageInstance
from knotis.contrib.identity.views import (
    get_identity_profile_badge,
    get_identity_profile_banner,
    get_identity_default_profile_banner_color
)
from knotis.contrib.transaction.models import Transaction
from knotis.views import (
    EmailView,
    FragmentView
)


class TransactionTileView(FragmentView):
    template_name = 'knotis/transaction/transaction_tile.html'
    view_name = 'transaction_tile'

    def process_context(self):
        identity = self.context['identity']

        profile_badge_image = get_identity_profile_badge(identity)
        profile_banner_image = get_identity_profile_banner(identity)
        profile_banner_color = get_identity_default_profile_banner_color(
            identity
        )

        self.context.update({
            'badge_image': profile_badge_image,
            'banner_image': profile_banner_image,
            'profile_banner_color': profile_banner_color
        })

        return self.context


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
            if p.owner != transaction.owner:
                customer = p.owner
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
