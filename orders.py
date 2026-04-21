# routes/orders.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, Cart, Product
import uuid
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/payments/create_order', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    total_price = 0
    orders_created = []

    for item in cart_items:
        product = Product.query.get(item.product_id)
        if not product or product.stock < item.quantity:
            return jsonify({"error": f"Product '{product.name}' out of stock"}), 400

        total = product.price * item.quantity
        total_price += total

        # Create order
        new_order = Order(
            user_id=user_id,
            product_id=product.id,
            quantity=item.quantity,
            total_price=total,
            status='Processing',
            order_date=datetime.now()
        )
        new_order.generate_tracking_id()

        # Decrease stock
        product.stock -= item.quantity

        db.session.add(new_order)
        orders_created.append({
            'product_id': product.id,
            'quantity': item.quantity,
            'price': product.price,
            'total_price': total,
            'tracking_id': new_order.tracking_id
        })

    # Clear the cart after order
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    return jsonify({
        "message": "Order(s) created successfully!",
        "orders": orders_created,
        "total_price": total_price
    }), 200


@orders_bp.route('/track/<int:order_id>', methods=['GET'])
@jwt_required()
def track_order(order_id):
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify({
        'status': order.status,
        'tracking_id': order.tracking_id,
        'order_date': order.order_date.strftime('%Y-%m-%d'),
        'product_id': order.product_id,
        'quantity': order.quantity,
        'total_price': order.total_price
    })


