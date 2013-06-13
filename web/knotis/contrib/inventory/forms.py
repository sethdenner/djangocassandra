from django.forms import ModelForm

from models import Inventory


class InventoryForm(ModelForm):
    class Meta:
        model = Inventory
        exclude = (
            'content_type',
            'deleted'
        )
