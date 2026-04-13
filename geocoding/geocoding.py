import pandas as pd
import requests
import json
from tqdm import tqdm
import time

# Load dataset
df = pd.read_csv("Listing of Building Energy Performance Data 2020.csv")
#df["address"] = df["blk_no"].astype(str) + " " + df["street"]

#print(df)

batch_size = 300
results = []

start_idx = 0

for i, addr in enumerate(tqdm(df["buildingaddress"][start_idx:]), start=start_idx):

    url = "https://www.onemap.gov.sg/api/common/elastic/search"

    params = {
        "searchVal": addr,
        "returnGeom": "Y",
        "getAddrDetails": "Y",
        "pageNum": 1
    }

    headers = {"Authorization": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMTY4MywiZm9yZXZlciI6ZmFsc2UsImlzcyI6Ik9uZU1hcCIsImlhdCI6MTc3MzY3NTU5NSwibmJmIjoxNzczNjc1NTk1LCJleHAiOjE3NzM5MzQ3OTUsImp0aSI6IjUxNzQ1MmI5LWQ5ZTctNDFmZi05OTE0LTAxZjk5NzcyMDcyYiJ9.mOEHkJPKviu-E2N1nK4RlxDwkt5JhInZWr1HgykXSC0Iiucku-oJXCNEUty_-9j_wSRaPe8FGbipsFcawHsAeUe4vNrZ2uFKDF-hwIvLZqua7zJ-c2_pH3-k2_KZ4RwrtHbllS6GRpkhQY-cetjYKYpBGHm0XjaieeOrx3rTV1CTF2A5u7ZJ93064LGlSNUuqu1lwVRZm60q-DxRx3gban5iGJC2LbPUyHoM83ie_mV55VSWGVaEPcxtzGA7r7jpJDkMHIAgquOmGtFOC50Wi9_GpariJNjRx-1FpUc1w_NN9jk9LKUi8KoFjQd8bgfArjJlDT0VoQLoYqIg11Jc-w"}

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
                #"max_floor_lvl": df["max_floor_lvl"].iloc[i],
                "year_completed": df["yearobtainedtopcsc"].iloc[i],
                "building_type": df["buildingtype"].iloc[i],
                "main_building_function": df["mainbuildingfunction"].iloc[i],
                "gross_floor_area": df["grossfloorarea"].iloc[i]

            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(r["LONGITUDE"]),  # GeoJSON = [lon, lat]
                    float(r["LATITUDE"])
                ]
            }
        }


        results.append(feature)

    #print(df.dtypes)
    #print(df.head())

    geojson = {
        "type": "FeatureCollection",
        "features": results
    }


    # Save every batch
    if (i + 1) % batch_size == 0:
        filename = f"onemap_energy_performance_data_{i+1}.geojson"
        with open(filename, "w") as f:
            json.dump(geojson, f, indent=2, default=str)

        results = []  # reset batch

    time.sleep(0.2)

# Save remaining records
if results:
    with open("onemap_energy_performance_data_final.geojson", "w") as f:
        json.dump(results, f, indent=2, default=str)