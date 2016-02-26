from wtforms import StringField, SubmitField, FileField, validators
from flask_wtf import Form
from app.models import User
from flask_login import current_user


class EditProfileForm(Form):
    profile_pic = FileField("Select file")
    name = StringField("Name", validators=[validators.DataRequired()])
    email = StringField("Email", validators=[validators.Email()])
    submit = SubmitField("Save")

    def validate(self, **kwargs):
        valid = Form.validate(self)
        if User.query.filter_by(
                email=self.email.data).filter(
                    User.email != current_user.email).first() is not None:
            self.email.errors.append("Email already in use")
            valid = False

        return valid
