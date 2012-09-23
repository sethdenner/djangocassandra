import urllib
import urllib2
import hashlib

from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from app.models.transactions import Transaction, TransactionTypes
from knotis_auth.models import User, UserProfile, AccountTypes


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

    custom_validation.split('_')
    ipn_hash = generate_ipn_hash(custom_validation[0])
    if ipn_hash != custom_validation[1]:
        return False

    return True


def buy_premium_service(request):
    if not is_ipn_valid(request):
        return

    user_id = request.POST.get('custom')
    transaction_id = request.POST.get('txn_id')

    user = None
    user_profile = None
    try:
        user = User.objects.get(pk=user_id)
        user_profile = UserProfile.objects.get(user=user)
    except:
        pass

    if not user or not user_profile:
        return

    try:
        user_profile.account_type = AccountTypes.BUSINESS_MONTHLY
        user_profile.save()

        Transaction.objects.create_transaction(
            user,
            TransactionTypes.PURCHASE_KNOTIS_UNLIMITED,
            value=settings.PRICE_MERCHANT_MONTHLY,
            transcation_context=transaction_id
        )
    except:
        pass


def render_paypal_button(parameters):
    default_parameters = {
        'action': settings.PAYPAL_FORM_URL,
        'button_text': settings.PAYPAL_DEFAULT_BUTTON_TEXT,
    }
    parameters = default_parameters.update(parameters)

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
