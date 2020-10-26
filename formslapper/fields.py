from .exceptions import ValidationError
from .mappers import Option
from .validators import build_validator
from .values import TextValue, GroupValue, meta_value_types


class Field:
    value_class = TextValue
    nested = None
    value = None

    def __init__(self, **kwargs):
        self.meta = None
        self.id = kwargs.get('id')
        self.is_multiple = kwargs.get('multiple', False)
        self.title = kwargs.get('title', '')
        self.type = kwargs.get('type')
        self.description = kwargs.get('description')
        self.value_type = kwargs.get('valueType')
        if self.value_type:
            self.value_class = meta_value_types[kwargs['valueType']]
        self.extra = kwargs.get('extra', {})
        self.validators = [
            build_validator(self, validation)
            for validation in kwargs.get('validation', [])
        ]

    @property
    def can_store_value(self):
        return True

    @property
    def is_group(self):
        return self.type == 'group'

    @property
    def is_file(self):
        return self.type == 'file'

    @property
    def is_select(self):
        return self.type == 'select'

    def update_schema(self, definition):
        return definition

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f'<{class_name}(id={self.id} title={self.title})'
        )

    def bind(self, value):
        self.value = self.value_class(value, self)

    def run_validators(self, value, full_data):
        for validator in self.validators:
            validator.validate(value, full_data)

    def validate_value(self, value):
        pass

    def _validate_value(self, value, full_data):
        self.value_class.validate(value, self)
        self.validate_value(value)
        self.run_validators(value, full_data)

    def full_validate(self, value, full_data):
        if self.is_multiple and not isinstance(value, list):
            raise ValidationError(
                'Field value must be a list', field_name=self.id
            )

        if self.is_multiple:
            errors = {}
            for index, v in enumerate(value):
                try:
                    self._validate_value(v, full_data)
                except ValidationError as e:
                    errors[index] = e.messages
            if errors:
                raise ValidationError(errors, field_name=self.id)
        else:
            self._validate_value(value, full_data)


class TextField(Field):
    pass


class SelectField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = [Option(**opt) for opt in kwargs.get('options')]

    def validate_value(self, value):
        if not any([value == opt.value for opt in self.options]):
            raise ValidationError(
                f'Incorrect value: {value}', field_name=self.id
            )


class GroupField(Field):
    value_class = GroupValue

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        schema = kwargs.get('schema')
        parents = [self.id]

        for field in schema:
            if field.get('parent') in parents:
                parents.append(field['id'])

        children_field_definition = [
            v for v in schema if v.get('parent') in parents
        ]
        self.children_field_ids = [
            v['id'] for v in children_field_definition
        ]
        from .forms import FormSchema
        self.nested = FormSchema(children_field_definition)

    def update_schema(self, definition):
        return [
            v for v in definition
            if v['id'] not in self.children_field_ids
        ]

    def validate_value(self, value):
        if isinstance(value, dict) and not value:
            raise ValidationError(
                'Objects cannot be empty',
                field_name=self.id
            )


def create_field_from_definition(field_definition, full_schema):
    cls_mapper = {
        'text': TextField,
        'select': SelectField,
        'group': GroupField,
    }
    field_class = cls_mapper[field_definition['type']]
    return field_class(schema=full_schema, **field_definition)
