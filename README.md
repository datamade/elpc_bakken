# ELPC Bakken Well File PDF Extraction

This Makefile extracts text from PDFs, OCR images in PDFS, and
extracts data. 

## requirements
* ocrfeeder 
* tesseract
* python3
* poppler-utils

```bash
> sudo apt-get install tesseract-ocr ocrfeeder poppler-utils
```

## To run
* Place pdfs in `pdf` directory
* run `make`

To parallelize task use the -j command `make -j 8` will use 8 processes.
