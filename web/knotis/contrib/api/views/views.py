from rest_framework.views import exception_handler


def knotis_exception_handler(exception, context):
    response = exception_handler(exception, context)
    if None is not response:
        response.data['status_code'] = response.status_code

    return response
