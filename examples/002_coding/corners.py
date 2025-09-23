
import argparse
import numpy
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
    corners = numpy.int32(corners)

    # Draw the corners on the original image
    for i in range(corners.shape[0]):
        corner = tuple(corners[i][0])
        x, y = corner[0], corner[1]
        cv2.circle(image, (x, y), 5, (0, 255), -1)

    # Save the visualization of the detected corners
    cv2.imwrite(output_image, image)

def detect_lines(input_image, output_image):
    """ This function detects lines in the given image and
        saves the visualization of the detected lines in a
        separate file
    """
    # Load the image from disk
    image = cv2.imread(input_image)

    # Convert the input image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection to find edges in the image
    edged = cv2.Canny(gray, 50, 150, apertureSize=3)
    # Find lines using Hough Line Transform
    lines = cv2.HoughLinesP(edged, 1, numpy.pi / 180, threshold=50, minLineLength=100, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 3)

    # Save the visualization of the detected lines
    cv2.imwrite(output_image, image)


def main(args):
    # detect_corners(args.image_path, args.output_image)

    detect_lines(args.image_path, args.output_image)



parser = argparse.ArgumentParser()
parser.add_argument("image_path", type=str, help="Path to input image file")
parser.add_argument("output_image", type=str, help="Output image where the corners will be saved")
args = parser.parse_args()
main(args)
