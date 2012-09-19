from app.models.transactions import Transaction, TransactionTypes
from knotis_auth.models import UserProfile, AccountTypes


def buy_premium_plan(request):
    try:
        user_id = request.POST.get('custom')
        user_profile = UserProfile.objects.get(user_id=user_id)

        user_profile.account_type = AccountTypes.BUSINESS_MONTHLY
        user_profile.save()

        Transaction.objects.create_transaction(
            user_profile.user,
            TransactionTypes.PURCHASE_KNOTIS_UNLIMITED,
            value=14.
        )
    except:
        pass
