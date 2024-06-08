import mysql.connector as mysql
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
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
def create_account(name, email, password, phone_number, dob, gender):
    try:
        def encrypt_password(password):
            password_key = os.getenv("PASSWORD_DECRYPT_KEY")
            password_binary_key = base64.b64decode(password_key.encode('utf-8'))
            cipher_suite = Fernet(password_binary_key)
            encrypted_message = cipher_suite.encrypt(password.encode())
            return encrypted_message

        def hash_password(password):
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        def insert_account(name, email, password, phone_number, dob,gender):
            try:
                encrypted_password = encrypt_password(hash_password(password))
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
def email_otp_verification(OTP,email):
    try:
        def send_otp_email(OTP, email):
            sender_email = 'otpbot01@gmail.com'
            password = os.getenv("EMAIL_PASSWORD_KEY")
            template_file = 'email_otp_template.html'
            with open(template_file, 'r') as file:
                email_body = file.read()

            email_body = email_body.replace('{otp}', OTP)

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
