from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.forms import ModelForm, CharField, ImageField, DateTimeField
from app.models.offers import Offer
from app.models.businesses import Business

from app.utils import View as ViewUtils


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        exclude = (
            'establishment',
            'offer_type',
            'title',
            'description',
            'restrictions',
            'address',
            'image',
            'purchased',
            'published',
            'pub_date'
        )

    title_value = CharField(max_length=128, initial='Food and Drinks')
    description_value = CharField(max_length=1024, initial='Description')
    restrictions_value = CharField(max_length=1024, initial='Restrictions')
    address_value = CharField(max_length=256)
    start_date = DateTimeField(initial='Start Date')
    end_date = DateTimeField(initial='End Date')
    image_source = ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']
        if None != instance:
            self.fields['description_value'].initial = instance.description.value
            self.fields['title_value'].initial = instance.title.value
            self.fields['restrictions_value'].initial = instance.restrictions.value
            self.fields['address_value'].initial = instance.address.value.value


    def save_offer(
        self,
        request,
        offer=None
    ):
        business = Business.objects.get(user=request.user)

        published = 'Publish' in request.POST

        if offer:
            offer.update(
                self.cleaned_data['title_value'],
                self.cleaned_data['title_type'],
                self.cleaned_data['description_value'],
                self.cleaned_data['restrictions_value'],
                self.cleaned_data['city'],
                self.cleaned_data['neighborhood'],
                self.cleaned_data['address_value'],
                self.cleaned_data['image_source'],
                self.cleaned_data['category'],
                self.cleaned_data['price_retail'],
                self.cleaned_data['price_discount'],
                self.cleaned_data['start_date'],
                self.cleaned_data['end_date'],
                self.cleaned_data['stock'],
                self.cleaned_data['unlimited'],
                published
            )
        else:
            Offer.objects.create_offer(
                request.user,
                business,
                self.cleaned_data['title_value'],
                self.cleaned_data['title_type'],
                self.cleaned_data['description_value'],
                self.cleaned_data['restrictions_value'],
                self.cleaned_data['city'],
                self.cleaned_data['neighborhood'],
                self.cleaned_data['address_value'],
                self.cleaned_data['image_source'],
                self.cleaned_data['category'],
                self.cleaned_data['price_retail'],
                self.cleaned_data['price_discount'],
                self.cleaned_data['start_date'],
                self.cleaned_data['end_date'],
                self.cleaned_data['stock'],
                self.cleaned_data['unlimited'],
                published
            )


def offers(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'offers.html',
        template_parameters
    )


@login_required
def edit(request, offer_id=None):
    try:
        business = Business.objects.get(user=request.user)
    except:
        return redirect(business.edit_profile)

    offer = None
    if None != offer_id:
        try:
            offer = Offer.objects.get(pk=offer_id)
        except:
            pass

    feedback = None
    if request.method == 'POST':
        form = OfferForm(
            request.POST,
            request.FILES,
            instance=offer
        )

        if form.is_valid():
            try:
                form.save_offer(request, offer)
                return redirect('/offers/')
            except ValueError as e:
                feedback = 'ValueError: ' + e.message
            except Exception as e:
                feedback = 'UnexpectedError: ' + e.message
        else:
            feedback = 'The following fields are invalid: '
            for error in form.errors:
                feedback += strip_tags(error) + '<br/>'
    else:
        form = OfferForm(instance=offer)

    template_parameters = ViewUtils.get_standard_template_parameters(request)
    template_parameters['business'] = Business.objects.get(user=request.user)
    template_parameters['offer_form'] = form
    template_parameters['offer'] = offer
    template_parameters['feedback'] = feedback

    return render(
        request,
        'create_offer.html',
        template_parameters
    )
