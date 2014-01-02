from  django.db.models import (
    Model,
    CharField
)
from knotis.contrib.denormalize.models import DenormalizedField


class TestDenormalizeModelA(Model):
    class Meta:
        app_label = 'denormalize'

    test_value = CharField(max_length=32)


class TestDenormalizeModelB(Model):
    class Meta:
        app_label = 'denormalize'

    test_value = CharField(max_length=32)


class TestDenormalizeModelC(Model):
    class Meta:
        app_label = 'denormalize'

    test_value = CharField(max_length=32)


class TestDenormalizedModel(Model):
    class Meta:
        app_label = 'denormalize'

    test_value = DenormalizedField(TestDenormalizeModelA)
    test_value_b = DenormalizedField(TestDenormalizeModelB, 'test_value')
    test_unmanaged = DenormalizedField(
        TestDenormalizeModelC,
        'test_value',
        auto_update=False
    )
