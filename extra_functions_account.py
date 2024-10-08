import mysql.connector as mysql
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Load environment variable
load_dotenv()

# Database connection setup
db = mysql.connect(
    host="localhost", 
    user="root", 
    password="mysql", 
    database="hydrateaccounts"
)
db_cursor = db.cursor()



# Basic String Encryption and Decryption functions

def string_encode(text):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            shifted_char = chr(((ord(char) - ord('a' if char.islower() else 'A') + 19) % 26) + ord('a' if char.islower() else 'A'))
            encrypted_text += shifted_char
        else:
            encrypted_text += char
    return encrypted_text

def string_decode(text):
    decrypted_text = ""
    for char in text:
        if char.isalpha():
            shifted_char = chr(((ord(char) - ord('a' if char.islower() else 'A') - 19) % 26) + ord('a' if char.islower() else 'A'))
            decrypted_text += shifted_char
        else:
            decrypted_text += char
    return decrypted_text


   
# Account creation function
def create_account(name, email, password, phone_number, dob, gender):
    try:
        def encrypt_password(password):
            password_key = os.getenv("PASSWORD_DECRYPT_KEY")
            password_binary_key = base64.b64decode(password_key.encode('utf-8'))
            cipher_suite = Fernet(password_binary_key)
            encrypted_message = cipher_suite.encrypt(password.encode())
            return encrypted_message

        def hash_password(password):
            ph = PasswordHasher()
            hashed_password = ph.hash(password)
            return hashed_password

        def insert_account(name, email, password, phone_number, dob,gender):
            try:
                encrypted_password = encrypt_password(string_encode(hash_password(password)))
                sql = "INSERT INTO accounts (name, email, password, phone_number, dob,gender) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (name, email, encrypted_password, phone_number, dob, gender)
                db_cursor.execute(sql, values)
                db.commit()
                print("Account created successfully!")
                return True
            except Exception as err:
                print(f"Error: {err}")
                db.rollback()
                return False

        return insert_account(name, email, password, phone_number, dob, gender)

    except Exception as e:
        print(f"Error creating account: {e}")
        return False


# Account verification function
def verify_account(email, password):
    try:
        def decrypt_password(encrypted_message):
            password_key = os.getenv("PASSWORD_DECRYPT_KEY")
            password_binary_key = base64.b64decode(password_key.encode('utf-8'))
            cipher_suite = Fernet(password_binary_key)
            decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
            return decrypted_message
        
        def verify_password(stored_hash, entered_password):
            ph = PasswordHasher()
            try:
                ph.verify(stored_hash, entered_password)
                return True
            except:
                return False
        
        def get_stored_hash(email):
            try:
                sql = "SELECT password FROM accounts WHERE email = %s"
                db_cursor.execute(sql, (email,))
                result = db_cursor.fetchone()

                if result:
                    return decrypt_password(result[0])
                else:
                    print("Email not found.")
                    return None
            except Exception as err:
                print(f"Error: {err}")
                return None

        stored_hash = get_stored_hash(email)
        if stored_hash:
            return verify_password(string_decode(stored_hash), password)
        else:
            return False
    
    except Exception as e:
        print(f"Error verifying account: {e}")
        return False


# Account existsance function
def account_existence_check(email,phone_number):
    try:
        sql = "SELECT * FROM accounts WHERE email = %s"
        db_cursor.execute(sql, (email,))
        email_exist = db_cursor.fetchone()
        sql = "SELECT * FROM accounts WHERE phone_number= %s"
        db_cursor.execute(sql, (phone_number,))
        phone_exists = db_cursor.fetchone()
        
        if email_exist:
            return "Email already associated with an account."
        elif phone_exists:
            return "Phone Number already associated with an account."
        else:
            return False
        
    except Exception as e:
        print(f"Error checking account existance: {e}")
        return "An error occurred while checking account existance."
    
    
# Email OTP verification function

email_template='''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>OTP Email Template</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .card {
            border-color: #F7F7F7;
            background-color: black;
            border-radius: 20px;
            color: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .otp {
            font-size: 40px;
            font-weight: bold;
            margin-top: 20px;
        }

        .logo {
            border-radius: 20px;
            width: 140px;
            margin-bottom: 20px;
            filter: invert(1);
	    border:solid;
            border-color:white;
            
        }
        .heading{
           font-size: 24px;
        }
    </style>
</head>
<body>
    <div class="card">
        <img class="logo" src="https://drive.google.com/uc?export=download&id=15RYokbtZEKkAq0guPqW1K30QpIwV0f7l" alt="Logo">
        <h2 class='heading'>Your Account Verification OTP</h2>
        <p class="otp">{otp}</p>
    </div>
</body>
</html>
'''
def email_otp_verification(OTP,email):
    try:
        def send_otp_email(OTP, email):
            sender_email = 'otpbot01@gmail.com'
            password = os.getenv("EMAIL_PASSWORD_KEY")
            email_body = email_template.replace('{otp}', OTP)

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = OTP
            msg['Subject'] = 'Hydrate eCommerce OTP Verification.'

            msg.attach(MIMEText(email_body, 'html'))
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP server and port
                server.starttls()  # Start TLS encryption
                server.login(sender_email, password)  # Login with Gmail email and password
                server.sendmail(sender_email, email, msg.as_string())  # Send email
                print('OTP sent successfully!')
                return True
            except Exception as e:
                print(f'Error: {e}')
                return False
            finally:
                server.quit()
        return send_otp_email(OTP,email)

    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False



