import unittest
from hypothesis import given
from hypothesis import strategies as st

from validators import ValidationError, Required
from fields import Field, FormField, ListField, DictField, ChoiceField


class TestField(unittest.TestCase):

    def test_simple(self):
        field = Field()
        for val in (None, 0, 1, -1, 0.1, 'text', [[]], {'key': 'val'}, object()):
            self.assertFalse(field.validate(val))

    def test_required(self):
        field = Field(validators=[Required()])
        for empty_val in ('', {}, [], None):
            self.assertListEqual(field.validate(empty_val), ["Field is required"])


class FieldListTest(unittest.TestCase):

    def test_min(self):
        pass

    def test_max(self):
        pass

if __name__ == '__main__':
    unittest.main()
