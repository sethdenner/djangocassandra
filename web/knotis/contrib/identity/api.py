from django.conf import settings
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.core.exceptions import ValidationError

from knotis.views import ApiView
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

from models import (
    Identity,
    IdentityIndividual,
    IdentityBusiness,
    IdentityTypes
)
from forms import (
    IdentityForm,
    IdentityIndividualForm,
    IdentityBusinessForm,
    IdentityEstablishmentForm
)


class IdentityApi(ApiView):
    api_url = 'identity/identity'

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

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        try:
            instance = self.create_identity(
                **dict(request.POST.iteritems())
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

        return self.generate_response(instance, errors)

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

        update_id = request.PUT.get('id')

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

            return self.generate_response({
                'message': e.message,
                'errors': errors
            })

        form = IdentityForm(
            data=request.PUT,
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
            return self.generate_response(data)

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

            return self.generate_response({
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

            return self.generate_response({
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

        return self.generate_response(data)


class IdentityIndividualApi(IdentityApi):
    api_url = 'identity/individual'

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

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        try:
            individual = self.create_individual(
                **dict(request.POST.iteritems())
            )

        except ValidationError, e:
            logger.exception(e.message)
            errors['no-field'] = e.message
            errors.update(e.field_errors)

        except Exception, e:
            logger.exception(e.message)
            errors['no-field'] = e.message

        if errors:
            return self.generate_response({
                'status': 'ERROR',
                'errors': errors
            })

        data['data'] = {
            'individual_id': individual.id,
            'individual_name': individual.name
        }

        data['message'] = 'Individual created successfully'
        return self.generate_response(data)

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(IdentityIndividualApi, self).put(
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


class IdentityBusinessApi(IdentityApi):
    api_url = 'identity/business'

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
            establishment = IdentityEstablishmentApi.create_establishment(
                business_id=business.pk,
                **kwargs
            )

        except:
            business.delete(hard=True)
            relation_manager.delete(hard=True)
            qrcode.delete(hard=True)
            raise

        return business, establishment

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        try:
            business, establishment = self.create_business(
                **dict(request.POST.iteritems())
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
            return self.generate_response({
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
        return self.generate_response(data)

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(IdentityBusinessApi, self).put(
            request,
            noun='business',
            *args,
            **kwargs
        )


class IdentityEstablishmentApi(IdentityApi):
    api_url = 'identity/establishment'

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

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        try:
            establishment = self.create_establishment(
                **dict(request.POST.iteritems())
            )

        except ValidationError, e:
            logger.exception(e.message)
            errors['no-field'] = e.message
            errors.update(e.field_errors)

        except Exception, e:
            logger.exception(e.message)
            errors['no-field'] = e.message

        if errors:
            return self.generate_response({
                'status': 'ERROR',
                'errors': errors
            })

        data['data'] = {
            'establishment_id': establishment.id,
            'establishment_name': establishment.name,
            'establishment_backend_name': establishment.backend_name
        }

        data['message'] = 'Establishment created successfully'
        return self.generate_response(data)

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(IdentityEstablishmentApi, self).put(
            request,
            noun='establishment',
            *args,
            **kwargs
        )
