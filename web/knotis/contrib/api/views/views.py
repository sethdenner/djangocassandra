from rest_framework.views import exception_handler


def knotis_exception_handler(exception):
    response = exception_handler(exception)
    if None is not response:
        response.data['status_code'] = response.status_code

    return response
