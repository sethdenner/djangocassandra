import urllib2
import hashlib

from django.utils.log import logging
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse,
    HttpResponseNotAllowed
)
from django.utils.http import urlencode
from django.shortcuts import redirect

from knotis.utils.email import generate_email
from knotis.apps.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.apps.auth.models import (
    KnotisUser,
    UserProfile,
    AccountTypes
)
from knotis.apps.offer.models import Offer

logger = logging.getLogger(__name__)


def generate_ipn_hash(value):
    salt = '1@#%^&()_+HYjI'
    return hashlib.sha1(''.join([
        salt,
        value,
        salt
    ])).hexdigest()


def is_ipn_valid(post):
    post_formatted = '\n'.join([
        '   key=%s, value=%s' % (k, v,) for k, v in post.items()
    ])
    logger.debug('\n'.join([
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
        data,
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
        logger.debug('ipn verified')
        return True

    logger.debug('ipn verification failed trying custom verification')
    custom_validation = post.get('custom')
    if not custom_validation:
        logger.debug('no custom verification parameters')
        return False

    custom_validation = custom_validation.split('|')
    if 3 != len(custom_validation):
        logger.debug('wrong number of verification parameters')
        return False

    ipn_hash = generate_ipn_hash(custom_validation[0])
    if ipn_hash != custom_validation[1]:
        logger.debug('ipn hashes did not match')
        return False

    logger.debug('ipn hashes match ipn verified')
    return True


@csrf_exempt
def paypal_return(request):
    if request.method.lower() != 'post':
        return HttpResponseNotAllowed('POST')

    next_url = request.GET.get('next')
    url = next_url if next_url else '/offers/dashboard/'

    return redirect(url)


@csrf_exempt
def ipn_callback(request):
    logger.debug('ipn request recieved')
    
    if request.method.lower() != 'post':
        logger.debug('method must be post')
        return HttpResponseNotAllowed('POST')

    if not is_ipn_valid(request.POST):
        logger.debug('invalid ipn')
        return HttpResponse('OK')

    logger.debug('ipn is valid')
    transaction_context = request.POST.get('custom')
    auth_amount = request.POST.get('auth_amount')
    item_name_1 = request.POST.get('item_name1')
    item_number_1 = request.POST.get('item_number1')
    quantity = request.POST.get('quantity1')
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
                    'pending transaction found with id %s' % (transaction.id,)
                )
                pending_transaction = transaction

            if transaction.transaction_type == TransactionTypes.PURCHASE:
                logger.debug(
                    'existing purchase found with id %s' % (transaction.id,)
                )
                purchased = True

        if pending_transaction and not purchased:
            logger.debug(
                'creating purchase transaction with context %s' % (
                    pending_transaction.transaction_context,
                )
            )
            transaction = Transaction.objects.create_transaction(
                pending_transaction.user,
                TransactionTypes.PURCHASE,
                pending_transaction.business,
                pending_transaction.offer,
                int(quantity) if quantity else None,
                auth_amount,
                pending_transaction.transaction_context
            )
            
        else:
            transaction = None
        
    except:
        logger.exception('failed to create transaction')
        transaction = None

    if item_name_1 == 'Business Monthly Subscription':
        logger.debug('paid business subscription purchase')
        try:
            logger.debug('getting user with id %s' % (user_id,))
            user = KnotisUser.objects.get(pk=user_id)
            logger.debug('user found')
            user_profile = UserProfile.objects.get(user=user)
            logger.debug('user profile found')

            logger.debug('upgrading account')
            user_profile.account_type = AccountTypes.BUSINESS_MONTHLY
            user_profile.save()
            logger.debug('account upgraded')

        except:
            logger.exception('failed to upgrade user')

    elif item_number_1:
        logger.debug('offer purchase')
        try:
            logger.debug('getting offer with id %s' % (item_number_1,))
            Offer.objects.get(pk=item_number_1).purchase()
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


def render_paypal_button(parameters):
    default_parameters = {
        'button_text': settings.PAYPAL_DEFAULT_BUTTON_TEXT,
    }
    default_parameters.update(parameters)
    parameters = default_parameters

    notify_url = parameters.get('notify_url')
    if notify_url:
        if not notify_url.startswith('http://'):
            parameters['notify_url'] = '/'.join([
                settings.BASE_URL,
                notify_url
            ])

    return_url = parameters.get('return')
    if return_url:
        parameters['return'] = return_url = '/'.join([
            settings.BASE_URL,
            'paypal',
            'return',
            ''.join([
                '?next=',
                return_url
            ])
        ])

    context = Context(parameters)
    template = get_template('paypal_button.html')
    return template.render(context)
