import django.db.models as models


class QuickFieldDefaultMixin(object):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        if 'default' not in kwargs:
            kwargs['default'] = None

        super(QuickFieldDefaultMixin, self).__init__(*args, **kwargs)


class QuickField(models.Field):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        self.required = kwargs.pop('required', False)

        if 'confidence' in kwargs:
            """
            define extra field in table containing numeric confidence.

            model.price.confidence
            model.price.stdev
            model.price.age
            """
            pass

        if 'null' not in kwargs:
            kwargs['null'] = True

        if 'blank' not in kwargs:
            kwargs['blank'] = True

        super(QuickField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        return super(QuickField, self).clean(*args, **kwargs)

    def validate(self, *args, **kwargs):
        return super(QuickField, self).validate(*args, **kwargs)

    @property
    def verbose_name(self):
        field_extras = self.field_extras()
        if hasattr(field_extras, 'verbose_name'):
            return field_extras['verbose_name']

        return models.Field.verbose_name

    @verbose_name.setter
    def verbose_name(self, value):
        field_extras = self.field_extras()
        if field_extras:
            self.Quick.field_extras['verbose_name'] = value

        else:
            models.Field.verbose_name = value

    def field_extras(self):
        if (
            hasattr(self, 'model') and
            hasattr(self.model, 'Quick') and
            hasattr(self.model.Quick, 'field_extras')
        ):
            return self.Quick.field_extras.get(self.name, {})

        else:
            return None


class QuickBooleanField(QuickField, models.BooleanField):
    def __init__(self, *args, **kwargs):
        if 'null' not in kwargs:
            kwargs['null'] = False
        if 'default' not in kwargs:
            kwargs['default'] = False
        super(QuickBooleanField, self).__init__(*args, **kwargs)


class QuickCharField(QuickField, QuickFieldDefaultMixin, models.CharField):
    pass


class QuickDateTimeField(
    QuickField,
    QuickFieldDefaultMixin,
    models.DateTimeField
):
    pass


class QuickFileField(QuickField, QuickFieldDefaultMixin, models.FileField):
    pass


class QuickFloatField(QuickField, QuickFieldDefaultMixin, models.FloatField):
    pass


class QuickImageField(QuickField, QuickFieldDefaultMixin, models.ImageField):
    def __init__(self, **kwargs):
        if 'upload_to' not in kwargs:
            kwargs['upload_to'] = 'image_uploads/%Y/%m/%d'
        super(type(self), self).__init__(**kwargs)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        import quick.forms
        defaults = {'widget': quick.forms.PrettyFileInput}
        defaults.update(kwargs)
        return super(QuickImageField, self).formfield(**defaults)


class QuickIntegerField(
    QuickField,
    QuickFieldDefaultMixin,
    models.IntegerField
):
    pass


class QuickTextField(QuickField, QuickFieldDefaultMixin, models.TextField):
    pass


class QuickForeignKey(QuickField, QuickFieldDefaultMixin, models.ForeignKey):
    def __init__(
        self,
        to,
        #to_field=None,
        #rel_class=models.ManyToOneRel,
        *args,
        **kwargs
    ):
        if 'null' not in kwargs:
            kwargs['null'] = True

        if 'blank' not in kwargs:
            kwargs['blank'] = True

        if 'default' not in kwargs:
            kwargs['default'] = None

        super(QuickForeignKey, self).__init__(
            to,
            #to_field,
            #rel_class,
            *args,
            **kwargs
        )

    def db_type(self, connection):
        return 'ForeignKeyNonRel'

from django.contrib.contenttypes import generic


class QuickGenericForeignKey(QuickField, generic.GenericForeignKey):
    def __init__(self, *args, **kwargs):
        super(QuickField, self).__init__(*args, **kwargs)

from django_extensions.db.fields import UUIDField


class QuickUUIDField(QuickField, QuickFieldDefaultMixin, UUIDField):
    pass
