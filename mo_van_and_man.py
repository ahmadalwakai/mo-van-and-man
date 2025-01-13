import os
from flask import Flask, request, redirect, url_for, flash, render_template, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from geopy.distance import geodesic
from fpdf import FPDF
from datetime import datetime
import logging
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegistrationForm
from app.models import User, Order, ChatMessage
from app.utils.helpers import calculate_price

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)
socketio = SocketIO(app)
limiter = Limiter(app, key_func=get_remote_address, default_limits=['200 per day', '50 per hour'])
csrf = CSRFProtect(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an uploads folder for images
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
            password=generate_password_hash(form.password.data)
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
        if user and check_password_hash(user.password, form.password.data):
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
        try:
            pickup_location = request.form['pickup_location']
            pickup_floors = int(request.form['pickup_floors'])
            dropoff_location = request.form['dropoff_location']
            dropoff_floors = int(request.form['dropoff_floors'])
            date = request.form['date']
            time = request.form['time']
            payment_method = request.form['payment_method']
            if payment_method not in ['Cash', 'Card']:
                flash('Invalid payment method selected.', 'danger')
                return redirect(url_for('place_order'))
        except KeyError as e:
            flash(f"Missing field: {e}", 'danger')
            return redirect(url_for('place_order'))

        price, error = calculate_price(pickup_location, pickup_floors, dropoff_location, dropoff_floors)
        if error:
            flash(error, 'danger')
            return redirect(url_for('place_order'))

        new_order = Order(
            customer_id=current_user.id if current_user.is_authenticated else None,
            pickup_location=pickup_location,
            pickup_floors=pickup_floors,
            dropoff_location=dropoff_location,
            dropoff_floors=dropoff_floors,
            distance_miles=price / 1.5,
            price=price,
            payment_method=payment_method,
            date=date,
            time=time
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('place_order.html')

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        message = request.form['message']
        recipient_id = request.form.get('recipient_id')
        attachment_url = request.form.get('attachment_url')
        new_message = ChatMessage(user_id=current_user.id, message=message, recipient_id=recipient_id, attachment_url=attachment_url)
        db.session.add(new_message)
        db.session.commit()
        flash('Message sent!', 'success')

    messages = ChatMessage.query.filter_by(user_id=current_user.id).all()
    return render_template('chat.html', messages=messages)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = f"{uuid.uuid4().hex}_{image.filename}"
    filepath = os.path.join('static/uploads', filename)
    image.save(filepath)

    return jsonify({'image_url': f'/static/uploads/{filename}'})

@app.route('/api/orders', methods=['GET'])
def api_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/users', methods=['GET'])
def api_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/order/<int:order_id>', methods=['GET'])
def api_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@app.route('/api/user/<int:user_id>', methods=['GET'])
def api_user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# Helper function to send confirmation email
def send_confirmation_email(email, username):
    # Disabled temporarily to avoid errors during deployment
    pass

# Helper function to send order invoice
def send_order_invoice(email, order):
    # Disabled temporarily to avoid errors during deployment
    pass

if __name__ == "__main__":
    socketio.run(app)
