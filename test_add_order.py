import requests

url = "http://127.0.0.1:5000/add_order"
data = {
    "customer_id": 1,
    "pickup_location": "Glasgow",
    "dropoff_location": "Edinburgh"
}

response = requests.post(url, json=data)
print(response.json())
