from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
    URLField,
    RadioField
)

from wtforms.validators import (
    InputRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    DataRequired,
    ValidationError
)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), 
    Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    pwd = PasswordField(validators=[InputRequired(), 
    Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data
        ).first()
        if existing_user_username:
            raise ValidationError("That username alredy exists.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), 
    Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    pwd = PasswordField(validators=[InputRequired(), 
    Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    submit = SubmitField("Login")