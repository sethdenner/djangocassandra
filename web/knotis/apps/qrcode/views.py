from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    redirect,
    render
)
from django.conf import settings

from knotis.utils.view import get_standard_template_parameters
from knotis.apps.offer.models import (
    Offer,
    OfferStatus
)
from knotis.apps.business.models import Business
from knotis.apps.business.views import edit_profile
from knotis.apps.qrcode.models import (
    Qrcode,
    QrcodeTypes,
    Scan
)
from knotis.apps.legacy.models import QrcodeIdMap


def scan(request, qrcode_id):
    qrcode = None
    try:
        qrcode = Qrcode.objects.get(pk=qrcode_id)
    except:
        pass

    if not qrcode:
        return redirect('/')

    qrcode.scan()
    
    return redirect(
        qrcode.uri,
        permanent=True
    )


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

    template_parameters = get_standard_template_parameters(request)
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

        try:
            id_map = QrcodeIdMap.objects.get(new_qrcode=qrcode)

        except Exception, e:
            id_map = None

        if id_map:
            qrcode_uri = '/'.join([
                settings.BASE_URL,
                'business',
                unicode(id_map.old_id),
            ])

        else:
            qrcode_uri = '/'.join([
                settings.BASE_URL,
                'qrcode',
                qrcode.id
            ])

        template_parameters['qrcode_uri'] = qrcode_uri

    template_parameters['BASE_URL'] = settings.BASE_URL

    return render(
        request,
        'manage_qrcode.html',
        template_parameters
    )
