import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class ProductType(SqlAlchemyBase):
    __tablename__ = 'product_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ready_to_use = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    expiration = sqlalchemy.Column(sqlalchemy.Integer)


