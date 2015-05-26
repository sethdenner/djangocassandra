#!/bin/python
from django.utils.log import logging
logger = logging.getLogger(__name__)

def convert_endpoint_contenttype(endpoint):
    from django.contrib.contenttypes.models import ContentType
    from knotis.contrib.endpoint.models import (
        EndpointTypes
    )

    endpoint_typename_map = {
        key: value.lower()
        for key, value in EndpointTypes.CHOICES
    }
    endpoint_type_to_content_type_map = {}
    content_type = endpoint_type_to_content_type_map.get(
        endpoint.endpoint_type
    )
    if None is content_type:
        app_label = 'endpoint'
        model = ''.join([
            'endpoint',
            endpoint_typename_map[
                endpoint.endpoint_type
            ]
        ])
        name = ' '.join([
            'endpoint',
            endpoint_typename_map[
                endpoint.endpoint_type
            ]
        ])
        content_type, _ = ContentType.objects.get_or_create(
            app_label=app_label,
            model=model,
            defaults={'name': name}
        )
        endpoint_type_to_content_type_map[
            endpoint.endpoint_type
        ] = content_type

    endpoint.content_type = content_type
    try:
        endpoint.save()
    except Exception, e:
        logger.error('Failed to convert %s. %s' % (endpoint.pk, e.message))
        pass


def convert_endpoint_contenttypes():
    from knotis.contrib.endpoint.models import (
        Endpoint
    )

    all_endpoints = Endpoint.objects.all()
    for e in all_endpoints:
        convert_endpoint_contenttype(e)
