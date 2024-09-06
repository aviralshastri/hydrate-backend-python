from flask import Flask, request, jsonify
import extra_functions_admin as ef

app = Flask(__name__)


@app.route('/add_product', methods=['POST'])
def add_product():
    data=request.get_json()
    data=request.files['thumbnail']
    data=request.files['image_links']

@app.route('/delete_product', methods=['DELETE'])
def delete_product():
    print("delete_product")

@app.route('/edit_product_image', methods=['PUT'])
def edit_product_image():
    print("edit_product_image")

@app.route('/edit_product_color', methods=['PUT'])
def edit_product_color():
    print("edit_product_color")

@app.route('/add_or_remove_size', methods=['PUT'])
def add_or_remove_size():
    print("add_remove_size")
    
@app.route('/delete_color_and_image', methods=['DELETE'])
def delete_color_and_image():
    print("delete_color_and_image")

@app.route('/edit_thumbnail', methods=['PUT'])
def edit_thumbnail():
    print("edit_thumbnail")

@app.route('/edit_product_name', methods=['PUT'])
def edit_product_name():
    print("edit_product_name")


if __name__ == '__main__':
    app.run(debug=True,port=9000)
