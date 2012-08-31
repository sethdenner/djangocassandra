from django.shortcuts import render_to_response
from django.template.context import RequestContext
from app.models.contents import Content
from app.utils import User as UserUtils
from app.models.users import UserProfile

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
        
    template_parameters.update(content)
    
    if 'login' == login:
        template_parameters['login'] = True
        
    if request.user.is_authenticated():
        user_profile = UserProfile.objects.get(user=request.user)
        template_parameters['user_profile'] = user_profile
        template_parameters['username_truncated'] = request.user.username[:9] + '...'
        template_parameters['avatar_uri'] = UserUtils.get_avatar(
            request.user.username, 
            None, 
            20
        )
        
    return render_to_response(
        'home.html',
        template_parameters,
        context_instance=RequestContext(request)
    )
