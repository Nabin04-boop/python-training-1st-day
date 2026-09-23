import requests
location = input("Eneter your location:")
date = input("Date(YYYY-MM-DD):")
print("weather of your location today:")
url = f"http://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}"
try:
    response = requests.get(url, params={'key':'HCU2HJXB7N2U8K26NM4E4W5GE'})
    data = response.json()
    print(data["description"])

except:
    print("invalid response")