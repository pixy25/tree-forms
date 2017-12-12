import unittest
from hypothesis import given
from hypothesis import strategies as st

from validators import ValidationError, Required
from fields import Field, FormField, FieldList, FieldDict, ChoiceField


class TestField(unittest.TestCase):

    def test_simple(self):
        field = Field()
        for val in (None, 0, 1, -1, 0.1, 'text', [[]], {'key': 'val'}, object()):
            self.assertFalse(field.validate(val, None))

    def test_required(self):
        field = Field(validators=[Required()])
        for empty_val in ('', {}, [], None):
            self.assertListEqual(field.validate(empty_val, None), ["Field is required"])


if __name__ == '__main__':
    unittest.main()