Due to copy right issue, we public images of PR1954 instead of PR1956 (their data and method are nearly the same)

This project is mainly based on our NeurIPS 2019 workshop paper [Information Extraction from Text Region with Complex Tabular Structure](https://openreview.net/pdf?id=Hkx0zpccLr)

# Repo Structure

### `Documents/`

Files explaining the methods of [preprocessing](Documemts/PreprocessingMethods.md) and [classification](Documemts/ClassificationMethods.md)

### `Visualization/`

Code for visualization results

### `OCR/`

Code for using Google Cloud Vision API

### `Preprocessing/`

Code for preprocessing pipeline

### `CNN/`, `GraphicalModel/`, and `Postprocessing/`

Code for classification pipeline

# Dataset

## Introduction

Please look at the second section of our [paper](https://openreview.net/pdf?id=Hkx0zpccLr). Notice that PR1954 doesn't have class `Table`.

|   |  |
| ------------- | ------------- |
| Number of Raw Scans | 684 |
| Page Bbox  | Yes  |
| ROI Bbox   | Yes  |
| Column Bbox   | Yes  |
| Row Bbox   | Yes  |

## Download

[Code](DownloadPR1954.sh) for downloading PR1954. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) is required to download PR1954.

## AWS S3 Directory Structure

### `Raw Image`
AWS S3 path: `s3://harvardaha-raw-data/personnel-records/1954/scans/`

### `Labeled Data`
AWS S3 path: `s3://harvardaha-results/personnel-records/1954/labeled_data/`

### `Image Segmentation Results`
AWS S3 path: `s3://harvardaha-results/personnel-records/1954/seg/`

### `Classification Results`
CNN probability output: `s3://harvardaha-results/personnel-records/1954/prob/`

CRF output: `s3://harvardaha-results/personnel-records/1954/cls/CRF/`

# Demo

If you have download the whole dataset and want to reproduce the results, please read the files in `Documents/` and run correspondent shell one by one. Remember to modify the input/output path.

If you have download the whole dataset and want to visualize the results, run correspondent shell in `Visualization/`. Remember to modify the input/output path.

(will update soon)
A demo [code]() which downloads one sample data and visualizes results.
