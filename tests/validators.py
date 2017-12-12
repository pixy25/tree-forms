__all__ = []

def validate_path(path, form=None, field=None):
    if not all(isinstance(elem, str) for elem in path):
        return "Path must be list of strings"


class Required(object):
    def __call__(self, data, form, field):
        if not data:
            return "Field %s required" % field


class RequiredIf(Required):
    def __init__(self, clause):
        self.clause = clause

    def __call__(self, data, form, field):
        if self.clause(form) and not data:
            return "Field %s required" % field


class NumRange(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, data, form, field):
        if self.min and data < self.min:
            return 'Must be at least %d' % self.min
        if self.max and data > self.max:
            return 'Must be less then %d' % self.max


class ChoiceValidator(object):
    def __init__(self, collection):
        self.collection = collection

    def __call__(self, data, form, field):
        if data not in self.collection:
            return 'Should be one of %s' % ', '.join(self.collection)


class TypeValidator(object):
    def __init__(self, type, msg=None):
        self.type = type
        self.msg=msg

    def __call__(self, elem, form, field):
        return not isinstance(elem, self.type) and (self.msg or 'Must be %s' % (self.type.__name__,))


def ConversionValidator(con, error_message, error_class=TypeError):
    def validator(f, data, n):
        try:
            con(data)
        except error_class:
            return error_message
    return validator