from wtforms import StringField, SubmitField, PasswordField,\
    validators
from flask_wtf import Form


class LoginForm(Form):
    email = StringField("Email", validators=[validators.Email()])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    submit = SubmitField("Log In")
