import requests

location = input("Enter location: ")
date = input("Enter date (YYYY-MM-DD): ")

print("Simple Python Weather Application")

url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}"

response = requests.get(
    url,
    params={
        "key": "HCU2HJXB7N2U8K26NM4E4W5GE"
    }
)

data = response.json()

print(data)