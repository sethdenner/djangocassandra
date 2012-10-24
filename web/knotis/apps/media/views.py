import posixpath
import urllib
import os
import json

from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.views.static import serve
from django.forms import (
    ModelForm,
    CharField
)
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect
)
from django.core.files.base import ContentFile

from knotis.apps.media.models import Image
from knotis.apps.business.models import Business


def render_image_list(
    options,
    request=None
):
    default_options = {
        'dimensions': '35x19'
    }
    default_options.update(options)
    options = default_options

    if request:
        return render(
            request,
            'image_list.html',
            options
        )
        
    else:
        context = Context(options)
        image_list = get_template('image_list.html')
        return image_list.render(context)
    

def get_image_row(
    request,
    image_id
):
    try:
        image = Image.objects.get(pk=image_id)
    
    except:
        logger.exception('failed to get image')
        
    if not image:
        return HttpResponseNotFound(
            'Could not find image with id %s' % (image_id, )
        )
        
    return render_image_list(
        {'images': [image]},
        request
    )

def get_image_list(
    request,
    related_object_id
):
    try: 
        images = Image.objects.filter(related_object_id=related_object_id)
        
    except:
        logger.exception()
        
    if not images:
        return HttpResponseNotFound(
            'No images found for related_object_id %s' % (related_object_id, )
        )
        
    try:
        related_object = Business.objects.get(pk=related_object_id)
        
    except:
        logger.exception()
        related_object = None
        
    options = {
        'images': images,
        'business': related_object
    }
        
    return render_image_list(
        options,
        request
    )


class ImageModelForm(ModelForm):
    class Meta:
        model = Image
        exclude = (
            'user',
            'caption'
        )

    caption_value = CharField(max_length=1024, required=False)
    related_object_id = CharField(max_length=36, required=False)

    def save_image(
        self,
        request,
        image=None
    ):
        if image:
            image.update(
                self.cleaned_data['image'],
                self.cleaned_data['caption_value']
            )


def _get(request):
    return HttpResponse()


def _upload(request):
    image_source = request.raw_post_data
    object_id = request.GET.get('id')
    name = request.GET.get('qqfile')
    response = {}
    try:
        image = Image(
            user=request.user,
            related_object_id=object_id
        )
        image.image.save(
            '/'.join([
                'images',
                name
            ]),
            ContentFile(image_source)
        )
        image.save()

        response['success'] = 'true'
        response['image_id'] = image.id

    except Exception, error:
        response['success'] = 'false'
        response['message'] = 'File upload failed.'

    return HttpResponse(
        json.dumps(response),
        content_type='application/json'
    )


def ajax(request):
    if request.method.lower() == 'post':
        return _upload(request)
    else:
        return _get(request)


USE_XSENDFILE = getattr(settings, 'USE_XSENDFILE', False)


def xsendfileserve(request, path, document_root=None):
    """
    Serve static files using X-Sendfile below a given point 
    in the directory structure.

    This is a thin wrapper around Django's built-in django.views.static,
    which optionally uses USE_XSENDFILE to tell webservers to send the
    file to the client. This can, for example, be used to enable Django's
    authentication for static files.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', login_required(xsendfileserve), 
                            {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """

    if USE_XSENDFILE:
        # Clean up given path to only allow serving files below document_root.
        path = posixpath.normpath(urllib.unquote(path))
        path = path.lstrip('/')
        newpath = ''
        for part in path.split('/'):
            if not part:
                # Strip empty path components.
                continue
            drive, part = os.path.splitdrive(part)
            head, part = os.path.split(part)
            if part in (os.curdir, os.pardir):
                # Strip '.' and '..' in path.
                continue
            newpath = os.path.join(newpath, part).replace('\\', '/')
        if newpath and path != newpath:
            return HttpResponseRedirect(newpath)
        fullpath = os.path.join(document_root, newpath)

        # This is where the magic takes place.
        response = HttpResponse()
        response['X-Sendfile'] = fullpath
        # Unset the Content-Type as to allow for the webserver
        # to determine it.
        response['Content-Type'] = ''

        return response

    return serve(request, path, document_root)
