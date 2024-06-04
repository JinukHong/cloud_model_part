from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import torch

app = Flask(__name__)
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

# Global variable to store answer texts
answer_texts = []

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
    app.run(debug=True, port=5001)
