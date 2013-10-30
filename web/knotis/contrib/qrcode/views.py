import copy

from django.shortcuts import redirect
from django.conf import settings
from django.views.generic import View

from knotis.views import ContextView

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


class ScanView(View):
    def get(
        self,
        request,
        qrcode_id,
        *args,
        **kwrags
    ):
        qrcode = None
        try:
            qrcode = Qrcode.objects.get(pk=qrcode_id)
        except:
            pass

        if not qrcode:
            return redirect('/')

        qrcode.scan()

        return redirect(
            qrcode.uri
        )


class ManageQRCodeView(ContextView):
    template_name = 'knotis/qrcode/manage_qrcode.html'

    def process_context(self):
        self.context = copy.copy(self.context)
        request = self.context.get('request')

        current_identity_id = request.session.get('current_identity_id')
        business = Identity.objects.get(pk=current_identity_id)

        try:
            qrcode = Qrcode.objects.get(owner=business)

        except:
            qrcode = None

        self.context['business'] = business

        try:
            self.context['offers'] = Offer.objects.filter(
                owner=business,
                status=OfferStatus.CURRENT
            )

        except:
            pass

        if qrcode:
            self.context['qrcode'] = qrcode
            try:
                self.context['scans'] = Scan.objects.filter(
                    qrcode=qrcode
                )

            except:
                pass

            qrcode_uri = '/'.join([
                settings.BASE_URL,
                'qrcode',
                qrcode.id
            ])

            self.context['qrcode_uri'] = qrcode_uri

        self.context['BASE_URL'] = settings.BASE_URL

        self.context['styles'] = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
        ]

        self.context['post_scripts'] = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'navigation/js/navigation.js',
        ]

        return self.context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity_id = request.session.get('current_identity_id')
        business = Identity.objects.get(pk=current_identity_id)
        qrcode = Qrcode.objects.get(owner=business)

        qrcode_type = request.POST.get('qrcode')

        if 'profile' == qrcode_type:
            qrcode.qrcode_type = QrcodeTypes.PROFILE
            qrcode.uri = '/'.join([
                settings.BASE_URL,
                'id',
                business.id,
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

        return self.get(
            request,
            *args,
            **kwargs
        )
