import firebase_admin
from firebase_admin import storage as fb_storage
from PIL import Image
from io import BytesIO
from flask import jsonify, request, send_file

# Inicjalizacja Firebase Admin bez jawnej nazwy bucketu (używamy domyślnego)
firebase_admin.initialize_app()

# Pobieramy domyślny bucket
bucket = fb_storage.bucket()

def resize_image(image_path, width, height):
    blob = bucket.blob(image_path)
    img_bytes = blob.download_as_bytes()

    image = Image.open(BytesIO(img_bytes))
    image = image.resize((width, height))

    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def resize_image_cloud_function(request):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Brak danych JSON w żądaniu'}), 400

        image_path = data.get('imagePath')
        width = data.get('width')
        height = data.get('height')

        if not image_path or not width or not height:
            return jsonify({'error': 'Brak wymaganych parametrów: imagePath, width, height'}), 400

        width = int(width)
        height = int(height)

        resized_image = resize_image(image_path, width, height)

        return send_file(
            resized_image,
            mimetype='image/jpeg',
            as_attachment=False,
            download_name='resized_image.jpg'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500