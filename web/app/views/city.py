from django.http import HttpResponse

from app.models.neighborhoods import Neighborhood

def get_neighborhoods(request, city=None):
    neighborhoods = None
    if not city:
        neighborhoods = Neighborhood.objects.all()
    else:
        neighborhoods = Neighborhood.objects.filter(city=city)

    option_template = '<option value="%s" >%s</option>\n'
    response = ''
    for neighborhood in neighborhoods:
        response += option_template % (neighborhood.id, neighborhood.name.value)

    if not response:
        response = '<option value="-1">All the City</option>'

    return HttpResponse(response)
