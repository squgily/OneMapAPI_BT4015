import requests
import json
from get_token import get_token

url = "https://www.onemap.gov.sg/api/public/popapi/getPopulationAgeGroup?"

token = get_token()

#print(token)

headers = {"Authorization": token}
    
##list areas
with open("data/sgp_planning_areas_2019.json", "r") as f:
    data = json.load(f)   # ✅ correct function for files

#print(data)

areas = []
areas_geom = []

#print(data["SearchResults"])

for item in data["SearchResults"]:
    areas.append(item["pln_area_n"])

    raw_geom = item["geojson"]
    geom = json.loads(raw_geom)  # Convert string to dict
    areas_geom.append(geom)


#print(areas)

data = []

for area, area_geom in zip(areas, areas_geom):

    params = {
        "year": 2020,
        "planningArea": area,
    }

    response = requests.get(url, params=params, headers=headers)
    household_type_data = response.json()

    props = {"planning_area": area, "year": 2020}

    print(f"Processing area: {area}")
    age_cols = [c for c in household_type_data[0] if c.startswith("age_")]

    for item in household_type_data:
        gender = item["gender"].lower()  # "female", "male", "total"
        for col in age_cols:
            props[f"{gender}_{col}"] = item[col]
        props[f"{gender}_total"] = item["total"]

    feature = {
        "type": "Feature",
        "geometry": area_geom,
        "properties": props
    }

    data.append(feature)

geojson_feature_collection = {
    "type": "FeatureCollection",
    "features": data
}

output_path = "data/sgp_age_range_data_area_2020.geojson"

with open(output_path, "w") as f:
    json.dump(geojson_feature_collection, f, indent=2, ensure_ascii=False)