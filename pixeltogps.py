import numpy as np
import sys


#Gets command line argument
if len(sys.argv) != 2:
    print("Usage: python pixeltogps.py <input_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    #Read input file while checking for errors
    with open(input_file, 'r') as f:
        altitude, current_x, current_y, N = map(float, f.readline().split())
        object_coords = [tuple(map(float, line.split())) for line in f]

    #Check if there are exactly N pixel coordinates
    if len(object_coords) != int(N):
        print(f"Error: Expected {int(N)} pixel coordinates, but found {len(object_coords)} coordinates.")
        sys.exit(1)

except FileNotFoundError:
    print(f"Error: Input file '{input_file}' not found.")
    sys.exit(1)
except ValueError:
    print("Error: Invalid input format in the input file.")
    sys.exit(1)

#Constants like image dimensions and fov degrees
image_width = 5472
image_height = 3648
horizontal_fov_deg = 23.4
vertical_fov_deg = 15.6
earth_radius = 6371000  #Earth's radius in meters

#Converts the fov to radians
horizontal_fov_rad = np.radians(horizontal_fov_deg)
vertical_fov_rad = np.radians(vertical_fov_deg)

#Finds the center x and y of the image
center_x = image_width / 2
center_y = image_height / 2

#List to store GPS coordinates
gps_coords = []

#For each object, this calculates GPS coordinates by looping through them
for pixel_x, pixel_y in object_coords:
    try:
        #This calculates the angular distances from the center of the image
        delta_horizontal = (pixel_x - center_x) / image_width * horizontal_fov_rad
        delta_vertical = (pixel_y - center_y) / image_height * vertical_fov_rad

        #This calculates the horizontal and vertical distances in meters
        horizontal_distance = altitude * np.tan(delta_horizontal)
        vertical_distance = altitude * np.tan(delta_vertical)

        #Calculates the GPS coordinates relative to the drone's current position in the image
        object_longitude = current_x + (horizontal_distance / earth_radius) * (180 / np.pi)
        object_latitude = current_y + (vertical_distance / earth_radius) * (180 / np.pi)

        gps_coords.append((round(object_longitude, 5), round(object_latitude, 5)))
    except ZeroDivisionError:
        print("Error: Divide by zero error. Please check input values.")
        sys.exit(1)

# Writes output to the pinpoint.out file
with open('pinpoint.out', 'w') as f:
    for lon, lat in gps_coords:
        f.write(f"{lon} {lat}\n")

print("Output successfully written to pinpoint.out")
