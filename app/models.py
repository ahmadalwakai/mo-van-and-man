
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Order Model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    pickup_location = db.Column(db.String(255), nullable=False)
    pickup_floors = db.Column(db.Integer, nullable=False)
    dropoff_location = db.Column(db.String(255), nullable=False)
    dropoff_floors = db.Column(db.Integer, nullable=False)
    distance_miles = db.Column(db.Float, nullable=True)
    price = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(20), nullable=False)  # Cash or Card
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)

# Chat Message Model
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    read = db.Column(db.Boolean, default=False)
    message_type = db.Column(db.String(50), default='text')
    recipient_id = db.Column(db.Integer, nullable=True)
    attachment_url = db.Column(db.String(255), nullable=True)
