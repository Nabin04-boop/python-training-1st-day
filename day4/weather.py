import requests

location = input("enter location ")
date  = input("enter date(YYYY-MM-DD) ")

print("simple python weather application ")

url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}"

try:
    response = requests.get(url, params={'key':'HCU2HJXB7N2U8K26NM4E4W5GE'})
    data = response.json()
    # print(data)
    print(data["timezone"])
    print(data["description"])
    print(data["conditions"])
except:
    print("invalid response")