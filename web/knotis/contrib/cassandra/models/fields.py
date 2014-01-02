import django.db.models as models


class ForeignKey(models.ForeignKey):
    def __init__(
        self,
        to,
        to_field=None,
        rel_class=models.ManyToOneRel,
        **kwargs
    ):
        if 'null' not in kwargs:
            kwargs['null'] = True

        if 'blank' not in kwargs:
            kwargs['blank'] = True

        if 'default' not in kwargs:
            kwargs['default'] = None

        super(ForeignKey, self).__init__(
            to,
            to_field,
            rel_class,
            **kwargs
        )

    def db_type(self, connection):
        return 'ForeignKeyNonRel'
