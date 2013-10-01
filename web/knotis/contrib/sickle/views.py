import json
import math

from django.forms import (
    ModelForm,
    HiddenInput,
    FloatField
)
from django.shortcuts import render
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseServerError
)

from knotis.contrib.identity.models import Identity
from knotis.contrib.media.models import (
    Image,
    ImageInstance
)

from knotis.views import FragmentView


class CropForm(ModelForm):
    class Meta:
        model = ImageInstance
        fields = (
            'owner',
            'image',
            'related_object_id',
            'crop_left',
            'crop_top',
            'crop_width',
            'crop_height'
        )
        widgets = {
            'owner': HiddenInput(),
            'image': HiddenInput(),
            'related_object_id': HiddenInput(),
            'crop_left': HiddenInput(),
            'crop_top': HiddenInput(),
            'crop_width': HiddenInput(),
            'crop_height': HiddenInput()
        }

    '''
    Scale factor is required to take into account any image scaling that
    takes place on the client side while the user is presented with the
    cropping UI.
    '''
    scale_factor = FloatField(widget=HiddenInput(), required=False)

    def __init__(
        self,
        owner,
        image,
        related_object_id,
        *args,
        **kwargs
    ):
        super(CropForm, self).__init__(
            *args,
            **kwargs
        )

        self.fields['owner'].initial = owner
        self.fields['image'].initial = image
        self.fields['related_object_id'].initial = related_object_id

    def save(
        self,
        force_insert=False,
        force_update=False,
        commit=True
    ):
        image_instance = super(CropForm, self).save(commit=False)

        scale_factor = self.cleaned_data.get('scale_factor')
        if scale_factor:
            scale_factor = 1. / scale_factor

            logger.debug('scale factor: %s' % (scale_factor, ))

            image_instance.crop_width = (
                image_instance.crop_width *
                scale_factor
            )
            image_instance.crop_height = (
                image_instance.crop_height *
                scale_factor
            )
            image_instance.crop_top = (
                image_instance.crop_top *
                scale_factor
            )
            image_instance.crop_left = (
                image_instance.crop_left *
                scale_factor
            )

            if commit:
                image_instance.save()

        return image_instance


class CropView(FragmentView):
    pass


def crop(
    request,
    image_id,
    related_object_id,
    image_max_width=None,
    image_max_height=None
):
    logger.debug('cropping image %s' % (image_id,))

    try:
        image = Image.objects.get(pk=image_id)
        logger.debug('got image')

    except:
        logger.exception('failed to get image')
        image = None

    if not image:
        try:
            image_instance = ImageInstance.objects.get(pk=image_id)
            logger.debug('got image instance')

        except:
            logger.exception('failed to get image instance')
            image = None

    else:
        image_instance = None

    if not image and not image_instance:
        return HttpResponseNotFound()

    try:
        current_identity_id = request.session['current_identity_id']
        current_identity = Identity.objects.get(pk=current_identity_id)

    except Exception, e:
        logger.exception('failed to get current identity')
        return HttpResponseServerError(e.message)

    if request.method.lower() == 'post':
        form = CropForm(
            data=request.POST,
            owner=current_identity,
            image=image,
            related_object_id=related_object_id,
            instance=image_instance
        )
        # This needs to be ajax style
        saved = False
        if form.is_valid():
            try:
                saved_instance = form.save()
                saved = True

            except:
                logger.exception()

        if saved:
            try:
                related_object = Identity.objects.get(pk=related_object_id)

            except:
                pass

            if related_object:
                if not related_object.badge_image:
                    related_object.badge_image = saved_instance

                    try:
                        related_object.save()

                    except:
                        logger.exception(
                            'failed to save instance as badge image.'
                        )

            return HttpResponse(
                json.dumps({
                    'status': 'success',
                    'image_id': saved_instance.id
                }),
                mimetype='application/json'
            )

        else:
            return HttpResponse(
                json.dumps({'status': 'failure'}),
                mimetype='application/json'
            )

    else:
        form = CropForm(
            owner=current_identity,
            image=image,
            related_object_id=related_object_id,
            instance=image_instance
        )

        logger.debug(image.image.url)

        if image_max_width and image_max_height:
            image_max_width = int(image_max_width)
            image_max_height = int(image_max_height)

            dw = image.image.width - image_max_width
            dh = image.image.height - image_max_height

            if dw > dh:
                scale_factor = (
                    (image.image.width - dw) / float(image.image.width)
                )

            else:
                scale_factor = (
                    (image.image.height - dh) / float(image.image.height)
                )

        else:
            scale_factor = 1.0

        form.fields['scale_factor'].initial = scale_factor
        image_width = int(math.floor(image.image.width * scale_factor))
        image_height = int(math.floor(image.image.height * scale_factor))

        return render(
            request,
            'crop_box.html', {
                'image': image,
                'form': form,
                'button_text': 'Crop Image',
                'post_url': '/'.join([
                    '/image/crop',
                    image.id,
                    related_object_id,
                    ''
                ]),
                'image_dimension': 'x'.join([
                    str(image_width),
                    str(image_height)
                ]),
            }
        )
