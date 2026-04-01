# web_api.py

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(__name__)

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)

# Sample database (replace with your actual database)
users = {}
portfolios = {}
orders = {}

# User registration
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    users[username] = password  # Store user (ensure to hash password in production)
    return jsonify(message="User registered successfully"), 201

# User login
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if users.get(username) == password:  # Validate user (check hashed password in production)
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify(message="Invalid credentials"), 401

# Multi-user portfolio management
@app.route('/portfolio', methods=['POST'])
@jwt_required()
def create_portfolio():
    username = get_jwt_identity()
    portfolio_data = request.json.get('portfolio_data')
    portfolios[username] = portfolio_data  # Save portfolio data
    return jsonify(message="Portfolio created successfully"), 201

@app.route('/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio():
    username = get_jwt_identity()
    return jsonify(portfolio=portfolios.get(username, {})), 200

# Order placement
@app.route('/order', methods=['POST'])
@jwt_required()
def place_order():
    username = get_jwt_identity()
    order_data = request.json.get('order_data')
    orders[username] = orders.get(username, []) + [order_data]  # Save order
    return jsonify(message="Order placed successfully"), 201

# SaaS Subscription
@app.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    username = get_jwt_identity()
    # Subscription logic here
    return jsonify(message="Subscribed successfully"), 200

if __name__ == '__main__':
    app.run(debug=True)