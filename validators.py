__all__ = []


class ValidationError(Exception):
    def __init__(self, data, *args):
        self.data = data
        super().__init__(*args)


class Required:
    def __call__(self, data, form, field):
        if not data:
            raise ValidationError("Field %s required" % field)


class RequiredIf(Required):
    def __init__(self, clause):
        self.clause = clause

    def __call__(self, data, form, field):
        if self.clause(form) and not data:
            raise ValidationError("Field %s required" % field)


class NumRange:
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, data, form, field):
        if self.min and data < self.min:
            raise ValidationError('Must be at least %d' % self.min)
        if self.max and data > self.max:
            raise ValidationError('Must be less then %d' % self.max)


class ChoiceValidator:
    def __init__(self, collection):
        self.collection = collection

    def __call__(self, data, form, field):
        if data not in self.collection:
            raise ValidationError('Should be one of %s' % ', '.join(self.collection))


class BaseFieldCollectionValidator:

    def __init__(self, field):
        self.field_obj = field

    def _validate(self, data, form, field):
        for key, field_data in data:
            errors = self.field_obj(form, field_data, key).validate()
            if errors:
                yield key, errors


class FieldSequenceValidator(BaseFieldCollectionValidator):
    def __call__(self,  data, form, field):
        errors = []
        for _, field_errors in self._validate(enumerate(data), form, field):
            if field_errors:
                errors.extend(field_errors)
        if errors:
            raise ValidationError(errors)


class FieldDictValidator(BaseFieldCollectionValidator):

    def __init__(self, field, key_validator=None):
        super().__init__(field)
        self.key_validator = key_validator

    def __call__(self, data, form, field):
        from collections import defaultdict
        result = defaultdict(list)
        for key, field_errors in self._validate(data.items(), form, field):
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
