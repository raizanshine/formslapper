import pytest

from formslapper.exceptions import ValidationError
from formslapper.forms import FormSchema


@pytest.mark.parametrize('data', ('data', [], None, False, 0, 1))
def test_schema_should_accept_only_dict(data):
    schema = [{
        'id': 'test_field',
        'type': 'text',
        'valueType': 'text'
    }]
    schema = FormSchema(schema)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(data)
    assert excinfo.value.messages == ['Data must be a dictionary']
