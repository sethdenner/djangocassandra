import json
from django.http import HttpResponse
from piston.resource import Resource


class JsonResource(Resource):
    def form_validation_response(
        self,
        error
    ):
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        
        error_message = ''
        for field in error.form.visible_fields():
            if field.errors:
                for message in field.errors:
                    error_message += message + ' '
            
        data = {
            'success': 'no',
            'message': error_message
        }

        response.write(json.dumps(data))
        return response
