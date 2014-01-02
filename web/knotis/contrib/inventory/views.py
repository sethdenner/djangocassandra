from django.contrib.auth.decorators import login_required
from djago.utils.decorators import method_decorator
from django.shortcuts import render

from django.utils import log
logger = log.getLogger(__name__)

from knotis.views import FragmentView
from knotis.contrib.product.forms import ProductSimpleForm

from forms import InventoryStackFromProductForm


class CreateInventoryFromProductView(FragmentView):
    template_name = 'knotis/inventory/create_from_product.html'
    view_name = 'inventory_from_product'

    @method_decorator(login_required)
    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return render(
            request,
            self.template_name, {
                'product_form': ProductSimpleForm(form_tag=False),
                'inventory_form': InventoryStackFromProductForm(form_tag=False)
            }
        )
