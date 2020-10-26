from copy import deepcopy

from .exceptions import ValidationError
from .fields import create_field_from_definition


class FormSchema:
    def __init__(self, json_definition: list, **kwargs):
        """
        Инициализация класса мета схемы
        :param json_definition: Определение полей в meta.json
        """
        json_definition = deepcopy(json_definition)
        self._fields = []
        self.data = None
        self.valuable = {}
        self.options = kwargs

        while json_definition:
            field_definition = json_definition.pop(0)
            field = create_field_from_definition(
                field_definition, json_definition
            )
            field.meta = self

            self._fields.append(field)
            if field.can_store_value:
                self.valuable[field.id] = field
                json_definition = field.update_schema(json_definition)

    def validate(self, data):
        errors = {}
        if not isinstance(data, dict):
            raise ValidationError('Data must be a dictionary')

        if not all(isinstance(x, str) for x in data.keys()):
            raise ValidationError('Dictionary keys must be only strings')

        for k, v in data.items():
            try:
                field = self.get_field(k)
                if field is None:
                    raise ValidationError(
                        'Unknown field', field_name=k
                    )
                if not field.can_store_value:
                    raise ValidationError(
                        'Field cannot store a value',
                        field_name=field.id
                    )
                field.full_validate(v, data)
            except ValidationError as e:
                errors[e.field_name] = e.messages
        if errors:
            raise ValidationError(errors)

    def get_field(self, k):
        for field in self._fields:
            if field.id == k:
                return field

    def bind_data(self, data):
        self.validate(data)
        for k, v in data.items():
            field = self.valuable.get(k)
            field.bind(v)

        self.data = data
