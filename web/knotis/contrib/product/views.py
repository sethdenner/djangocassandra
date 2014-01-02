from django.shortcuts import render

from knotis.views import FragmentView

from forms import ProductForm


class ProductView(FragmentView):
    template_name = 'knotis/product/view.html'
    view_name = 'product'


class ProductEditView(FragmentView):
    template_name = 'knotis/product/edit.html'
    view_name = 'product_edit'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return render(
            request,
            self.template_name, {
                'product_form': ProductForm()
            }
        )
