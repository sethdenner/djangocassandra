import copy
import random

from django.utils import log
logger = log.getLogger(__name__)

from django.utils import log
logger = log.getLogger(__name__)


from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.views.generic import View

from knotis.views import (
    EmbeddedView,
)
from knotis.contrib.layout.views import DefaultBaseView

from knotis.contrib.offer.models import (
    Offer,
    OfferStatus
)
from knotis.contrib.transaction.models import (
    Transaction,
    TransactionCollection,
)
from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.qrcode.models import (
    Qrcode,
    QrcodeTypes,
    Scan
)
from knotis.contrib.identity.models import (
    IdentityTypes,
    IdentityEstablishment,
)
from knotis.utils.regex import REGEX_UUID


class ScanView(View):
    def get(
        self,
        request,
        qrcode_id,
        *args,
        **kwargs
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
    template_name = 'knotis/qrcode/redeem_qrcode_offer.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r''.join([
            '^qrcode/redeem/(?P<transaction_id>',
            REGEX_UUID,
            ')/$'
        ]),
    ]
    post_scripts = [
        'knotis/qrcode/js/redeem.js'
    ]

    def process_context(self):
        request = self.request
        transaction_collection_id = self.context.get(
            'transaction_id'
        )
        current_identity = self.get_current_identity(request)
        identity_type = current_identity.identity_type

        self.context.update({
            'redeem_url': '/qrcode/redeem/%s/' % transaction_collection_id,
            'random_pin': random.randint(1000, 9999),
            'identity_type': identity_type,
            'IdentityTypes': IdentityTypes,
        })

        return self.context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}
        data = {}

        transaction_id = kwargs.get('transaction_id')
        pin = request.POST.get('pin')
        pin_check = request.POST.get('pin_check')
        if pin != pin_check:
                errors['no-field'] = (
                    'Wrong PIN!'
                )
                return self.render_to_response(
                    errors=errors
                )

        current_identity = self.get_current_identity(self.request)
        if current_identity.identity_type == IdentityTypes.INDIVIDUAL:
            my_transactions = TransactionApi.get_transaction_for_identity(
                transaction_id,
                current_identity
            )
            if len(my_transactions) == 0:
                errors['no-field'] = (
                    'This does not belong to you.',
                    'Did you connect your passport book yet?'
                )
                return self.render_to_response(
                    errors=errors
                )
            transaction = my_transactions[0]

        else:
            transaction = get_object_or_404(Transaction, pk=transaction_id)

        try:
            TransactionApi.create_redemption(
                request,
                transaction,
                current_identity,
            )

        except TransactionApi.AlreadyRedeemedException:
            errors['no-field'] = 'This has already been redeemed.'
            return self.render_to_response(
                errors=errors
            )

        except TransactionApi.WrongOwnerException:
            errors['no-field'] = ''.join([
                'This does not belong to you.'
            ])
            return self.render_to_response(
                errors=errors
            )

        except Exception, e:
            logger.exception(e.message)

        data['next'] = '/qrcode/redeem/success/'
        if not request.is_ajax():
            self.response_format = self.RESPONSE_FORMATS.REDIRECT

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )


class RedeemSuccessView(EmbeddedView):
    template_name = 'knotis/qrcode/redeem_success.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r'^qrcode/redeem/success/$'
    ]


class OfferCollectionConnectView(EmbeddedView, GetCurrentIdentityMixin):
    template_name = 'knotis/qrcode/offer_collection_connect.html'
    url_patterns = [
        r''.join([
            '^qrcode/connect/(?P<transaction_collection_id>',
            REGEX_UUID,
            ')/$'
        ])
    ]
    default_parent_view_class = DefaultBaseView

    def process_context(self):
        request = self.request
        transaction_collection_id = self.context.get(
            'transaction_collection_id'
        )

        logged_in = request.user.is_authenticated()
        if logged_in:
            current_identity = self.get_current_identity(request)
            is_individual = (
                current_identity.identity_type == IdentityTypes.INDIVIDUAL
            )
        else:
            is_individual = False

        self.context.update({
            'connect_url': '/qrcode/connect/%s/' % transaction_collection_id,
            'is_individual': is_individual,
            'logged_in': logged_in,
        })

        return self.context

    def get(
        self,
        request,
        transaction_collection_id=None,
        *args,
        **kwargs
    ):
        if not request.user.is_authenticated():
            return redirect(
                '/qrcode/connect/login/%s/' % transaction_collection_id
            )
        else:
            return super(OfferCollectionConnectView, self).get(
                request,
                transaction_collection_id,
                *args,
                **kwargs
            )

    def post(
        self,
        request,
        transaction_collection_id=None,
        *args,
        **kwargs
    ):

        errors = {}
        data = {}
        self.response_format = self.RESPONSE_FORMATS.REDIRECT

        if not request.user.is_authenticated():
            message = ''.join([
                'An error occurred while attempting to transfer offers. ',
                'User is not logged in.'
            ])
            logger.exception(message)
            errors['no-field'] = message
            data['next'] = '/signup/?next=/qrcode/connect/%s/' % (
                transaction_collection_id,
            )
            return self.render_to_response(
                data=data,
                errors=errors,
                render_template=False
            )

        current_identity = self.get_current_identity(request)

        if current_identity.identity_type != IdentityTypes.INDIVIDUAL:
            message = ''.join([
                'An error occurred while attempting to transfer offers. ',
                'Wrong identity type'
            ])

            logger.exception(message)
            errors['no-field'] = message

            data['next'] = '/signup/?next=/qrcode/connect/%s/' % (
                transaction_collection_id,
            )
            return self.render_to_response(
                data=data,
                errors=errors,
                render_template=False
            )

        if len(errors) == 0:
            transaction_collection = get_object_or_404(
                TransactionCollection,
                pk=transaction_collection_id
            )

            try:
                TransactionApi.transfer_transaction_collection(
                    request,
                    current_identity,
                    transaction_collection,
                )
                data['next'] = '/qrcode/connect/success/'

            except Exception, e:
                logger.exception(e.message)
                data['next'] = '/'

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )


class ConnectLoginView(EmbeddedView):
    template_name = 'knotis/qrcode/connect_login.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r''.join([
            '^qrcode/connect/login/(?P<transaction_collection_id>',
            REGEX_UUID,
            ')/$'
        ])
    ]

    def process_context(self):
        transaction_collection_id = self.context.get(
            'transaction_collection_id'
        )
        self.context.update({
            'connect_url': '/qrcode/connect/%s/' % transaction_collection_id,
        })
        return self.context


class ConnectionSuccessView(EmbeddedView):
    template_name = 'knotis/qrcode/connect_success.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r'^qrcode/connect/success/$'
    ]


class RandomPassportLoginView(EmbeddedView):
    template_name = 'knotis/qrcode/random_pass_login.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r''.join([
            '^qrcode/random/login/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ])
    ]

    def process_context(self):
        offer_id = self.context.get(
            'offer_id'
        )
        self.context.update({
            'connect_url': '/qrcode/random/%s/' % offer_id,
        })
        return self.context


class RandomPassportView(EmbeddedView, GetCurrentIdentityMixin):
    template_name = 'knotis/qrcode/random_pass_connect.html'
    url_patterns = [
        r''.join([
            '^qrcode/random/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ])
    ]
    default_parent_view_class = DefaultBaseView

    def process_context(self):
        request = self.request
        offer_id = self.context.get(
            'offer_id'
        )

        current_identity = self.get_current_identity(request)
        is_individual = (
            current_identity.identity_type == IdentityTypes.INDIVIDUAL
        )

        self.context.update({
            'connect_url': '/qrcode/random/%s/' % offer_id,
            'is_individual': is_individual,
        })

    def get(
        self,
        request,
        offer_id=None,
        *args,
        **kwargs
    ):
        if not request.user.is_authenticated():
            return redirect(
                '/qrcode/random/login/%s/' % offer_id
            )
        else:
            return super(RandomPassportView, self).get(
                request,
                offer_id,
                *args,
                **kwargs
            )

    def post(
        self,
        request,
        offer_id=None,
        *args,
        **kwargs
    ):

        errors = {}
        data = {}
        self.response_format = self.RESPONSE_FORMATS.REDIRECT

        if not request.user.is_authenticated():
            message = ''.join([
                'An error occurred while attempting to recieve offers. ',
                'User is not logged in.'
            ])
            logger.exception(message)
            errors['no-field'] = message
            data['next'] = '/signup/?next=/qrcode/random/%s/' % (
                offer_id,
            )
            return self.render_to_response(
                data=data,
                errors=errors,
                render_template=False
            )

        current_identity = self.get_current_identity(request)

        if current_identity.identity_type != IdentityTypes.INDIVIDUAL:
            message = ''.join([
                'An error occurred while attempting to recieve offers. ',
                'Wrong identity type'
            ])

            logger.exception(message)
            errors['no-field'] = message

            data['next'] = '/signup/?next=/qrcode/random/%s/' % (
                offer_id,
            )
            return self.render_to_response(
                data=data,
                errors=errors,
                render_template=False
            )

        connect_transactions = TransactionApi.purchase_random_collection(
            request,
            offer_id,
            current_identity,
        )
        data['next'] = '/qrcode/random/success/'
        data['transactions'] = connect_transactions

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )


class RandomPassportSuccessView(EmbeddedView):
    template_name = 'knotis/qrcode/random_pass_success.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r'^qrcode/random/success/$'
    ]
