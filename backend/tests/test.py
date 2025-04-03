import requests

url = "http://localhost:8000/api/v1/wallets/refresh_stats/"
data = "123123"
data = {
    'address': '123'
}

r = requests.post(url, json=data)
print(r.text)
