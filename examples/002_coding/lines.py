import cv2
import numpy as np

import  argparse

def detect_lines(image_path, output_path):

    image = cv2.imread(image_path)

    # Convert the input image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection to find edges in the image
    edged = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Find the lines in the edge map using Hough transform
    lines = cv2.HoughLinesP(edged, 1, np.pi/180, 100, minLineLength=10, maxLineGap=20)
    print(lines.shape)

    # Draw the detected lines on a separate image
    vis_lines = image.copy()

    # Loop over the detected lines and draw them on the original image as green pixels
    for line in lines:
        line = line[0]
        cv2.line(vis_lines, (line[0], line[1]), (line[2], line[3]), (255, 0, 0), thickness=2)

    # Save the visualization of the detected lines to a separate file
    cv2.imwrite(output_path, vis_lines)


def main(args):
    detect_lines(args.image_path, args.output_path)

parser = argparse.ArgumentParser()

parser.add_argument("image_path", help="Path to input image file")
parser.add_argument("output_path", help="Path to save visualization image")
main(parser.parse_args())
