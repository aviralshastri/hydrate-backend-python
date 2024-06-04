from flask import Flask, request, jsonify
import extra_functions_client as ef

app = Flask(__name__)


@app.route('/get_product_images', methods=['GET'])
def get_product_images():
    if request.is_json:
        data = request.get_json()
        id = data.get('ID')
        if id:
            links=(ef.get_image_dict(id=id))
            return jsonify(links)
        else:
            return jsonify({'error': 'ID parameter is missing'}), 400
    else:
        return jsonify({'error': 'Request must be JSON'}), 400

@app.route('/get_product_details', methods=['GET'])
def get_product_details():
    if request.is_json:
        data = request.get_json()
        id = data.get('ID')
        if id:
            details=(ef.get_product_details(id=id))
            return jsonify(details)
        else:
            return jsonify({'error': 'ID parameter is missing'}), 400
    else:
        return jsonify({'error': 'Request must be JSON'}), 400

@app.route('/get_product_details', methods=['GET'])
def get_product_details():
    if request.is_json:
        data = request.get_json()
        keyword = data.get('keyword')
        if id:
            details=(ef.get_product_list(keyword=keyword))
            return jsonify(details)
        else:
            return jsonify({'error': 'ID parameter is missing'}), 400
    else:
        return jsonify({'error': 'Request must be JSON'}), 400

@app.route('/search_product_from_image', methods=['POST'])
def search_product_from_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        print(file)
        return jsonify({"message": f"File successfully uploaded and saved as {file_path}"}), 200



if __name__ == '__main__':
    app.run(debug=True,port=9000)
