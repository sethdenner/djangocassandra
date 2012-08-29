from django.shortcuts import render_to_response
from django.template.context import RequestContext
from app.models.contents import Content

def index(
    request,
    login
):
    template_parameters = {}
    
    content = {}

    content_set = Content.content_objects.get_template_content('home')
    for c in content_set:
        content[c.name] = c.value
        
    content_set = Content.content_objects.get_template_content('header')
    for c in content_set:
        content[c.name] = c.value
        
    content_set = Content.content_objects.get_template_content('footer')
    for c in content_set:
        content[c.name] = c.value
        
    if 'login' == login:
        content['login'] = True
        
    template_parameters.update(content)
    
    return render_to_response(
        'home.html',
        template_parameters,
        context_instance=RequestContext(request)
    )
