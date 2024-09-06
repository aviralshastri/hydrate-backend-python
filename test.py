import requests

VERIFY_URL = 'http://localhost:5000/verify_account'
CREATE_URL = 'http://localhost:5000/create_account'

def verify_account(email, password):
    data = {'email': email, 'password': password}
    response = requests.post(VERIFY_URL, json=data)
    if response.status_code == 200:
        result = response.json().get('verified')
        return result
    else:
        print(f"Failed to verify account: {response.text}")
        return False

def create_account(email, password, phone_number):
    data = {'email': email, 'password': password, 'phone_number': phone_number}
    response = requests.post(CREATE_URL, json=data)
    if response.status_code == 200:
        message = response.json().get('message')
        print(message)
        return True
    else:
        print(f"Failed to create account: {response.text}")
        return False

