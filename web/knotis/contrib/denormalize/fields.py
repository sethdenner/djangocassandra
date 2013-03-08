import copy

from django.db.models import Field
from django.db.models.fields.related import add_lazy_relation
from django.db.models.signals import post_save
from django_extensions.db.fields import UUIDField


class DenormalizedField(Field):
    denormalized_field_names_attr_name  = '_denormalized_field_names'

    @staticmethod
    def update_denormalized_fields(
        signal,
        sender,
        instance,
        created,
        raw,
        using
    ):
        denormalized_model_field_names = sender.__dict__[
            DenormalizedField.denormalized_field_names_attr_name
        ]

        for model, field_names in denormalized_model_field_names.iteritems():
            for field_name in field_names:
                def get_original_field_name(denormalized_field_name):
                    split_field = field_name.split('_')
                    is_rest_name = False
                    original_name = ''
                    for part in split_field:
                        if is_rest_name:
                            original_name = '_'.join([
                                original_name,
                                part
                            ])

                        if sender.__name__ == part:
                            is_rest_name = True

                    return original_name.strip('_')

                original_field_name = get_original_field_name(
                    field_name
                )
                object_filter = {}
                object_filter['_'.join([
                    field_name,
                    'pk'
                ])] = instance.id
                rows = model.objects.filter(**object_filter)
                for row in rows:
                    if row.__dict__[field_name] == instance.__dict__[
                        original_field_name
                    ]:
                        continue

                    else:
                        row.__dict__[field_name] = instance.__dict__[
                            original_field_name
                        ]
                        row.save()

    def __init__(
        self,
        related_model,
        related_field_name=None,
        *args,
        **kwargs
    ):
        super(DenormalizedField, self).__init__(
            *args,
            **kwargs
        )

        self.related_model = related_model
        self.related_field_name = related_field_name

    def contribute_to_class(
        self,
        cls,
        name
    ):
        if not self.related_field_name:
            self.related_field_name = name

        self.related_field = None
        for field in self.related_model._meta.fields:
            if field.name == self.related_field_name:
                self.related_field = copy.deepcopy(field)
                break

        if not self.related_field:
            raise Exception(' '.join([
                'AttributeError: No attribute named',
                self.related_field_name,
                'on related model.'
            ]))

        self.denormalized_field_name = '_'.join([
            '_denormalized',
            self.related_model.__name__,
            self.related_field_name
        ])
        self.related_field.contribute_to_class(
            cls,
            self.denormalized_field_name
        )
        UUIDField(db_index=True).contribute_to_class(
            cls,
            '_'.join([
                self.denormalized_field_name,
                'pk'
            ])
        )
        setattr(
            cls,
            name,
            DenormalizedFieldDescriptor(
                self.related_model,
                self.related_field_name,
                self.denormalized_field_name
            )
        )

        def resolve_related_class(
            field,
            model,
            cls
        ):
            field.related_model = model
            field.do_related_class(
                model,
                cls
            )
        add_lazy_relation(
            cls,
            self,
            self.related_model.__name__,
            resolve_related_class
        )

    def do_related_class(
        self,
        other,
        cls
    ):
        if not cls._meta.abstract:
            self.contribute_to_related_class(
                other,
                cls
            )

    def contribute_to_related_class(
        self,
        other,
        cls
    ):
        if hasattr(
            other,
            DenormalizedField.denormalized_field_names_attr_name
        ):
            denormalized_field_names = getattr(
                other,
                DenormalizedField.denormalized_field_names_attr_name
            )
            if cls in denormalized_field_names:
                denormalized_field_names[cls].add(self.denormalized_field_name)

            else:
                denormalized_field_names[cls] = set(
                    [self.denormalized_field_name]
                )

        else:
            denormalized_fields = {}
            denormalized_fields[cls] = set(
                [self.denormalized_field_name]
            )
            setattr(
                other,
                DenormalizedField.denormalized_field_names_attr_name,
                denormalized_fields
            )

        post_save.connect(
            DenormalizedField.update_denormalized_fields,
            sender=other,
            weak=False,
            dispatch_uid='_'.join([
                'denormalize_update',
                other.__name__
            ]),
        )


class DenormalizedFieldDescriptor(object):
    def __init__(
        self,
        related_model,
        related_field_name,
        denormalized_field_name
    ):
        self.related_model = related_model
        self.related_field_name = related_field_name
        self.denormalized_field_name = denormalized_field_name

    def __get__(
        self,
        instance,
        owner
    ):
        return instance.__dict__[self.denormalized_field_name]

    def __set__(
        self,
        instance,
        value
    ):
        if isinstance(value, self.related_model):
            instance.__dict__[
                '_'.join([
                    self.denormalized_field_name,
                    'pk'
                ])
            ] = value.id

            instance.__dict__[self.denormalized_field_name] = value.__dict__[
                self.related_field_name
            ]

        else:
            instance.__dict__[self.denormalized_field_name] = value
