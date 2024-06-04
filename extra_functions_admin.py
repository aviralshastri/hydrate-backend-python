import mysql.connector as mysql
import firebase_admin
from firebase_admin import credentials, storage
import tempfile
import os

# DB and firebase initialization
db=mysql.connect(host="localhost",user="root",password="mysql",database="hydrateproducts")
db_cursor=db.cursor()
cred = credentials.Certificate('serviceAccount.json')


def delete_file(file_name):
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'hydrate-ecommerce.appspot.com'
    })

    try:
        bucket = storage.bucket()
        blob = bucket.blob(f'thumbnails/{file_name}')

        if not blob.exists():
            return {"error": "File not found"}, 404

        blob.delete()

        return {"message": "File deleted successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500


def upload_file(file, filename):
    
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'hydrate-ecommerce.appspot.com'
    })
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        bucket = storage.bucket()
        blob = bucket.blob(f'thumbnails/{filename}')

        blob.upload_from_filename(file)
        
        blob.make_public()

        os.remove(temp_file_path)

        return {"message": "File uploaded successfully", "url": blob.public_url}, 200

    except Exception as e:
        return {"error": str(e)}, 500



def add_product(data):

    def MySQL_add_product(data):
        
        title, price, category, colors, thumbnail, tagline1, tagline2, material, tags, gender = data['title'],data['price'],data['category'],data['colors'],data['thumbnail'],data['tagline1'],data['tagline2'],data['material'],data['tags'],data['gender']
        query_products=""
        query_sizes=""
        query_detail=""
        query_images=""


        if data:
            query_products=f"""
            insert into products(title,price,category,colors,thumbnail,tagline1,tagline2,material,tags,gender)
            values('{title}',{price},'{category}','{colors}','{thumbnail}','{tagline1}','{tagline2}','{material}','{tags}','{gender}')
            """
        
        db_cursor.execute(query_products)
        db.commit()

    
    return MySQL_add_product(data)


