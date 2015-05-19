from django.utils.log import logging
logger = logging.getLogger(__name__)

def add_missing_followers_endpoint_to_identity(identity):
    from knotis.contrib.endpoint.models import (
        EndpointFollowers,
        EndpointTypes
    )

    existing = EndpointFollowers.objects.filter(
        identity=identity
    )

    if len(existing):
        return existing[0]

    followers = EndpointFollowers.objects.create(
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
