from marshmallow import Schema, fields
from marshmallow.validate import Length


class InputModel(Schema):
    content = fields.Str()
    hashtags = fields.List(fields.String(required=True, validate=Length(min=3)),
                           required=True,
                           validate=Length(min=1)
                           )