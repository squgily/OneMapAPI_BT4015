import requests
import json
from get_token import get_token

url = "https://www.onemap.gov.sg/api/public/popapi/getTypeOfDwellingPop?"

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

household_types = []

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

    household_type_data = response.json()

    item = household_type_data[0]

    feature = {
        "type": "Feature",
        "geometry": area_geom,
        "properties": {
            "planning_area": area,
            "population_hdb_1_and_2_room_flats": item["hdb_1_and_2_room_flats"],
            "population_hdb_3_room_flats": item["hdb_3_room_flats"],
            "population_hdb_4_room_flats": item["hdb_4_room_flats"],
            "population_hdb_5_room_and_executive_flats": item["hdb_5_room_and_executive_flats"],
            "population_condominiums_and_other_apartments": item["condominiums_and_other_apartments"],
            "population_landed_properties": item["landed_properties"],
            "population_others": item["others"],
            "population_year": item["year"],
            "population_total_hdb": item["total_hdb"]
        }
    }

    household_types.append(feature)

geojson_feature_collection = {
    "type": "FeatureCollection",
    "features": household_types
}

print(response.text)

output_path = "data/sgp_household_pop_data_area_2020.geojson"
 
with open(output_path, "w") as f:
    json.dump(geojson_feature_collection, f, indent=2, ensure_ascii=False)
 