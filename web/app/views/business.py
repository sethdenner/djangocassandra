from django.contrib.auth.models import User
from django.forms import Form, ModelChoiceField, CharField, URLField
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template.context import RequestContext

from app.models.users import UserProfile
from app.models.contents import Content
from app.utils import User as UserUtils

class CreateBusinessForm(Form):
    user = ModelChoiceField(label="User", queryset=User.objects.all())
    backend_name = CharField(label="Backend Name", max_length=100)
    business_name = CharField(label="Business Name", max_length=100, required=False)
    avatar = URLField(label="Avatar URI.", required=False)
    hours = CharField(label="Business Hours", max_length=100, required=False)


def create_business(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = CreateBusinessForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/thanks/')  # Redirect after POST
    else:
        form = CreateBusinessForm()  # An unbound form

    return render(request, 'create_business.html', {
        'form': form,
    })

    """
    return render_to_response(
        'create_business.html',
        {},
        context_instance=RequestContext(request))
    """

def list_businesses(request):
    return render(request, 'list_businesses.html')


class UpdateBusinessForm(Form):
    name = CharField(label='Name')
    summary = CharField(label='Summary', max_length=140)
    description = CharField(label='Description')
    address = CharField(label='Address')
    phone = CharField(label='Phone')
    twitter_name = CharField(label='Twitter')
    facebook_uri = CharField(label='Facebook')
    yelp_id = CharField(label='Yelp ID')
    

class AddBusinessLinkForm(Form):
    uri = CharField()
    title = CharField()
    
def edit_profile(request):
    template_parameters = {}
    
    content = {}
        
    content_set = Content.content_objects.get_template_content('header')
    for c in content_set:
        content[c.name] = c.value
        
    content_set = Content.content_objects.get_template_content('footer')
    for c in content_set:
        content[c.name] = c.value
        
    template_parameters.update(content)
            
    if request.user.is_authenticated():
        user_profile = UserProfile.objects.get(user=request.user)
        template_parameters['user_profile'] = user_profile
        template_parameters['username_truncated'] = request.user.username[:9] + '...'
        template_parameters['avatar_uri'] = UserUtils.get_avatar(
            request.user.username, 
            None, 
            20
        )
        
    template_parameters['update_form'] = UpdateBusinessForm()
    template_parameters['link_form'] = AddBusinessLinkForm()

    return render(
        request,
        'edit_business_profile.html',
        template_parameters
    )
