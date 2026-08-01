import requests

response = requests.post("http://localhost:8000/api/v1/auth/login", json={
    "email": "djspinall@beatpush.com",
    "password": "password123"
})

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
