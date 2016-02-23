from wtforms import validators, StringField, SubmitField, TextAreaField, \
    DateField, RadioField
from flask_wtf import Form
from app.models import Asset


class AssetForm(Form):
    name = StringField("Name", validators=[validators.DataRequired()])
    type = StringField("Type", validators=[validators.DataRequired()])
    description = TextAreaField("Description")
    serial_no = StringField("Serial Number",
                            validators=[validators.DataRequired()])
    code = StringField("Andela Serial Code",
                       validators=[validators.DataRequired()])
    purchased = DateField("Date Purchased",
                          format='%d/%m/%Y', validators=[validators.Optional()])


class AddAssetForm(AssetForm):
    submit = SubmitField("Add Asset")

    def validate(self, **kwargs):
        valid = Form.validate(self)
        if Asset.query.filter_by(code=self.code.data).first() is not None:
            self.code.errors.append("Andela Serial Code must be unique")
            valid = False

        return valid


class EditAssetForm(AssetForm):
    submit = SubmitField("Save")

    def __init__(self, **kwargs):
        super(EditAssetForm, self).__init__()
        self.asset_id = kwargs.get('asset_id')

    def validate(self, **kwargs):
        valid = Form.validate(self)
        if Asset.query.filter_by(code=self.code.data).filter(Asset.id != self.asset_id).first() is not None:
            self.code.errors.append("Andela Serial Code must be unique")
            valid = False

        return valid


class AssignAssetForm(Form):
    user = RadioField("User to assign", coerce=int, validators=[validators.DataRequired()])
    return_date = DateField("Return date",
                            format='%d/%m/%Y')
    submit = SubmitField("Assign")