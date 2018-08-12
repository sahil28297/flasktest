from flask import render_template, url_for, flash, redirect, request, abort
from hello import app, db, bcrypt
from hello.forms import RegistrationForm, LoginForm, UpdateAccountForm, ProductForm, LocationForm, MoveProductForm
from hello.models import User, Product, Location, ProductMovement
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    movements = ProductMovement.query.all()
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('home.html', products=products, locations=locations, movements=movements)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        return render_template('account.html', title='New Product',
                               form=form, legend='New Product')


@app.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, author=current_user)
        db.session.add(product)
        db.session.commit()
        flash('Your product has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_product.html', title='New Product',
                           form=form, legend='New Product')


@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', name=product.name, product=product)


@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        db.session.commit()
        flash('Your product has been updated!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.name.data = product.name
    return render_template('create_product.html', title='Update Product',
                           form=form, legend='Update Product')


@app.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/location/new", methods=['GET', 'POST'])
@login_required
def new_location():
    form = LocationForm()
    if form.validate_on_submit():
        location = Location(location_name=form.location_name.data, qty=form.quantity.data)
        db.session.add(location)
        db.session.commit()
        flash('Your location has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_location.html', title='New Location',
                           form=form, legend='New Location')


@app.route("/location/<int:location_id>/update", methods=['GET', 'POST'])
@login_required
def update_location(location_id):
    location = Location.query.get_or_404(location_id)
    form = LocationForm()
    if form.validate_on_submit():
        location.location_name = form.location_name.data
        location.qty = form.quantity.data
        db.session.commit()
        flash('Your location has been updated!', 'success')
        return redirect(url_for('location', location_id=location.id))
    elif request.method == 'GET':
        form.location_name.data = location.location_name
        form.quantity.data = location.qty
    return render_template('create_location.html', title='Update Location',
                           form=form, legend='Update Location')


@app.route("/location/<int:location_id>")
def location(location_id):
    location = Location.query.get_or_404(location_id)
    return render_template('location.html', location_name=location.location_name, qty=location.qty, location=location)


@app.route("/location/<int:location_id>/delete", methods=['POST'])
@login_required
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    flash('Your location has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/moveproduct", methods=['GET', 'POST'])
def move_product():
    form = MoveProductForm()
    if form.validate_on_submit():
        fromloc = form.fromlocation.data
        toloc = form.tolocation.data
        pid = form.productid.data
        pq = form.productquantity.data
        product = Product.query.filter_by(id=pid).first()
        loc1 = Location.query.filter_by(location_name=fromloc).first()
        loc2 = Location.query.filter_by(location_name=toloc).first()
        if product and loc1 and loc2 and pq > loc1.qty:
            flash('Error , insufficient quantity', 'danger')
            return redirect(url_for('home'))
        elif product and loc1 and loc2 and toloc and pq < loc1.qty:
            loc1.qty = loc1.qty - pq
            loc2.qty = loc2.qty + pq
            mp = ProductMovement(from_location=fromloc, to_location=toloc, pid=pid, qty=pq)
            db.session.add(mp)
            db.session.commit()
            flash('Product Moved', 'success')
            return redirect(url_for('home'))
        elif product and loc1 and toloc and pq < loc1.qty:
            loc1.qty = loc1.qty - pq
            newloc = Location(location_name=toloc, qty=pq)
            mp = ProductMovement(from_location=fromloc, to_location=toloc, pid=pid, qty=pq)
            db.session.add(mp)
            db.session.add(newloc)
            db.session.commit()
            flash('Product Moved', 'success')
            return redirect(url_for('home'))
        elif product and loc1 and pq < loc1.qty:
            loc1.qty = loc1.qty - pq
            mp = ProductMovement(from_location=fromloc, pid=pid, qty=pq)
            db.session.add(mp)
            db.session.commit()
            flash('Product Moved', 'success')
            return redirect(url_for('home'))
        elif product and loc2:
            loc2.qty = loc2.qty + pq
            mp = ProductMovement(to_location=toloc, pid=pid, qty=pq)
            db.session.add(mp)
            db.session.commit()
            flash('Product Moved', 'success')
            return redirect(url_for('home'))
        else:
            flash('Error', 'danger')
            return redirect(url_for('move_product'))
    return render_template('mp.html', title='Move Product',
                           form=form, legend='Move Product')


@app.route("/moveproduct/<int:movement_id>", methods=['GET', 'POST'])
def productmovement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    return render_template('movement.html', floc=movement.from_location, toloc=movement.to_location, pdid=movement.pid, qty=movement.qty, movement=movement)


@app.route("/movement/<int:movement_id>/delete", methods=['POST'])
@login_required
def delete_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    fl = movement.from_location
    tl = movement.to_location
    qt = movement.qty
    addtolocation = Location.query.filter_by(location_name=fl).first()
    deletefromlocation = Location.query.filter_by(location_name=tl).first()
    if addtolocation and deletefromlocation:
        addtolocation.qty = addtolocation.qty + movement.qty
        deletefromlocation.qty = deletefromlocation.qty - movement.qty
    elif addtolocation:
        addtolocation.qty = addtolocation.qty + movement.qty
    elif deletefromlocation:
        deletefromlocation.qty = deletefromlocation.qty - movement.qty
    db.session.delete(movement)
    db.session.commit()
    flash('Your movement has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/movement/<int:movement_id>/update", methods=['GET', 'POST'])
@login_required
def update_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    form = MoveProductForm()
    if form.validate_on_submit():

        fl = movement.from_location
        tl = movement.to_location
        pd = movement.pid
        qt = movement.qty

        movement.from_location = form.fromlocation.data
        movement.to_location = form.tolocation.data
        movement.pid = form.productid.data
        movement.qty = form.productquantity.data

        beforefromlocation = Location.query.filter_by(location_name=fl).first()
        beforetolocation = Location.query.filter_by(location_name=tl).first()

        afterfromlocation = Location.query.filter_by(location_name=movement.from_location).first()
        aftertolocation = Location.query.filter_by(location_name=movement.to_location).first()

        beforepid = Product.query.filter_by(id=pd).first()
        afterpid = Product.query.filter_by(id=movement.pid).first()

        if qt != movement.qty and fl == movement.from_location and tl == movement.to_location and pd == movement.pid:
            afterfromlocation.qty = afterfromlocation.qty + qt - movement.qty
            aftertolocation.qty = aftertolocation.qty - qt + movement.qty
            if afterfromlocation.qty < 0 or aftertolocation.qty < 0:
                flash('Error', 'danger')
                return redirect(url_for('home'))
            db.session.commit()
            flash('Your location has been updated!', 'success')
            return redirect(url_for('productmovement', movement_id=movement.id))
        elif qt == movement.qty and fl == movement.from_location and tl == movement.to_location and pd != movement.pid:
            if afterpid:
                db.session.commit()
                flash('Your location has been updated!', 'success')
                return redirect(url_for('productmovement', movement_id=movement.id))
            else:
                flash('Error', 'danger')
                return redirect(url_for('home'))
        elif qt == movement.qty and fl == movement.from_location and tl != movement.to_location and pd == movement.pid:
            if aftertolocation:
                if beforetolocation:
                    beforetolocation.qty = beforetolocation.qty - movement.qty
                    aftertolocation.qty = aftertolocation.qty + movement.qty
                    if beforetolocation.qty < 0 or aftertolocation.qty < 0:
                        flash('Error', 'danger')
                        return redirect(url_for('home'))
                    db.session.commit()
                    flash('Your location has been updated!', 'success')
                    return redirect(url_for('productmovement', movement_id=movement.id))
                else:
                    aftertolocation.qty = aftertolocation.qty + movement.qty
                    if aftertolocation.qty < 0:
                        flash('Error', 'danger')
                        return redirect(url_for('home'))
                    db.session.commit()
                    flash('Your location has been updated!', 'success')
                    return redirect(url_for('productmovement', movement_id=movement.id))
            else:
                if beforetolocation:
                    beforetolocation.qty = beforetolocation.qty - movement.qty
                    if beforetolocation.qty < 0:
                        flash('Error', 'danger')
                        return redirect(url_for('home'))
                    if movement.to_location:
                        newloc = Location(location_name=movement.to_location, qty=movement.qty)
                        db.session.add(newloc)
                else:
                    flash('Error', 'danger')
                    return redirect(url_for('home'))
                db.session.commit()
                flash('Your location has been updated!', 'success')
                return redirect(url_for('productmovement', movement_id=movement.id))
        elif qt == movement.qty and fl != movement.from_location and tl == movement.to_location and pd == movement.pid:
            if afterfromlocation:
                if beforefromlocation:
                    beforefromlocation.qty = beforefromlocation.qty + movement.qty
                    afterfromlocation.qty = afterfromlocation.qty - movement.qty
                    if beforefromlocation.qty < 0 or afterfromlocation.qty < 0:
                        flash('Error', 'danger')
                        return redirect(url_for('home'))
                else:
                    afterfromlocation.qty = afterfromlocation.qty - movement.qty
                    if afterfromlocation.qty < 0:
                        flash('Error', 'danger')
                        return redirect(url_for('home'))
                db.session.commit()
                flash('Your location has been updated!', 'success')
                return redirect(url_for('productmovement', movement_id=movement.id))
            else:
                beforefromlocation.qty = beforefromlocation.qty + movement.qty
                if beforefromlocation.qty < 0:
                    flash('Error', 'danger')
                    return redirect(url_for('home'))
                db.session.commit()
                flash('Your location has been updated!', 'success')
                return redirect(url_for('productmovement', movement_id=movement.id))
        else:
            db.session.commit()
            flash('Your location has been updated!', 'success')
            return redirect(url_for('productmovement', movement_id=movement.id))

    elif request.method == 'GET':
        form.fromlocation.data = movement.from_location
        form.tolocation.data = movement.to_location
        form.productid.data = movement.pid
        form.productquantity.data = movement.qty
    return render_template('mp.html', title='Update Movement',
                           form=form, legend='Update Movement')
