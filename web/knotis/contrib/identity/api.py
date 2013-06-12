from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import ApiView
from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.relation.models import Relation

from models import (
    Identity,
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment
)
from forms import IdentityForm


class IdentityApi(ApiView):
    model = Identity
    api_url = 'identity'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        form = IdentityForm(
            data=request.POST
        )

        if form.is_valid():
            try:
                instance = form.save()

            except Exception, e:
                instance = None
                logger.exception(
                    'An Exception occurred during identity creation'
                )
                errors['no-field'] = e.message

        else:
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

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
    model = IdentityIndividual
    api_url = 'individual'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        form = IdentityForm(
            data=request.POST
        )

        if not form.is_valid():
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            data['message'] = (
                'An error occurred during individual creation.'
            )
            data['errors'] = errors
            return self.generate_response(data)

        try:
            individual = form.save()

        except Exception, e:
            message = 'An error occurred during individual creation.'
            logger.exception(message)
            errors['no-field']  = e.message

            return self.generate_response({
                'message': message,
                'errors': errors
            })

        user = None
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                user = KnotisUser.objects.get(pk=user_id)

            except Exception, e:
                individual.delete()

                message = 'User does not exist.'
                logger.exception(message)
                errors['no-field'] = e.message
                return self.generate_response({
                    'message': message,
                    'errors': errors
                })

            try:
                Relation.objects.create_individual(
                    user,
                    individual
                )

            except Exception, e:
                individual.delete()
                message = (
                    'An error occurred during individual '
                    'relation creation.'
                )
                logger.exception(message)
                errors['no-field'] = e.message

                return self.generate_response({
                    'message': message,
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
    model = IdentityBusiness
    api_url = 'business'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        form = IdentityForm(
            data=request.POST
        )

        if not form.is_valid():
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            data['message'] = (
                'An error occurred during business creation.'
            )
            data['errors'] = errors
            return self.generate_response(data)

        try:
            business = form.save()

        except Exception, e:
            message = 'An error occurred during business creation.'
            logger.exception(message)
            errors['no-field']  = e.message

            return self.generate_response({
                'message': message,
                'errors': errors
            })

        individual = None
        individual_id = request.POST.get('individual_id')
        if individual_id:
            try:
                individual = IdentityIndividual.objects.get(
                    pk=individual_id
                )

            except Exception, e:
                business.delete()

                message = 'Individual does not exist.'
                logger.exception(message)
                errors['no-field'] = e.message
                return self.generate_response({
                    'message': message,
                    'errors': errors
                })

            try:
                Relation.objects.create_manager(
                    individual,
                    business
                )

            except Exception, e:
                business.delete()
                message = (
                    'An error occurred during manager '
                    'relation creation.'
                )
                logger.exception(message)
                errors['no-field'] = e.message

                return self.generate_response({
                    'message': message,
                    'errors': errors
                })

        data['data'] = {
            'business_id': business.id,
            'business_name': business.name
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
    model = IdentityEstablishment
    api_url = 'establishment'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        form = IdentityForm(
            data=request.POST
        )

        if not form.is_valid():
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            data['message'] = (
                'An error occurred during business creation.'
            )
            data['errors'] = errors
            return self.generate_response(data)

        try:
            establishment = form.save()

        except Exception, e:
            message = 'An error occurred during establishment creation.'
            logger.exception(message)
            errors['no-field']  = e.message

            return self.generate_response({
                'message': message,
                'errors': errors
            })

        business = None
        business_id = request.POST.get('business_id')
        if business_id:
            try:
                business = IdentityBusiness.objects.get(
                    pk=business_id
                )

            except Exception, e:
                establishment.delete()

                message = 'Business does not exist.'
                logger.exception(message)
                errors['no-field'] = e.message
                return self.generate_response({
                    'message': message,
                    'errors': errors
                })

            try:
                Relation.objects.create_establishment(
                    business,
                    establishment
                )

            except Exception, e:
                establishment.delete()
                message = (
                    'An error occurred during establishment '
                    'relation creation.'
                )
                logger.exception(message)
                errors['no-field'] = e.message

                return self.generate_response({
                    'message': message,
                    'errors': errors
                })

        data['data'] = {
            'establishment_id': establishment.id,
            'establishment_name': establishment.name
        }

        data['message'] = 'Establishment created successfully'
        return self.generate_response(data)

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(IdentityBusinessApi, self).put(
            request,
            noun='establishment',
            *args,
            **kwargs
        )
