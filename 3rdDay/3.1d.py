import requests
response = requests.get("http://api.github.com")
print(response.status_code)
print(response.json())