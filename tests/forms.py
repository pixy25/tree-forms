import unittest
from hypothesis import given
from hypothesis import strategies as st

from forms import BaseForm
from fields import *
from validators import *


class Form1(BaseForm):
    int_field = IntField(validators=[NumRange(1, 10)])
    str_field = TextField(validators=[LenValidator(minimum=1, maximum=16)])


class Form2(BaseForm):
    form1 = FormField(Form1)


class Form3(BaseForm):
    forms1 = ListField(FormField(Form1), min_len=2, max_len=4)


class Form4(BaseForm):
    forms1_dict = DictField(FormField(Form1), keys_validator=LenValidator(minimum=1,maximum=3))


class Form5(BaseForm):
    form1_or_int = Either((FormField(Form1), IntField()))


class Form6(BaseForm):
    id = IntField()
    to_self = FormField('self')
    to_self_list = ListField(FormField('self'))
    to_self_dict = DictField(FormField('self'))


class Form7(BaseForm):
    id = IntField()
    form8 = FormField('Form8')


class Form8(BaseForm):
    id = IntField()
    form7 = FormField(Form7)


class SimpleFormTest(unittest.TestCase):

    @given(
        st.integers(min_value=1, max_value=10),
        st.text(min_size=1, max_size=16)
    )
    def test_valid(self, int_field, str_field):
        form = Form1({'int_field': int_field, 'str_field': str_field})
        self.assertTrue(form.validate())

    @given(
        st.integers(min_value=11),
        st.text(min_size=20)
    )
    def test_not_valid(self, int_field, str_field):
        form = Form1({'int_field': int_field, 'str_field': str_field})
        self.assertFalse(form.validate())
        self.assertDictEqual(form.errors, {
            'int_field': ['Must be from 1 to 10'],
            'str_field': ['From 1 to 16 elements expected']
        })


class WithFormFieldTest(unittest.TestCase):
    @given(
        st.integers(min_value=1, max_value=10),
        st.text(min_size=1, max_size=16)
    )
    def test_valid(self, int_field, str_field):
        form = Form2({'form1': {'int_field': int_field, 'str_field': str_field}})
        self.assertTrue(form.validate())

    @given(
        st.integers(min_value=11),
        st.text(min_size=20)
    )
    def test_not_valid(self, int_field, str_field):
        form = Form2({'form1': {'int_field': int_field, 'str_field': str_field}})
        self.assertFalse(form.validate())
        self.assertDictEqual(form.errors, {'form1': [{
            'int_field': ['Must be from 1 to 10'],
            'str_field': ['From 1 to 16 elements expected']
        }]})



class WithFormFieldListTest(unittest.TestCase):
    @given(
        st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=10),
                st.text(min_size=1, max_size=16)
            ),
            min_size=2,
            max_size=4
        )
    )
    def test_valid(self, data):
        form = Form3({'forms1': [
            {'int_field': int_field, 'str_field': str_field}
            for int_field, str_field in data
        ]})
        self.assertTrue(form.validate())

    @given(
        st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=10),
                st.text(min_size=1, max_size=16)
            ),
            min_size=5
        )
    )
    def test_not_valid_size(self, data):
        form = Form3({'forms1': [
            {'int_field': int_field, 'str_field': str_field}
            for int_field, str_field in data
        ]})
        self.assertFalse(form.validate())
        self.assertDictEqual(form.errors, {'forms1': ['From 2 to 4 elements expected']})


    @given(
        st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=10),
                st.text(min_size=1, max_size=16)
            ),
            min_size=2,
            max_size=4
        )
    )
    def test_not_valid_element(self, data):
        int_field, str_field = data[1]
        data[1] = (int_field + 20, str_field)
        form = Form3({'forms1': [
            {'int_field': int_field, 'str_field': str_field}
            for int_field, str_field in data
        ]})
        self.assertFalse(form.validate())
        self.assertDictEqual(form.errors, {'forms1': [[{'int_field': ['Must be from 1 to 10']}]]})


class WithFormFieldDictTest(unittest.TestCase):
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=3),
                st.integers(min_value=1, max_value=10),
                st.text(min_size=1, max_size=16)
            ),
            min_size=2,
            max_size=4
        )
    )
    def test_valid(self, data):
        form = Form4({'forms1_dict': {
            key: {'int_field': int_field, 'str_field': str_field}
            for key, int_field, str_field in data
        }})
        self.assertTrue(form.validate())

    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=3),
                st.integers(min_value=1, max_value=10),
                st.text(min_size=1, max_size=16)
            ),
            min_size=54
        ),
        st.text(min_size=5),
        st.integers(min_value=1, max_value=10),
        st.text(min_size=1, max_size=16)
    )
    def test_not_valid_key(self, data, too_long_key, int_field, str_field):
        data = {
            'forms1_dict': {
                key: {'int_field': intf, 'str_field': strf}
                for key, intf, strf in data
            }
        }
        data['forms1_dict'][too_long_key] = {'int_field': int_field, 'str_field': str_field}
        form = Form4(data)
        self.assertFalse(form.validate())
        self.assertDictEqual(form.errors, {'forms1': ['From 2 to 4 elements expected']})


    @given(
        st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=10),
                st.text(min_size=1, max_size=16)
            ),
            min_size=2,
            max_size=4
        )
    )
    def test_not_valid_element(self, data):
        int_field, str_field = data[1]
        data[1] = (int_field + 20, str_field)
        form = Form3({'forms1': [
            {'int_field': int_field, 'str_field': str_field}
            for int_field, str_field in data
        ]})
        self.assertFalse(form.validate())
        self.assertDictEqual(form.errors, {'forms1': [[{'int_field': ['Must be from 1 to 10']}]]})




if __name__ == '__main__':
    unittest.main()