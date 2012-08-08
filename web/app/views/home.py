from django.shortcuts import render_to_response
from django.template.context import RequestContext
from app.models.contents import Content

def index(request):
    template_parameters = {}

    content_set = Content.content_objects.get_template_content('home')
    content = {}
    for c in content_set:
        content[c.name] = c.value;
    
    template_parameters.update(content)
    
    return render_to_response(
        'home.html',
        template_parameters,
        context_instance=RequestContext(request))
