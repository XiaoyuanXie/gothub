#!/usr/bin/env python
# Brandon Heller
#
# Utility functions for geo-graphs
#
# Geo-graphs are NetworkX graphs where:
# nodes are (lat, long) tuples with these fields:
#   selfedges: float
#   name: array of names
#   location: array of locations
# edges have these fields:
#   weight: float
from operator import itemgetter

import networkx as nx

# From http://hoegners.de/Maxi/geo/
import geo
# To test, go to http://www.daftlogic.com/projects-google-maps-distance-calculator.htm
# and run this code - see if the Portland - SanFran distance is ~533 miles.
# portland = geo.xyz(45.5, -122.67)
# sanfran = geo.xyz(37.777, -122.419)
METERS_TO_MILES = 0.000621371192
# print geo.distance(portland, sanfran) * METERS_TO_MILES


def geo_stats(g, sep = "\t"):
    """Compute stats for a geo-graph."""
    i = 0
    node_weight = 0
    selfedges = 0
    locations = 0
    for node in g.nodes_iter():
        node_weight += len(g.node[node]["name"])
        selfedges += g.node[node]["selfedges"]
        locations += len(g.node[node]["location"])
    edge_weight = 0
    for src, dst in g.edges_iter():
        edge_weight += g[src][dst]["weight"]

    s = ''
    s += sep + "nodes: %i\n" % g.number_of_nodes()
    s += sep + "edges: %i\n" % g.number_of_edges()
    s += sep + "node weight: %0.2f\n" % node_weight
    s += sep + "edge weight: %0.2f\n" % edge_weight
    s += sep + "selfedges: %i\n" % selfedges
    s += sep + "locations: %i\n" % locations

    return s


# Filter out unusable locations, like 106 people who said Earth...
BAD_LOCATIONS = [
]

# Top 12 cities, just a start.
CITIES = [
    ((u'37.777125', u'-122.419644'), 'San Francisco', 100),
    ((u'51.506325', u'-0.127144'), 'London', 100),
    ((u'40.714550', u'-74.007124'), 'New York', 100),
    ((u'35.670479', u'139.740921'), 'Tokyo', 100),
    ((u'41.884150', u'-87.632409'), 'Chicago', 100),
    ((u'47.603560', u'-122.329439'), 'Seattle', 90),
    #((u'51.164175', u'10.454145'), 'Germany', 200)
    ((u'52.516074', u'13.376987'), 'Berlin', 50),
    ((u'48.856930', u'2.341200'), 'Paris', 150),
    #((u'55.008390', u'-5.822485'), 'UK', 270) # would subsume London, but Ireland too.
    #((u'32.991405', u'138.460247'), 'Japan', 50),
    ((u'45.511795', u'-122.675629'), 'Portland', 80),
    ((u'43.648560', u'-79.385324'), 'Toronto', 100),
    ((u'-33.869629', u'151.206955'), 'Sydney', 100),
    ((u'34.053490', u'-118.245319'), 'Los Angeles', 100)
]

def valid(node, location):
    if node in BAD_LOCATIONS:
        return False
    if node == (None, None):
        return False
    return True


def in_range(node, city, radius):
    node_geo = geo.xyz(float(node[0]), float(node[1]))
    city_geo = geo.xyz(float(city[0]), float(city[1]))
    dist = geo.distance(node_geo, city_geo) * METERS_TO_MILES
    return dist < radius


def geo_cluster(g):
    '''Cluster nodes via curated city descriptions.'''
    # Find/print the top N geo locations
    n = 100
    data = []  # Array of ((lat, long), names, [location]) tuples
    filtered_users = 0
    filtered_locations = []
    valid_users = 0
    # For each node, add those users to the total.
    for node in g:
        location = g.node[node]["location"]
        name = g.node[node]["name"]
        if valid(node, location):
            data.append((node, len(name), location))
            valid_users += len(name)
        else:
            filtered_users += len(name)
            filtered_locations.append(location)
    try:
        data = sorted(data, key = itemgetter(1), reverse = True)
    except IndexError:
        print e
    top = []
    # Print out data as a sanity check.
    for i in range(n):
        top.append(data[i])
        locs = list(data[i][2])
        loc_strs = []
        for j in range(min(5, len(locs))):
            loc_strs.append(locs[j])
        print data[i][0], data[i][1], loc_strs

    print "stats for filtered graph:"
    print "\tunique geo-locations: %i" % g.number_of_nodes()
    print "\tvalid users: %i" % valid_users
    print "\tfiltered users: %i" % filtered_users
    print "\tfiltered locations: %s" % len(filtered_locations)
    print "\ttotal users: %i" % (valid_users + filtered_users)

    city_data = {} # map of city (lat, long) pairs to dict of total,
    # Allocate each city to the nearest 12, or don't allocate.
    # A starting implementation only - doesn't handle edge reassignment.
    edge_map = {} # map original node locations to new ones.
    city_total = 0
    others_total = 0
    for (node, names, location) in data:
        found = False
        for city_loc, city_name, radius in CITIES:
            if in_range(node, city_loc, radius):
                if city_loc not in city_data:
                    city_data[city_loc] = {'total': 0, 'name': city_name}
                #print "%s @%s covers %s @ %s\n" % (city_name, city_loc, node, location)
                city_data[city_loc]['total'] += names
                edge_map[node] = city_loc
                found = True
                break
        if not found:
            others_total += names
            edge_map[node] = (0, 0)
        else:
            city_total += names

    print "stats for geo-clustered graph:"
    print "\tunique geo-locations (eq 13?): %i" % len(set(edge_map.values()))
    print "\tcity_total: %i" % city_total
    print "\tothers_total: %i" % others_total
    print "\tcity_data: %s" % city_data

    # note coverage

    r = nx.DiGraph()

    return r


def geo_node_stats(g):
    '''Print detailed stats for each node'''
    for node in g:
        print "node %i: %s" % (i, node)
        #print g.node[node]
        selfedges = g.node[node]["selfedges"]
        location = g.node[node]["location"]
        name = g.node[node]["name"]
        print "\tselfedges: %s" % selfedges
        print "\tlocations (%i): %s" % (len(location), location)
        print "\tnames: %i" % len(name)
        #print "\tnames (%i): %s" % (len(name), name)
        print "\tout_degree: %i" % len(g.neighbors(node))
        print "\tin_degree: %i" % len(g.predecessors(node))
        i += 1