from django.forms import ModelForm

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
            'perishable',
            'unlimited'
        )
