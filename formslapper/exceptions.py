SCHEMA = '_meta'


class ValidationError(Exception):
    def __init__(self, message, field_name=SCHEMA, **kwargs):
        if isinstance(message, (str, bytes)):
            self.messages = [message]
        else:
            self.messages = message
        self.field_name = field_name
        self.kwargs = kwargs
        super().__init__(message)
