from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from forms.search_form import SearchForm


class ProductListForm(SearchForm):
    expiration = BooleanField('Срок годности')
    filter = StringField('Найти')
