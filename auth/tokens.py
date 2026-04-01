import jwt
import datetime

# Secret key for encoding and decoding the token (should be kept secret)
SECRET_KEY = 'your_secret_key_here'

# Function to generate JWT token

def generate_token(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token valid for 1 day
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

# Function to verify JWT token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token expired.'
    except jwt.InvalidTokenError:
        return 'Invalid token.'

# Function to securely get the secret key (if needed)

def get_secret_key():
    return SECRET_KEY
