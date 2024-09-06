import requests
import json


url = 'http://127.0.0.1:9000/get_product_details'


payload = {
    'keyword': 't-shirt'
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers, data=json.dumps(payload))


print(response.json())
