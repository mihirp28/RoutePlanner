#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: snemanoh-mjp5-npoojary
#
# Based on skeleton code by B551 Course Staff, Fall 2023
#

import sys
import math
import heapq

class AStarSearch():
    def __init__(self, start, end, cost):
        self.start = start
        self.end = end
        self.cost = cost
        self.gps_city = {}
        self.segs_road = {}
        self.route = []
        self.cities_notknown = []
        self.dataset_preprocessor()

    def function_heuristic(self, city_1, city_2, cost):
        # Checking if the cost to be calculated is of segments
        if cost == 'segments':
            return 0
        
        # Checking if the cost to be calculated is of time
        elif cost == 'time' or cost == 'delivery':
            point1 = self.gps_city[city_1]
            point2 = self.gps_city[city_2]
            return math.dist(point1, point2) / 50
    
        # Checking if the cost to be calculated is of distance and delievery
        elif cost == 'distance':
            point1 = self.gps_city[city_1]
            point2 = self.gps_city[city_2]
            return math.dist(point1, point2)
        
    def dataset_preprocessor(self):
        with open("city-gps.txt", "r") as gps_file:
            for line in gps_file:
                words = line.strip().split()

                if len(words) >= 3:
                    city = " ".join(words[:-2])
                    latitude = float(words[-2])
                    longitude = float(words[-1])
                    
                    self.gps_city[city] = (latitude, longitude)

        # Loading data of the road segments from the .txt file
        with open("road-segments.txt", "r") as segments_file:
            for line in segments_file:
                words = line.split()
            
                city_1 = words[0]
                city_2 = words[1]

                dist = int(words[2])
                speed_lim = int(words[3])
                time = dist / speed_lim

                freeway = words[-1]

                if city_1 not in self.segs_road:
                    self.segs_road[city_1] = {}

                self.segs_road[city_1][city_2] = (dist, speed_lim, time, freeway)

                if city_2 not in self.segs_road:
                    self.segs_road[city_2] = {}

                self.segs_road[city_2][city_1] = (dist, speed_lim, time, freeway)

    def calculate_cost(self, city_1, city_2, d):
        if self.cost == 'distance':
            return self.segs_road[city_1][city_2][0]
        
        elif self.cost == 'segments':
            return 1
        
        elif self.cost == 'time':
            return self.segs_road[city_1][city_2][2]
        
        elif self.cost == 'delivery':
            length = self.segs_road[city_1][city_2][0]
            speed_lim = self.segs_road[city_1][city_2][1]
            time_cost = self.segs_road[city_1][city_2][2]
            
            if speed_lim >= 50:
                p = math.tanh(length / 1000)
                return time_cost + p * 2 * (time_cost + d)
            else:
                return time_cost

    def reconstruct_route(self, past_route, current_location):
        while current_location in past_route:
            for key, value in past_route.items():
                if key == current_location:
                    point_1 = key
                    point_2 = value[0]
                    dist = value[1]
                    current_location = point_2
                    self.route.append((point_1, point_2, dist))
        self.route.reverse()
        return self.route
    
    def junction_solve(self, jnc):

        def find_nearby_cities(city_from, lvl = 0, prev_cities_real = [], prev_jncs = []):
            jnc_cons = self.segs_road[city_from]
            cities_real = [city for city in jnc_cons if city in self.gps_city and city not in self.cities_notknown and city not in prev_cities_real]
            cities_real_props = [[(city, self.segs_road[city_from][city])] for city in set(cities_real)]
            
            if lvl < 1:
                junctions = [junction for junction in jnc_cons if junction not in self.gps_city and junction not in self.cities_notknown and junction not in prev_jncs]
                
                for junction in junctions:
                    nearby_cities_junction = find_nearby_cities(junction, lvl + 1, (cities_real + prev_cities_real), (junctions + prev_jncs) + [city_from])
                    nearby_cities_junction = [path for path in nearby_cities_junction if path[0][0] in self.gps_city and path[0][0] not in self.cities_notknown and path[0][0] not in (cities_real + prev_cities_real)]
                    
                    nearby_cities_junction_temp = [(path + [(junction, self.segs_road[city_from][junction])]) for path in nearby_cities_junction]
                    cities_real_props = cities_real_props + nearby_cities_junction_temp
            
            return cities_real_props

        num = [0.0, 0.0]
        den = 1.0

        for (to, data) in self.segs_road[jnc].items():
            if to not in self.gps_city:
                if to not in self.cities_notknown: self.cities_notknown.append(to)
                nearby_city_paths = find_nearby_cities(to)

                for nearby_city_path in nearby_city_paths:
                    gps_last = self.gps_city[nearby_city_path[0][0]]

                    i = len(nearby_city_path) // 2
                    minimized_distance_to_city = abs(sum([dis[1][0] for dis in nearby_city_path[:i]]) - sum([dis[1][0] for dis in nearby_city_path[i:]])) 
                    maximized_distance_to_city = sum([dis[1][0] for dis in nearby_city_path])

                    latitude_minimized = minimized_distance_to_city * gps_last[0]
                    latitude_maximized = maximized_distance_to_city * gps_last[0]

                    longitude_minimized = minimized_distance_to_city * gps_last[1]
                    longitude_maximized = maximized_distance_to_city * gps_last[1]

                    num[0] = (latitude_minimized + latitude_maximized) / 2
                    num[1] = (longitude_minimized + longitude_maximized) / 2

                    den = den + ((maximized_distance_to_city + minimized_distance_to_city) / 2)
            else:
                if to in self.gps_city:
                    to_gps = self.gps_city[to]

                    num[0] = num[0] + data[1] * to_gps[0]
                    num[1] = num[1] + (data[1] * to_gps[1])

                    den = den + data[1]

        self.gps_city[jnc] = (num[0] / den, num[1] / den)

    def a_star(self):   
        set_op = [(0, self.start)]
        visited_location = {}

        g_scr = {city: float('inf') for city in self.segs_road}
        g_scr[self.start] = 0

        f_scr = {city: float('inf') for city in self.segs_road}
        f_scr[self.start] = self.function_heuristic(self.start, self.end, self.cost)

        while set_op:
            _, current_location = heapq.heappop(set_op)

            if current_location == self.end:
                return self.reconstruct_route(visited_location, current_location)
            
            for route in self.segs_road[current_location]:
                seg_info = self.segs_road[current_location][route]

                if route not in self.gps_city:
                    if route not in self.cities_notknown:
                        self.cities_notknown.append(route)
                    self.junction_solve(route)
                    
                temp = g_scr[current_location]
                new_g_scr = g_scr[current_location] + self.calculate_cost(current_location, route, temp)

                if new_g_scr < g_scr[route]:
                    visited_location[route] = (current_location, seg_info)

                    g_scr[route] = new_g_scr
                    f_scr[route] = new_g_scr + self.function_heuristic(route, self.end, self.cost)

                    heapq.heappush(set_op, (f_scr[route], route))

def get_route(start, end, cost):
    
    """
    Find shortest driving route between start city and end city
    based on a cost function.

    1. Your function should return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-delivery-hours": a float indicating the expected (average) time 
                                   it will take a delivery driver who may need to return to get a new package
    2. Do not add any extra parameters to the get_route() function, or it will break our grading and testing code.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """
    a_star = AStarSearch(start, end, cost)
    path = a_star.a_star()

    total_delivery_hours = 0.0

    for i in range(len(path)):
        seg = path[i][2]
        road_len = seg[0]
        speed_lim = seg[1]
        time_cost = seg[2]

        if speed_lim >= 50:
            p = math.tanh(road_len / 1000)
            total_delivery_hours = total_delivery_hours + (time_cost + p * 2 * (time_cost + total_delivery_hours))
        else:
            total_delivery_hours = total_delivery_hours + time_cost

    route = {"total-segments" : len(path), 
            "total-miles" : float(sum([mile[2][0] for mile in path])),
            "total-hours" : sum([hours[2][2] for hours in path]), 
            "total-delivery-hours" : total_delivery_hours, 
            "route-taken" : [(city[0], f"{city[2][3]} for {city[2][0]} miles") for city in path]}
    
    return route

if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "delivery"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])
