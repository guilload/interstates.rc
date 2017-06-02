import json
import itertools
from geopy.distance import vincenty

# Converts city data e.g....

    # [{
    #     'city': 'New York', 
    #     'state': 'New York', 
    #     'routes': [
    #                   'I-95',
    #               ], 
    #     'rank': u '1', 
    #     'latitude': 40.7127837, 
    #     'longitude': -74.0059413, 
    #     'growth_from_2000_to_2013': '4.8%', 
    #     'population': '8405837'
    # }, etc.]

# Into...

    # [
    #   {from, to, distance, route},
    #   {from, to, distance, route},
    #   {from, to, distance, route},
    #   {from, to, distance, route},
    # ]


with open('data/cities.json') as data_file:
    cities = json.load(data_file)


def get_route_pairs(cities):
    # takes list of city objects
    # returns:
        # [
        #   {
        #       "route": route, 
        #       "pairs": [(city1, state1), (city2, state2)), etc.]
        #   },
        # ]
    by_routes = {}
    route_pairs = []
    for city in cities:
        for route in city['routes']:
            if route not in by_routes.keys():
                by_routes[route] = []
            by_routes[route] += [(city['city'], city['state'])]
    for route, city_states in by_routes.iteritems():
        pairs = list(itertools.combinations(city_states, 2))
        route_pairs.append({
            "pairs": pairs,
            "route": route
            })
    return route_pairs


def get_distance(pair, cities):
    for city in cities:
        if city['city'] == pair[0][0] and city['state'] == pair[0][1]:
            lat1 = city['latitude']
            long1 = city['longitude']
        elif city['city'] == pair[1][0] and city['state'] == pair[1][1]:
            lat2 = city['latitude']
            long2 = city['longitude']
        else:
            pass
    distance = vincenty((lat1, long1), (lat2, long2)).miles
    return distance 


def get_edges(cities):
    edges = []
    route_pairs = get_route_pairs(cities)
    for route in route_pairs:
        for pair in route['pairs']:        
            edges.append({
                "route": route['route'],
                "from": pair[0],
                "to": pair[1],
                "distance": get_distance(pair, cities),
                })
    return edges


print(get_edges(cities))

