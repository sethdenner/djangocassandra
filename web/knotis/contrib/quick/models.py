from knotis.contrib.quick import views as quick_views
import polymodels.models
import polymodels.managers
from knotis.contrib.quick.fields import (
    QuickDateTimeField,
    QuickBooleanField
)


class QuickManager(polymodels.managers.PolymorphicManager):
    """
    How does this make sense????
    Sometimes you want to view deleted data...
    Isn't that the point of not actually deleting it???
    HOURS OF DEBUGGING AHHHH!!!!!

    def get_query_set(self):
        #print dir(self)
        #print self.model
        return super(QuickManager, self).get_query_set().filter(**({
            'deleted':False
        })).filter(**(self.model.Quick.filters))
    """
    def get(
        self,
        *args,
        **kwargs
    ):
        if not 'deleted' in kwargs:
            kwargs['deleted'] = False

        return super(QuickManager, self).get(
            *args,
            **kwargs
        )

    def filter(
        self,
        *args,
        **kwargs
    ):
        if not 'deleted' in kwargs:
            kwargs['deleted'] = False

        return super(QuickManager, self).filter(
            *args,
            **kwargs
        )


@staticmethod
def get_form_class(model, extra=0):
    from quick.forms import quick_modelform_factory
    from django.forms.models import modelformset_factory

    QuickForm = quick_modelform_factory(model)
    ModelFormSet = modelformset_factory(model, form=QuickForm, extra=extra)
    return ModelFormSet


class QuickModelBase(object):

    class Quick:
        exclude = ()
        filters = {}
        views = {
            'detail': 'quick/DetailView.html',
            'list': 'quick/ListView.html',
            'edit': 'quick/EditView.html'
        }
        view = quick_views.QuickView

        form_class = get_form_class

    def __unicode__(self):
        if hasattr(self, 'name'):
            return u'%s' % self.name
        if hasattr(self, 'id'):
            return u'%s' % self.id
        return u'%s' % self.__class__

    @property
    def model_type(self):
        #return str(type(self))
        return u'%s' % type(self).__name__
    
    def get_fields_dict(self):
        fields = {
            field.name: (
                field.value_to_string(self) for
                field in type(self)._meta.fields
            )
        }
        #print self.yelp_extra
        #fields.update(self._meta.local_fields)
        #if hasattr(self,'ExtraFields'):
        #    print "has extra fields"
        #    for attr in dir(self.ExtraFields):
        #        print attr
        #        print type(attr)
        #        if isinstance(attr, models.Field):
        #            print str(attr) + "is a Field"
        #            fields[attr.name] = attr.value_to_string(self)
        return fields

    def get_fields_values(self):
        return [field.value_to_string(self) for field in type(self)._meta.fields]

    @classmethod
    def get_arg_value_by_name(
        cls,
        field_name,
        *args,
        **kwargs
    ):
        i = 0
        for field in cls._meta.fields:
            if field.name == field_name:
                break

            ++i

        return args[i] if len(args) > i else kwargs.get(field_name)

    def get_absolute_url(self):
        root = "/"+type(self).__name__.lower()
        try:
            return root+("/%i/" % self.id)
        except: 
            return root

    #FIXME -- I don't like this method name. Better way to do this?
    @classmethod
    def get_filterable_fields(cls):
        return cls._meta.get_all_field_names()


class QuickModel(QuickModelBase, polymodels.models.PolymorphicModel ):
    deleted = QuickBooleanField(
        default=False,
        db_index=True
    )
    pub_date = QuickDateTimeField('date published', auto_now_add=True)
    objects = QuickManager()

    # looks at polymodels and generates a choice field based arround all the proxy classes of this class.	
    # types = QuickSubTypeField() 

    class Meta:
        abstract = True

    def clean(self, *args, **kwargs):
        return super(QuickModel, self).clean(*args, **kwargs)

    def validate(self, *args, **kwargs):
        return super(QuickModel, self).validate(*args, **kwargs)

    def delete(self):
        self.deleted = True
        super(QuickModel, self).save()
    
    @classmethod
    def get_filterable_fields(cls):
        filterable_fields = []
        for field in cls._meta.fields:
            if field.primary_key or field.db_index:
                filterable_fields.append(field.name)

        return filterable_fields
        
