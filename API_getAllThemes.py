import requests
import json
from get_token import get_token

url = "https://www.onemap.gov.sg/api/public/themesvc/getAllThemesInfo?moreInfo=Y"

token = get_token()

#print(token)

headers = {"Authorization": token}

response = requests.request("GET", url, headers=headers)
    
print(response.text)
