import pandas as pd
import requests
import json
from sqlalchemy import null
from tqdm import tqdm
import time
from get_token import get_token

# Load dataset
df = pd.read_csv("PublicationofBuildingEnergyPerformanceData (1)/Listing of Building Energy Performance Data for Commercial Buildings.csv")
#df["address"] = df["blk_no"].astype(str) + " " + df["street"]

#print(df)

batch_size = 400
results = []

start_idx = 600

for i, addr in enumerate(tqdm(df["buildingaddress"][start_idx:]), start=start_idx):

    url = "https://www.onemap.gov.sg/api/common/elastic/search"
    token = get_token()

    if pd.isna(addr):
        continue

    addr_clean = str(addr).replace(",", "").strip()

    params = {
        "searchVal": addr_clean,
        "returnGeom": "Y",
        "getAddrDetails": "Y",
        "pageNum": 1
    }

    #print(addr)
    #print(addr_clean)

    headers = {"Authorization": token}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    api_results = data.get("results", [])
    

    for r in api_results:
        
        # Skip if no coordinates OR no address given
        if (
            not r.get("LATITUDE")
            or not r.get("LONGITUDE")
            or pd.isna(addr)
        ):
            
            continue

        feature = {
            "type": "Feature",
            "properties": {
                "searchval": addr,
                "blk_no": r.get("BLK_NO"),
                "road_name": r.get("ROAD_NAME"),
                "building": r.get("BUILDING"),
                "building_name": df["buildingname"].iloc[i],
                "address": r.get("ADDRESS"),
                "postal": r.get("POSTAL"),
                #"max_floor_lvl": df["max_floor_lvl"].iloc[i],
                #"year_completed": df["yearobtainedtopcsc"].iloc[i],
                "building_type": df["buildingtype"].iloc[i],
                #"main_building_function": df["mainbuildingfunction"].iloc[i],
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
        filename = f"onemap_energy_performance_data_misc_{i+1}.geojson"
        with open(filename, "w") as f:
            json.dump(geojson, f, indent=2, default=str)

        results = []  # reset batch

    time.sleep(0.2)

# Save remaining records
if results:
    with open("onemap_energy_performance_data_misc_final.geojson", "w") as f:
        json.dump(results, f, indent=2, default=str)