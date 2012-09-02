from django.contrib.auth.models import User
from django.forms import Form, ModelChoiceField, CharField, URLField
from django.http import HttpResponseRedirect
from django.shortcuts import render

from app.models.users import UserProfile
from app.models.contents import Content
from app.models.businesses import Business
from app.utils import User as UserUtils
from app.utils import View as ViewUtils

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
    summary = CharField(label='Summary', max_length=140, required=False)
    description = CharField(label='Description', required=False)
    address = CharField(label='Address', required=False)
    phone = CharField(label='Phone', required=False)
    twitter_name = CharField(label='Twitter', required=False)
    facebook_uri = CharField(label='Facebook', required=False)
    yelp_id = CharField(label='Yelp ID', required=False)
    

class AddBusinessLinkForm(Form):
    uri = CharField()
    title = CharField()

    
def edit_profile(request):
    update_form = None
    link_form = None
    
    business = None
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        pass #fine
    except:
        pass #fatal
    
    if request.method.lower() == 'post':
        update_form = UpdateBusinessForm(request.POST)                
        if update_form.is_valid():
            if business:
                business.update(
                    **update_form.cleaned_data
                )
            else:
                business = Business.objects.create_business(
                    request.user, 
                    **update_form.cleaned_data
                )
    
    template_parameters = ViewUtils.get_standard_template_parameters(request)
                    
    if not update_form:
        if business:
            business_values = {
                'name': business.business_name.value,
                'summary': business.summary.value,
                'description': business.description.value,
                'address': business.address.value.value,
                'phone': business.phone.value.value,
                'twitter_name': business.twitter_name.value.value,
                'facebook_uri': business.facebook_uri.value.value,
                'yelp_id': business.yelp_id.value.value
            }
            update_form = UpdateBusinessForm(business_values)
        else:
            update_form = UpdateBusinessForm()

    template_parameters['business'] = business
    template_parameters['update_form'] = update_form
    template_parameters['link_form'] = link_form if link_form else AddBusinessLinkForm()

    return render(
        request,
        'edit_business_profile.html',
        template_parameters
    )
    
def qrcode(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    
    return render(
        request,
        'manage_qrcode.html',
        template_parameters
    )

def tickets(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    
    template_parameters['user_profile'] = UserProfile.objects.get(user=request.user)
    
    return render(
        request,
        'manage_tickets.html',
        template_parameters
    )
