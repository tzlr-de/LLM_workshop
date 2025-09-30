#!/usr/bin/env python

import argparse

import numpy as np
import cv2


def detect_corners(input_image, output_image):
    """ This function detects corners in the given image and
        saves the visualization of the detected corners in a
        separate file
    """
    # Load the image from disk
    image = cv2.imread(input_image)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    corners = cv2.goodFeaturesToTrack(gray, 200, 0.01, 0.01)

    # convert the corners to int32
    corners = np.int32(corners)

    # Draw the corners on the original image
    for i in range(corners.shape[0]):
        corner = tuple(corners[i][0])
        x, y = corner[0], corner[1]
        cv2.circle(image, (x, y), 5, (0, 255), -1)

    # Save the visualization of the detected corners
    cv2.imwrite(output_image, image)

def main(args):
    detect_corners(args.image_path, args.output_image)



parser = argparse.ArgumentParser()
parser.add_argument("image_path", type=str, help="Path to input image file")
parser.add_argument("output_image", type=str, help="Output image where the corners will be saved")
args = parser.parse_args()
main(args)
