import razorpay
import hashlib
import random
import string
import hmac
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, Product,User  # Import Product model as well

payments_bp = Blueprint('payments_bp', __name__)

def get_razorpay_client():
    return razorpay.Client(auth=(
        current_app.config["RAZORPAY_KEY"],
        current_app.config["RAZORPAY_SECRET"]
    ))

#  1. Create Razorpay Order
@payments_bp.route('/create_order', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    print("Incoming data:", data)

    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    total_price = product.price * quantity
    tracking_id = 'TRK' + str(uuid.uuid4().hex[:8])

    razorpay_client = razorpay.Client(auth=(
        current_app.config['RAZORPAY_KEY'],
        current_app.config['RAZORPAY_SECRET']
    ))

    payment = razorpay_client.order.create({
        "amount": int(total_price * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    new_order = Order(
        user_id=user.id,
        product_id=product.id,
        quantity=quantity,
        total_price=total_price,
        tracking_id=tracking_id,
        status="Processing",
        razorpay_order_id=payment['id']
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({
        'order_id': payment['id'],
        'amount': int(total_price * 100),
        'currency': 'INR',
        'razorpay_key': current_app.config["RAZORPAY_KEY"],
        'tracking_id': tracking_id
    })


# 2. Verify Razorpay Signature
@payments_bp.route("/verify_payment", methods=["POST"])
def verify_payment():
    try:
        data = request.get_json()
        razorpay_order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        if not razorpay_order_id or not payment_id or not signature:
            return jsonify({"error": "Missing payment details"}), 400

        secret = current_app.config["RAZORPAY_SECRET"]
        generated_signature = hmac.new(
            bytes(secret, "utf-8"),
            bytes(f"{razorpay_order_id}|{payment_id}", "utf-8"),
            hashlib.sha256
        ).hexdigest()

        if generated_signature == signature:
            return jsonify({"message": "Payment verified successfully!"}), 200
        else:
            return jsonify({"error": "Invalid payment signature"}), 400

    except Exception as e:
        return jsonify({"error": f"Payment verification failed: {str(e)}"}), 500

#  3. Confirm Order and Generate Tracking ID
def generate_tracking_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@payments_bp.route('/payment-success', methods=['POST'])
@jwt_required()
def payment_success():
    try:
        data = request.get_json()
        order_id = data.get("order_id")
        user_id = get_jwt_identity()

        order = Order.query.filter_by(razorpay_order_id=order_id, user_id=user_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        order.status = "Processing"
        order.tracking_id = generate_tracking_id()
        db.session.commit()

        return jsonify({'message': 'Payment successful and order confirmed!', 'tracking_id': order.tracking_id}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

