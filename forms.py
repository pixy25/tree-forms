from wtforms import Form


class BaseForm(object):

    def __init__(self, data):
        self._data = data
        self._structure = {}
        self._validated = False
        to_delete = [field for field in self._data if field not in self.fields]
        for field in to_delete:
            del self._data[field]
        for field_name, field in self.fields.items():
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

