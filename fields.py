from collections import defaultdict
from validators import ChoiceValidator, FieldSequenceValidator, FieldDictValidator, ValidationError


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
        errors = []
        for validator in self._validators:
            try:
                validator(self.data, self.form, self.name)
            except ValidationError as ve:
                errors.append(ve.data)
        return errors


class FormField(BaseField):
    def __init__(self, FormClass, *args, **kwargs):
        if isinstance(FormClass, str):
            FormClass = self._form_class_from_name(FormClass)

        def validate(data, form, field_name):
            inner_form = FormClass(data)
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


class FieldList(BaseField):
    def __init__(self, field, *args, **kwargs):
        self.add_validators(FieldSequenceValidator(field))
        super().__init__(*args, **kwargs)


class FieldDict(BaseField):
    def __init__(self, field, keys_validator=None, *args, **kwargs):
        self.add_validators(FieldDictValidator(field, keys_validator))
        super().__init__(*args, **kwargs)


class ChoiceField(BaseField):
    def __init__(self, collection, *args, **kwargs):
        self.add_validators(ChoiceValidator(collection))
        super().__init__(*args, **kwargs)
