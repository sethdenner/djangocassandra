from django.db.models import ForeignKey, ManyToOneRel


class ForeignKeyNonRel(ForeignKey):
    def __init__(self, to, to_field=None, rel_class=ManyToOneRel, **kwargs):

        if 'null' not in kwargs:
            kwargs['null'] = True

        if 'blank' not in kwargs:
            kwargs['blank'] = True

        super(ForeignKeyNonRel, self).__init__(
            to,
            to_field,
            rel_class,
            **kwargs
        )
        
    def db_type(self, connection):
        return 'ForeignKeyNonRel'
