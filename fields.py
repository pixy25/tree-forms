from collections import defaultdict
from validators import ChoiceValidator, FieldSequenceValidator, FieldDictValidator, ValidationError, TypeValidator


class Field(object):
    validators = []

    def copy(self):
        copy = self.__class__()
        copy._validators = self._validators
        return copy

    def add_validators(self, *validators):
        self._validators.extend(validators)

    def __init__(self, validators=None):
        if not hasattr(self, '_validators'):
            self._validators = self.validators[:]
        if validators:
            self.add_validators(*validators)
        else:
            self.add_validators()

    def validate(self, data, form):
        errors = []
        for validator in self._validators:
            try:
                validator(data, form)
            except ValidationError as ve:
                errors.append(ve.data)
        return errors


class TextField(Field):
    validators = [TypeValidator(str, 'Should be string')]


class IntField(Field):
    validators = [TypeValidator(int, 'Should be integer')]


class FormField(Field):
    def __init__(self, form_class, *args, **kwargs):
        if isinstance(form_class, str):
            form_class = self._form_class_from_name(form_class)

        def validate(data, form):
            inner_form = form_class(data)
            if not inner_form.validate():
                raise ValidationError(inner_form.errors)

        self.add_validators(validate)
        super().__init__(*args, **kwargs)

    def _form_class_from_name(self, cls_name):
        from forms import BaseForm
        for subclass in BaseForm.__subclasses__():
            if subclass.__name__ == cls_name:
                return subclass
        raise AttributeError('Form named %s is not defined' % cls_name)


class FieldList(Field):
    def __init__(self, field, *args, **kwargs):
        self.add_validators(FieldSequenceValidator(field))
        super().__init__(*args, **kwargs)


class FieldDict(Field):
    def __init__(self, field, keys_validator=None, *args, **kwargs):
        self.add_validators(FieldDictValidator(field, keys_validator))
        super().__init__(*args, **kwargs)


class ChoiceField(Field):
    def __init__(self, collection, *args, **kwargs):
        self.add_validators(ChoiceValidator(collection))
        super().__init__(*args, **kwargs)
