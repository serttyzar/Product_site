import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    type_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("product_types.id"))
    type = orm.relation("ProductType")
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    brand = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    purchase_date = sqlalchemy.Column(sqlalchemy.DateTime)
    product_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    expiration_date = sqlalchemy.Column(sqlalchemy.Date)
    amount_text = sqlalchemy.Column(sqlalchemy.String)
    amount = sqlalchemy.Column(sqlalchemy.Float)


