import datetime
import os

from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
import requests

from forms.user import RegisterForm
from forms.login import LoginForm
from forms.product_type_form import ProductTypeForm
from forms.product_form import ProductForm
from forms.search_form import SearchForm
from forms.new_recipe_form import NewRecipeForm
from forms.recipe_edit_form import RecipeEditForm
from forms.recipe_add_product_form import RecipeProductForm
from forms.product_list_form import ProductListForm
from forms.recognize_product_form import RecognizeProductForm
from Prediction_food_images import predict_class

from data.users import User
from data.products import Product
from data.product_types import ProductType
from data.recipes import Recipe
from data.recipes import RecipeProductAmount

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'img')
login_manager = LoginManager()
login_manager.init_app(app)


photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/data.db")
    app.run()


@app.route('/')
def index():
    return render_template('index.html', title='Домашняя страница')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

# продукты
@app.route('/products', methods=['GET', 'POST'])
def products():
    form = ProductListForm()
    filter = ''
    expiration = False
    ok_products = []
    if form.validate_on_submit():
        expiration = form.expiration.data
        filter = form.filter.data
    products = []
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        if not filter:
            products = sorted(db_sess.query(Product).filter(Product.owner_id == current_user.id).all(), key=lambda x: x.brand)
        else:
            products = sorted(db_sess.query(Product).filter(Product.owner_id == current_user.id).filter((Product.brand.like(f'%{filter.capitalize()}%'))).all(), key=lambda x: x.brand)

    now = datetime.date.today()
    for product in products:
        if product.expiration_date <= now:
            product.expiration_state = 2
        else:
            if (product.expiration_date - now).total_seconds() < 86400 * 2:
                product.expiration_state = 1
            else:
                product.expiration_state = 0
                if expiration:
                    ok_products.append(product)
    for ok_product in ok_products:
        products.remove(ok_product)
    return render_template('products.html', title='Продукты', products=products, form=form)


product_type_name_dictionary = {'frozen_yogurt': 'Йогурт', 'panna_cotta': 'Сыр'}
@app.route('/new_product', methods=['GET', 'POST'])
@login_required
def new_product():
    message = ''
    form = ProductForm()
    if form.validate_on_submit():
        if form.submit.data:
            db_sess = db_session.create_session()
            product = Product(
                type_id=form.type_id.data,
                owner_id=current_user.id,
                brand=form.brand.data.capitalize(),
                purchase_date=datetime.datetime.now(),
                product_date=form.product_date.data,
                expiration_date=form.expiration_date.data,
                amount_text=form.amount_text.data,
                amount=form.amount_text.data.split()[0]
            )
            db_sess.add(product)
            db_sess.commit()
            message = 'Успешно добавлено'
        if form.submit_recognize.data:
            filename = 'img/' + photos.save(form.photo.data)
            product_type_name = predict_class(filename)
            if product_type_name in product_type_name_dictionary.keys():
                product_type_name = product_type_name_dictionary[product_type_name]
            db_sess = db_session.create_session()
            product_type = db_sess.query(ProductType).filter(ProductType.name == product_type_name).first()
            if product_type:
                form.type_id.default = product_type.id
                form.process()
    return render_template('new_product.html', title='Добавление продукта', form=form, message=message)


@app.route('/products/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    message = ''
    form = ProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id).first()
        if product:
            form.type_id.default = product.type.id
            form.process()
            form.brand.data = product.brand
            form.product_date.data = product.product_date
            form.expiration_date.data = product.expiration_date
            form.amount_text = product.amount_text
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id).first()
        if product:
            product.type_id = form.type_id.data
            product.brand = form.brand.data
            product.product_date = form.product_date.data
            product.expiration_date = form.expiration_date.data
            product.amount_text = form.amount_text.data
            product.amount = form.amount_text.data.split()[0]
            db_sess.commit()
            return redirect('/products')
        else:
            abort(404)
    return render_template('new_product.html', form=form, title='Изменение продукта', message=message)


@app.route('/product_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def product_delete(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    if product:
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/products')


# типы продуктов
@app.route('/product_types', methods=['GET', 'POST'])
def product_types():
    form = SearchForm()
    db_sess = db_session.create_session()
    filter = ''
    if form.validate_on_submit():
        filter = form.filter.data

    db_sess = db_session.create_session()
    if not filter:
        product_types = sorted(db_sess.query(ProductType).all(), key=lambda x: x.name)
    else:
        product_types = sorted(db_sess.query(ProductType).filter
                               (ProductType.name.like(f'%{filter.capitalize()}%') | ProductType.type.like(
                                   f'%{filter.capitalize()}%')).all(), key=lambda x: x.name)
    return render_template('product_types.html', title='Виды продуктов', product_types=product_types, form=form)


@app.route('/new_product_type', methods=['GET', 'POST'])
@login_required
def new_product_type():
    message = ''
    form = ProductTypeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product_type = ProductType(
            name=form.name.data.capitalize(),
            type=form.type.data.capitalize(),
            ready_to_use=form.ready_to_use.data,
            expiration=form.expiration.data
        )
        db_sess.add(product_type)
        db_sess.commit()
        message = 'Успешно добавлено'
    return render_template('new_product_type.html', title='Добавление вида продукта', form=form, message=message)


@app.route('/product_types/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product_type(id):
    form = ProductTypeForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        product_type = db_sess.query(ProductType).filter(ProductType.id == id).first()
        if product_type:
            form.name.data = product_type.name
            form.type.data = product_type.type
            form.ready_to_use.data = product_type.ready_to_use
            form.expiration.data = product_type.expiration
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product_type = db_sess.query(ProductType).filter(ProductType.id == id).first()
        if product_type:
            product_type.name = form.name.data.capitalize()
            product_type.type = form.type.data.capitalize()
            product_type.ready_to_use = form.ready_to_use.data
            product_type.expiration = form.expiration.data
            db_sess.commit()
            return redirect('/product_types')
        else:
            abort(404)
    return render_template('edit_product_type.html', form=form, title='Изменение вида продукта')


@app.route('/product_type_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def product_type_delete(id):
    db_sess = db_session.create_session()
    product_type = db_sess.query(ProductType).filter(ProductType.id == id).first()
    if product_type:
        db_sess.delete(product_type)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/product_types')


# рецепты
@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    form = SearchForm()
    filter = ''
    if form.validate_on_submit():
        filter = form.filter.data
    recipes = []
    db_sess = db_session.create_session()
    if not filter:
        recipes = sorted(db_sess.query(Recipe).all(), key=lambda x: x.name)
    else:
        recipes = sorted(db_sess.query(Recipe).filter
                               (Recipe.name.like(f'%{filter.capitalize()}%')).all(), key=lambda x: x.name)
    return render_template('recipes.html', title='Рецепты', recipes=recipes, form=form)


@app.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def new_recipe():
    message = ''
    form = NewRecipeForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        db_sess = db_session.create_session()
        recipe = Recipe(
            name=form.name.data.capitalize(),
            description=form.description.data,
            guide=form.guide.data,
            photo_path=file_url,

        )
        db_sess.add(recipe)
        db_sess.commit()
        message = 'Успешно добавлено'
        return redirect('/recipe_info/' + str(recipe.id))
    return render_template('new_recipe.html', title='Добавление рецепта', form=form, message=message)




@app.route('/recognize_product', methods=['GET', 'POST'])
@login_required
def recognize_product():
    message = ''
    form = RecognizeProductForm()
    if form.validate_on_submit():
        filename = 'img/' + photos.save(form.photo.data)
        print(photos.save(form.photo.data))
        message = predict_class(filename)

        # file_url = photos.url(filename)
        # db_sess = db_session.create_session()
        # recipe = Recipe(
        #     name=form.name.data.capitalize(),
        #     description=form.description.data,
        #     guide=form.guide.data,
        #     photo_path=file_url,
        # )
        # db_sess.add(recipe)
        # db_sess.commit()
    return render_template('recognize_product.html', title='Распознавание продукта', form=form, message=message)


@app.route('/recipe_info/<int:id>', methods=['GET', 'POST'])
@login_required
def view_recipe(id):
    form = RecipeEditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipe).filter(Recipe.id == id).first()
        if not recipe:
            abort(404)
        return render_template('recipe_info.html', recipe=recipe, title='Редактирование рецепта')


@app.route('/recipe_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def recipe_edit(id):
    global recipe_product_amount
    form = RecipeProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipe).filter(Recipe.id == id).first()
        if not recipe:
            abort(404)
        return render_template('recipe_edit.html', recipe=recipe, title='Добавление вида продукта в рецепт', form=form)
    else:
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            recipe = db_sess.query(Recipe).filter(Recipe.id == id).first()
            recipe_product_amount = RecipeProductAmount(
                recipe_id=id,
                type_id=form.type_id.data,
                amount_text=form.amount_text.data,
                amount=form.amount_text.data.split()[0]
            )
            recipe.product_amounts.append(recipe_product_amount)
            db_sess.commit()
        return redirect('/recipe_info/' + str(id))


@app.route('/recipe_product_delete/<int:recipe_id>/<int:product_type_id>', methods=['GET'])
@login_required
def recipe_product_type_delete(recipe_id, product_type_id):
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        abort(404)
    else:
        product_amount = list(filter(lambda x: x.type_id == product_type_id, recipe.product_amounts))[0]
        if not product_amount:
            return redirect('/recipe_info/' + str(recipe_id))
        else:
            #recipe.product_amounts.remove(product_amount)
            db_sess.delete(product_amount)
            db_sess.commit()
            return redirect('/recipe_info/' + str(recipe_id))


if __name__ == '__main__':
    main()