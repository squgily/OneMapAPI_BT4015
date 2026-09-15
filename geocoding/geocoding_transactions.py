import pandas as pd
import requests
import json
from tqdm import tqdm
import time
from datetime import datetime
from get_token import get_token

# Load dataset
df = pd.read_csv("geocoding/OneMap_georeference_commercial_URA/OfficeTransaction20260428041132_URA.csv")
#df["address"] = df["blk_no"].astype(str) + " " + df["street"]

#print(df)

batch_size = 300
results = []

start_idx = 900

def extract_year(date_str):
    """Convert 'Apr-26' to 2026 as integer"""
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str.strip(), "%b-%y")
        return int(date_obj.year)
    except:
        return None

df['Year'] = df['Sale Date'].apply(extract_year)

for i, addr in enumerate(tqdm(df["Project Name"][start_idx:]), start=start_idx):

    url = "https://www.onemap.gov.sg/api/common/elastic/search"
    token = get_token()

    params = {
        "searchVal": addr,
        "returnGeom": "Y",
        "getAddrDetails": "Y",
        "pageNum": 1
    }

    headers = {"Authorization": token}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    api_results = data.get("results", [])

    for r in api_results:
        # Skip if no coordinates
        if not r.get("LATITUDE") or not r.get("LONGITUDE"):
            continue

        feature = {
            "type": "Feature",
            "properties": {
                "searchval": r.get("SEARCHVAL"),
                "blk_no": r.get("BLK_NO"),
                "road_name": r.get("ROAD_NAME"),
                "building": r.get("BUILDING"),
                "address": r.get("ADDRESS"),
                "postal": r.get("POSTAL"),
                "building_type": df["Property Type"].iloc[i],
                "transacted_price": df["Transacted Price ($)"].iloc[i],
                "area_sqft": df["Area (SQFT)"].iloc[i],
                "unit_price_psf": df["Unit Price ($ PSF)"].iloc[i],
                "sale_date": df["Sale Date"].iloc[i],
                "year": df["Year"].iloc[i],
                "type_of_area": df["Type of Area"].iloc[i],
                "area_sqm": df["Area (SQM)"].iloc[i],
                "unit_price_psm": df["Unit Price ($ PSM)"].iloc[i],
                "tenure": df["Tenure"].iloc[i],
                "postal_district": df["Postal District"].iloc[i],
                "floor_level": df["Floor Level"].iloc[i],


            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(r["LONGITUDE"]),  # GeoJSON = [lon, lat]
                    float(r["LATITUDE"])
                ]
            }
        }

        #print(feature)


        results.append(feature)

    #print(df.dtypes)
    #print(df.head())

    geojson = {
        "type": "FeatureCollection",
        "features": results
    }


    # Save every batch
    if (i + 1) % batch_size == 0:
        filename = f"data_hedonicPrice/office/onemap_office_HPM_{i+1}.geojson"
        with open(filename, "w") as f:
            json.dump(geojson, f, indent=2, default=str)

        results = []  # reset batch

    time.sleep(0.2)

# Save remaining records
if results:
    with open("data_hedonicPrice/office/onemap_office_HPM_final.geojson", "w") as f:
        json.dump(results, f, indent=2, default=str)