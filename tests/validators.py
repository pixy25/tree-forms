import unittest
from hypothesis import given
from hypothesis import strategies as st

from validators import ValidationError, Required, RequiredIf, NumRange, ChoiceValidator, \
    FieldSequenceValidator, FieldDictValidator


class TestRequired(unittest.TestCase):

    def test_fails_on_empty(self):
        for empty_val in ('', {}, [], None):
            with self.assertRaises(ValidationError) as context:
                Required()(empty_val, form=None)
            self.assertEqual(context.exception.data, "Field is required")

    def test_ok_on_non_empty(self):
        for val in (0, 1, -1, {'': ''}, [''], [None]):
            self.assertIsNone(Required()(val, form=None))


class TestRequiredIf(unittest.TestCase):


    def test_ok_on_non_empty(self):
        for val in (0, 1, -1, {'': ''}, [''], [None]):
            self.assertIsNone(RequiredIf(lambda _: True)(val, form=None))

    def test_ok_on_empty_when_clause_is_false(self):
        for empty_val in ('', {}, [], None):
            RequiredIf(lambda _: False)(empty_val, form=None)

    def test_fails_on_empty_when_clause_is_true(self):
        for empty_val in ('', {}, [], None):
            with self.assertRaises(ValidationError) as context:
                RequiredIf(lambda _: True)(empty_val, form=None)
            self.assertEqual(context.exception.data, "Field is required")


if __name__ == '__main__':
    unittest.main()