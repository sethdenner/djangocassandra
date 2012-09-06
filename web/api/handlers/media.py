from piston.handler import BaseHandler
from piston.utils import validate

from app.models.media import Image
from app.views.media import ImageModelForm

class ImageModelHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    model = Image

    @validate(ImageModelForm, 'POST')
    def create(self, request, *args, **kwargs):
        post_data = request.POST
        file_data = request.FILES

        user = request.user
        image = file_data.get('image')
        related_object_id = post_data.get('related_object_id')
        caption_value = post_data.get('caption_value')

        image = Image.objects.create_image(
            user,
            image,
            caption_value,
            related_object_id
        )

        return image
