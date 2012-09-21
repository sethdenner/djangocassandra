from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.conf import settings

from app.utils import View as ViewUtils
from app.models.offers import Offer, OfferStatus

from app.views.business import edit_profile
from app.models.businesses import Business

from knotis_qrcodes.models import Qrcode, Scan


def scan(request, qrcode_id):
    qrcode = None
    try:
        qrcode = Qrcode.objects.get(pk=qrcode_id)
    except:
        pass

    if not qrcode:
        return redirect('/')

    return qrcode.scan()


@login_required
def manage(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    business = None
    try:
        business = Business.objects.get(user=request.user)
        template_parameters['business'] = business
    except:
        redirect(edit_profile)

    if business:
        try:
            template_parameters['offers'] = Offer.objects.filter(
                business=business,
                status=OfferStatus.CURRENT
            )
        except:
            pass

        qrcode = None
        try:
            qrcode = Qrcode.objects.get(business=business)
            template_parameters['qrcode'] = qrcode
        except:
            pass

        if qrcode:
            try:
                template_parameters['scans'] = Scan.objects.filter(qrcode=qrcode)
            except:
                pass

    template_parameters['BASE_URL'] = settings.BASE_URL

    return render(
        request,
        'manage_qrcode.html',
        template_parameters
    )


