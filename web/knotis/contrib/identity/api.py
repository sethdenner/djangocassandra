from django.conf import settings
from django.utils.log import logging
logger = logging.getLogger(__name__)
import warnings

from django.core.exceptions import (
    ValidationError
)

from rest_framework.response import Response
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed
)


from knotis.views import (
    ApiView,
    ApiViewSet,
    ApiModelViewSet
)
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin

from knotis.contrib.auth.models import (
    KnotisUser,
    UserInformation
)
from knotis.contrib.relation.models import Relation
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointIdentity,
    EndpointTypes
)

from knotis.contrib.qrcode.models import (
    Qrcode,
    QrcodeTypes
)

from .models import (
    Identity,
    IdentityIndividual,
    IdentityBusiness,
    IdentityTypes
)
from .forms import (
    IdentityForm,
    IdentityIndividualForm,
    IdentityBusinessForm,
    IdentityEstablishmentForm
)
from .serializers import (
    IdentitySerializer,
    IndividualSerializer,
    EstablishmentSerializer,
    BusinessSerializer,
    IdentitySwitcherSerializer
)

class IdentityApi(object):

    @staticmethod
    def create_identity(
        form_class=IdentityForm,
        *args,
        **kwargs
    ):
        errors = {}

        form = form_class(
            data=kwargs
        )

        if form.is_valid():
            instance = form.save()

            # create identity endpoint
            Endpoint.objects.create(
                endpoint_type=EndpointTypes.IDENTITY,
                value=instance.name,
                identity=instance
            )

        else:
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            exception = ValidationError('Some fields are invalid')
            exception.field_errors = errors
            raise exception

        return instance

    @staticmethod
    def create_individual(
        user_id=None,
        *args,
        **kwargs
    ):
        if user_id:
            user = KnotisUser.objects.get(pk=user_id)

        else:
            raise Exception('No user_id provided')

        kwargs['identity_type'] = IdentityTypes.INDIVIDUAL
        individual = IdentityApi.create_identity(
            form_class=IdentityIndividualForm,
            **kwargs
        )

        try:
            Relation.objects.create_individual(
                user,
                individual
            )

        except:
            individual.delete(hard=True)
            raise

        return individual

    @staticmethod
    def create_establishment(
        business_id=None,
        *args,
        **kwargs
    ):
        if business_id:
            business = IdentityBusiness.objects.get(pk=business_id)

        else:
            raise Exception('No business_id provided')

        kwargs['identity_type'] = IdentityTypes.ESTABLISHMENT
        establishment = IdentityApi.create_identity(
            form_class=IdentityEstablishmentForm,
            **kwargs
        )

        try:

            Relation.objects.create_establishment(
                business,
                establishment
            )

        except:
            establishment.delete(hard=True)
            raise

        return establishment

    @staticmethod
    def create_business(
        individual_id=None,
        *args,
        **kwargs
    ):
        if individual_id:
            individual = IdentityIndividual.objects.get(pk=individual_id)

        else:
            raise Exception('No individual_id provided')

        kwargs['identity_type'] = IdentityTypes.BUSINESS
        business = IdentityApi.create_identity(
            form_class=IdentityBusinessForm,
            **kwargs
        )

        try:
            relation_manager = Relation.objects.create_manager(
                individual,
                business
            )

        except:
            business.delete(hard=True)
            raise

        try:
            qrcode = Qrcode.objects.create(
                owner=business,
                uri='/'.join([
                    settings.BASE_URL,
                    'id',
                    business.id,
                    ''
                ]),
                qrcode_type=QrcodeTypes.PROFILE
            )

        except:
            business.delete(hard=True)
            relation_manager.delete(hard=True)
            raise

        try:
            user_information = UserInformation.objects.get(
                user=KnotisUser.objects.get_identity_user(individual)
            )
            user_information.default_identity_id = business.id
            user_information.save()

        except Exception, e:
            # This is non-critical, no need to reraise
            logger.exception(e.message)

        try:
            establishment = IdentityApi.create_establishment(
                business_id=business.pk,
                **kwargs
            )

        except:
            business.delete(hard=True)
            relation_manager.delete(hard=True)
            qrcode.delete(hard=True)
            raise

        return business, establishment


class IdentityApiView(ApiView):
    api_version = 'v1'
    api_path = 'identity/identity'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        try:
            instance = IdentityApi.create_identity(
                **dict(request.DATA.iteritems())
            )

        except ValidationError, e:
            logger.exception(e.message)
            errors['no-field'] = e.message
            errors.update(e.field_errors)

        except Exception, e:
            instance = None
            logger.exception(
                'An Exception occurred during identity creation'
            )
            errors['no-field'] = e.message

        warnings.warn("deprecated", DeprecationWarning)

        return self.generate_ajax_response(instance, errors)

    def put(
        self,
        request,
        noun='identity',
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        noun = noun.lower()

        update_id = request.DATA.get('id')

        try:

            identity = Identity.objects.get(pk=update_id)

        except Exception, e:
            message = ''.join([
                'Failed to get ',
                noun,
                ' to update.'
            ])
            logger.exception(message)
            errors['no-field'] = message

            return self.generate_ajax_response({
                'message': e.message,
                'errors': errors
            })

        form = IdentityForm(
            data=request.DATA,
            instance=identity
        )

        if not form.is_valid():
            for field, messages in form.errors.iteritems():
                errors[field] = [m for m in messages]

            data['message'] = ''.join([
                'An error occurred during ',
                noun,
                ' update.'
            ])
            data['errors'] = errors
            return self.generate_ajax_response(data)

        try:
            identity = form.save()

        except Exception, e:
            message = ''.join([
                'An error occurred while updating ',
                noun,
                '.'
            ])
            logger.exception(message)
            errors['no-field']  = e.message

            return self.generate_ajax_response({
                'message': message,
                'errors': errors
            })

        try:
            EndpointIdentity.objects.update_identity_endpoints(identity)

        except Exception, e:
            message = ''.join([
                'An error occurred while updating ',
                noun,
                '.'
            ])
            logger.exception(message)
            errors['no-field']  = e.message

            return self.generate_ajax_response({
                'message': message,
                'errors': errors
            })

        data['data'] = {
            noun + '_id': identity.id,
            noun + '_name': identity.name
        }

        data['message'] = ''.join([
            noun.capitalize(),
            ' updated successfully.'
        ])

        warnings.warn("deprecated", DeprecationWarning)

        return self.generate_ajax_response(data)


class IdentityIndividualApiView(IdentityApiView):
    api_version = 'v1'
    api_path = 'identity/individual'


    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        try:
            individual = IdentityApi.create_individual(
                **dict(request.DATA.iteritems())
            )

        except ValidationError, e:
            logger.exception(e.message)
            errors['no-field'] = e.message
            errors.update(e.field_errors)

        except Exception, e:
            logger.exception(e.message)
            errors['no-field'] = e.message

        if errors:
            return self.generate_ajax_response({
                'status': 'ERROR',
                'errors': errors
            })

        data['data'] = {
            'individual_id': individual.id,
            'individual_name': individual.name
        }

        data['message'] = 'Individual created successfully'

        warnings.warn("deprecated", DeprecationWarning)
        return self.generate_ajax_response(data)

    def put(
        self,
        request,
        *args,
        **kwargs
    ):

        warnings.warn("deprecated", DeprecationWarning)
        return super(IdentityIndividualApiView, self).put(
            request,
            noun='individual',
            *args,
            **kwargs
        )

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        pass

    def delete(
        self,
        request,
        *args,
        **kwargs
    ):
        pass


class IdentityBusinessApiView(IdentityApiView):
    api_version = 'v1'
    api_path = 'identity/business'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        try:
            business, establishment = IdentityApi.create_business(
                **dict(request.DATA.iteritems())
            )
            request.session['current_identity_id'] = business.id

        except ValidationError, e:
            logger.exception(e.message)
            errors['no-field'] = e.message
            errors.update(e.field_errors)

        except Exception, e:
            logger.exception(e.message)
            errors['no-field'] = e.message

        if errors:
            return self.generate_ajax_response({
                'status': 'ERROR',
                'errors': errors
            })

        data['data'] = {
            'business_id': business.id,
            'business_name': business.name,
            'establishment_id': establishment.id,
            'establishment_name': establishment.name
        }

        data['message'] = 'Business created successfully'

        warnings.warn("deprecated", DeprecationWarning)
        return self.generate_ajax_response(data)

    def put(
        self,
        request,
        *args,
        **kwargs
    ):

        warnings.warn("deprecated", DeprecationWarning)
        return super(IdentityBusinessApiView, self).put(
            request,
            noun='business',
            *args,
            **kwargs
        )


class IdentityEstablishmentApiView(IdentityApiView):
    api_version = 'v1'
    api_path = 'identity/establishment'


    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        try:
            establishment = IdentityApi.create_establishment(
                **dict(request.DATA.iteritems())
            )

        except ValidationError, e:
            logger.exception(e.message)
            errors['no-field'] = e.message
            errors.update(e.field_errors)

        except Exception, e:
            logger.exception(e.message)
            errors['no-field'] = e.message

        if errors:
            return self.generate_ajax_response({
                'status': 'ERROR',
                'errors': errors
            })

        data['data'] = {
            'establishment_id': establishment.id,
            'establishment_name': establishment.name,
            'establishment_backend_name': establishment.backend_name
        }

        data['message'] = 'Establishment created successfully'

        warnings.warn("deprecated", DeprecationWarning)
        return self.generate_ajax_response(data)

    def put(
        self,
        request,
        *args,
        **kwargs
    ):

        warnings.warn("deprecated", DeprecationWarning)
        return super(IdentityEstablishmentApiView, self).put(
            request,
            noun='establishment',
            *args,
            **kwargs
        )


class IdentityApiModelViewSet(ApiModelViewSet):
    api_path = 'identity'
    resource_name = 'identity'

    model = Identity
    queryset = Identity.objects.all()
    serializer_class = IdentitySerializer

    def list(
        self,
        request
    ):
        raise MethodNotAllowed(request.method)

    def update(
        self,
        request,
        noun='identity',
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        noun = noun.lower()

        update_id = request.DATA.get('id')

        try:

            identity = Identity.objects.get(pk=update_id)

        except Exception, e:
            message = ''.join([
                'Failed to get ',
                noun,
                ' to update.'
            ])
            logger.exception(message)
            errors['no-field'] = message

            raise self.IdentityNotFound(e.message)

        form = IdentityForm(
            data=request.DATA,
            instance=identity
        )

        if not form.is_valid():
            for field, messages in form.errors.iteritems():
                errors[field] = [m for m in messages]

            data['message'] = ''.join([
                'An error occurred during ',
                noun,
                ' update.'
            ])
            data['errors'] = errors
            raise self.IdentityValidationException(data['message'])

        try:
            identity = form.save()

        except Exception, e:
            message = ''.join([
                'An error occurred while updating ',
                noun,
                '.'
            ])
            logger.exception(message)
            errors['no-field']  = e.message
            raise self.IdentityUpdatingException(message)

        try:
            EndpointIdentity.objects.update_identity_endpoints(identity)

        except Exception, e:
            message = ''.join([
                'An error occurred while updating ',
                noun,
                '.'
            ])
            logger.exception(message)
            errors['no-field']  = e.message
            raise self.EndpointUpdateException(message)

        data['data'] = {
            noun + '_id': identity.id,
            noun + '_name': identity.name
        }

        data['message'] = ''.join([
            noun.capitalize(),
            ' updated successfully.'
        ])

        serialize = self.serializer_class(identity)
        return Response(serialize.data)

    class IdentityNotFound(APIException):
        status_code = '500'
        default_detail = 'The identity requested is not available.'

    class IdentityValidationException(APIException):
        status_code = '500'
        default_detail = 'The identity did not validate correctly.'

    class IdentityUpdatingException(APIException):
        status_code = '500'
        default_detail = 'The identity did not update correctly.'

    class EndpointUpdateException(APIException):
        status_code = '500'
        default_detail = 'The identity endpoint did not update correctly.'


class BusinessApiModelViewSet(IdentityApiModelViewSet, GetCurrentIdentityMixin):
    api_path = 'identity/business'
    resource_name = 'business'

    model = Identity
    queryset = Identity.objects.filter(
        identity_type=IdentityTypes.BUSINESS,
        available=True
    )
    serializer_class = BusinessSerializer

    def initial(self, request, *args, **kwargs):
        super(BusinessApiModelViewSet, self).initial(request, *args, **kwargs)
        self.get_current_identity(request)

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        try:
            business, establishment = IdentityApi.create_business(
                **dict(request.DATA.iteritems())
            )

            request.session['current_identity_id'] = business.id

        except ValidationError, e:
            logger.exception(e.message)
            errors['no-field'] = e.message
            errors.update(e.field_errors)

        except Exception, e:
            logger.exception(e.message)
            errors['no-field'] = e.message

        if errors:
            return self.generate_ajax_response({
                'status': 'ERROR',
                'errors': errors
            })

        data['data'] = {
            'business_id': business.id,
            'business_name': business.name,
            'establishment_id': establishment.id,
            'establishment_name': establishment.name
        }

        data['message'] = 'Business created successfully'

        serialize = self.serializer_class(business)
        return Response(serialize.data)


class IndividualApiModelViewSet(IdentityApiModelViewSet):
    api_path = 'identity/individual'
    resource_name = 'individual'

    model = Identity
    queryset = Identity.objects.filter(
        identity_type=IdentityTypes.INDIVIDUAL,
        available=True
    )
    serializer_class = IndividualSerializer


class EstablishmentApiModelViewSet(IdentityApiModelViewSet):
    api_path = 'identity/establishment'
    resource_name = 'establishment'

    model = Identity
    queryset = Identity.objects.filter(
        identity_type=IdentityTypes.ESTABLISHMENT,
        available=True
    )
    serializer_class = EstablishmentSerializer


class IdentitySwitcherApiViewSet(ApiViewSet):
    api_path = 'identity/switcher'
    resource_name = 'switcher'

    def retrieve(
        self,
        request,
        pk=None
    ):
        raise MethodNotAllowed(request.method)

    def list(
        self,
        request
    ):
        try:
            available_identities = Identity.objects.get_available(request.user)

        except:
            available_identities = Identity.objects.none()

        serializer = IdentitySwitcherSerializer(
            available_identities,
            many=True
        )
        return Response(serializer.data)

    def update(
        self,
        request,
        pk=None
    ):
        try:
            available_identities = Identity.objects.get_available(
                user=request.user
            )
            identity = None
            for i in available_identities:
                if i.id == pk:
                    identity = i
                    break

            if not identity:
                msg = ''.join([
                    'identity {',
                    pk,
                    '} is not available to user {',
                    request.user.id,
                    '}'
                ])
                logger.warning(msg)
                raise self.IdentityNotAvailableException(msg)

            user_information = UserInformation.objects.get(user=request.user)
            user_information.default_identity_id = identity.pk
            user_information.save()

            serializer = IdentitySwitcherSerializer(identity)
            return Response(serializer.data)

        except Exception, e:
            logger.exception(
                e.message
            )
            raise

    class IdentityNotAvailableException(APIException):
        status_code = '500'
        default_detail = 'The identity requested is not available.'
