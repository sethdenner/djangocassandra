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
    HttpResponseNotFound
)

from knotis.contrib.media.models import Image


class CropForm(ModelForm):
    class Meta:
        model = Image
        fields = (
            'crop_left',
            'crop_top',
            'crop_right',
            'crop_bottom',
            'crop_width',
            'crop_height'
        )
        widgets = {
            'crop_left': HiddenInput(),
            'crop_top': HiddenInput(),
            'crop_right': HiddenInput(),
            'crop_bottom': HiddenInput(),
            'crop_width': HiddenInput(),
            'crop_height': HiddenInput()
        }

    scale_factor = FloatField(widget=HiddenInput(), required=False)

    def save(
        self,
        force_insert=False,
        force_update=False,
        commit=True
    ):
        image = super(CropForm, self).save(commit=False)

        scale_factor = self.cleaned_data.get('scale_factor')
        if scale_factor:
            scale_factor = 1. / scale_factor

            logger.debug('scale factor: %s' % (scale_factor, ))

            image.crop_width = image.crop_width * scale_factor
            image.crop_height = image.crop_height * scale_factor
            image.crop_top = image.crop_top * scale_factor
            image.crop_bottom = image.crop_bottom * scale_factor
            image.crop_right = image.crop_right * scale_factor
            image.crop_left = image.crop_left * scale_factor

            if commit:
                image.save()

        return image


def crop(
    request,
    image_id,
    image_max_width=None,
    image_max_height=None
):
    logger.debug('cropping image %s' % (image_id,))

    try:
        image = Image.objects.get(pk=image_id)
        logger.debug('got image')

    except:
        logger.exception('failded to get image')
        image = None

    if not image:
        return HttpResponseNotFound()

    if request.method.lower() == 'post':
        form = CropForm(
            request.POST,
            instance=image
        )
        # This needs to be ajax style
        saved = False
        if form.is_valid():
            try:
                image = form.save()
                saved = True

            except:
                logger.exception()

        if saved:
            return HttpResponse(
                json.dumps({
                    'status': 'success',
                    'image_id': image.id
                }),
                mimetype='application/json'
            )

        else:
            return HttpResponse(
                json.dumps({'status': 'failure'}),
                mimetype='application/json'
            )

    else:
        form = CropForm(instance=image)

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
                'post_url': ''.join([
                    '/image/crop/',
                    image.id,
                    '/'
                ]),
                'image_dimension': 'x'.join([
                    str(image_width),
                    str(image_height)
                ]),
            }
        )
