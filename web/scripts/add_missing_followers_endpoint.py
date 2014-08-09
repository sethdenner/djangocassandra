from django.utils.log import logging
logger = logging.getLogger(__name__)


def add_missing_followers_endpoint_to_identity(identity):
    from knotis.contrib.endpoint.models import (
        Endpoint,
        EndpointTypes
    )

    existing = Endpoint.objects.filter(
        endpoint_type=EndpointTypes.FOLLOWERS,
        identity=identity
    )

    if len(existing):
        return existing[0]

    followers = Endpoint.objects.create(
        endpoint_type=EndpointTypes.FOLLOWERS,
        value=' '.join([
            identity.name,
            'Followers'
        ]),
        identity=identity
    )

    return followers


def add_missing_followers_endpoints():
    from knotis.contrib.inventory.models import Identity

    all_identities = Identity.objects.all()
    failed_endpoint_creations = []
    x = 0
    chunk_size = 20
    identity_chunk = all_identities[x:x + chunk_size]

    while len(identity_chunk):
        for i in identity_chunk:
            try:
                add_missing_followers_endpoint_to_identity(i)

                logger.info(''.join([
                    'Successfully created followers endpoint for identity ',
                    i.name,
                    ' (',
                    str(i.identity_type),
                    ').'
                ]))

            except Exception, e:
                logger.exception(e.message)
                failed_endpoint_creations.append({
                    'identity': i,
                    'exception': e
                })

        x += chunk_size
        identity_chunk = all_identities[x:x + chunk_size]

    return failed_endpoint_creations
