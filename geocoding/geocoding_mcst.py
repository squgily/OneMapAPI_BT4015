import pandas as pd
import requests
import json
from tqdm import tqdm
import time
from get_token import get_token

# Load dataset
df = pd.read_csv("geocoding/OneMap_georeference_commercial_URA/RetailTransaction20260428041104_URA.csv")
#df["address"] = df["blk_no"].astype(str) + " " + df["street"]

#print(df)

batch_size = 300
results = []

start_idx = 3600

for i, addr in enumerate(tqdm(df["devt_location"][start_idx:]), start=start_idx):

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
                "date_cert": df["mc_form_date"].iloc[i],
                "year_completed": int(df["mc_form_date"].iloc[i].split("/")[-1]) - 1


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
        filename = f"geocoding_MCST_cYearEstimacion/onemap_retail_HPM_{i+1}.geojson"
        with open(filename, "w") as f:
            json.dump(geojson, f, indent=2, default=str)

        results = []  # reset batch

    time.sleep(0.2)

# Save remaining records
if results:
    with open("geocoding_MCST_cYearEstimacion/onemap_retail_HPM_final.geojson", "w") as f:
        json.dump(results, f, indent=2, default=str)