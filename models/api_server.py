from flask import Flask, request, send_file
import requests
from PIL import Image
import io
import os
import jsonify

app = Flask(__name__)

# OpenAI API key
API_KEY = os.getenv('OPENAI_API_KEY')

@app.route('/generate-and-send-image/<texts>', methods=['GET'])
def generate_and_send_image(texts):
    words = texts.split(',')
    words = [word.strip() for word in words]
    prompt = "Create an image that clearly shows all of these elements: " + ", ".join(words)
    print(prompt)
    
    image_url = create_image_from_text(prompt)
    if not image_url:
        return jsonify({'error': 'Failed to generate image'}), 500

    # 이미지를 메모리에 로드
    image_response = requests.get(image_url)
    image = Image.open(io.BytesIO(image_response.content))
    
    # 이미지를 바이트로 변환
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # 바이트 스트림을 응답으로 전송
    return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name=f'{", ".join(words)}_image.png')

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
