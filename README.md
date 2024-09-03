# RoutePlanner
## Problem
As dedicated museum professionals, we bear the responsibility of securely transporting precious artifacts and treasures from a museum, private collector, or a gallery in one city to another. Picture this: we are tasked with the mission of relocating a highly valuable treasure from an East Coast city to a West Coast city. However, here's the catch: the United States is an expansive country, crisscrossed by an intricate road network spanning over 4 million miles. Attempting to explore every conceivable route between these two treasure troves would be an insurmountable challenge. So, how do vigilant custodians like us
formulate an intelligent strategy for the efficient transportation of these priceless relics from one city to another? The solution lies in the ingenious A* algorithm!

We’ve prepared a dataset of major highway segments of the United States (and parts of southern Canada and northern Mexico), including highway names, distances, and speed limits; you can visualize this as a graph with nodes as towns and highway segments as edges. We’ve also prepared a dataset of cities and towns with corresponding latitude-longitude positions.
Your job is to find good driving directions between pairs of cities given by the user.
The skeleton code can be run on the command line like this:
  python3 ./route.py [start-city] [end-city] [cost-function]
where:
  • start-city and end-city are the cities we need a route between.
  • cost-function is one of:
  – segments tries to find a route with the fewest number of road segments (i.e. edges of the graph).
  – distance tries to find a route with the shortest total distance.
  – time finds the fastest route, assuming one drives the speed limit.
  – delivery finds the fastest route, in expectation, for a certain delivery driver. Whenever this driver drives on a road with a speed limit ≥ 50 mph, there is a chance that a package will fall out of their truck and be destroyed. They will have to drive to the end of that road, turn around, return to the start city to get a replacement, then drive all the way back to where they were (they won’t make the same mistake the second time they drive on that road).
Consequently, this mistake will add an extra 2·(troad +ttrip) hours to their trip, where ttrip is the time it took to get from the start city to the beginning of the road, and troad is the time it takes to drive the length of the road segment.
For a road of length ` miles, the probability p of this mistake happening is equal to tanh ( l/1000) if the speed limit is ≥ 50 mph, and 0 otherwise(1). This means that, in expectation, it will take troad + p · 2(troad + ttrip) hours to drive on this road.

For example:
  python3 ./route.py Bloomington,_Indiana Indianapolis,_Indiana segments

(1)--> This formula is not incredibly special, but what’s important is that it increases as the length of the road l increases, and it will always be between 0 and 1, which means it can be interpreted as a probability. You can access the tanh function in Python by using the math
module: from math import tanh

You’ll need to complete the get route() function, which returns the best route according to the specified cost function, as well as the number of segments, number of miles, number of hours for a car driver, and expected number of hours for the delivery driver. See skeleton code for details.

Like any real-world dataset, our road network has mistakes and inconsistencies; in the example above, for example, the third city visited is a highway intersection instead of the name of a town. Some of these “towns” will not have latitude-longitude coordinates in the cities dataset; you should design your code to still work well in the face of these problems.

## Solution
AStarSearch Class: It initializes A* search class with information about start and end city, as well as cost function chosen (segments, distance, time, or delivery). It also sets up data structures to store GPS coordinates, the final route, and road segment information.

function_heuristic: It estimates cost of traveling from one city to another based on specified cost function. For segments, it returns 0 since the cost is constant. For time, it calculates the time based on distance between GPS coordinates divided by 50. For distance or delivery, it calculates straight-line distance between GPS coordinates. This estimation guides A* search algorithm.

dataset_preprocessor: It processes and loads data from two text files, city-gps.txt and road-segments.txt. It extracts GPS coordinates of cities and road segment information, storing them for later use in A* search.

calculate_cost: Given two cities, function calculates cost of traveling between them based on chosen cost function (distance, segments, time, or delivery). It retrieves information about road segments and computes cost accordingly.

reconstruct_route: It reconstructs the route taken by backtracking through visited locations and road segments. It starts from destination city and works backward to starting city, collecting route information as it goes.

junction_solve: It handles cases where a city is also a junction point. It calculates the GPS coordinates of such junctions based on nearby cities and road lengths, allowing for more accurate routing.

a_star: The A* search algorithm is implemented here. It finds the shortest route from the start to end city while considering the estimated cost provided by heuristic function. It uses priority queue to explore most promising routes first.

get_route: Entry point for obtaining a driving route. It creates an instance of the AStarSearch class and uses the A* algorithm to find the best route based on the specified cost function. It returns a dictionary with route details, including segments, miles, hours, and delivery hours.
