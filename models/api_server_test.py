import requests

# Flask 앱의 엔드포인트 주소
url = 'http://172.22.145.8:5001/generate-and-send-image'

# 요청할 텍스트 데이터
data = {
    "text": "A futuristic city skyline at night"
}

# POST 요청으로 이미지 요청
response = requests.post(url, json=data)

if response.status_code == 200:
    # 이미지 파일로 저장
    with open('received_image_2.png', 'wb') as f:
        f.write(response.content)
else:
    print("Failed to receive image:", response.content)
