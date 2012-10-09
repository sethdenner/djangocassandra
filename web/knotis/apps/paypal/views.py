import urllib
import urllib2
import hashlib

from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.http import urlquote

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


def generate_ipn_hash(value):
    salt = '1@#%^&()_+HYjI'
    return hashlib.sha1(''.join([
        salt,
        value,
        salt
    ])).hexdigest()


@csrf_exempt
def is_ipn_valid(request):
    if request.method.lower() != 'post':
        return  # log something here

    parameters = 'cmd=_notify-validate'
    for key, value in request.POST.items():
        parameters += '&%s=%s' % (
            urlquote(key),
            urlquote(value),
        )

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': len(parameters)
    }

    if request.POST.get('test_ipn') == '1':
        uri = settings.PAYPAL_TEST_URL
    else:
        uri = settings.PAYPAL_URL

    validation_request = urllib2.Request(
        uri,
        parameters,
        headers
    )

    try:
        connection = urllib2.urlopen(validation_request)
        try:
            response = connection.read()

        finally:
            connection.close()

    except urllib2.HTTPError, error:
        response = error.read()

    except Exception, error:
        response = error.message

    if response == 'VERIFIED':
        return True

    custom_validation = request.POST.get('custom')
    if not custom_validation:
        return False

    custom_validation = custom_validation.split('|')
    if 3 != len(custom_validation):
        return False

    ipn_hash = generate_ipn_hash(custom_validation[0])
    if ipn_hash != custom_validation[1]:
        return False

    return True


@csrf_exempt
def ipn_callback(request):
    if not is_ipn_valid(request):
        return HttpResponse('OK')

    transaction_context = request.POST.get('custom')
    auth_amount = request.POST.get('auth_amount')
    item_name_1 = request.POST.get('item_name_1')
    item_number_1 = request.POST.get('item_number_1')
    quantity = request.POST.get('quantity')
    context_parts = transaction_context.split('|')
    user_id = context_parts[0]

    try:
        transactions = Transaction.objects.filter(
            user_id=user_id,
            transaction_context=transaction_context
        )

        purchased = False
        pending_transaction = None
        for transaction in transactions:
            if transaction.transaction_type == TransactionTypes.PENDING:
                pending_transaction = transaction

            if transaction.transaction_type == TransactionTypes.PURCHASE:
                purchased = True

        if pending_transaction and not purchased:
            Transaction.objects.create_transaction(
                pending_transaction.user,
                TransactionTypes.PURCHASE,
                pending_transaction.business,
                pending_transaction.offer,
                int(quantity),
                auth_amount,
                pending_transaction.transaction_context
            )

    except:
        pass

    if item_name_1 == 'Business Monthly Subscription':
        try:
            user = KnotisUser.objects.get(pk=user_id)
            user_profile = UserProfile.objects.get(user=user)

            user_profile.account_type = AccountTypes.BUSINESS_MONTHLY
            user_profile.save()

        except:
            pass

    elif item_number_1:
        try:
            Offer.objects.get(pk=item_number_1).purchase()

        except:
            pass

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
        if not return_url.startswith('http://'):
            parameters['return'] = '/'.join([
                settings.BASE_URL,
                return_url
            ])

    context = Context(parameters)
    template = get_template('paypal_button.html')
    return template.render(context)
