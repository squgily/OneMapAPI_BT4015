import requests
import json
from get_token import get_token
    
url = "https://www.onemap.gov.sg/api/public/popapi/getAllPlanningarea?year=2019"

token = get_token()
    
headers = {"Authorization": token}
    
response = requests.request("GET", url, headers=headers)

data = response.json()
geometries = data['SearchResults']

print(data)
    
features = []
for item in geometries:
    # Convert the geojson string to a geometry object
    geometry = json.loads(item["geojson"])

 
    # Create a single Feature (NOT a FeatureCollection)
    feature = {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "pln_area_n": item["pln_area_n"],
            "id": item["id"]
        }
    }
 
    # Append the feature to the list
    features.append(feature)
 
# After the loop, wrap all features in ONE FeatureCollection
geojson_feature_collection = {
    "type": "FeatureCollection",
    "features": features
}

output_path = "sgp_planning_areas_2019.geojson"
 
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(geojson_feature_collection, f, indent=2, ensure_ascii=False)
 
