import requests
import json
from get_token import get_token

url = "https://www.onemap.gov.sg/api/public/popapi/getEthnicGroup?"

token = get_token()

#print(token)

headers = {"Authorization": token}
    
##list areas
with open("sgp_planning_areas_2019.json", "r") as f:
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

ethnic = []

for area, area_geom in zip(areas, areas_geom):

    params = {
    "year": 2020,
    "planningArea": area
    } 

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    print(response.text)

    ethnic_data = response.json()

    item = ethnic_data[0]

    feature = {
        "type": "Feature",
        "geometry": area_geom,
        "properties": {
            "planning_area": area,
            "chinese": item["chinese"],
            "malays": item["malays"],
            "indian": item["indian"],
            "others": item["others"],
            "year": item["year"]
        }
    }

    ethnic.append(feature)

geojson_feature_collection = {
    "type": "FeatureCollection",
    "features": ethnic
}

print(response.text)

output_path = "sgp_ethnic_data_area_2020.geojson"
 
with open(output_path, "w") as f:
    json.dump(geojson_feature_collection, f, indent=2, ensure_ascii=False)
 