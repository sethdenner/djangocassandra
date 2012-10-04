import urllib
import urllib2
import hashlib

from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from app.models.transactions import Transaction, TransactionTypes
from knotis_auth.models import User, UserProfile, AccountTypes
from app.models.offers import Offer


def generate_ipn_hash(value):
    salt = '1@#%^&()_+HYjI'
    return hashlib.sha1(''.join([
        salt,
        value,
        salt
    ])).hexdigest()


def is_ipn_valid(request):
    if request.method.lower() != 'post':
        return  # log something here

    parameters = 'cmd=_notify-validata'
    for key, value in request.POST:
        parameters += '&%s=%s' % (
            urllib.urlencode(key),
            urllib.urlencode(value)
        )

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': len(parameters)
    }

    if request.POST.get('test_ipn') == '1':
        uri = settings.PAYPAL_TEST_URL
    else:
        uri = settings.PAYPAL_URL

    request = urllib2.Request(
        uri,
        parameters,
        headers
    )
    try:
        connection = urllib2.urlopen(request)
        try:
            response = connection.read()
        finally:
            connection.close()
    except urllib2.HTTPError, error:
        response = error.read()

    if response == 'VERIFIED':
        return True

    custom_validation = request.POST.get('custom')
    if not custom_validation or len(custom_validation) != 2:
        return False

    custom_validation = custom_validation.split('_')
    if 2 != len(custom_validation):
        return False

    ipn_hash = generate_ipn_hash(custom_validation[0])
    if ipn_hash != custom_validation[1]:
        return False

    return True


def ipn_callback(request):
    if not is_ipn_valid(request):
        return

    transaction_context = request.POST.get('custom')
    auth_amount = request.POST.get('auth_amount')
    item_name_1 = request.POST.get('item_name_1')
    item_number_1 = request.POST.get('item_number_1')

    try:
        transactions = Transaction.objects.filter(
            transaction_context=transaction_context
        )

        purchased = False
        completed = False
        purchase = None
        for transaction in transactions:
            if transaction.transaction_type == TransactionTypes.PURCHASE:
                purchased = True
                purchase = transaction

            if transaction.transaction_type == TransactionTypes.COMPLETE:
                completed = True

        if purchased and not completed:
            Transaction.objects.create_transaction(
                purchase.user,
                TransactionTypes.COMPLETE,
                purchase.business,
                purchase.offer,
                purchase.quantity,
                auth_amount,
                purchase.transaction_context
            )

    except:
        pass

    if item_name_1 == 'Business Monthly Subscription':
        try:
            context_parts = transaction_context.split('_')
            user_id = context_parts[0]
            user = User.objects.get(pk=user_id)
            user_profile = UserProfile.objects.get(user=user)

            user_profile.account_type = AccountTypes.BUSINESS_MONTHLY
            user_profile.save()

        except:
            pass

    elif item_number_1:
        try:
            offer = Offer.objects.get(pk=item_number_1)
        except:
            offer = None

        if not offer:
            return

        offer.purchase()


def render_paypal_button(parameters):
    default_parameters = {
        'action': settings.PAYPAL_FORM_URL,
        'button_text': settings.PAYPAL_DEFAULT_BUTTON_TEXT,
    }
    default_parameters.update(parameters)
    parameters = default_parameters

    notify_url = parameters.get('notify_url')
    if notify_url:
        if not notify_url.startswith(settings.BASE_URL):
            parameters['notify_url'] = '/'.join([
                settings.BASE_URL,
                notify_url
            ])

    context = Context(parameters)
    template = get_template('paypal_button.html')
    return template.render(context)
