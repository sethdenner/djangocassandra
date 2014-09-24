import copy

from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.views.generic import View

from knotis.views import EmbeddedView
from knotis.contrib.layout.views import DefaultBaseView

from knotis.contrib.offer.models import (
    Offer,
    OfferStatus
)
from knotis.contrib.transaction.models import (
    TransactionCollection,
    TransactionCollectionItem
)
from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.qrcode.models import (
    Qrcode,
    QrcodeTypes,
    Scan
)
from knotis.contrib.identity.models import IdentityEstablishment
from knotis.utils.regex import REGEX_UUID


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

        if (
            qrcode.uri.startswith('/') or
            qrcode.uri.startswith('http://') or
            qrcode.uri.startswith('https://')
        ):
            redirect_uri = qrcode.uri

        else:
            redirect_uri = ''.join([
                'http://',
                qrcode.uri
            ])

        return redirect(
            redirect_uri
        )


class ManageQRCodeView(EmbeddedView):
    template_name = 'knotis/qrcode/manage_qrcode.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [r'^settings/qrcode/$']

    def process_context(self):
        self.context = copy.copy(self.context)
        request = self.context.get('request')

        current_identity_id = request.session.get('current_identity')
        establishment = IdentityEstablishment.objects.get(
            pk=current_identity_id
        )

        try:
            qrcode = Qrcode.objects.get(owner=establishment)

        except:
            qrcode = None

        self.context['establishment'] = establishment

        try:
            self.context['offers'] = Offer.objects.filter(
                owner=establishment,
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
        self.context['fixed_side_nav'] = True

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
        current_identity_id = request.session.get('current_identity')
        establishment = IdentityEstablishment.objects.get(
            pk=current_identity_id
        )
        qrcode = Qrcode.objects.get(owner=establishment)

        qrcode_type = request.POST.get('qrcode')

        if 'profile' == qrcode_type:
            qrcode.qrcode_type = QrcodeTypes.PROFILE
            qrcode.uri = '/'.join([
                settings.BASE_URL,
                'id',
                establishment.id,
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


class CouponRedemptionView(EmbeddedView, GetCurrentIdentityMixin):
    template_name = 'knotis/qrcode/redeem_offer.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r''.join([
            '^qrcode/coupon/(?P<transaction_collection_id>',
            REGEX_UUID,
            ')/(?P<page_numb>\d+)$'
        ])
    ]

    def get(
        self,
        request,
        transaction_collection_id=None,
        page_numb=None,
        *args,
        **kwargs
    ):

        current_identity = self.get_current_identity(self.request)

        transaction_collection = get_object_or_404(
            TransactionCollection,
            pk=transaction_collection_id
        )

        transaction_collection_item = get_object_or_404(
            TransactionCollectionItem,
            transaction_collection=transaction_collection,
            page=page_numb
        )

        request = self.request
        transaction = transaction_collection_item.transaction
        TransactionApi.create_redemption(
            request,
            transaction,
            current_identity
        )
        return super(CouponRedemptionView, self).get(
            request,
            *args,
            **kwargs
        )


class OfferCollectionConnectView(EmbeddedView, GetCurrentIdentityMixin):
    template_name = 'knotis/qrcode/offer_collection_connect.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r''.join([
            '^qrcode/connect/(?P<transaction_collection_id>',
            REGEX_UUID,
            ')$'
        ])
    ]

    def get(
        self,
        request,
        transaction_collection_id=None,
        *args,
        **kwargs
    ):

        current_identity = self.get_current_identity(self.request)

        transaction_collection = get_object_or_404(
            TransactionCollection,
            pk=transaction_collection_id
        )

        TransactionApi.transfer_transaction_collection(
            self.request,
            current_identity,
            transaction_collection,
        )
        return super(OfferCollectionConnectView, self).get(
            request,
            *args,
            **kwargs
        )
