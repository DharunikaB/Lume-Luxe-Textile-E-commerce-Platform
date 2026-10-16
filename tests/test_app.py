import pytest
from app import app, db
from models import User, Cart

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_add_to_cart_omitted_quantity(client):
    # Create a test user
    user = User(email='test@example.com', password='password', is_admin=False)
    db.session.add(user)
    db.session.commit()

    # Login the user
    response = client.post('/users/login', json={'email': 'test@example.com', 'password': 'password'})
    token = response.json['token']

    # Add a product to the cart with omitted quantity
    response = client.post('/add_to_cart', json={'product_id': 1}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Product added to cart!'

    # Verify the quantity is set to 1
    cart_item = Cart.query.filter_by(user_id=user.id, product_id=1).first()
    assert cart_item.quantity == 1

def test_add_to_cart_valid_quantity(client):
    # Create a test user
    user = User(email='test@example.com', password='password', is_admin=False)
    db.session.add(user)
    db.session.commit()

    # Login the user
    response = client.post('/users/login', json={'email': 'test@example.com', 'password': 'password'})
    token = response.json['token']

    # Add a product to the cart with a valid quantity
    response = client.post('/add_to_cart', json={'product_id': 1, 'quantity': 2}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Product added to cart!'

    # Verify the quantity is set to 2
    cart_item = Cart.query.filter_by(user_id=user.id, product_id=1).first()
    assert cart_item.quantity == 2

def test_add_to_cart_zero_quantity(client):
    # Create a test user
    user = User(email='test@example.com', password='password', is_admin=False)
    db.session.add(user)
    db.session.commit()

    # Login the user
    response = client.post('/users/login', json={'email': 'test@example.com', 'password': 'password'})
    token = response.json['token']

    # Add a product to the cart with a zero quantity
    response = client.post('/add_to_cart', json={'product_id': 1, 'quantity': 0}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 400
    assert response.json['error'] == 'Quantity must be a positive integer'


def test_add_to_cart_negative_quantity(client):
    # Create a test user
    user = User(email='test@example.com', password='password', is_admin=False)
    db.session.add(user)
    db.session.commit()

    # Login the user
    response = client.post('/users/login', json={'email': 'test@example.com', 'password': 'password'})
    token = response.json['token']

    # Add a product to the cart with a negative quantity
    response = client.post('/add_to_cart', json={'product_id': 1, 'quantity': -1}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 400
    assert response.json['error'] == 'Quantity must be a positive integer'


def test_add_to_cart_non_numeric_quantity(client):
    # Create a test user
    user = User(email='test@example.com', password='password', is_admin=False)
    db.session.add(user)
    db.session.commit()

    # Login the user
    response = client.post('/users/login', json={'email': 'test@example.com', 'password': 'password'})
    token = response.json['token']

    # Add a product to the cart with a non-numeric quantity
    response = client.post('/add_to_cart', json={'product_id': 1, 'quantity': 'abc'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 400
    assert response.json['error'] == 'Quantity must be a positive integer'
