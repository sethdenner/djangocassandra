import os

from django.utils import log
logger = log.getLogger(__name__)

from knotis.views import ApiView

from knotis.contrib.identity.views import get_current_identity

from .models import (
    Image,
    ImageInstance,
)

from django.core.files.base import ContentFile


class ImageApi(object):
    @staticmethod
    def import_offer_image(src, offer):

        image_source = open(src).read()
        image = Image(
            owner=offer.owner,
        )
        image.image.save(
            os.path.join('images', os.path.basename(src)),
            ContentFile(image_source)
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
        ImageInstance.objects.create(
            owner=offer.owner,
            image=image,
            related_object_id=offer.id,
            context='offer_banner',
            primary=True
        )


class ImageApiView(ImageApi, ApiView):
    api_path = 'media/image'


class ImageInstanceApiView(ImageInstanceApi, ApiView):
    api_path = 'media/imageinstance'

    def delete(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_current_identity(request)
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
