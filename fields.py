from collections import defaultdict

from utils.time import unserialize_time


def dict_to_value_paths(mapping):
    result = []

    def _helper(dct, base_path):
        for path, value in dct.items():
            if not isinstance(value, dict):
                result.append((base_path + [path], value))
            else:
                _helper(value, base_path + [path])

    _helper(mapping, [])
    return result




class BaseField(object):

    def add_validators(self, *validators):
        if not hasattr(self, '_validators'):
            self._validators = []
        self._validators.extend(validators)

    def __init__(self, validators=None):
        if validators:
            self.add_validators(*validators)
        else:
            self.add_validators()

    def __call__(self, form, data, name):
        self.form, self.data, self.name = form, data, name
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
            error = validator(self.form, self.data, self.name)
            if error:
                errors.append(error)
        return errors


class FormField(BaseField):
    def __init__(self, FormClass, *args, **kwargs):

        def validate(form, data, field_name):
            inner_form = FormClass(data)
            if not inner_form.validate():
                return inner_form.errors

        self.add_validators(validate)
        super(FormField, self).__init__(*args, **kwargs)


class FieldList(BaseField):
    def __init__(self, field_obj, *args, **kwargs):

        def validate(form, data, field_name):
            field_clbl = field_obj
            if not isinstance(field_obj, BaseField):
                field_clbl = field_clbl()  # for recursive forms
            errors = [field_clbl(form, field_data, field_name).validate() for field_data in data]
            filtered_errors = filter(lambda _:_, errors)
            return errors if filtered_errors else None

        self.add_validators(validate)
        super(FieldList, self).__init__(*args, **kwargs)


class BaseFieldDict(BaseField):
    def __init__(self, field_obj, keys_validator=None, *args, **kwargs):
        def validate(form, data, field_name):
            field_clbl = field_obj
            if not isinstance(field_obj, BaseField):
                field_clbl = field_clbl()  # for recursive forms
            key_errors = keys_validator(form, data.keys(), field_name) if keys_validator else {}
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
        def validate(form, data, field_name):
            field_clbls = field_objects
            field_clbls = [field_clbl() if not isinstance(field_clbl, BaseField) else field_clbl for field_clbl in field_clbls]
            errors = [
                field_clbl(form, field_data, field_name).validate()
                for field_clbl, field_data in zip(field_clbls, data)
            ]
            filtered_errors = filter(lambda _: _, errors)
            return errors if filtered_errors else None

        self.add_validators(validate)
        super(BaseFieldTuple, self).__init__(*args, **kwargs)



def validate_path(form, path, field):
    if not all(isinstance(elem, str) for elem in path):
        return "Path must be list of strings"


class Required(object):
    def __call__(self, form, data, field):
        if not data:
            return "Field %s required" % field


class RequiredIf(Required):
    def __init__(self, clause):
        self.clause = clause

    def __call__(self, form, data, field):
        if self.clause(form) and not data:
            return "Field %s required" % field


class NumRange(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, form, data, field):
        if self.min and data < self.min:
            return 'Must be at least %d' % self.min
        if self.max and data > self.max:
            return 'Must be less then %d' % self.max


class ChoiceValidator(object):
    def __init__(self, collection):
        self.collection = collection

    def __call__(self, form, data, field):
        if data not in self.collection:
            return 'Should be one of %s' % ', '.join(self.collection)


class TypeValidator(object):
    def __init__(self, type, msg=None):
        self.type = type
        self.msg=msg

    def __call__(self, form, elem, field):
        return not isinstance(elem, self.type) and (self.msg or 'Must be %s' % (self.type.__name__,))


class ChoiceField(BaseField):
    def __init__(self, collection, *args, **kwargs):
        self.add_validators(ChoiceValidator(collection))
        super(ChoiceField, self).__init__(*args, **kwargs)


class StringField(BaseField):
    def __init__(self, *args, **kwargs):
        self.add_validators(lambda f, s, n: (not isinstance(s, str)) and "Must be string")
        super(StringField, self).__init__(*args, **kwargs)


class DateTimeField(BaseField):
    def __init__(self, *args, **kwargs):

        def validator(form, dt, field):
            try:
                unserialize_time(dt)
                return
            except TypeError:
                return 'Expected date time string, got %s' % str(dt)

        self.add_validators(validator)
        super(DateTimeField, self).__init__(*args, **kwargs)


class IntField(BaseField):
    def __init__(self, *args, **kwargs):
        self.add_validators(TypeValidator(int))
        super(IntField, self).__init__(*args, **kwargs)


class FloatField(BaseField):
    def __init__(self, *args, **kwargs):
        def validate(form, elem, field):
            try:
                float(elem)
            except ValueError:
                return 'Must be decimal'
        self.add_validators(validate)
        super(FloatField, self).__init__(*args, **kwargs)


class StringListField(BaseField):
    def __init__(self, *args, **kwargs):
        self.add_validators(validate_path)
        super(StringListField, self).__init__(*args, **kwargs)


class BooleanField(BaseField):
    def __init__(self, *args, **kwargs):
        self.add_validators(TypeValidator(bool))
        super(BooleanField, self).__init__(*args, **kwargs)


class PathsField(BaseField):
    def __init__(self, *args, **kwargs):

        def validator(form, paths, field):
            errors = []
            for path in paths:
                error = validate_path(form, path, field)
                if error:
                    errors.append(error)
            return errors or None

        self.add_validators(validator)
        super(PathsField, self).__init__(*args, **kwargs)
