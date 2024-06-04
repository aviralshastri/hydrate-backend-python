import requests


file_name = "images.jpg"
data = {"file_name": file_name}

'''
delete_url = 'http://127.0.0.1:9000/delete'


response = requests.delete(delete_url, json=data)

print(response.text)
'''

url = 'http://127.0.0.1:9000/upload'


image_path ="images.jpg"
if not image_path:
    print("No file selected.")

else:
    with open(image_path, 'rb') as img:
        
        files = {'file': img}
        response = requests.post(url, files=files,json=data)

    print(response.text)
    

