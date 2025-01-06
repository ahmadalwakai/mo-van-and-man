from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Order, db
from werkzeug.security import check_password_hash

routes = Blueprint('routes', __name__)

@routes.route('/')
@login_required
def home():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('index.html', orders=orders)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('routes.home'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('routes.login'))
