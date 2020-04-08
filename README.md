# Image Sorter

Python script to sort images based on histogram similarity via OpenCV.

Single-threaded and unoptimized. But hey, at least it works.

## Usage

```
usage: sort.py [-h] [-p PATH] [-i] image [image ...]

positional arguments:
  image                 input images to sort

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  output directory for sorted images
  -i, --ignore-errors   ignore invalid input file errors
```

## Requirements

* Python >= 3.6
* [OpenCV](https://opencv.org/) (`opencv-python` when using pip)

## Supported image formats

The script accepts the following image extensions:

* Windows bitmaps - *.bmp, *.dib
* JPEG files - *.jpeg, *.jpg, *.jpe
* JPEG 2000 files - *.jp2
* Portable Network Graphics - *.png
* WebP - *.webp
* Portable image format - *.pbm, *.pgm, *.ppm *.pxm, *.pnm
* Sun rasters - *.sr, *.ras
* TIFF files - *.tiff, *.tif
* OpenEXR Image files - *.exr
* Radiance HDR - *.hdr, *.pic

Please note that this list contains all formats, which **MAY** be supported by [OpenCV's imread()](https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html#ga288b8b3da0892bd651fce07b3bbd3a56). Whether or not OpenCV can actually read all these file formats depends on your system.