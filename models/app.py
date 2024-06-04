from flask import Flask, request, send_file, jsonify
import requests
from PIL import Image
import io
import os
from googletrans import Translator
from sentence_transformers import SentenceTransformer
import torch

app = Flask(__name__)
translator = Translator()
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

# OpenAI API key
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Global variable to store answer texts
answer_texts = []

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

@app.route('/initialize/<words>', methods=['GET'])
def initialize_answers(words):
    global answer_texts
    answer_texts = words.split(',')
    if len(answer_texts) == 0:
        return jsonify({'error': 'No answer texts provided'}), 400
    return jsonify({'message': 'Answer texts initialized successfully', 'answers': answer_texts}), 200

@app.route('/similarity/<words>', methods=['GET'])
def calculate_similarities(words):
    input_texts = words.split(',')
    if len(input_texts) == 0:
        return jsonify({'error': 'No input texts provided'}), 400

    # Calculate similarities for each input text against each answer text
    results = []
    for input_text in input_texts:
        similarities = []
        for answer_text in answer_texts:
            score = calculate_text_similarity(answer_text, input_text)
            similarities.append(score)
        results.append(similarities)
    
    return jsonify({'similarity_scores': results})

def calculate_text_similarity(text1, text2):
    # 문장 임베딩 생성 및 코사인 유사도 계산
    embeddings = model.encode([text1, text2])
    cos_sim = torch.nn.functional.cosine_similarity(torch.tensor([embeddings[0]]), torch.tensor([embeddings[1]]))
    return cos_sim.item()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
