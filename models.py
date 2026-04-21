from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
import uuid

# Initialize db instance
db = SQLAlchemy()

# User model
class User(db.Model):
    __tablename__ = 'users'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Product model
class Product(db.Model):
    __tablename__ = 'products'  # Optional: makes it cleaner
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# Cart model
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ✅ fixed
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

# Order model
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ✅ fixed
    status = db.Column(db.String(50), default='Processing')  # Add this
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.now)
    tracking_id = db.Column(db.String(50), unique=True, nullable=True)
    razorpay_order_id = db.Column(db.String(100), nullable=True) 
    current_location = db.Column(db.String(100), default="Chennai")  # starting location
    status = db.Column(db.String(100), default="Order Placed")

    def generate_tracking_id(self):
        self.tracking_id = str(uuid.uuid4())[:12]

# Tracking Model 
class Tracking(db.Model):
    __tablename__ = 'tracking'
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(100), unique=True, nullable=False)
    current_location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))  # link to orders if needed

# Payment model
class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ✅ fixed
    order_id = db.Column(db.String(255), nullable=False)
    payment_id = db.Column(db.String(255), nullable=False, unique=True)
    signature = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending")

    user = db.relationship('User', backref=db.backref('payments', lazy=True))

    def calculate_total(self):
        total = 0
        for cart_item in self.cart_items:
            total += cart_item.product.price * cart_item.quantity
        return total

