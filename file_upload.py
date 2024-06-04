import firebase_admin
from firebase_admin import credentials, storage
from flask import Flask, request, jsonify
import tempfile
import os

app = Flask(__name__)


cred = credentials.Certificate('serviceAccount.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'hydrate-ecommerce.appspot.com'
})

def delete_file(file_name):
    try:
        # Initialize Firebase storage
        bucket = storage.bucket()
        blob = bucket.blob(f'thumbnails/{file_name}')

        # Check if the file exists
        if not blob.exists():
            return {"error": "File not found"}, 404

        # Delete the file from Firebase Storage
        blob.delete()

        return {"message": "File deleted successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

def upload_file(file, filename):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        # Initialize Firebase storage
        bucket = storage.bucket()
        blob = bucket.blob(f'thumbnails/{filename}')

        # Upload the file to Firebase Storage
        blob.upload_from_filename(temp_file_path)

        # Make the file publicly accessible (optional)
        blob.make_public()

        # Clean up the temporary file
        os.remove(temp_file_path)

        return {"message": "File uploaded successfully", "url": blob.public_url}, 200

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.get_json()
    file_name = data['file_name']
    file = request.files['file']
    response, status_code = upload_file(file,file_name)
    return jsonify(response), status_code

@app.route('/delete', methods=['DELETE'])
def delete_image():
    data = request.get_json()
    file_name = data['file_name']
    response, status_code = delete_file(file_name)
    return jsonify(response), status_code

if __name__ == '__main__':
    app.run(debug=True, port=9000)
