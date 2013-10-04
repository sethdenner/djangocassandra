import urllib2
import hashlib

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse,
    HttpResponseNotAllowed
)
from django.utils.http import urlencode
from django.shortcuts import redirect
from django.views.generic import View

from knotis.views import FragmentView

from knotis.utils.email import generate_email
from knotis.contrib.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.offer.models import Offer
from knotis.contrib.identity.models import Identity


class PayPalReturn(View):
    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        next_url = request.GET.get('next')
        url = next_url if next_url else '/my/purchases/redeemable/'

        return redirect(url)


class IPNCallbackView(View):
    @csrf_exempt
    def dispatch(
        self,
        *args,
        **kwargs
    ):
        return super(IPNCallbackView, self).dispatch(
            *args,
            **kwargs
        )

    @staticmethod
    def generate_ipn_hash(value):
        salt = '1@#%^&()_+HYjI'
        return hashlib.sha1(''.join([
            salt,
            value,
            salt
        ])).hexdigest()

    @staticmethod
    def is_ipn_valid(request):
        post = request.POST

        post_formatted = '\n'.join([
            '   key=%s, value=%s' % (k, v,) for k, v in post.items()
        ])
        logger.info('\n'.join([
            'validating ipn with post parameters:',
            post_formatted
        ]))

        data = post.copy()
        data['cmd'] = '_notify-validate'

        parameters_formatted = '\n'.join([
            '   key=%s, value=%s' % (k, v,) for k, v in data.items()
        ])
        logger.debug('\n'.join([
            'request parameters:',
            parameters_formatted
        ]))

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        if post.get('test_ipn') == '1':
            uri = settings.PAYPAL_TEST_URL
            logger.debug('using paypal test url: %s' % (uri,))

        else:
            uri = settings.PAYPAL_URL
            logger.debug('using paypal live url: %s' % (uri,))

        validation_request = urllib2.Request(
            uri,
            urlencode(data),
            headers
        )

        try:
            logger.debug('sending request')
            connection = urllib2.urlopen(validation_request)
            try:
                response = connection.read()

            finally:
                connection.close()

        except urllib2.HTTPError, error:
            logger.exception('request failed')
            response = error.read()

        except Exception, error:
            logger.exception('request failed')
            response = error.message

        if response == 'VERIFIED':
            logger.info('ipn verified')
            return True

        logger.error('ipn verification failed trying custom verification')
        custom_validation = post.get('custom')
        if not custom_validation:
            logger.error('no custom verification parameters')
            return False

        custom_validation = custom_validation.split('|')
        if 2 > len(custom_validation):
            logger.error('not enough verification parameters')
            return False

        ipn_hash = IPNCallbackView.generate_ipn_hash(custom_validation[0])
        if ipn_hash != custom_validation[1]:
            logger.error('ipn hashes did not match')
            return False

        logger.info('ipn hashes match ipn verified')
        return True

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        logger.debug('ipn request recieved')

        if request.method.lower() != 'post':
            logger.debug('method must be post')
            return HttpResponseNotAllowed('POST')

        if not IPNCallbackView.is_ipn_valid(request):
            logger.debug('invalid ipn')
            return HttpResponse('OK')

        logger.debug('ipn is valid')
        txn_type = request.POST.get('txn_type')
        transaction_context = request.POST.get('custom')
        ammount3 = request.POST.get('ammount3')
        mc_gross = request.POST.get('mc_gross')
        item_name = request.POST.get('item_name')
        item_name1 = request.POST.get('item_name1')
        item_number1 = request.POST.get('item_number1')
        quantity1 = request.POST.get('quantity1')
        context_parts = transaction_context.split('|')
        user_id = context_parts[0]

        try:
            logger.debug('getting pending transaction')
            user = KnotisUser.objects.get(pk=user_id)
            transactions = Transaction.objects.filter(
                user=user,
                transaction_context=transaction_context
            )

            purchased = False
            pending_transaction = None
            for transaction in transactions:
                if transaction.transaction_type == TransactionTypes.PENDING:
                    logger.debug(
                        'pending transaction found with id %s' % (
                            transaction.id,
                        )
                    )
                    pending_transaction = transaction

                if transaction.transaction_type == TransactionTypes.PURCHASE:
                    logger.debug(
                        'existing purchase found with id %s' % (
                            transaction.id,
                        )
                    )
                    purchased = True

            if pending_transaction and not purchased:
                logger.debug(
                    'creating purchase transaction with context %s' % (
                        pending_transaction.transaction_context,
                    )
                )

                if txn_type == 'subscr_cancel':
                    pending_transaction.transaction_type = (
                        TransactionTypes.CANCEL
                    )
                    pending_transaction.save()

                else:
                    value = mc_gross if mc_gross else ammount3
                    transaction = Transaction.objects.create_transaction(
                        pending_transaction.user,
                        TransactionTypes.PURCHASE,
                        pending_transaction.business,
                        pending_transaction.offer,
                        int(quantity1) if quantity1 else None,
                        value,
                        pending_transaction.transaction_context
                    )

            else:
                transaction = None

        except:
            logger.exception('failed to create transaction')
            transaction = None

        logger.debug('offer purchase')
        try:
            logger.debug('getting offer with id %s' % (item_number1,))
            Offer.objects.get(pk=item_number1).purchase()
            logger.debug('offer purchased')

            logger.debug('sending offer purchase email')
            generate_email(
                'offer_purchase',
                transaction.offer.title_formatted(),
                settings.EMAIL_HOST_USER,
                [transaction.user.username], {
                    'transaction': transaction,
                    'BASE_URL': settings.BASE_URL,
                    'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE
                }
            ).send()
            logger.debug('email sent to %s' % (
                transaction.user.username
            ))

        except:
            logger.exception('failed to purchase offer.')

        return HttpResponse('OK')


class PayPalButton(FragmentView):
    template_name = 'knotis/paypal/paypal_button.html'
    view_name = 'paypal_button'

    def process_context(self):
        local_context = Context({
            'button_text': settings.PAYPAL_DEFAULT_BUTTON_TEXT,
        })
        local_context.update(self.context.__dicts__)

        notify_url = local_context.get('notify_url')
        if notify_url:
            if not notify_url.startswith('http://'):
                local_context['notify_url'] = '/'.join([
                    settings.BASE_URL,
                    notify_url
                ])

        return_url = local_context.get('return')
        if return_url:
            local_context['return'] = return_url = '/'.join([
                settings.BASE_URL,
                'paypal',
                'return',
                ''.join([
                    '?next=',
                    return_url
                ])
            ])

        return local_context
