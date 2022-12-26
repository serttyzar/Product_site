import sqlalchemy
from sqlalchemy import orm, Table
from .db_session import SqlAlchemyBase


class RecipeProductAmount(SqlAlchemyBase):
    __tablename__ = 'product_amount'
    recipe_id = sqlalchemy.Column('recipe_id', sqlalchemy.Integer, sqlalchemy.ForeignKey("recipes.id"), primary_key=True)
    type_id = sqlalchemy.Column('type_id', sqlalchemy.Integer, sqlalchemy.ForeignKey("product_types.id"), primary_key=True)
    amount_text = sqlalchemy.Column('amount_text', sqlalchemy.String)
    amount = sqlalchemy.Column('amount', sqlalchemy.Float)
    product_type = orm.relationship("ProductType")


class Recipe(SqlAlchemyBase):
    __tablename__ = 'recipes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.Text)
    guide = sqlalchemy.Column(sqlalchemy.Text)
    photo_path = sqlalchemy.Column(sqlalchemy.String, default='without_photo')
    product_amounts = orm.relationship("RecipeProductAmount")


