import os

from django.utils import log
logger = log.getLogger(__name__)

from knotis.views import ApiView

from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin

from .models import (
    Image,
    ImageInstance,
)
from .serializers import (
    CroppedImageUrlSerializer,
    # ImageInstanceSerializer,
)

from django.core.files.base import ContentFile


class ImageApi(object):
    @staticmethod
    def import_offer_image_from_path(src, offer):
        # Only left this function because there's a srcipt that uses it.
        image_source = open(src).read()
        return ImageApi.import_image(
            image_source,
            offer.owner,
            name=os.path.basename(src),
        )

    @staticmethod
    def import_image_from_path(src, owner):
        image_source = open(src).read()
        return ImageApi.import_image(
            image_source,
            owner,
            name=os.path.basename(src),
        )

    @staticmethod
    def import_image(
        raw_image_source,
        owner,
        name,
    ):
        image = Image(
            owner=owner,
        )
        path = '/'.join(['images', name])

        image.image.save(
            path,
            ContentFile(raw_image_source)
        )
        image.save()
        return image


class ImageInstanceApi(object):
    @staticmethod
    def delete(instance):
        '''
        This method is for deleting an image instance. If
        there are no more image instances pointing to the image
        that this image instance points to the image itself should
        also be deleted.
        '''
        if not isinstance(instance, ImageInstance):
            instance = ImageInstanceApi.get(instance)

        instance.delete()
        return instance

    @staticmethod
    def get(pk):
        return ImageInstance.objects.get(pk=pk)

    @staticmethod
    def create_offer_image_instance(image, offer):
        return ImageInstance.objects.create(
            owner=offer.owner,
            image=image,
            related_object_id=offer.id,
            context='offer_banner',
            primary=True
        )

    @staticmethod
    def create_image_instance(
        image,
        owner,
        related_object_id=None,
        context=None
    ):
        return ImageInstance.objects.create(
            owner=owner,
            image=image,
            related_object_id=(
                owner.id if related_object_id is None else related_object_id
            ),
            context=context,
            primary=True
        )


class ImageInstanceApiView(ImageInstanceApi, ApiView, GetCurrentIdentityMixin):
    api_path = 'media/imageinstance'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):

        image_upload = request.FILES.get('image', None)
        if image_upload is None:
            raise self.NoImageIncludedException()

        image_source = image_upload.read()

        name = request.DATA.get('name', None)
        current_identity = self.get_current_identity(request)

        try:

            image = ImageApi.import_image(
                image_source,
                current_identity,
                name
            )

        except Exception, e:
            logger.exception(e.message)
            raise self.ImageCreationFailedException()

        related_object_id = request.DATA.get('related_id', current_identity.id)
        context = request.DATA.get('context', 'business_profile_carousel')

        if context != 'business_profile_carousel':
            raise self.PermissionsNotImplmentedException()
        try:
            image_instance = ImageInstanceApi.create_image_instance(
                image,
                current_identity,
                related_object_id,
                context=context
            )

        except Exception, e:
            logger.exception(e.message)
            raise self.ImageInstanceCreationFailedException()

        # related_id = request.DATA.get('related_id', None)
        serializer = CroppedImageUrlSerializer(image_instance)
        return Response(serializer.data, status=200)

    class PermissionsNotImplmentedException(APIException):
        status = status.HTTP_501_NOT_IMPLEMENTED
        default_detail = (
            'Only Support carousel images.'
        )

    class NoImageIncludedException(APIException):
        status_code = 400
        default_detail = (
            'Failed to import image.'
        )

    class ImageCreationFailedException(APIException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        default_detail = (
            'Failed to import image.'
        )

    class ImageInstanceCreationFailedException(APIException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        default_detail = (
            'Failed to create image instance.'
        )

    class PermissionDeniedException(APIException):
        status_code = 500
        default_detail = (
            'You do not have permission to access or modify this resource.'
        )

    def delete(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = self.get_current_identity(request)
        pk = request.DATA.get('pk')

        if not pk:
            return self.generate_ajax_response({
                'status': self.Status.Error,
                'errors': {
                    'pk': self.Errors.FieldRequired
                }
            })

        try:
            instance = ImageInstanceApi.get(pk)

        except Exception, e:
            logger.exception(''.join([
                'Failed to get image instance with pk = ',
                pk
            ]))
            return self.generate_ajax_response({
                'status': 'error',
                'errors': {
                    'no-field': self.Errors.ExceptionThrown,
                    'exception': e.message
                }
            })

        if instance.owner.pk != current_identity.pk:
            return self.generate_ajax_response({
                'status': 'error',
                'errors': {
                    'no-field': self.Errors.PermissionDenied
                }
            })

        try:
            ImageInstanceApi.delete(instance)

        except Exception, e:
            logger.exception(''.join([
                'Failed to delete ImageInstance with pk=',
                pk
            ]))
            return self.generate_ajax_response({
                'status': 'error',
                'errors': {
                    'no-field': self.Errors.ExceptionThrown,
                    'exception': e.message
                }
            })

        return self.generate_ajax_response({
            'status': 'ok',
            'instance': pk
        })
