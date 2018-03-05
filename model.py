from sqlalchemy import inspect, Column

from forms import BaseForm


class ModelForm(BaseForm):

    def __init__(self, data):
        super().__init__(data)
        self.meta = self.Meta()
        self._model = self.meta.model

    @property
    def fields(self):
        fields = self.model_fields
        fields.update(super().fields)
        return fields

    @property
    def model_fields(self):
        model_fields = self.get_model_fields(self._model)
        fields = self.meta.fields or model_fields.keys()
        return {
            key: self.model_field_to_form_field(field)
            for key, field in model_fields.items()
            if key in fields and key not in self.meta.exclude_fields
        }

    def get_model_fields(self, model):
        raise NotImplementedError()

    def model_field_to_form_field(self, field):
        raise NotImplementedError()

    def save(self):
        self._model

    class Meta:
        fields = ()
        exclude_fields = ()


class AlchemyForm(ModelForm):
    def get_model_fields(self, model):
        mapper = inspect(model)
        return mapper.colums

    def model_field_to_form_field(self, field):
        raise NotImplementedError()