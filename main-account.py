from flask import Flask, request, jsonify
from extra_functions_account import verify_account, create_account, account_existence_check,email_otp_verification, generate_jwt_token
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route('/verify_account', methods=['POST'])
def verify():
    print("verify_called")
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    result = verify_account(email, password)
    return jsonify({'verified': result})

@app.route('/create_account', methods=['POST'])
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
def get_jwt_token():
    token= generate_jwt_token()
    if token:
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'An error occured while tokenizing account.'}), 500



if __name__ == '__main__':
    app.run(debug=True,port=9000)
