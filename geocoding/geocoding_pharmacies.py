import pandas as pd
import requests
import json
from sqlalchemy import null
from tqdm import tqdm
import time
from get_token import get_token
from geocoding.convert_address import convert_address

# Load dataset
df = pd.read_csv("ListingofLicensedPharmacies.csv")
#df["address"] = df["blk_no"].astype(str) + " " + df["street"]

#print(df)

batch_size = 100
results = []

start_idx = 100

for i, addr in enumerate(tqdm(df["pharmacy_address"][start_idx:]), start=start_idx):

    url = "https://www.onemap.gov.sg/api/common/elastic/search"
    token = get_token()

    if pd.isna(addr):
        continue

    if addr == "SG":
        continue

    addr_clean = convert_address(str(addr))

    params = {
        "searchVal": addr_clean,
        "returnGeom": "Y",
        "getAddrDetails": "Y",
        "pageNum": 1
    }

    #print(addr)
    print(addr_clean)

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
                "building_name": df["pharmacy_name"].iloc[i],
                "building_type": "PHARMACY",
                "address": r.get("ADDRESS"),
                "postal": r.get("POSTAL"),
                #"max_floor_lvl": df["max_floor_lvl"].iloc[i],
                #"year_completed": df["yearobtainedtopcsc"].iloc[i],
                #"building_type": df["buildingtype"].iloc[i],
                #"main_building_function": df["mainbuildingfunction"].iloc[i],
                #"gross_floor_area": df["grossfloorarea"].iloc[i]

            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(r["LONGITUDE"]),  # GeoJSON = [lon, lat]
                    float(r["LATITUDE"])
                ]
            }
        }

        print(feature)


        results.append(feature)

    #print(df.dtypes)
    #print(df.head())

    geojson = {
        "type": "FeatureCollection",
        "features": results
    }


    # Save every batch
    if (i + 1) % batch_size == 0:
        filename = f"onemap_pharmacies_{i+1}.geojson"
        with open(filename, "w") as f:
            json.dump(geojson, f, indent=2, default=str)

        results = []  # reset batch

    time.sleep(0.2)

# Save remaining records
if results:
    with open("onemap_pharmacies_final.geojson", "w") as f:
        json.dump(results, f, indent=2, default=str)