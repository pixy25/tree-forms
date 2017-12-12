from fields import Field


__all__ = ['BaseForm']


class FormMeta(type):
    def __new__(mcls, name, bases, namespace):
        namespace['_fields'] = property(lambda self: {
            key: value.copy()
            for key, value in namespace.items()
            if isinstance(value, Field)
        })

        super(FormMeta, mcls).__new__(name, bases, namespace)


class BaseForm(object):

    def __init__(self, data: dict):
        self._data = data
        self._validated = False
        self._clean_data()
        self.errors = {}

    def _clean_data(self):
        for field in self._data:
            if field not in self._fields:
                del self._data[field]

    def validate(self):
        for field_name, field in self._fields.items():
            field_errors = field.validate(self, self.get(field_name))
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
