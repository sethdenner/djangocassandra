from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    redirect,
    render
)
from django.conf import settings
from django.template import Context

from knotis.contrib.offer.models import (
    Offer,
    OfferStatus
)
from knotis.contrib.qrcode.models import (
    Qrcode,
    QrcodeTypes,
    Scan
)
from knotis.contrib.identity.models import Identity


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
        current_identity_id = request.session.get('current_identity_id')
        business = Identity.objects.get(pk=current_identity_id)

    except:
        return redirect('/')

    try:
        qrcode = Qrcode.objects.get(owner=business)

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

    template_parameters = Context()
    template_parameters['business'] = business

    try:
        template_parameters['offers'] = Offer.objects.filter(
            owner=business,
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
