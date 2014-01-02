from django.test import TestCase

from models import (
    TestDenormalizeModelA,
    TestDenormalizeModelB,
    TestDenormalizeModelC,
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
        model_c = TestDenormalizeModelC.objects.create(
            test_value='test_value_c'
        )

        denormalized = TestDenormalizedModel()
        denormalized.test_value = model_a
        denormalized.test_value_b = model_b
        denormalized.test_unmanaged = model_c
        denormalized.save()

        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)

        model_a.test_value += 'MODIFIED'
        model_a.save()

        denormalized = TestDenormalizedModel.objects.get(pk=denormalized.id)
        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)
        self.assertEqual(model_c.test_value, denormalized.test_unmanaged)

        model_b.test_value += 'MODIFIED'
        model_b.save()

        denormalized = TestDenormalizedModel.objects.get(pk=denormalized.id)
        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)
        self.assertEqual(model_c.test_value, denormalized.test_unmanaged)

        model_c.test_value += 'MODIFIED'
        model_c.save()

        denormalized = TestDenormalizedModel.objects.get(pk=denormalized.id)
        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)
        self.assertNotEqual(model_c.test_value, denormalized.test_unmanaged)

        denormalized.test_value += '_AGAIN'
        denormalized.save()

        model_a = TestDenormalizeModelA.objects.get(pk=model_a.id)
        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)
        self.assertNotEqual(model_c.test_value, denormalized.test_unmanaged)

        denormalized.test_unmanaged += 'MODIFIED'
        denormalized.save()

        model_c = TestDenormalizeModelC.objects.get(pk=model_c.id)
        self.assertEqual(model_a.test_value, denormalized.test_value)
        self.assertEqual(model_b.test_value, denormalized.test_value_b)
        self.assertEqual(model_c.test_value, denormalized.test_unmanaged)
