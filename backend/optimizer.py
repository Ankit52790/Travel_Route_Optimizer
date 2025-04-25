# backend/optimizer.py

import random
import math

def distance(a, b):
    return math.sqrt((a['lat'] - b['lat'])**2 + (a['lng'] - b['lng'])**2)

def total_distance(route, points):
    return sum(distance(points[route[i]], points[route[i + 1]]) for i in range(len(route) - 1))

def genetic_algorithm(points, generations=100, population_size=50):
    num_points = len(points)
    if num_points < 2:
        return []

    population = [random.sample(range(num_points), num_points) for _ in range(population_size)]

    for _ in range(generations):
        population.sort(key=lambda r: total_distance(r, points))
        next_gen = population[:10]  # elite selection
        while len(next_gen) < population_size:
            a, b = random.sample(population[:20], 2)
            half = len(a) // 2
            cross = a[:half] + [x for x in b if x not in a[:half]]
            if len(set(cross)) == num_points:
                next_gen.append(cross)
        population = next_gen

    best = min(population, key=lambda r: total_distance(r, points))
    return [points[i] for i in best]

def optimize_route(coordinate_list):
    """
    coordinate_list: List of tuples [(lat, lon), ...]
    returns: Optimized list of coordinates in route order
    """
    if not coordinate_list or len(coordinate_list) < 2:
        return []  # Need at least 2 points to form a route

    if len(coordinate_list) == 2:
        return coordinate_list  # No optimization needed, just return as-is

    points = [{'lat': lat, 'lng': lng} for lat, lng in coordinate_list]
    optimized = genetic_algorithm(points)

    # Convert back to list of tuples
    return [(p['lat'], p['lng']) for p in optimized]
