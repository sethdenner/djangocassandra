from django.contrib.auth.models import User
from django.forms import Form, ModelChoiceField, CharField, URLField
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template.context import RequestContext


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
