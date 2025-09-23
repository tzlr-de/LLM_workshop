import cv2
import numpy as np
import argparse

def detect_corners(image_path, output_path):
    # Load the image
    img = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect corners using the Shi-Tomasi algorithm
    corner_params = dict(maxCorners=500, qualityLevel=0.3, minDistance=7, blockSize=7, useHarrisDetector=False, k=0.04)
    corners = cv2.goodFeaturesToTrack(gray, mask=None, **corner_params)

    # Draw corners on the original image
    for corner in corners:
        x, y = corner.ravel().astype(int)
        cv2.circle(img, (x, y), 3, (0, 255, 0), -1)

    # Save the visualization to a separate file
    cv2.imwrite(output_path, img)

def main(args):
    detect_corners(args.image_path, args.output_path)


parser = argparse.ArgumentParser(description="Corner Detection Example")
parser.add_argument("image_path", help="Path to the input image.")
parser.add_argument("output_path", help="Path to save the output image with detected corners.")

args = parser.parse_args()
main(args)
