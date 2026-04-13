import requests
import json
    
url = "https://www.onemap.gov.sg/api/public/popapi/getAllPlanningarea?year=2019"
    
headers = {"Authorization": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMTY4MywiZm9yZXZlciI6ZmFsc2UsImlzcyI6Ik9uZU1hcCIsImlhdCI6MTc3MzY3NTU5NSwibmJmIjoxNzczNjc1NTk1LCJleHAiOjE3NzM5MzQ3OTUsImp0aSI6IjUxNzQ1MmI5LWQ5ZTctNDFmZi05OTE0LTAxZjk5NzcyMDcyYiJ9.mOEHkJPKviu-E2N1nK4RlxDwkt5JhInZWr1HgykXSC0Iiucku-oJXCNEUty_-9j_wSRaPe8FGbipsFcawHsAeUe4vNrZ2uFKDF-hwIvLZqua7zJ-c2_pH3-k2_KZ4RwrtHbllS6GRpkhQY-cetjYKYpBGHm0XjaieeOrx3rTV1CTF2A5u7ZJ93064LGlSNUuqu1lwVRZm60q-DxRx3gban5iGJC2LbPUyHoM83ie_mV55VSWGVaEPcxtzGA7r7jpJDkMHIAgquOmGtFOC50Wi9_GpariJNjRx-1FpUc1w_NN9jk9LKUi8KoFjQd8bgfArjJlDT0VoQLoYqIg11Jc-w"}
    
response = requests.request("GET", url, headers=headers)

data = response.json()
geometries = data['SearchResults']
    
features = []
for item in geometries:
    # Convert the geojson string to a geometry object
    geometry = json.loads(item["geojson"])
 
    # Create a single Feature (NOT a FeatureCollection)
    feature = {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "pln_area_n": item["pln_area_n"]
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
 
