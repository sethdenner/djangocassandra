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


class QuickField(object):
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
        #print "field cleaning" + str(self.__class__)
        return super(QuickField, self).clean(*args, **kwargs)

    def validate(self, *args, **kwargs):
        #print "field validateing" + str(self.__class__)
        return super(QuickField, self).validate(*args, **kwargs)


class QuickBooleanField(QuickField, models.BooleanField):
    def __init__(self, *args, **kwargs):
        if 'null' not in kwargs:
            kwargs['null'] = False
        if 'default' not in kwargs:
            kwargs['default'] = False
        super(QuickBooleanField, self).__init__(*args, **kwargs)


class QuickCharField(QuickField, QuickFieldDefaultMixin, models.CharField):
    pass


class QuickURLField(QuickField, QuickFieldDefaultMixin, models.URLField):
    pass


class QuickIPAddressField(
        QuickField,
        QuickFieldDefaultMixin,
        models.IPAddressField
):
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

    def get_internal_type(self):
        return 'ForeignKey'


from django.contrib.contenttypes import generic


class QuickGenericForeignKey(QuickField, generic.GenericForeignKey):
    def __init__(self, *args, **kwargs):
        super(QuickField, self).__init__(*args, **kwargs)


from django_extensions.db.fields import UUIDField


class QuickUUIDField(QuickField, QuickFieldDefaultMixin, UUIDField):
    pass
