import csv
import json

nodes = []
links = []

with open ("candidate_correlations.csv", "r") as csvfile:
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

with open("candidate_links.json", "w") as outfile:
    json.dump(data, outfile)