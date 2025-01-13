import requests

url = "http://127.0.0.1:5000/add_user"
data = {
    "name": "Ahmad Alwakai",
    "email": "ahmadalwakai76@gmail.com",
    "role": "customer"
}

response = requests.post(url, json=data)
print(response.json())

