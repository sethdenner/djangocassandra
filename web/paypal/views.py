from django.conf import settings
from django.template import Template, Context
from django.template.loader import get_template
from app.models.transactions import Transaction, TransactionTypes
from knotis_auth.models import UserProfile, AccountTypes


def buy_premium_service(request):
    try:
        user_id = request.POST.get('custom')
        user_profile = UserProfile.objects.get(user_id=user_id)

        user_profile.account_type = AccountTypes.BUSINESS_MONTHLY
        user_profile.save()

        Transaction.objects.create_transaction(
            user_profile.user,
            TransactionTypes.PURCHASE_KNOTIS_UNLIMITED,
            value=settings.PRICE_MERCHANT_MONTHLY
        )
    except:
        pass


def render_paypal_button(parameters):
    default_parameters = {
        'action': settings.PAYPAL_FORM_URL,
        'button_text': settings.PAYPAL_DEFAULT_BUTTON_TEXT,
        'hosted_button_id': None,
        'custom': None,
        'return': None,
        'rm': 0
    }
    default_parameters.update(parameters)
    context = Context(default_parameters)
    template = get_template('paypal_button.html')
    return template.render(context)
