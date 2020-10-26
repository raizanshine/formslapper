import datetime
from copy import deepcopy

from .exceptions import ValidationError


class TextValue:
    python_class = str

    def __init__(self, raw_value, field):
        self.field = field
        self.raw_value = raw_value
        self.clean_value = self.get_clean_value(raw_value)

    def get_clean_value(self, raw_value):
        if self.field.is_multiple:
            return [self.python_class(v) for v in raw_value]
        return self.python_class(raw_value)

    @classmethod
    def validate(cls, value, field):
        if not isinstance(value, str):
            raise ValidationError(
                'Value must be a string', field_name=field.id
            )


class LocaleTextValue(TextValue):
    python_class = dict

    @classmethod
    def validate(cls, value, field):
        if not isinstance(value, dict):
            raise ValidationError(
                'Value must be an object', field_name=field.id
            )


class GroupValue(TextValue):
    def get_clean_value(self, raw_value):
        nested = self.field.nested
        clean_value = []
        for obj in raw_value:
            nested = deepcopy(nested)
            nested.bind_data(obj)
            clean_value.append(nested)

        return clean_value

    @classmethod
    def validate(cls, value, field, index=0):
        try:
            field.nested.validate(value)
        except ValidationError as e:
            raise ValidationError(e.messages, field_name=field.id)


class DateValue(TextValue):
    python_class = datetime.date


class DateTimeValue(TextValue):
    python_class = datetime.datetime

    def get_clean_value(self, raw_value):
        return datetime.datetime.strptime(raw_value, '%Y-%m-%dT%H:%M:%S')


class BooleanValue(TextValue):
    python_class = bool

    truthy = {
        "t", "T", "true", "True", "TRUE", "on", "On", "ON", "y", "Y", "yes",
        "Yes", "YES", "1", 1, True,
    }
    falsy = {
        "f", "F", "false", "False", "FALSE", "off", "Off", "OFF", "n",
        "N", "no", "No", "NO", "0", 0, 0.0, False,
    }

    @classmethod
    def validate(cls, value, field):
        if value not in cls.truthy | cls.falsy:
            raise ValidationError(
                'Value is not a valid boolean type',
                field_name=field.id
            )

    def get_clean_value(self, raw_value):
        if raw_value in self.truthy:
            return True
        if raw_value in self.falsy:
            return False
        return None


class IntegerValue(TextValue):
    python_class = int

    @classmethod
    def validate(cls, value, field):
        if not isinstance(value, int):
            raise ValidationError(
                'Value is not an integer', field_name=field.id
            )


class FloatValue(TextValue):
    python_class = float


meta_value_types = {
    'text': TextValue,
    'locale_text': LocaleTextValue,
    'date': DateValue,
    'datetime': DateTimeValue,
    'integer': IntegerValue,
    'float': FloatValue,
    'boolean': BooleanValue,
}
