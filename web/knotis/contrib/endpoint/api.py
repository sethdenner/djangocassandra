from django.utils.log import logging
logger = logging.getLogger(__name__)

from models import (
    Endpoint,
    EndpointPhone,
    EndpointYelp,
    EndpointFacebook,
    EndpointTwitter,
    EndpointEmail,
    EndpointTypes,
    EndpointWebsite
)

from knotis.contrib.identity.models import (
    Identity
)

from knotis.views import ApiView

get_class = lambda x: globals()[x]

class EndpointApi(ApiView):
    api_url = 'endpoint'
    
    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return self.generate_response({
            data: {'something': None}
        })

    def post(
        self,
        request,
        *args,
        **kwargs
    ):

        errors = {}
        
        try:
            identity_id = request.POST.get('identity_id')
            endpoint_type = request.POST.get('endpoint_type')
            value = request.POST.get('value')

            if not identity_id:
                raise Exception('no identity_id supplied')
            if not endpoint_type:
                raise Exception('no endpoint_type supplied')
            if endpoint_type not in ('phone', 'email', 'facebook', 'twitter', 'yelp', 'website'):
                raise Exception('invalid endpoint_type')
            if not value:
                raise Exception('no value supplied')
            
            endpoint_id = request.POST.get('endpoint_id')
            
            EndpointClass = get_class('Endpoint' + endpoint_type.capitalize())

            if endpoint_id:
                endpoint = EndpointClass.objects.get(endpoint_id)
            else:
                endpoint = EndpointClass.objects.create(
                    endpoint_type=getattr(EndpointTypes, endpoint_type.upper()),
                    identity=Identity.objects.filter(id=identity_id)[0],
                    value='',
                    primary=True
                )

            endpoint.value = value.strip()
            endpoint.save()
            endpoint.clean()
            endpoint.save()

            return self.generate_response({
                'errors': errors
            })

        except Exception, e:
            errors['no-field'] = '%s %s' % ( e.__class__, e.message )
            return self.generate_response({
                'errors': errors,
                'data': {}
            })

