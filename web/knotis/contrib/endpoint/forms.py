from models import (
    Endpoint,
    Credentials
)

from knotis.forms import ModelForm


class EndpointForm(ModelForm):
    class Meta:
        model = Endpoint
        exclude = (
            'content_type',
            'deleted'
        )


class CredentialsForm(ModelForm):
    class Meta:
        model = Credentials
        exclude = (
            'content_type',
            'deleted'
        )
