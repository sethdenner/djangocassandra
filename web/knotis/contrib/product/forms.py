from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_froms.layout import (
    Layout,
    Div,
    Field
)

from models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = (
            'content_type',
            'deleted'
        )


class ProductSimpleForm(ProductForm):
    class Meta(ProductForm.Meta):
        exclude = ProductForm.Meta.exclude + (
            'description',
            'primary_image',
            'public',
            'sku'
        )

    def __init__(
        self,
        form_tag=True,
        *args,
        **kwargs
    ):
        super(ProductSimpleForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-product-form',
        self.helper.form_action = '/api/v1/product/'
        self.helper.form_method = 'post'
        self.helper.form_tag = form_tag
        self.helper.layout = Layout(
            Div(
                Field(
                    'product_type',
                    id='product-type-input'
                ),
                Field(
                    'title',
                    id='title-input'
                )
            )
        )
