from django.forms import (
    ModelForm,
    CharField
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Div,
    Field,
    Submit,
    Button
)
from crispy_forms.bootstrap import FormActions

from models import Inventory


class InventoryForm(ModelForm):
    class Meta:
        model = Inventory
        exclude = (
            'content_type',
            'deleted'
        )


class InventoryStackFromProductForm(InventoryForm):
    class Meta(InventoryForm.Meta):
        exclude = (
            'id',
            'content_type',
            'deleted',
            'recipient',
            'perishable'
        )

    product_name = CharField(
        required=False,
        max_length=256
    )

    def __init__(
        self,
        form_tag=True,
        *args,
        **kwargs
    ):
        super(InventoryStackFromProductForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-inventory-from-product-form'
        self.helper.form_action = '/api/v1/inventory/'
        self.helper.form_method = 'post'
        self.helper.form_tag = form_tag
        self.helper.layout = Layout(
            Div(
                Field(
                    'product_name',
                    id='product-name-input'
                ),
                Field(
                    'stock',
                    id='stock-input'
                ),
                Field(
                    'unlimited',
                    id='unlimited-input'
                ),
                Field(
                    'price',
                    id='price-input'
                )
            ),
            FormActions(
                Submit(
                    'save-inventory',
                    'Save'
                ),
                Button(
                    'cancel',
                    'Cancel'
                )
            )
        )
