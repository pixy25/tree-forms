from collections import defaultdict
from functools import partial

from validators import Required, ChoiceValidator, TypeValidator, ConversionValidator, validate_path
from utils.time import unserialize_time


filter_out_empty = partial(filter, lambda _: _)


class BaseField(object):
    validators = []

    def copy(self):
        copy = self.__class__()
        copy._validators = self._validators

    def add_validators(self, *validators):
        self._validators.extend(validators)

    def __new__(cls, *args, **kwargs):
        self = super(BaseField, cls).__new__(*args, **kwargs)
        if not hasattr(self, '_validators'):
            self._validators = cls.validators[:]
        return self

    def __init__(self, validators=None):
        if validators:
            self.add_validators(*validators)
        else:
            self.add_validators()

    def __call__(self, data, form, name):
        self.form, self.data, self.name = data, form, name
        return self

    def validate(self):
        required_validators = []
        other_validators = []
        for i, validator in enumerate(self._validators):
            if isinstance(validator, Required):
                required_validators.append(validator)
            else:
                other_validators.append(validator)
        if self.data not in [None, '', [], {}]:
            return self.run_validators(other_validators) or None
        required_errors = self.run_validators(required_validators)
        return required_errors or None

    def run_validators(self, validators):
        errors = []
        for validator in validators:
            error = validator(self.data, self.form, self.name)
            if error:
                errors.append(error)
        return errors


class FormField(BaseField):
    def __init__(self, FormClass, *args, **kwargs):

        def validate(data, form, field_name):
            inner_form = FormClass(data)
            if not inner_form.validate():
                return inner_form.errors

        self.add_validators(validate)
        super(FormField, self).__init__(*args, **kwargs)


def field_callable(field_instance):
    if not isinstance(field_instance, BaseField):
        field_instance = field_instance() # for recursive forms
    return field_instance


class FieldList(BaseField):
    def __init__(self, field_obj, *args, **kwargs):

        def validate(data, form, field_name):
            errors = [
                field_callable(field_obj)(
                    form,
                    field_data,
                    field_name
                ).validate()
                for field_data in data
            ]
            if filter_out_empty(errors):
                return errors

        self.add_validators(validate)
        super(FieldList, self).__init__(*args, **kwargs)


class BaseFieldDict(BaseField):
    def __init__(self, field_obj, keys_validator=None, *args, **kwargs):
        def validate(data, form, field_name):
            field_clbl = field_callable(field_obj)
            key_errors = keys_validator(data, form.keys(), field_name) if keys_validator else {}
            result = defaultdict(list, key_errors)
            for key, field_data in data.items():
                errors = field_clbl(form, field_data, key).validate()
                if errors:
                    if type(errors) == list:
                        result[key].extend(errors)
                    else:
                        result[key].append(errors)
            return dict(result) or None

        self.add_validators(validate)
        super(BaseFieldDict, self).__init__(*args, **kwargs)


class BaseFieldTuple(BaseField):
    def __init__(self, field_objects, *args, **kwargs):
        def validate(data, form, field_name):
            errors = [
                field_callable(field_obj)(form, field_data, field_name).validate()
                for field_obj, field_data in zip(field_objects, data)
            ]
            filtered_errors = filter(lambda _: _, errors)
            return errors if filtered_errors else None

        self.add_validators(validate)
        super(BaseFieldTuple, self).__init__(*args, **kwargs)


class ChoiceField(BaseField):
    def __init__(self, collection, *args, **kwargs):
        self.add_validators(ChoiceValidator(collection))
        super(ChoiceField, self).__init__(*args, **kwargs)


class StringField(BaseField):
    validators = [TypeValidator(str)]


class DateTimeField(BaseField):
    validators = [
        ConversionValidator(unserialize_time, 'Expected date time string')
    ]


class IntField(BaseField):
    validators = [TypeValidator(int)]


class FloatField(BaseField):
    validators = [ConversionValidator(float, 'Must be decimal', ValueError)]


class StringListField(BaseField):
    validators = [validate_path]


class BooleanField(BaseField):
    validators = [TypeValidator(bool)]


class PathsField(BaseField):
    validators = [
        lambda paths, f, n: filter(lambda _:_, map(validate_path, paths)) or None
    ]
