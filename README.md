# Image Sorter

Python script to sort images based on histogram similarity via OpenCV.

The sorting algorithm is unoptimized, but otherwise it works pretty well.

## Usage

```
usage: sort.py [-h] [-p PATH] [-b N] [-t N] [-i] image [image ...]

positional arguments:
  image                 input images to sort

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  output directory for sorted images (def: ./sorted)
  -b N, --bins N        number of bins for histogram computation (def: 10)
  -t N, --threads N     max. number of processes to use (def: 1)
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

## Adjusting bins

How many bins to use to computate the histograms has a great influence on the resulting sort order.

One thing that can be said with certainty: **More bins take longer.** However, they don't necessarily increase the quality of the image matching.

Lower bin counts are more likely to match similar images with small differences (e.g. changed background). Higher bin counts are more likely to match the same image with shifted colors or cropped images. Going either too high or too low will get rid of these beneficial effects and only match on a very basic level.

**Recommended values:** 10-50
