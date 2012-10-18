from django.forms import (
    ModelForm,
    HiddenInput,
    IntegerField
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
            
    def save(
        self,
        request,
        image_id
    ):
        try:
            pass
            
        except:
            pass
    

def crop(
    request,
    image_id
):
    try:
        image = Image.objects.get(pk=image_id)
        
    except:
        image = None
        
    if not image:
        return

    if request.method.lower() == 'post':
        form = CropForm(
            request.POST,
            instance=image
        )
        if form.is_valid():
            pass
        
        else:
            # Handle Errors
            pass
        
    else:
        form = CropForm(instance=Image)
    