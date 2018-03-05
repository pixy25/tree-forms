from collections import defaultdict
from re import compile as re_compile

from utils import current_form


class ValidationError(Exception):
    def __init__(self, data, *args):
        self.data = data
        super().__init__(*args)


class Validator:
    def __init__(self, error_msg=None):
        self.error_msg = error_msg

    def validate(self, data):
        raise NotImplementedError()

    def __call__(self, data):
        if not self.validate(data):
            raise ValidationError(self.error_msg)


class FormValidator:

    def __init__(self, form_class):
        self.form_class = form_class

    def _get_actual_form_class(self):
        from forms import BaseForm
        if not isinstance(self.form_class, str):
            return self.form_class
        if self.form_class == 'self':
            return current_form().__class__
        for subclass in BaseForm.__subclasses__():
            if subclass.__name__ == self.form_class:
                return subclass
        raise AttributeError('Form named %s is not defined' % self.form_class)

    def __call__(self, data):
        form_class = self._get_actual_form_class()
        form = form_class(data)
        if not form.validate():
            raise ValidationError(form.errors)


class If(Validator):
    def __init__(self, clause, validators=None, error_msg=None):
        self.validators = validators or ()
        self.clause = clause
        super().__init__(error_msg)

    def validate(self, data):
        if self.clause(current_form().data):
            for validate in self.validators:
                validate(data)
        return True


class TypeValidator(Validator):
    def __init__(self, expected_type, error_msg):
        self.expected_type = expected_type
        super().__init__(error_msg)

    def validate(self, data):
        return isinstance(data, self.expected_type)


class Required(Validator):
    def __init__(self, error_msg="Field is required"):
        super().__init__(error_msg)

    def validate(self, data):
        return data not in ('', {}, [], None)


def RequiredIf(clause, error_msg="Field is required"):
    return If(clause, (Required(), ), error_msg)


class RegexValidator(Validator):
    def __init__(self, regex, error_msg):
        self.regex = re_compile(regex)
        super().__init__(error_msg)

    def validate(self, data):
        return self.regex.fullmatch(data)


class NumRange(Validator):
    def __init__(self, minimum=None, maximum=None, error_msg='Must be from {} to {}'):
        self.min = minimum
        self.max = maximum
        super().__init__(error_msg)
        self.error_msg = self.error_msg.format(self.min, self.max)

    def validate(self, data):
        less_then = self.min and data < self.min
        more_than = self.max and data > self.max
        return not less_then and not more_than


class LenValidator(NumRange):
    def __init__(self, minimum=None, maximum=None, error_msg='From {} to {} elements expected'):
        super().__init__(minimum, maximum, error_msg)

    def validate(self, data):
        return super().validate(len(data))


class ChoiceValidator(Validator):
    def __init__(self, collection, error_msg=None):
        self.collection = collection
        super().__init__(error_msg or 'Should be one of %s' % ', '.join(self.collection))

    def validate(self, data):
        return data in self.collection


class BaseFieldCollectionValidator:

    def __init__(self, field):
        self.field_obj = field

    def _validate(self, data):
        for key, field_data in data:
            errors = self.field_obj.validate(field_data)
            if errors:
                yield key, errors


class FieldSequenceValidator(BaseFieldCollectionValidator):

    def __init__(self, field, min_len=0, max_len=None):
        super().__init__(field)
        self.min_len = min_len
        self.max_len = max_len

    def __call__(self, data):
        errors = []
        range_validator = LenValidator(self.min_len, self.max_len)
        range_validator(data)
        for i, field_errors in self._validate(enumerate(data)):
            if field_errors:
                errors.extend(field_errors)
        if errors:
            raise ValidationError(errors)


class FieldDictValidator(BaseFieldCollectionValidator):

    def __init__(self, field, key_validator=None):
        super().__init__(field)
        self.key_validator = key_validator

    def __call__(self, data):
        errors = defaultdict(list)
        for key, field_errors in self._validate(data.items()):
            if field_errors:
                errors[key].extend(field_errors)
            if self.key_validator:
                try:
                    self.key_validator(key)
                except ValidationError as ve:
                    key_error = ve.data
                    errors[key].append(key_error)
        errors = dict(errors)
        if errors:
            raise ValidationError(errors)


class EitherValidator:

    def __init__(self, fields):
        self.fields = fields

    def _validate(self, data):
        for field in self.fields:
            errors = field.validate(data)
            if errors:
                yield errors

    def __call__(self, data):
        errors = [field.validate(data) for field in self.fields]
        if all(errors):
            raise ValidationError(errors)
