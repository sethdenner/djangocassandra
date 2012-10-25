import json

from django.forms import (
    ModelForm,
    HiddenInput,
    IntegerField
)
from django.shortcuts import render
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.http import (
    HttpResponse,
    HttpResponseNotFound
)

from knotis.apps.media.models import Image


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
            

def crop(
    request,
    image_id
):
    logger.debug('cropping image %s' %(image_id,))
    
    try:
        image = Image.objects.get(pk=image_id)
        logger.debug('got image')
        
    except:
        logger.debug('failded to get image')
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
                ])
            }
        )
