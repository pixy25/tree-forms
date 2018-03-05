from validators import (
    ChoiceValidator,
    FieldSequenceValidator,
    FieldDictValidator,
    ValidationError,
    TypeValidator,
    FormValidator,
    EitherValidator
)


class Field(object):
    validators = []

    def add_validators(self, *validators):
        if not hasattr(self, '_validators'):
            self._validators = self.validators[:]
        self._validators.extend(validators)

    def __init__(self, validators=None):
        if validators:
            self.add_validators(*validators)
        else:
            self.add_validators()

    def validate(self, data):
        errors = []
        for validator in self._validators:
            try:
                validator(data)
            except ValidationError as ve:
                errors.append(ve.data)
        return errors


class TextField(Field):
    validators = [TypeValidator(str, 'Should be string')]


class IntField(Field):
    validators = [TypeValidator(int, 'Should be integer')]


class FormField(Field):

    def __init__(self, form_class, *args, **kwargs):
        self.add_validators(FormValidator(form_class))
        super().__init__(*args, **kwargs)

class ListField(Field):

    def __init__(self, field, min_len=0, max_len=None, *args, **kwargs):
        self.add_validators(FieldSequenceValidator(field, min_len, max_len))
        super().__init__(*args, **kwargs)


class DictField(Field):

    def __init__(self, field, keys_validator=None, *args, **kwargs):
        self.add_validators(FieldDictValidator(field, keys_validator))
        super().__init__(*args, **kwargs)


class ChoiceField(Field):

    def __init__(self, collection, *args, **kwargs):
        self.add_validators(ChoiceValidator(collection))
        super().__init__(*args, **kwargs)


class Either(Field):

    def __init__(self, fields, *args, **kwargs):
        self.add_validators(EitherValidator(fields))
        super().__init__(*args, **kwargs)

