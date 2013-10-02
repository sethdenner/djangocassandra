from django.forms import ModelForm

from models import Relation


class RelationForm(ModelForm):
    class Meta:
        model = Relation
        exclude = (
            'content_type',
            'subject_content_type',
            'subject_object_id',
            'related_content_type',
            'related_object_id',
        )
