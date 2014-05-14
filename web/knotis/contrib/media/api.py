from django.utils import log
logger = log.getLogger(__name__)

from knotis.views import ApiView

from knotis.contrib.identity.views import get_current_identity

from .models import ImageInstance


class ImageApi(object):
    pass


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
        pk = request.DELETE.get('pk')

        if not pk:
            return self.generate_response({
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
            return self.generate_response({
                'status': self.Status.Error,
                'errors': {
                    'no-field': self.Errors.ExceptionThrown,
                    'exception': e.message
                }
            })

        if instance.owner.pk != current_identity.pk:
            return self.generate_response({
                'status': self.Status.Error,
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
            return self.generate_response({
                'status': self.Status.Error,
                'errors': {
                    'no-field': self.Errors.ExceptionThrown,
                    'exception': e.message
                }
            })

        return self.generate_response({
            'status': self.Status.Ok,
            'instance': pk
        })
