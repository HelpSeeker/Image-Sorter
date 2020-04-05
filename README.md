# Image Sorter

Python script to sort images based on histogram similarity via OpenCV.

Single-threaded, unoptimized and RAM hungry. But hey, at least it works.

## Usage

```
usage: sort.py [-h] [-p PATH] image [image ...]

positional arguments:
  image                 input images to sort

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  output directory for sorted images
```

## Requirements

* Python >= 3.6
* [OpenCV](https://opencv.org/) (`opencv-python` when using pip)
