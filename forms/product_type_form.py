from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class ProductTypeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    type = StringField('Вид', validators=[DataRequired()])
    ready_to_use = BooleanField('Готовность к употреблению')
    expiration = StringField('Cрок годности(в часах)', validators=[DataRequired()])
    submit = SubmitField('Добавить вид продукта')