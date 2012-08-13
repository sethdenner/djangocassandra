from django.shortcuts import render
from app.models.contents import Content

def plans(request):
    template_parameters = {}
    
    content = {}

    content_set = Content.content_objects.get_template_content('plans')
    for c in content_set:
        content[c.name] = c.value
        
    content_set = Content.content_objects.get_template_content('header')
    for c in content_set:
        content[c.name] = c.value
        
    content_set = Content.content_objects.get_template_content('footer')
    for c in content_set:
        content[c.name] = c.value
        
    
    template_parameters.update(content)

    return render(
        request, 
        'plans.html',
        template_parameters
    )
