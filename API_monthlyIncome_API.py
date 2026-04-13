import requests
import json
import time
from get_token import get_token

url = "https://www.onemap.gov.sg/api/public/popapi/getHouseholdMonthlyIncomeWork"

token = get_token()
headers = {"Authorization": token}

with open("sgp_planning_areas_2019.json", "r") as f:
    data = json.load(f)

areas = []
areas_geom = []

for item in data["SearchResults"]:
    areas.append(item["pln_area_n"])
    raw_geom = item["geojson"]
    geom = json.loads(raw_geom)
    areas_geom.append(geom)

income = []

for area, area_geom in zip(areas, areas_geom):
    print(f"Processing area: {area}")

    params = {"year": 2020, "planningArea": area}

    # Retry logic
    for attempt in range(3):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            break
        print(f"  Attempt {attempt+1} failed ({response.status_code}), retrying...")
        time.sleep(2)
    else:
        print(f"  Skipping {area} after 3 failed attempts")
        continue

    # Check no-data before parsing JSON
    if response.text.strip() == '{"Result": "No Data Available!"}':
        print(f"  No data for {area}")
        continue

    try:
        income_data = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"  Invalid JSON for {area}: {response.text[:100]}")
        continue

    # ✅ check income_data, not data (data is your geojson file!)
    if isinstance(income_data, dict) and income_data.get('Result') == 'No Data Available!':
        print(f"  No data for {area}")
        continue

    if not isinstance(income_data, list) or len(income_data) == 0:
        print(f"  Unexpected response for {area}: {income_data}")
        continue

    item = income_data[0]

    feature = {
        "type": "Feature",
        "geometry": area_geom,
        "properties": {
            "planning_area": area,
            "total": int(item.get("total", 0)),
            "below_sgd_1000": int(item.get("below_sgd_1000", 0)),
            "no_working_person": int(item.get("no_working_person", 0)),
            "sgd_1000_to_1999": int(item.get("sgd_1000_to_1999", 0)),
            "sgd_2000_to_2999": int(item.get("sgd_2000_to_2999", 0)),
            "sgd_3000_to_3999": int(item.get("sgd_3000_to_3999", 0)),
            "sgd_4000_to_4999": int(item.get("sgd_4000_to_4999", 0)),
            "sgd_5000_to_5999": int(item.get("sgd_5000_to_5999", 0)),
            "sgd_6000_to_6999": int(item.get("sgd_6000_to_6999", 0)),
            "sgd_7000_to_7999": int(item.get("sgd_7000_to_7999", 0)),
            "sgd_8000_to_8999": int(item.get("sgd_8000_to_8999", 0)),
            "sgd_9000_to_9999": int(item.get("sgd_9000_to_9999", 0)),
            "sgd_10000_to_10999": int(item.get("sgd_10000_to_10999", 0)),
            "sgd_11000_to_11999": int(item.get("sgd_11000_to_11999", 0)),
            "sgd_12000_to_12999": int(item.get("sgd_12000_to_12999", 0)),
            "sgd_13000_to_13999": int(item.get("sgd_13000_to_13999", 0)),
            "sgd_14000_to_14999": int(item.get("sgd_14000_to_14999", 0)),
            "sgd_15000_to_17499": int(item.get("sgd_15000_to_17499", 0)),
            "sgd_17500_to_19999": int(item.get("sgd_17500_to_19999", 0)),
            "sgd_20000_over": int(item.get("sgd_20000_over", 0)),
            "sgd_8000_over": int(item.get("sgd_8000_over", 0)),
            "sgd_10000_over": int(item.get("sgd_10000_over", 0)),
            "year": item.get("year")
        }
    }

    income.append(feature) 

geojson_feature_collection = {
    "type": "FeatureCollection",
    "features": income
}

output_path = "sgp_monthly_income_household_data_area_2020.geojson"

with open(output_path, "w") as f:
    json.dump(geojson_feature_collection, f, indent=2, ensure_ascii=False)

print(f"{len(income)} areas written to {output_path}")