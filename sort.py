#!/usr/bin/env python3
"""Simple image sorter based on histogram differences."""

import argparse
import os
import shutil
import sys

from concurrent.futures import ProcessPoolExecutor

import cv2

class Image:
    """Hold all image-related information."""

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.out = None

        # BGR->HSV leads to more accurate results in my experience
        data = cv2.cvtColor(cv2.imread(self.path), cv2.COLOR_BGR2HSV)
        self.hist = [cv2.calcHist([data], [0], None, [256], (0, 256)),
                     cv2.calcHist([data], [1], None, [256], (0, 256)),
                     cv2.calcHist([data], [2], None, [256], (0, 256))]
        # Normalizing the histograms leads to more accurate results for (large)
        # dimension differences for chi-square and intersection comparisons
        # The L1 norm performed the best in my tests
        self.hist = [cv2.normalize(h, h, norm_type=cv2.NORM_L1) for h in self.hist]

    def assign_label(self, label):
        """Assemble output path."""
        in_name = os.path.basename(self.path)
        out_name = f"{label}_{in_name}"

        self.out = os.path.join(opts.out_dir, out_name)

    def copy(self):
        """Copy file with new label to output directory."""
        shutil.copy(self.path, self.out)


def valid_image(img):
    """Check input for existence and support."""
    # List of potentially supported image formats (varies across systems)
    # https://docs.opencv.org/4.3.0/d4/da8/group__imgcodecs.html#ga288b8b3da0892bd651fce07b3bbd3a56
    supported = (
        ".bmp", ".dib",                          # Windows bitmaps
        ".jpeg", ".jpg", ".jpe",                 # JPEG files
        ".jp2",                                  # JPEG 2000 files
        ".png",                                  # Portable Network Graphics
        ".webp",                                 # WebP
        ".pbm", ".pgm", ".ppm", ".pxm", ".pnm",  # Portable image format
        ".pfm",                                  # PFM files
        ".sr", ".ras",                           # Sun rasters
        ".tiff", ".tif",                         # TIFF files
        ".exr",                                  # OpenEXR Image files
        ".hdr", ".pic",                          # Radiance HDR
    )

    valid = True
    ext = os.path.splitext(img)[1]
    if not os.path.exists(img):
        print(f"{img}: image doesn't exist")
        valid = False
    elif not (os.path.isfile(img) and ext in supported):
        print(f"{img}: invalid input image")
        valid = False

    if not (valid or opts.ignore_errors):
        sys.exit(1)

    return valid


def positive_int(string):
    """Convert string provided by parse_cli() to a positive int."""
    try:
        value = int(string)
        if value <= 0:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError("invalid positive int")

    return value


def parse_cli():
    """Parse the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("images", metavar="image", type=os.path.abspath,
                        nargs="+", help="input images to sort")
    parser.add_argument("-p", "--path", dest="out_dir", type=os.path.abspath,
                        metavar="PATH", default=os.path.join(os.getcwd(), "sorted"),
                        help="output directory for sorted images (def: ./sorted)")
    parser.add_argument("-t", "--threads", type=positive_int, default=1, metavar="N",
                        help="how many images to read in parallel (def: 1)")
    parser.add_argument("-i", "--ignore-errors", action="store_true",
                        help="ignore invalid input file errors")

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
    images = [i for i in opts.images if valid_image(i)]
    if opts.threads > 1:
        with ProcessPoolExecutor(max_workers=opts.threads) as executor:
            images = [*executor.map(Image, images)]
    else:
        images = [Image(i) for i in images]

    # Brute-force closest pair of points problem (only with higher score = closer)
    # https://en.wikipedia.org/wiki/Closest_pair_of_points_problem
    for i in range(len(images)-1):
        max_score = 0
        max_img = i+1
        for j in range(i+1, len(images)):
            score = similarity(images[i], images[j])
            if score > max_score:
                max_score = score
                max_img = j
        images[i+1], images[max_img] = images[max_img], images[i+1]

    # Create output directory
    if not os.path.exists(opts.out_dir):
        os.mkdir(opts.out_dir)

    # Copy opts.images based on their new sorting
    label = 1
    width = len(str(len(images)))
    for img in images:
        img.assign_label(f"{label:0{width}}")   # Pad sort number with zeros
        img.copy()
        label += 1


if __name__ == '__main__':
    try:
        opts = parse_cli()
        main()
    except KeyboardInterrupt:
        print("\nUser interrupt!")
