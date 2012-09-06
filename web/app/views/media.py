from PIL import Image
from app.models.images import Image as KnotisImage

def get_image_response(
    image_id,
    width,
    height
):
    pass

def get(
    request,
    media_type,
    media_id,
    width=None,
    height=None
):
    if media_type == 'image':
        return get_image_response(
            media_id,
            width,
            height
        )
