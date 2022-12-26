from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired
from data import db_session
from data.product_types import ProductType
from flask_wtf.file import FileField, FileRequired
import datetime


class ProductForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        db_sess = db_session.create_session()
        product_types = db_sess.query(ProductType).all()
        self.type_id.choices = [(g.id, g.name) for g in product_types]
        if not self.product_date.data:
            self.product_date.data = datetime.date.today()
        if not self.expiration_date.data:
            self.expiration_date.data = datetime.date.today()
    type_id = SelectField('Вид', default=1)
    brand = StringField('Название')
    photo = FileField('Фотография')
    submit_recognize = SubmitField('Распознать')
    product_date = DateField('Дата изготовления')
    expiration_date = DateField('Срок годности')
    amount_text = StringField('Количество(мл / г)')
    submit = SubmitField('Добавить продукт')
    # type_id = SelectField('Вид', default=1)
    # brand = StringField('Название')
    # photo = FileField('Фотография', validators=[FileRequired('Файл был пустой!')])
    # submit_recognize = SubmitField(label='Распознать')
    # product_date = DateField('Дата изготовления')
    # expiration_date = DateField('Срок годности')
    # amount_text = StringField('Количество(мл / г)')
    # submit = SubmitField(label='Добавить продукт')


