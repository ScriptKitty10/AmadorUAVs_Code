import numpy as np
import cv2
import sys
from collections import defaultdict

#Converts rgb into a tuple
def rgb_to_tuple(rgb_value):
    return tuple(map(int, rgb_value))

#Converts rgb value to color name like red or blue
def rgb_to_color_name(rgb_value):
    r, g, b = rgb_value
    
    #Color ranges and names
    color_ranges = {
        "red": [(100, 0, 0), (255, 100, 100)],
        "green": [(0, 100, 0), (100, 255, 100)],
        "blue": [(0, 0, 100), (100, 100, 255)],
        "yellow": [(150, 150, 0), (255, 255, 180)],
        "orange": [(200, 100, 0), (255, 200, 100)],
        "purple": [(100, 0, 100), (150, 150, 255)],
        "pink": [(200, 100, 150), (255, 200, 200)],
        "brown": [(100, 50, 0), (150, 100, 50)],
        "gray": [(50, 50, 50), (200, 200, 200)],
        "white": [(200, 200, 200), (255, 255, 255)]
    }

    for color, (lower, upper) in color_ranges.items():
        if lower[0] <= r <= upper[0] and lower[1] <= g <= upper[1] and lower[2] <= b <= upper[2]:
            return color

    return "Unknown"

#Checks if two colors are similar and applies tolerance if they are almost the same
def are_colors_similar(color1, color2, tolerance=10):
    return all(abs(max(0, min(a, 255)) - max(0, min(b, 255))) <= tolerance for a, b in zip(color1, color2))

#Gets top colors
def get_top_common_colors(image, color_tolerance=10):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  #Converts BGR to RGB
    pixels = image.reshape(-1, 3)  #Reshapes the pixels into a list
    
    color_counts = defaultdict(int)
    for pixel in pixels:
        color = rgb_to_tuple(pixel) #This loop checks if colors are similar
        color_name = rgb_to_color_name(pixel)
        is_similar = False
        for stored_color in color_counts.keys():
            if are_colors_similar(color, stored_color, color_tolerance):
                is_similar = True
                color_counts[stored_color] += 1
                break
        if not is_similar:
            color_counts[color] += 1

    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    #Filters repeated colors and gets the top common colors of object
    top_common_colors = []
    previous_color_name = None
    for color, count in sorted_colors:
        color_name = rgb_to_color_name(color)
        if len(top_common_colors) < 3 and color_name != previous_color_name:
            top_common_colors.append((color, color_name, count))
            previous_color_name = color_name
    
    return top_common_colors


#Gets input from command line arguments as image file
if len(sys.argv) != 2:
    print("Usage: python imagecolors.py <image_file>")
    sys.exit(1)

input = sys.argv[1]

try:
    #Reads image
    img = cv2.imread(input)

    #Checks if image is usable
    if img is None:
        raise Exception("Error: Could not load image.")

    #Resize image for better detection
    img = cv2.resize(img, (0, 0), fx=0.6, fy=0.6)

    #Converts image to grayscale
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #This applies threshold values for grayscale
    ret, thresh = cv2.threshold(imgray, 100, 150, 0)

    #Now find contours for shape detection
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    #Filter small contours using threshold value
    min_contour_area = 1

    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_contour_area:
            filtered_contours.append(contour)

    #Draws the lines around the shapes detected
    cv2.drawContours(img, filtered_contours, -1, (0, 255, 0), 3)
    cv2.drawContours(imgray, filtered_contours, -1, (0, 255, 0), 3)

    #Gets the top colors found in shape
    top_common_colors = get_top_common_colors(img, color_tolerance=10)
    top_common_colors.pop(0)

    #Gets the color's names
    color_names = [color_name for _, color_name, _ in top_common_colors]
    color_names_str = ', '.join(color_names)

    #Writes output to colordetect.out
    with open('colordetect.out', 'w') as output_file:
        output_file.write(color_names_str)

    print("Output successfully written to colordetect.out")

#Check if theres any errors such as file not found and code errors
except FileNotFoundError:
    print(f"Error: The file '{input}' does not exist.")
except cv2.error as e:
    print(f"OpenCV Error: {e}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
