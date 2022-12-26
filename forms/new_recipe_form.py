from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed


class NewRecipeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание')
    guide = TextAreaField('Инструкция по приготовлению')
    photo = FileField('Фотография', validators=[FileRequired('Файл был пустой!')])
    submit = SubmitField('Добавить рецепт')

