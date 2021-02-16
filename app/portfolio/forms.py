from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class ProjectPortfolioForm(FlaskForm):
    title_bg = StringField('Title Post', validators=[DataRequired(), Length(min=12, max=80)])
    description_bg = StringField('Description Post', validators=[DataRequired(), Length(min=12, max=240)])

    title_intro = StringField('Title Intro', validators=[DataRequired(), Length(min=2, max=120)])
    description_intro = TextAreaField('Description Intro', validators=[DataRequired()])
    title_end = StringField('Title End', validators=[Length(min=2, max=120)])
    description_end = TextAreaField('Description End', validators=[])
    badges = SelectField('Categorii proiect', choices=[], coerce=int)

    submit = SubmitField('Submit')