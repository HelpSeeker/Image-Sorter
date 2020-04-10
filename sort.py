#!/usr/bin/env python3
"""Simple image sorter based on histogram differences."""

import argparse
import os
import shutil
import sys

from concurrent.futures import ProcessPoolExecutor

import cv2


class DefaultOptions:
    """Define and store all import user settings."""

    ### Common options ###
    # Output directory for the sorted images
    PATH = os.path.join(os.getcwd(), "sorted")

    # Number of bins used for histogram computation
    #   Low numbers  -> less prone to small differences (e.g added background)
    #   High numbers -> less prone to color shifts or cropping
    # Recommended: 10-50
    BINS = 10

    # Max. number of processes (!) for image reading/histogram calculation
    THREADS = 1

    # Whether to ignore invalid input files
    IGNORE_ERRORS = False

    ### Advanced Options ###
    CHANNELS = [0, 1, 2]
    # OpenCV uses 0-179 as Hue range, but 0-255 gives me better results somehow
    # Also makes it easier to switch between BGR and HSV input
    RANGE = [0, 256, 0, 256, 0, 256]

    # OpenCV normalization methods for histogram normalization
    # https://docs.opencv.org/master/d2/de8/group__core__array.html#gad12cefbcb5291cf958a85b4b67b6149f
    NORM = cv2.NORM_L1

    # OpenCV histogram comparison methods
    # https://docs.opencv.org/master/d6/dc7/group__imgproc__hist.html#ga994f53817d621e2e4228fc646342d386
    # IMPORTANT:
    #   Correlation, Intersection           -> higher = more similar
    #   Chi-Square,  Bhattacharyya distance -> lower  = more similar (more akin to distance)
    COMP_METHOD = cv2.HISTCMP_INTERSECT


class Image:
    """Hold all image-related information."""

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.out = None

        # BGR->HSV leads to more accurate results in my experience
        data = cv2.cvtColor(cv2.imread(self.path), cv2.COLOR_BGR2HSV)
        self.hist = cv2.calcHist([data], opts.channels, None,
                                 [opts.bins, opts.bins, opts.bins], opts.range)
        # Normalizing the histograms leads to more accurate results
        self.hist = cv2.normalize(self.hist, self.hist, norm_type=opts.norm)

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
    defaults = DefaultOptions()

    parser = argparse.ArgumentParser()
    parser.add_argument("images", metavar="image", type=os.path.abspath,
                        nargs="+", help="input images to sort")
    parser.add_argument("-p", "--path", dest="out_dir", type=os.path.abspath,
                        metavar="PATH", default=defaults.PATH,
                        help="output directory for sorted images (def: ./sorted)")
    parser.add_argument("-b", "--bins", type=positive_int,
                        metavar="N", default=defaults.BINS,
                        help="number of bins for histogram computation (def: %(default)s)")
    parser.add_argument("-t", "--threads", type=positive_int,
                        default=defaults.THREADS, metavar="N",
                        help="max. number of processes to use (def: %(default)s)")
    parser.add_argument("-i", "--ignore-errors", action="store_true",
                        default=defaults.IGNORE_ERRORS,
                        help="ignore invalid input file errors")

    parser.set_defaults(
        channels=defaults.CHANNELS,
        range=defaults.RANGE,
        norm=defaults.NORM,
        comp_method=defaults.COMP_METHOD,
    )

    return parser.parse_args()


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
            score = cv2.compareHist(images[i].hist, images[j].hist, opts.comp_method)
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
