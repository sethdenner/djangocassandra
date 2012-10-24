from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect
)
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.utils.view import get_standard_template_parameters
from knotis.apps.business.models import Business
from knotis.apps.offer.models import Offer
from knotis.apps.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.apps.qrcode.models import Scan
from knotis.apps.highchart.views import (
    render_monthly_revenue_chart,
    render_monthly_qrcode_chart
)


@login_required
def redeem_offer(request):
    transaction_id = request.POST.get('transaction_id')
    quantity = request.POST.get('quantity')

    try:
        transaction = Transaction.objects.get(pk=transaction_id)
    except:
        transaction = None

    if not transaction:
        return False

    try:
        Transaction.objects.create_transaction(
            transaction.user,
            TransactionTypes.REDEMPTION,
            transaction.business,
            transaction.offer,
            quantity,
            0.,
            transaction.transaction_context
        )
        return True

    except Exception, error:
        return False


@login_required
def dashboard(request):
    if request.method.lower() == 'post':
        redeem_offer(request)

    template_parameters = get_standard_template_parameters(request)

    try:
        business = Business.objects.get(user=request.user)
    except:
        business = None
        
    if not business:
        return redirect('/business/profile/')

    try:
        offers = Offer.objects.filter(
            business=business
        )

        purchases = Transaction.objects.filter(
            business=business,
            transaction_type=TransactionTypes.PURCHASE
        )

        offer_purchase_map = {}
        for offer in offers:
            offer_purchase_map[offer] = []
            for purchase in purchases:
                if purchase.offer_id == offer.id and \
                    purchase.transaction_type == TransactionTypes.PURCHASE:
                    offer_purchase_map[offer].append(purchase)

        template_parameters['offer_purchase_map'] = offer_purchase_map

        total_revenue = 0.
        for purchase in purchases:
            total_revenue = total_revenue + purchase.value

        template_parameters['total_purchases'] = len(purchases)
        template_parameters['total_revenue'] = ("%.2f" % round(
            total_revenue,
            2
        )).replace('.00', '')

    except:
        logger.exception('failed rendering transaction data')

    template_parameters['graphics'] = True
    template_parameters['highchart'] = render_monthly_revenue_chart(business)

    return render(
        request,
        'dashboard.html',
        template_parameters
    )


@login_required
def dashboard_qrcode(request):
    template_parameters = get_standard_template_parameters(request)

    try:
        business = Business.objects.get(user=request.user)
    except:
        business = None

    try:
        scans = Scan.objects.filter(business=business)
        template_parameters['scans'] = scans
    except:
        pass

    template_parameters['graphics'] = True
    template_parameters['highchart'] = render_monthly_qrcode_chart(business)

    return render(
        request,
        'dashboard_qrcode.html',
        template_parameters
    )
