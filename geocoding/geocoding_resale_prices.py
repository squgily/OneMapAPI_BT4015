import pandas as pd
import requests
import json
from tqdm import tqdm
import time
from get_token import get_token

# Load dataset
df = pd.read_csv("geocoding/OneMap_georeference_commercial_URA/Residential_ResaleFlatPrices/aggregated_carpeta/Resale_Mar_2017_agg.csv")
df["address"] = df["block"].astype(str) + " " + df["street_name"]

token = get_token()

#print(df)

batch_size = 300
results = []

start_idx = 0

for i, addr in enumerate(tqdm(df["address"][start_idx:]), start=start_idx):

    url = "https://www.onemap.gov.sg/api/common/elastic/search"

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
                "txn_month": df["month"].iloc[i],
                "town": df["town"].iloc[i],
                "building_type": "Residential",
                "gross_floor_area": df["floor_area_sqm"].iloc[i],
                "lease_commence_date": df["lease_commence_date"].iloc[i],
                "flat_type": df["flat_type"].iloc[i],
                "min_price": df["min_price"].iloc[i],
                "max_price": df["max_price"].iloc[i],
                "avg_price": df["avg_price"].iloc[i],

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
        filename = f"data_hedonicPrice/resale_residential/onemap_resale_2017_{i+1}.geojson"
        with open(filename, "w") as f:
            json.dump(geojson, f, indent=2, default=str)

        results = []  # reset batch

    time.sleep(0.2)

# Save remaining records
if results:
    with open("data_hedonicPrice/resale_residential/onemap_resale_2017_final.geojson", "w") as f:
        json.dump(results, f, indent=2, default=str)