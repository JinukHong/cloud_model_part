import requests

url = 'http://127.0.0.1:5001/similarity'
data = {'text1': '불', 'text2': '얼음'}
response = requests.post(url, json=data)
print(response.json())
