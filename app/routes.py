
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import User, Order
from app.forms import LoginForm, RegistrationForm
from app.utils.helpers import calculate_price
from app.utils.send_order_invoice import send_order_invoice

@app.route('/')
@login_required
def home():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('index.html', orders=orders)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            password=form.password.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please check your email to confirm your account.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    if not current_user.is_authenticated and 'guest' not in session:
        flash('Please log in or access as a guest to place an order.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        pickup_location = request.form.get('pickup_location')
        pickup_floors = int(request.form.get('pickup_floors', 0))
        dropoff_location = request.form.get('dropoff_location')
        dropoff_floors = int(request.form.get('dropoff_floors', 0))
        payment_method = request.form.get('payment_method')
        date = request.form.get('date')
        time = request.form.get('time')

        if payment_method not in ['Cash', 'Card']:
            flash('Invalid payment method selected.', 'danger')
            return redirect(url_for('place_order'))

        price, error = calculate_price(pickup_location, pickup_floors, dropoff_location, dropoff_floors)
        if error:
            flash(error, 'danger')
            return redirect(url_for('place_order'))

        order = Order(
            customer_id=current_user.id if current_user.is_authenticated else None,
            pickup_location=pickup_location,
            pickup_floors=pickup_floors,
            dropoff_location=dropoff_location,
            dropoff_floors=dropoff_floors,
            price=price,
            payment_method=payment_method,
            date=date,
            time=time
        )
        db.session.add(order)
        db.session.commit()

        if payment_method == 'Card':
            send_order_invoice(current_user.email, order)

        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('place_order.html')
