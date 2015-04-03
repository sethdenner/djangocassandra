from unittest import TestCase

from .models import (
    SimpleTestModel,
    ClusterPrimaryKeyModel
)

from .util import (
    connect_db,
    destroy_db,
    create_model
)


class DatabaseSimpleQueryTestCase(TestCase):
    def setUp(self):
        self.connection = connect_db()

        self.cached_rows = {}

        '''
        Let's create some simple data.
        '''
        create_model(
            self.connection,
            SimpleTestModel
        )

        field_names = [
            field.name if field.get_internal_type() != 'AutoField' else None
            for field in SimpleTestModel._meta.fields
        ]
        field_values = ['foo', 'bar', 'raw', 'awk', 'lik', 'sik', 'dik', 'doc']

        self.total_rows = 10
        for x in xrange(self.total_rows):
            test_data = {}
            i = 0
            for name in field_names:
                if not name:
                    continue

                test_data[name] = field_values[i]
                i += 1

            created_instance = SimpleTestModel.objects.create(**test_data)
            self.cached_rows[created_instance.pk] = created_instance

        '''
        Now let's create some data that is clustered
        '''
        create_model(
            self.connection,
            ClusterPrimaryKeyModel
        )

        manager = ClusterPrimaryKeyModel.objects
        manager.create(
            field_1='aaaa',
            field_2='aaaa',
            field_3='bbbb',
            data='Foo'
        )

        manager.create(
            field_1='aaaa',
            field_2='bbbb',
            field_3='cccc',
            data='Tao'
        )

        manager.create(
            field_1='bbbb',
            field_2='aaaa',
            field_3='aaaa',
            data='Bar'
        )

        manager.create(
            field_1='bbbb',
            field_2='bbbb',
            field_3='aaaa',
            data='Lel'
        )

        import django
        django.setup()

    def tearDown(self):
        destroy_db(self.connection)

    def test_query_all(self):
        all_rows = list(SimpleTestModel.objects.all())

        self.assertEqual(len(all_rows), self.total_rows)

        for row in all_rows:
            cache = self.cached_rows.get(row.pk)
            fields = cache._meta.fields
            for field in fields:
                self.assertEqual(
                    getattr(cache, field.name),
                    getattr(row, field.name)
                )

    def test_orderby(self):
        manager = ClusterPrimaryKeyModel.objects
        all_rows = list(manager.filter(field_1='bbbb'))
        all_rows_ordered = list(manager.filter(field_1='bbbb').order_by('field_2'))
        all_rows_ordered_desc = list(manager.filter(field_1='bbbb').order_by('-field_2'))

        all_rows.sort(
            key=lambda x: x.field_2,
            reverse=False
        )

        for i in range(len(all_rows)):
            self.assertEqual(
                all_rows[i].data,
                all_rows_ordered[i].data
            )

        all_rows.sort(
            key=lambda x: x.field_2,
            reverse=True
        )

        for i in range(len(all_rows)):
            self.assertEqual(
                all_rows[i].data,
                all_rows_ordered[i].data
            )

    '''
    def test_inefficient_orderby(self):
        self.assertIsNotNone(None)

    def test_filter(self):
        self.assertIsNotNone(None)

    def test_inefficient_filter(self):
        self.assertIsNotNone(None)
    '''
