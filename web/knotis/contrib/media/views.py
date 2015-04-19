import posixpath
import urllib
import os
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import (
    Context,
)
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
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponseServerError
)

from knotis.views import FragmentView

from .models import Image
from .api import ImageApi
from knotis.contrib.identity.models import Identity


class ImageUploadView(FragmentView):
    template_name = 'knotis/media/image_upload.html'
    view_name = 'image_upload'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        object_id = request.GET.get('object_id')
        return render(
            request,
            self.template_name, {
                'object_id': object_id
            }
        )


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


@login_required
def delete_image(
    request,
    image_id
):
    if request.method.lower() != 'post':
        return HttpResponseBadRequest('Method must be post.')

    try:
        image = Image.objects.get(pk=image_id)

    except:
        image = None

    if not image:
        return HttpResponseNotFound('Image not found')

    if image.user.id != request.user.id:
        return HttpResponseBadRequest('Image does not belong to user!')

    try:
        image.delete()

    except Exception, error:
        return HttpResponseServerError(error)

    return HttpResponse('OK')


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


def _upload(request):
    image_source = request.raw_post_data
    name = request.GET.get('qqfile')
    response = {}
    try:
        identity = Identity.objects.get(
            pk=request.session['current_identity']
        )
        image = ImageApi.import_image(
            image_source,
            identity,
            name
        )

        response['success'] = 'true'
        response['image_id'] = image.id

    except Exception, e:
        logger.exception('File upload failed. %s' % e.message)

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
        return HttpResponse()


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
