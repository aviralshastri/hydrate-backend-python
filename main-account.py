from flask import Flask, request, jsonify
from extra_functions_account import verify_account, create_account, account_existence_check,email_otp_verification
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
import mysql.connector as mysql
from datetime import timedelta
import datetime
from dotenv import load_dotenv
import os


load_dotenv()

db = mysql.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="hydrateapikeys"
)

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)



def verify_api_key(token):
    try:
        user_id, api_key = token.split(':')
        with db.cursor() as db_cursor:
            sql = "SELECT id FROM api_keys WHERE api_key = %s AND id = %s"
            db_cursor.execute(sql, (api_key, user_id))
            
            result = db_cursor.fetchone()
            
            if result:
                return user_id
            else:
                return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def verify_api_key_and_jwt(token):
    try:
        user_id, api_key = token.split(':')

        with db.cursor() as db_cursor:
            sql = "SELECT id FROM api_keys WHERE api_key = %s AND id = %s"
            db_cursor.execute(sql, (api_key, user_id))
            result = db_cursor.fetchone()

            if result:
                print('api key verified')
                jwt_token = request.headers.get('JWT', None)
                if jwt_token:
                    try:
                        decoded_token = decode_token(jwt_token)
                        print(decoded_token)
                        return True
                    except Exception as e:
                        print(f"Error decoding JWT token: {e}")
                        return None
                else:
                    return None
            else:
                return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None


@auth.verify_token
def verify_token(token):
    if request.headers.get('JWT', None)!='':
        return verify_api_key_and_jwt(token)
    elif request.headers.get('JWT', None)=='':
        return verify_api_key(token) 
    else:
        return None
   
    
@app.route('/verify_account', methods=['POST'])
@auth.login_required
def verify():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    result = verify_account(email, password)
    return jsonify({'verified': result})

@app.route('/create_account', methods=['POST'])
@auth.login_required
def create():
    data = request.get_json()
    name= data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    dob = data.get('dob')
    gender = data.get('gender')
    if not email or not password or not phone_number or not dob or not gender:
        return jsonify({'error': 'Email, password,dob,gender and phone number are required'}), 400
    
    success = create_account(name,email, password, phone_number,dob,gender)
    if success:
        return jsonify({'created': success})
    else:
        return jsonify({'error': 'Failed to create account'}), 500
    
@app.route('/account_existence_check', methods=['POST'])
@auth.login_required
def account_existance():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phone_number')
    if not email or not phone_number:
        return jsonify({'error': 'Email and phone number is required'}), 400
    exist = account_existence_check(email, phone_number)
    if exist == False or exist == 'Email already associated with an account.' or exist == "Phone Number already associated with an account.":
        return jsonify({'existance': exist})
    else:
        return jsonify({'error': 'Failed to check account existance'}), 500

@app.route('/email_verification', methods=['POST'])
@auth.login_required
def email_verification():
    data = request.get_json()
    email = data.get('email')
    OTP = data.get('otp')
    if not email or not OTP:
        return jsonify({'error': 'Email and phone number is required'}), 400
    otp_sent = email_otp_verification(OTP,email)
    if otp_sent:
        return jsonify({'status': 'OTP sent'})
    else:
        return jsonify({'status': 'An error occured while sending otp'}), 500

@app.route('/get_jwt_token', methods=['GET'])
@auth.login_required
def get_jwt_token():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        payload = {
            'user_id': user_id,
        }
        expires = timedelta(minutes=2)
        token = create_access_token(identity=payload, expires_delta=expires)
        return jsonify({'user_id': user_id, 'token': token, 'expires': str(datetime.datetime.now() + expires)})
    except Exception as e:
        print(f"Error generating JWT token: {e}")
        return jsonify({'error': 'Failed to generate JWT token'}), 500




if __name__ == '__main__':
    app.run(debug=True,port=9000)
