import csv
import json
from pathlib import Path

# inputs sit next to this script; the JSON it writes is imported by the site from src/data/
HERE = Path(__file__).resolve().parent
OUT = HERE.parent

# info

info = {}

with open(HERE / "candidate_info.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:

        mainkey = row["main"]

        dict1 = {}

        for key in row: 
            dict1.update({key: row[key]})

        info.update({mainkey: dict1})

print(info)

with open(OUT / "candidate_info.json", "w") as outfile:
    json.dump(info, outfile)


# correlations

nodes = []
links = []

with open(HERE / "candidate_correlations.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        
        source = row["x"]
        group = row["x"][-4:]
        print(group)
        nodes.append({"id": source, "group": group})

        for key in row:
            value = row[key]
            
            if value == '1':
                break
            
            if key != "x" and float(value):
                links.append({"source": source, "target": key, "value": float(value)})

print(nodes)
print(links)

data = {
    "nodes": nodes,
    "links": links
}

with open(OUT / "candidate_links.json", "w") as outfile:
    json.dump(data, outfile)