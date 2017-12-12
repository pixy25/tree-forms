from fields import BaseField


class FormMeta(type):
    def __new__(mcls, name, bases, namespace):
        namespace['_fields'] = property(lambda self: {
            key: value.copy()
            for key, value in namespace.items()
            if isinstance(value, BaseField)
        })

        super(FormMeta, mcls).__new__(name, bases, namespace)


class BaseForm(object):

    def __init__(self, data):
        self._data = data
        self._structure = {}
        self._validated = False
        to_delete = [field for field in self._data if field not in self._fields]
        for field in to_delete:
            del self._data[field]
        for field_name, field in self._fields.items():
            self._structure[field_name] = field(self, self.get(field_name), field_name)

    def validate(self):
        self.errors = {}
        for key, val in self._structure.items():
            error_structure = val.validate()
            if error_structure:
                self.errors[key] = error_structure
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
