from fields import Field
from utils import set_current_form, rollback_current_form


class BaseForm:

    def __init__(self, data):
        set_current_form(self)
        self.fields = {
            key: field
            for key, field in (self.__dict__).items()
            if isinstance(field, Field)
        }
        self._data = data
        self._validated = False
        self.errors = {}

    def __del__(self):
        rollback_current_form()


    def validate(self):
        for field_name, field in self.fields.items():
            field_errors = field.validate(self.get(field_name))
            if field_errors:
                self.errors[field_name] = field_errors
        if self.errors:
            return False
        self._validated = True
        return True

    @property
    def data(self):
        if self._validated:
            return self._data

    def get(self, name):
        return self._data.get(name)
