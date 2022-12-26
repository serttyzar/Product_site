from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed


class RecognizeProductForm(FlaskForm):
    photo = FileField('Фотография', validators=[FileRequired('Файл был пустой!')])
    submit = SubmitField('Распознать')

