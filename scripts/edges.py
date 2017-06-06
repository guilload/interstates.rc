import json
import itertools
import heapq
from geopy.distance import vincenty
from collections import defaultdict

# Converts city data e.g....

    # [{
    #     'id': 0, 
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
            if route not in by_routes:
                by_routes[route] = []
            by_routes[route] += [(city['city'], city['state'], city['id'])]
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

routes = ['I-10','I-12','I-15','I-17','I-19','I-20','I-24','I-25','I-27','I-29','I-30','I-35','I-35E','I-35W','I-37','I-4','I-40','I-41','I-43','I-44','I-45','I-49','I-5','I-55','I-57','I-64','I-65','I-66','I-69','I-69 West','I-70','I-71','I-73*','I-74','I-75','I-76','I-77','I-78','I-8','I-80','I-83','I-84','I-85','I-87','I-90','I-93','I-94','I-95','I-96']

def get_edges(cities):
    edges = []
    route_pairs = get_route_pairs(cities)
    for route in route_pairs:
        for pair in route['pairs']:        
            edges.append({
                "group_name": route['route'],
                "group": routes.index(route['route']), # routes.. called group to color in D3
                "source_id": "%s" % pair[0][2],
                "source": "%s, %s" % (pair[0][0], pair[0][1]),
                "target_id": "%s" % pair[1][2],
                "target": "%s, %s" % (pair[1][0], pair[1][1]),
                "value": get_distance(pair, cities),
                })
    return edges


def put_edges_in_heaps(cities):
    heaps = []
    edges = get_edges(cities)
    routes = [route for city in cities for route in city['routes']]
    unique_routes = set(routes)
    for route in unique_routes:
        heap = []
        for item in edges:
            if item['route'] == route:
                heapq.heappush(heap, item)
        heaps.append({
            "route": route,
            "heap": heap,
        })

    # TEST
    # while heap:
    #     print(heappop(heap)['distance'])

    return heaps

states = ['Alaska', 'Arizona', 'California', 'Colorado', 'District of Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Kansas', 'Kentucky', 'Louisiana', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Missouri', 'Nebraska', 'Nevada', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Tennessee', 'Texas', 'Virginia', 'Washington', 'Wisconsin']

def get_nodes(cities):
    new_cities_list = []
    for city in cities:
        city_map = {}
        city_map['id'] = "%s, %s" % (city['city'], city['state'])
        city_map['latitude'] = city['latitude']
        city_map['longitude'] = city['longitude']
        city_map['population'] = int(city['population'])
        city_map['group'] = states.index(city['state'])
        new_cities_list.append(city_map)
    return new_cities_list



with open("data/edges.json", "w") as f:
    f.write(json.dumps(get_edges(cities), sort_keys=True, indent=4))

with open("data/vis.json", "w") as f:
    f.write(json.dumps({"links": get_edges(cities), "nodes": get_nodes(cities)}, indent=4))



class UnionFind(object):

    def __init__(self, capacity):
        self._array = range(capacity)
        self._sizes = [1] * capacity
        self.count = capacity

    def connected(self, p, q):
        return p == q or self.find(p) == self.find(q)

    def find(self, p):
        while p != self._array[p]:
            p = self._array[p]

        return p

    def union(self, p, q):
        if p != q:
            proot = self.find(p)
            qroot = self.find(q)

            if proot != qroot:
                psize = self._sizes[proot]
                qsize = self._sizes[qroot]

                if psize < qsize:
                    self._array[proot] = qroot
                    self._sizes[qroot] += psize
                else:
                    self._array[qroot] = proot
                    self._sizes[proot] += qsize

                self.count -= 1


def mst(edges):
    groups = defaultdict(list)
    mst_edges = []

    for edge in edges:
        groups[edge["group_name"]].append((edge["value"], edge))

    for route, group in groups.items():

        city_ids = set()
        for _, edge in group:
            city_ids.add(edge["source_id"]) 
            city_ids.add(edge["target_id"])

        uf_id_to_city_id = dict(enumerate(city_ids))
        city_id_to_uf_id = {v: k for k, v in uf_id_to_city_id.items()}


        heapq.heapify(group)
        n = len(city_ids) - 1
        uf = UnionFind(len(city_ids))

        while n > 0:
            _, edge = heapq.heappop(group)
            from_id = city_id_to_uf_id[edge["source_id"]]
            to_id = city_id_to_uf_id[edge["target_id"]]

            if not uf.connected(from_id, to_id):
                mst_edges.append(edge)
                n -= 1
                uf.union(from_id, to_id)
    return mst_edges            


with open("data/mst_vis.json", "w") as f:
    f.write(json.dumps({"links": mst(get_edges(cities)), "nodes": get_nodes(cities)}, indent=4))


