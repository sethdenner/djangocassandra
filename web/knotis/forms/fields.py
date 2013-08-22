import re

from django.core.exceptions import ValidationError
from django.forms import (
    Field,
    CharField
)

from knotis.utils.regex import REGEX_UUID


class UUIDField(CharField):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        kwargs['max_length'] = '36'
        super(UUIDField, self).__init__(
            *args,
            **kwargs
        )

    def clean(
        self,
        value
    ):
        if not re.match(
            REGEX_UUID,
            value
        ):
            raise ValidationError('value is not a UUID string')

        return value


class DynamicField(Field):
    def __init__(
        self,
        query_set,
        field_type,
        field_params={},
        *args,
        **kwargs
    ):
        self.query_set = query_set
        self.field_type = field_type
        self.field_params = field_params

        super(DynamicField, self).__init__(
            *args,
            **kwargs
        )

    def add_dynamic_fields(
        self,
        instance,
        field_name
    ):
        field_counter = 0
        for obj in self.query_set:
            instance.setattr(
                instance,
                '_'.join([
                    field_name,
                    field_counter
                ]),
                self.field_type(self.field_params)
            )
            field_counter += 1
