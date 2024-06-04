from flask import Flask, request, send_file, jsonify
import requests
from PIL import Image
import io
import os
from googletrans import Translator


app = Flask(__name__)
translator = Translator()

# OpenAI API key
API_KEY = os.getenv('OPENAI_API_KEY')

@app.route('/generate-and-send-image/<texts>', methods=['GET'])
def generate_and_send_image(texts):
    if not texts or texts.strip() == '':
        return jsonify({'error': 'Missing or invalid text data in request'}), 400

    words = texts.split(',')
    if not all(words):  # 빈 문자열이 있는지 확인
        return jsonify({'error': 'Empty words are not allowed'}), 400
    
    words = [word.strip() for word in words]
    # Translate words to English
    translated_words = [translator.translate(word, dest='en').text for word in words]
    prompt = "Create an image that clearly shows all of these elements: " + ", ".join(translated_words)
    print("Translated prompt: ", prompt)
    
    image_url = create_image_from_text(prompt)
    if not image_url:
        return jsonify({'error': 'Failed to generate image'}), 500

    # Load the image into memory
    image_response = requests.get(image_url)
    image = Image.open(io.BytesIO(image_response.content))
    
    # Convert image to byte array
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Send the byte stream as a response
    return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name=f'{", ".join(translated_words)}_image.png')

def create_image_from_text(prompt):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=data)
    if response.status_code == 200:
        image_data = response.json()
        return image_data['data'][0]['url']
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
