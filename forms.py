from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class CustomerForm(FlaskForm):
    name = StringField('Namn', validators=[DataRequired()])
    contact = StringField('Kontaktperson')
    phone = StringField('Telefon')
    email = StringField('E-post')
    notes = TextAreaField('Anteckningar')

    invoice_row1 = StringField('Address')
    invoice_row2 = StringField('')
    invoice_zip_code = StringField('Postkod')
    invoice_postal = StringField('Postort')

    visitation_row1 = StringField('Address')
    visitation_row2 = StringField('')
    visitation_zip_code = StringField('Postkod')
    visitation_postal = StringField('Postort')