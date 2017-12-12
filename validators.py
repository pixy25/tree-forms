from collections import defaultdict


class ValidationError(Exception):
    def __init__(self, data, *args):
        self.data = data
        super().__init__(*args)


class TypeValidator:
    def __init__(self, expected_type, error_msg):
        self.expected_type = expected_type
        self.error_msg = error_msg

    def __call__(self, data, form):
        if not isinstance(data, self.expected_type):
            raise ValidationError(self.error_msg)


class Required:
    def __call__(self, data, form):
        if data in ('', {}, [], None):
            raise ValidationError("Field is required")


class RequiredIf(Required):
    def __init__(self, clause):
        self.clause = clause

    def __call__(self, data, form):
        if self.clause(form):
            super().__call__(data, form)


class NumRange:
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, data, form):
        if self.min and data < self.min:
            raise ValidationError('Must be at least %d' % self.min)
        if self.max and data > self.max:
            raise ValidationError('Must be less then %d' % self.max)


class ChoiceValidator:
    def __init__(self, collection):
        self.collection = collection

    def __call__(self, data, form):
        if data not in self.collection:
            raise ValidationError('Should be one of %s' % ', '.join(self.collection))


class BaseFieldCollectionValidator:

    def __init__(self, field):
        self.field_obj = field

    def _validate(self, data, form):
        for key, field_data in data:
            errors = self.field_obj(form, field_data, key).validate()
            if errors:
                yield key, errors


class FieldSequenceValidator(BaseFieldCollectionValidator):
    def __call__(self,  data, form):
        errors = []
        for _, field_errors in self._validate(enumerate(data), form):
            if field_errors:
                errors.extend(field_errors)
        if errors:
            raise ValidationError(errors)


class FieldDictValidator(BaseFieldCollectionValidator):

    def __init__(self, field, key_validator=None):
        super().__init__(field)
        self.key_validator = key_validator

    def __call__(self, data, form):
        result = defaultdict(list)
        for key, field_errors in self._validate(data.items(), form):
            if field_errors:
                result[key].extend(field_errors)
            if self.key_validator:
                try:
                    self.key_validator(key)
                except ValidationError as ve:
                    key_errors = ve.data
                    if type(key_errors) == list:
                        result[key].extend(key_errors)
                    else:
                        result[key].append(key_errors)
