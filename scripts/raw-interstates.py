import json

from collections import defaultdict


with open("raw-cities.json") as lines:
    CITIES = json.loads("\n".join(lines.readlines()))


ROUTES = defaultdict(set)


with open("raw-interstates.tsv") as lines:
    for line in lines:
        route, state, cities = line.strip().split("\t")

        for city in cities.split(","):
            ROUTES[(state, city.strip())].add(route)

for city in CITIES:
    city["routes"] = sorted(ROUTES[(city["state"], city["city"])])


with open("cities.json", "w") as f:
    f.write(json.dumps(CITIES, sort_keys=True, indent=4))
