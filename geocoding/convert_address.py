import pandas as pd
import requests
import json
from sqlalchemy import null
from tqdm import tqdm
import time
from get_token import get_token
import re


url = "https://www.onemap.gov.sg/api/common/elastic/search"
token = get_token()


def convert_address(address):
    parts = [p.strip() for p in address.split(",")]
    
    # First part = street number, second = street name
    street = f"{parts[0]} {parts[1]}"
    
    # Extract postal code from last part
    match = re.search(r"SG\((\d{6})\)", address)
    postal_code = match.group(1) if match else ""
    
    return f"{street} SINGAPORE {postal_code}".strip()

# Example
addr = "10, AIRPORT BOULEVARD, #02-55/56, CHANGI AIRPORT TERMINAL 4, SG(819665)"
new_addr = convert_address(addr)
print(new_addr)

#sample: 91 JALAN BAHAR SINGAPORE 649735

params = {
    "searchVal": new_addr,
    "returnGeom": "Y",
    "getAddrDetails": "Y",
    "pageNum": 1
}

print(addr)

headers = {"Authorization": token}

response = requests.get(url, params=params, headers=headers)
data = response.json()
api_results = data.get("results", [])

print(response.text)