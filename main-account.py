from flask import Flask, request, jsonify
from extra_functions_account import verify_account, create_account
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://192.168.1.9:3000"}})

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
    if not email or not password or not phone_number:
        return jsonify({'error': 'Email, password, and phone_number are required'}), 400
    
    success = create_account(name,email, password, phone_number,dob)
    if success:
        return jsonify({'created': success})
    else:
        return jsonify({'error': 'Failed to create account'}), 500

if __name__ == '__main__':
    app.run(host='192.168.1.9', port=9000, debug=True)
