"""
Aggregate HDB resale CSV by block + street name.
Produces one row per block with count, min, avg, and max resale price.
 
Usage:
    python aggregate_blocks.py input.csv [output.csv]
 
If output.csv is omitted the results are printed to stdout.


"""
 
import csv
from collections import defaultdict

input_path = "OneMap_georeference_commercial_URA/Residential_ResaleFlatPrices/Resale flat prices based on registration date from Jan-2017 onwards.csv" 
output_path = "OneMap_georeference_commercial_URA/Residential_ResaleFlatPrices/aggregated_carpeta/Resale_Mar_2017_agg.csv"

groups = defaultdict(list)

with open(input_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row["block"], row["street_name"])
        groups[key].append(row)

with open(output_path, "w", newline="") as f:
    fieldnames = [
        "month", "town", "flat_type", "block", "street_name",
        "floor_area_sqm", "flat_model", "lease_commence_date",
        "num_transactions", "min_price", "max_price", "avg_price", "total_price"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for (block, street), rows in sorted(groups.items(), key=lambda x: (x[0][1], x[0][0])):
        prices = [int(r["resale_price"]) for r in rows]
        sample = rows[0]
        writer.writerow({
            "month": sample["month"],
            "town": sample["town"],
            "flat_type": sample["flat_type"],
            "block": block,
            "street_name": street,
            "floor_area_sqm": sample["floor_area_sqm"],
            "flat_model": sample["flat_model"],
            "lease_commence_date": sample["lease_commence_date"],
            "num_transactions": len(prices),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": round(sum(prices) / len(prices)),
            "total_price": sum(prices),
        })

print(f"Done. Written to {output_path}")
