import pytest

from formslapper.exceptions import ValidationError
from formslapper.forms import FormSchema


@pytest.mark.parametrize('value', (None, {'ru': 'test'}, 1, True))
def test_invalid_data_for_text_field(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'text'
    }]
    schema = FormSchema(schema)
    with pytest.raises(ValidationError):
        schema.bind_data({'test_field': value})


@pytest.mark.parametrize('value', ('text', 'текст'))
def test_valid_data_for_text_field(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'text'
    }]
    schema = FormSchema(schema)
    schema.bind_data({'test_field': value})
    assert schema.valuable['test_field'].value.raw_value == value


@pytest.mark.parametrize('value', (None, {'ru': 'test'}, 'int'))
def test_invalid_data_for_integer_value_type(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'integer'
    }]
    schema = FormSchema(schema)
    with pytest.raises(ValidationError):
        schema.bind_data({'test_field': value})


@pytest.mark.parametrize('value', (0, 10, -10))
def test_valid_data_for_integer_value_type(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'integer'
    }]
    schema = FormSchema(schema)
    schema.bind_data({'test_field': value})
    assert schema.valuable['test_field'].value.raw_value == value


@pytest.mark.parametrize('value', (None, 42, 'int'))
def test_invalid_data_for_locale_text_value_type(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'locale_text'
    }]
    schema = FormSchema(schema)
    with pytest.raises(ValidationError):
        schema.bind_data({'test_field': value})


@pytest.mark.parametrize('value', (
        {'en': 'value', 'ru': 'значение'},
        {'en': 'value'},
        {'ru': 'значение'},
))
def test_valid_data_for_locale_text_value_type(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'locale_text'
    }]
    schema = FormSchema(schema)
    schema.bind_data({'test_field': value})
    assert schema.valuable['test_field'].value.raw_value == value


@pytest.mark.parametrize('value,error_msg', (
        (None, ['Field value must be a list']),
        (42, ['Field value must be a list']),
        ('int', ['Field value must be a list']),
        ([{'another_field': 'value'}], {0: {'another_field': ['Unknown field']}}),
        ([{}], {0: ['Objects cannot be empty']})))
def test_valid_error_messages_for_group_field(value, error_msg):
    schema = [{
        'id': 'test_field',
        'type': 'group',
        'multiple': True
    }, {
        'id': 'child_field',
        'parent': 'test_field',
        'type': 'text'
    }]
    schema = FormSchema(schema)
    with pytest.raises(ValidationError) as excinfo:
        schema.bind_data({'test_field': value})

    assert error_msg == excinfo.value.messages['test_field']


@pytest.mark.parametrize('value', (None, 42, 'int'))
def test_invalid_data_for_boolean_value_type(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'boolean'
    }]
    schema = FormSchema(schema)
    with pytest.raises(ValidationError) as excinfo:
        schema.bind_data({'test_field': value})

    error_msg = ['Value is not a valid boolean type']
    assert error_msg == excinfo.value.messages['test_field']


@pytest.mark.parametrize('value', (
        "t", "T", "true", "True", "TRUE", "on", "On", "ON", "y", "Y", "yes",
        "Yes", "YES", "1", 1, True))
def test_valid_true_data_for_boolean_value_type(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'boolean'
    }]
    schema = FormSchema(schema)
    schema.bind_data({'test_field': value})
    assert schema.valuable['test_field'].value.clean_value is True


@pytest.mark.parametrize('value', (
        "f", "F", "false", "False", "FALSE", "off", "Off", "OFF", "n",
        "N", "no", "No", "NO", "0", 0, 0.0, False))
def test_valid_false_data_for_boolean_value_type(value):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'boolean'
    }]
    schema = FormSchema(schema)
    schema.bind_data({'test_field': value})
    assert schema.valuable['test_field'].value.clean_value is False


@pytest.mark.parametrize('error_msg', (
    'Field is required',
    'Fill the field'
))
def test_required_validator(error_msg):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        "validation": [
            {
                "invalidMsg": error_msg,
                "rule": "required"
            }
        ]
    }]
    schema = FormSchema(schema)
    with pytest.raises(ValidationError) as excinfo:
        schema.bind_data({'test_field': ''})

    assert [error_msg] == excinfo.value.messages['test_field']


@pytest.mark.parametrize('error_msg', (
    'Wrong value',
    'Fill the value according to regexp'
))
def test_regexp_validator_shows_correct_error_message(error_msg):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        "validation": [
          {
            "invalidMsg": error_msg,
            "rule": "regexp",
            "extra": {
              "regexp": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]+$"
            }
          }
        ]
    }]
    schema = FormSchema(schema)
    with pytest.raises(ValidationError) as excinfo:
        schema.bind_data({'test_field': 'test_value'})

    assert [error_msg] == excinfo.value.messages['test_field']
