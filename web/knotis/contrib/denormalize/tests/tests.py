from django.test import TestCase

from models import (
    TestDenormalizeModelA,
    TestDenormalizeModelB,
    TestDenormalizedModel
)


class DenormalizedFieldTests(TestCase):
    def test_denormalized_field(self):
        model_a = TestDenormalizeModelA.objects.create(
            test_value='test_value_a'
        )
        model_b = TestDenormalizeModelB.objects.create(
            test_value='test_value_b'
        )

        denormalized = TestDenormalizedModel()
        denormalized.test_value = model_a
        denormalized.test_value_b = model_b
        denormalized.save()

        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)

        model_a.test_value += 'MODIFIED'
        model_a.save()

        denormalized = TestDenormalizedModel.objects.get(pk=denormalized.id)
        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)

        model_b.test_value += 'MODIFIED'
        model_b.save()

        denormalized = TestDenormalizedModel.objects.get(pk=denormalized.id)
        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)
