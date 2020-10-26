import re

from .exceptions import ValidationError


class RegexpValidation:
    def __init__(self, field, **kwargs):
        self.field = field
        self.error_msg = kwargs.get(
            'invalidMsg', 'Field does not satisfy regular expression'
        )
        self.regexp = kwargs.get('extra').get('regexp', r'.*')

    def validate(self, value, full_data):
        if not re.match(self.regexp, value):
            raise ValidationError(self.error_msg, field_name=self.field.id)


class RequiredValidation:
    def __init__(self, field, **kwargs):
        self.field = field
        self.error_msg = kwargs.get(
            'invalidMsg', 'Required field'
        )

    def validate(self, value, full_data):
        if value in [None, '']:
            raise ValidationError(self.error_msg, field_name=self.field.id)


rule_mapper = {
    'required': RequiredValidation,
    'regexp': RegexpValidation
}


def build_validator(field, definition):
    validation_class = rule_mapper.get(definition.get('rule'))
    return validation_class(field, **definition)
