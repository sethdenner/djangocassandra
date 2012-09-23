from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.conf import settings

from app.utils import View as ViewUtils
from app.models.offers import Offer, OfferStatus

from app.views.business import edit_profile
from app.models.businesses import Business

from knotis_qrcodes.models import Qrcode, QrcodeTypes, Scan


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
    try:
        business = Business.objects.get(user=request.user)

    except:
        return redirect(edit_profile)

    try:
        qrcode = Qrcode.objects.get(business=business)

    except:
        qrcode = None

    if request.method.lower() == 'post':
        qrcode_type = request.POST.get('qrcode')
        if 'profile' == qrcode_type:
            qrcode.qrcode_type = QrcodeTypes.PROFILE
            qrcode.uri = '/'.join([
                settings.BASE_URL,
                business.backend_name,
                ''
            ])
            qrcode.save()

        elif 'link' == qrcode_type:
            qrcode.qrcode_type = QrcodeTypes.LINK
            qrcode.uri = request.POST.get('link_content')
            qrcode.save()

        elif 'video' == qrcode_type:
            qrcode.qrcode_type = QrcodeTypes.VIDEO
            qrcode.uri = request.POST.get('video_content')
            qrcode.save()

        else:
            qrcode.qrcode_type = QrcodeTypes.OFFER
            qrcode.uri = '/'.join([
                settings.BASE_URL,
                'offer',
                qrcode_type,
                ''
            ])
            qrcode.save()
                
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    template_parameters['business'] = business
    
    try:
        template_parameters['offers'] = Offer.objects.filter(
            business=business,
            status=OfferStatus.CURRENT
        )

    except:
        pass

    if qrcode:
        template_parameters['qrcode'] = qrcode
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
