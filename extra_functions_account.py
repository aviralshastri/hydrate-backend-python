import mysql.connector as mysql
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import base64

# Load environment variables
load_dotenv()

# Database connection setup
db = mysql.connect(
    host="localhost", 
    user="root", 
    password="mysql", 
    database="hydrateaccounts"
)
db_cursor = db.cursor()

# Account verification function
def verify_account(email, password):
    try:
        def decrypt_password(encrypted_message):
            password_key = os.getenv("PASSWORD_DECRYPT_KEY")
            password_binary_key = base64.b64decode(password_key.encode('utf-8'))
            cipher_suite = Fernet(password_binary_key)
            decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
            return decrypted_message
        
        def verify_password(stored_hash, provided_password):
            return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
        
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
            return verify_password(stored_hash, password)
        else:
            return False
    
    except Exception as e:
        print(f"Error verifying account: {e}")
        return False

# Account creation function
def create_account(name, email, password, phone_number, dob):
    try:
        def encrypt_password(password):
            password_key = os.getenv("PASSWORD_DECRYPT_KEY")
            password_binary_key = base64.b64decode(password_key.encode('utf-8'))
            cipher_suite = Fernet(password_binary_key)
            encrypted_message = cipher_suite.encrypt(password.encode())
            return encrypted_message

        def hash_password(password):
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        def insert_account(name, email, password, phone_number, dob):
            try:
                encrypted_password = encrypt_password(hash_password(password))
                sql = "INSERT INTO accounts (name, email, password, phone_number, dob) VALUES (%s, %s, %s, %s, %s)"
                db_cursor.execute(sql, (name, email, encrypted_password, phone_number, dob))
                db.commit()
                print("Account created successfully!")
            except Exception as err:
                print(f"Error: {err}")
                db.rollback()

        insert_account(name, email, password, phone_number, dob)
        return True
    except Exception as e:
        print(f"Error creating account: {e}")
        return False
