from wtforms import validators, StringField, SubmitField, TextAreaField, \
    DateField, RadioField
from flask_wtf import Form


class AddAssetForm(Form):
    name = StringField("Name", validators=[validators.DataRequired()])
    type = StringField("Type", validators=[validators.DataRequired()])
    description = TextAreaField("Description")
    serial_no = StringField("Serial Number",
                            validators=[validators.DataRequired()])
    code = StringField("Andela Serial Code",
                       validators=[validators.DataRequired()])
    purchased = DateField("Date Purchased",
                          format='%d/%m/%Y', validators=[validators.Optional()])
    submit = SubmitField("Add Asset")


class AssignAssetForm(Form):
    user = RadioField("User to assign", coerce=int, validators=[validators.DataRequired()])
    return_date = DateField("Return date",
                            format='%d/%m/%Y')
    submit = SubmitField("Assign")
