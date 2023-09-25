import numpy as np
import math
import sys


#Convex hull algorithm based on Graham's Scan
def graham_scan(points):
    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    #Nested method
    def convex_hull(points):
        n = len(points)
        if n < 3:
            return points

        hull = []

        #Find the leftmost point of the shape
        l = 0
        for i in range(1, n):
            if points[i][0] < points[l][0]:
                l = i
            elif points[i][0] == points[l][0] and points[i][1] < points[l][1]:
                l = i

        p = l
        while True:
            hull.append(points[p])

            q = (p + 1) % n
            for i in range(n):
                if orientation(points[p], points[i], points[q]) == 2:
                    q = i

            p = q

            if p == l:
                break

        return hull

    #Set hull_points to the convex hull
    hull_points = convex_hull(points)
    return np.array(hull_points)

#Calculates the angle and area of the box
def minimum_bounding_box(points):
    pi2 = np.pi / 2.

    #Gets the convex hull using Graham's Scan
    hull_points = graham_scan(points)

    #Gets the edge angles
    edges = np.zeros((len(hull_points) - 1, 2))
    edges = hull_points[1:] - hull_points[:-1]

    angles = np.zeros((len(edges)))
    angles = np.arctan2(edges[:, 1], edges[:, 0])

    angles = np.abs(np.mod(angles, pi2))
    angles = np.unique(angles)


    #Finds rotation Matrices
    rotations = np.vstack([
        np.cos(angles),
        np.cos(angles - pi2),
        np.cos(angles + pi2),
        np.cos(angles)]).T
    rotations = rotations.reshape((-1, 2, 2))

    #Put rotations to the convex hull
    rot_points = np.dot(rotations, hull_points.T)

    #Finds the 4 bounding points
    min_x = np.nanmin(rot_points[:, 0], axis=1)
    max_x = np.nanmax(rot_points[:, 0], axis=1)
    min_y = np.nanmin(rot_points[:, 1], axis=1)
    max_y = np.nanmax(rot_points[:, 1], axis=1)

    #Finds the box with the best area and smallest |θ|
    min_area = np.inf
    best_idx = None

    for i, (min_x_i, max_x_i, min_y_i, max_y_i) in enumerate(zip(min_x, max_x, min_y, max_y)):
        current_area = (max_x_i - min_x_i) * (max_y_i - min_y_i)
        current_orientation = angles[i]
        current_orientation_degrees = 90 - math.degrees(current_orientation)

        if current_area < min_area or (current_area == min_area and abs(current_orientation_degrees) < abs(orientation_degrees)):
            min_area = current_area
            best_idx = i

    #Gets the best angle in radians
    orientation = angles[best_idx]

    #Converts the radian angle to degrees (-90 to 90)
    orientation_degrees = 90 - math.degrees(orientation)

    #Adjust angle if its outside of range
    if orientation_degrees > 90:
        orientation_degrees -= 180
    elif orientation_degrees < -90:
        orientation_degrees += 180

    #Sets area as minimum area
    area = min_area


    return orientation_degrees, area


#Gets file by command line argument
if len(sys.argv) != 2:
    print("Usage: python boxpoints.py <input_file>")
    sys.exit(1)

input_file = sys.argv[1]

#Error handling in case file is not properly formatted
try:
    with open(input_file, 'r') as file:
        lines = file.readlines()

    if len(lines) < 2:
        print("Error: Input file should contain at least 2 lines (number of coordinates and the coordinates themselves).")
        sys.exit(1)

    N = int(lines[0])
    if N < 0:
        print("Error: The number of coordinates should be non-negative.")
        sys.exit(1)

    if len(lines[1:]) != N:
        print(f"Error: Expected {N} coordinates, but found {len(lines[1:])}.")
        sys.exit(1)

    coordinates = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != 2:
            print("Error: Each line should contain two coordinates.")
            sys.exit(1)

        try:
            x, y = map(int, parts)
            coordinates.append([x, y])
        except ValueError:
            print("Error: Invalid coordinates. Both coordinates should be integers.")
            sys.exit(1)

    points = np.array(coordinates)


    orientation, area = minimum_bounding_box(points)
    
    
    orientation = int(orientation * 100) / 100.0

    area = round(area, 2)

    #Output to box.out 
    with open('box.out', 'w') as output_file:
        output_file.write(f"{orientation} {area}")
    
    print("Output successfully written to box.out")

#Checks if file is not found or if there is an error
except FileNotFoundError:
    print(f"Error: Input file '{input_file}' not found.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {str(e)}")
    sys.exit(1)
