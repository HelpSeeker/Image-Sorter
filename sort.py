#!/usr/bin/env python3
"""Simple image sorter based on histogram differences."""

import argparse
import os
import shutil

import cv2

class Image:
    """Hold all image-related information."""

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.out = None
        if not os.path.exists(self.path):
            raise argparse.ArgumentTypeError(f"image doesn't exist ({self.path})")

        try:
            # BGR->HSV leads to more accurate results in my experience
            self.data = cv2.cvtColor(cv2.imread(self.path), cv2.COLOR_BGR2HSV)
        except cv2.error:
            raise argparse.ArgumentTypeError(f"invalid input image ({self.path})")
        self.hist = [cv2.calcHist([self.data], [0], None, [256], (0, 256)),
                     cv2.calcHist([self.data], [1], None, [256], (0, 256)),
                     cv2.calcHist([self.data], [2], None, [256], (0, 256))]

    def assign_label(self, label):
        """Assemble output path."""
        in_name = os.path.basename(self.path)
        out_name = f"{label}_{in_name}"

        self.out = os.path.join(opts.out_dir, out_name)

    def copy(self):
        """Copy file with new label to output directory."""
        shutil.copy(self.path, self.out)


def parse_cli():
    """Parse the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("images", metavar="image", type=Image,
                        nargs="+", help="input images to sort")
    parser.add_argument("-p", "--path", dest="out_dir", type=os.path.abspath,
                        metavar="PATH", default=os.path.join(os.getcwd(), "sorted"),
                        help="output directory for sorted images")
    return parser.parse_args()


def similarity(img1, img2):
    """Calculate histogram difference between 2 images."""
    # OpenCV histogram comparison methods
    # https://docs.opencv.org/4.3.0/d8/dc8/tutorial_histogram_comparison.html
    #   0: Correlation
    #   1: Chi-Square
    #   2: Intersection
    #   3: Bhattacharyya distance
    # IMPORTANT: 0,2 -> higher = more similar
    #            1,3 -> lower  = more similar (more akin to distance)
    score = cv2.compareHist(img1.hist[0], img2.hist[0], 2) + \
            cv2.compareHist(img1.hist[1], img2.hist[1], 2) + \
            cv2.compareHist(img1.hist[2], img2.hist[2], 2)
    return score


def main():
    """Run the main function body."""
    # Brute-force closest pair of points problem (only with higher score = closer)
    # https://en.wikipedia.org/wiki/Closest_pair_of_points_problem
    for i in range(len(opts.images)-1):
        max_score = 0
        max_img = i+1
        for j in range(i+1, len(opts.images)):
            score = similarity(opts.images[i], opts.images[j])
            if score > max_score:
                max_score = score
                max_img = j
        opts.images[i+1], opts.images[max_img] = opts.images[max_img], opts.images[i+1]

    # Create output directory
    if not os.path.exists(opts.out_dir):
        os.mkdir(opts.out_dir)

    # Copy opts.images based on their new sorting
    label = 1
    width = len(str(len(opts.images)))
    for img in opts.images:
        img.assign_label(f"{label:0{width}}")   # Pad sort number with zeros
        img.copy()
        label += 1


if __name__ == '__main__':
    try:
        opts = parse_cli()
        main()
    except KeyboardInterrupt:
        print("\nUser interrupt!")
