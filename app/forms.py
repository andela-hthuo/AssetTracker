from wtforms import StringField, SubmitField, PasswordField,\
    validators
from flask_wtf import Form
from models import User


class LoginForm(Form):
    email = StringField("Email", validators=[validators.Email()])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    submit = SubmitField("Log In")


class SignUpForm(Form):
    name = StringField("Name", validators=[validators.DataRequired()])
    email = StringField("Email", validators=[validators.DataRequired()])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    confirm = PasswordField("Confirm password", validators=[validators.DataRequired()])
    submit = SubmitField("Sign Up")

    def validate(self, **kwargs):
        valid = Form.validate(self)
        if User.query.filter_by(email=self.email.data).first() is not None:
            self.email.errors.append("Email already in use")
            valid = False

        if self.confirm.data != self.password.data:
            self.confirm.errors.append("Confirmation doesn't match password")
            valid = False

        return valid
