from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email

class ContactForm(FlaskForm):
    name = StringField('Nume intreg', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Numar de Telefon', validators=[DataRequired()])
    message = TextAreaField('Mesajul Dumneavoastra', validators=[Length(min=30)])

    contact_submit = SubmitField('Contacteaza-ne')

class EmployeeForm(FlaskForm):
    name = StringField('Nume intreg', validators=[DataRequired()])
    about = TextAreaField('Despre acest angajat', validators=[Length(min=20)])
    job = SelectField('Tipuri munca', choices=[], coerce=int)

    employeeform_submit = SubmitField('Inscrie')

class NoCheckInForm(FlaskForm):
    observation = TextAreaField('Observatii despre muncitor', validators=[Length(min=30)])

    no_checkin_submit = SubmitField('Trimite')