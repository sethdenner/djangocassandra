from django.db.models.base import ModelBase
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from djangotoolbox.fields import ListField
from string import Template
from utils.functional import curry
from views import ManyToManyFormField


class ManyRelatedManagerFactory:
    managers = {}

    @staticmethod
    def get(model_class):
        manager = ManyRelatedManagerFactory.managers.get(model_class)
        if manager:
            return manager
        else:
            class ManyRelatedManager(model_class):
                def __init__(self, instance, field):
                    super(ManyRelatedManager, self).__init__()
                    self.rel_instance = instance
                    self.rel_field = field
                    self.model = field.othermodel
                    self.model_class = model_class

                """
                def __iter__(self):
                    count = 0
                    field = getattr(
                        self.rel_instance,
                        self.rel_instance
                    )
                    length = len(self.rel_field)

                    while count < length:
                        yield field[count]
                        count += 1
                """
                def get_query_set(self):
                    filter_values = {
                        "pk__in": getattr(
                            self.rel_instance,
                            self.rel_field.helper_field_name
                        )
                    }
                    return super(ManyRelatedManager, self)\
                        .get_query_set()\
                        .filter(**filter_values)

                def add(self, *objects):
                    current_values = self._get_pk_list()
                    object_pks = self._get_pk_list(objects)
                    new_values = \
                        [o for o in object_pks if o not in current_values]
                    new_values = new_values + current_values

                    self._local_save(new_values)

                def remove(self, *objects):
                    current_values = self._get_pk_list()
                    object_pks = self._get_pk_list(objects)
                    new_values = [v for v in current_values \
                        if v not in object_pks]

                    self._local_save(new_values)

                def clear(self):
                    self._local_save([])

                def create(self, **kwargs):
                    model = self.rel_field.othermodel
                    new_object = model(**kwargs)
                    new_object.save()

                    current_values = self._get_pk_list()
                    current_values.append(new_object.pk)

                    self._local_save(current_values)

                def _local_save(self, new_values):
                    setattr(
                        self.rel_instance,
                        self.rel_field.helper_field_name,
                        new_values
                    )

                    model = self.rel_instance.__class__
                    temp = model._base_manager\
                        .filter(pk=self.rel_instance.pk)[0]

                    setattr(temp, self.rel_field.helper_field_name, new_values)
                    temp.save()

                def _get_pk_list(self, value=None):
                    if value is None:
                        return getattr(
                            self.rel_instance,
                            self.rel_field.helper_field_name
                        )

                    error_templates = {
                        'unknown_type_in_list':
                            Template('Unknown type for element of \
                            list or tuple: ${cls}'),
                        'unknown_type_in_conversion':
                            Template('Unknown type in conversion: \
                            ${cls}'),
                        'unknown_error':
                            Template('Unknown error in conversion: \
                            ${cls}, ${msg}')
                    }

                    try:
                        if isinstance(value, (QuerySet, Manager)) and \
                            hasattr(value, 'all'):

                            values = []
                            for v in value.all():
                                if not isinstance(
                                    v,
                                    self.rel_field.othermodel
                                ):
                                    raise TypeError(
                                        error_templates['unknown_type_in_list']\
                                        .substitute(cls=v.__class__))

                                values.append(v.pk)

                        elif isinstance(value, (list, tuple)):
                            values = []
                            for v in value:
                                if not isinstance(
                                    v,
                                    self.rel_field.othermodel
                                ):
                                    raise TypeError(
                                        error_templates['unknown_type_in_list']\
                                        .substitute(cls=v.__class__))

                                values.append(v.pk)

                        else:
                            raise TypeError(
                                error_templates['unknown_type_in_conversion']\
                                .substitute(cls=value.__class__)
                            )

                    except TypeError, e:
                        raise e
                    except Exception, e:
                        raise TypeError(
                            error_templates['unknown_error']\
                            .substitute(cls=e.__class__, msg=e.message)
                        )

                    return values

            return ManyRelatedManager

class ManyRelatedObjectsDescriptorNonRel(object):
    # This class provides the functionality that makes the related-object
    # managers available as attributes on a model class, for fields that have
    # multiple "remote" values and have a ManyToManyField pointed at them by
    # some other model (rather than having a ManyToManyField themselves).
    # In the example "publication.article_set", the article_set attribute is a
    # ManyRelatedObjectsDescriptor instance.
    def __init__(self, related):
        self.related = related   # RelatedObject instance

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        # Dynamically create a class that subclasses the related
        # model's default manager.
        rel_model = self.related.model
        superclass = rel_model._default_manager.__class__
        manager = ManyRelatedManagerFactory.get(superclass)

        return manager

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError('Manager must be accessed via instance')

        if not self.related.field.rel.through._meta.auto_created:
            opts = self.related.field.rel.through._meta
            raise AttributeError("Cannot set values on a ManyToManyField "
                "which specifies an intermediary model. Use %s.%s's Manager "
                "instead." % (opts.app_label, opts.object_name))

        manager = self.__get__(instance)
        manager.clear()
        manager.add(*value)


class ReverseManyRelatedObjectsDescriptor(object):
    # This class provides the functionality that makes the related-object
    # managers available as attributes on a model class, for fields that have
    # multiple "remote" values and have a ManyToManyField defined in their
    # model (rather than having another model pointed *at* them).
    # In the example "article.publications", the publications attribute is a
    # ReverseManyRelatedObjectsDescriptor instance.
    def __init__(self, m2m_field):
        self.field = m2m_field

    def _through(self):
        # through is provided so that you have easy access to the through
        # model (Book.authors.through) for inlines, etc. This is done as
        # a property to ensure that the fully resolved value is returned.
        return self.field.rel.through
    through = property(_through)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        # Dynamically create a class that subclasses the related
        # model's default manager.
        rel_model = self.field.rel.to
        superclass = rel_model._default_manager.__class__

        manager = ManyRelatedManagerFactory.get(superclass)

        return manager


class ManyToManyFieldNonRel(ListField):
    def __init__(self, othermodel, **kwargs):
        is_symetrical = False
        lazy_eval = False

        if isinstance(othermodel, basestring):
            if othermodel == 'self':
                is_symetrical = True
            else:
                lazy_eval = True

        elif issubclass(othermodel.__class__, ModelBase):
            self.othermodel = othermodel

        if is_symetrical or lazy_eval:
            raise NotImplementedError

        base_manager_class = self.othermodel._base_manager.__class__
        self.many_related_manager = ManyRelatedManagerFactory.get(base_manager_class)

        super(ManyToManyFieldNonRel, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        return ManyToManyFormField(**kwargs)

    def contribute_to_class(self, cls, name):
        # To support multiple relations to self, it's useful to have a non-None
        # related name on symmetrical relations for internal reasons. The
        # concept doesn't make a lot of sense externally ("you want me to
        # specify *what* on my non-reversible relation?!"), so we set it up
        # automatically. The funky name reduces the chance of an accidental
        # clash.
        if self.rel.symmetrical and \
            (self.rel.to == "self" or self.rel.to == cls._meta.object_name):
            self.rel.related_name = "%s_rel_+" % name

        self.field_name = name
        self.model_class = cls
        cls._meta.add_virtual_field(self)

        setattr(cls, self.field_name, self)

        self.helper_field_name = "__" + self.field_name + "_helper"

        setattr(cls, self.helper_field_name, self)

        super(ManyToManyFieldNonRel, self)\
            .contribute_to_class(cls, self.helper_field_name)

    def contribute_to_related_class(self, cls, related):
        # Internal M2Ms (i.e., those with a related name ending with '+')
        # don't get a related descriptor.
        if not self.rel.is_hidden():
            setattr(
                cls,
                related.get_accessor_name(),
                ManyRelatedObjectsDescriptorNonRel(related)
            )

        # Set up the accessors for the column names on the m2m table
        self.m2m_column_name = curry(self._get_m2m_attr, related, 'column')
        self.m2m_reverse_name = curry(self._get_m2m_reverse_attr, related, 'column')

        self.m2m_field_name = curry(self._get_m2m_attr, related, 'name')
        self.m2m_reverse_field_name = curry(self._get_m2m_reverse_attr, related, 'name')

        get_m2m_rel = curry(self._get_m2m_attr, related, 'rel')
        self.m2m_target_field_name = lambda: get_m2m_rel().field_name
        get_m2m_reverse_rel = curry(self._get_m2m_reverse_attr, related, 'rel')
        self.m2m_reverse_target_field_name = lambda: get_m2m_reverse_rel().field_name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.many_related_manager(instance, self)

    """
    def __set__(self, instance, value):
        if not isinstance(value, (tuple, list)):
            value = list(value)

        self.item_field = value

        setattr(instance, self.helper_field_name, self)
    """
