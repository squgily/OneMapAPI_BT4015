from urllib import response

import requests
from dotenv import load_dotenv
import os

def get_token():
    load_dotenv()
    
    url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    
    payload = {
        "email": os.environ['ONEMAP_EMAIL'],
        "password": os.environ['ONEMAP_EMAIL_PASSWORD']
    }
    
    response = requests.post(url, json=payload)
    data = response.json()  # convert response to dict
    
    return data["access_token"]