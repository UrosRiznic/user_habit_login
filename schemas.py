from marshmallow import Schema, fields

class PlainHabitSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    checked = fields.Str(required=True)

class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    pwd = fields.Str(required=True, load_only=True)

class HabitSchema(PlainHabitSchema):
    user_id = fields.Int(required=True, load_only=True)
    user = fields.Nested(PlainUserSchema(), dump_only=True)

class HabitUpdateSchema(Schema):
    name = fields.Str()
    checked = fields.Str()
    user_id = fields.Int()

class UserSchema(PlainUserSchema):
    items = fields.List(fields.Nested(PlainHabitSchema()), dump_only=True)