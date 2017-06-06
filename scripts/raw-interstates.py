import json

from collections import defaultdict


with open("data/raw-cities.json") as lines:
    CITIES = json.loads("\n".join(lines.readlines()))


ROUTES = defaultdict(set)


with open("data/raw-interstates.tsv") as lines:
    for line in lines:
        route, state, cities = line.strip().split("\t")

        for city in cities.split(","):
            ROUTES[(state, city.strip())].add(route)


for i, city in enumerate(CITIES):
    city["id"] = i
    city["routes"] = sorted(ROUTES[(city["state"], city["city"])])


with open("data/cities.json", "w") as f:
    f.write(json.dumps(CITIES, sort_keys=True, indent=4))


