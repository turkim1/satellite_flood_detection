# Satellite Flood Detection with Multispectral Satellite Imagery
### Candela Pelliza, Mohamed Dhia TURKI, Rodrigo Brust Santos

### Software Development

Paris-Lodron Universität Salzburg
Z-GIS

August 2023
_______

## 1. Introduction

This repository contains workflow codes for flood detection using Landsat or Sentinel-2 multispectral imagery. It is part of the final project of the course Software Development, Summer Semester 2023, University of Salzburg (PLUS).


## 2. Objectives
The final project contains two objectives, one general and one specific:

`1. General Objective`: Apply the knowledge acquired throughout the semester about the Python language and geospatial applications.

`2. Specific Objective`: Develop a workflow in which the user can extract flooded areas of a specific region using pixel difference. The final outputs are the flooded areas in rasterized and polygonal formats.

## 3. Methodology
The work was divided into 3 main parts:

`1. Image Download`: In this first part of the workflow, with the help of APIs, functions were built to enable the download of satellite scenes. Additionally, some preprocessing steps were performed, such as clipping the area to a perfect polygon, thereby avoiding edge effects in the raster file.

`2. Image Pre-processing`: In the second part of the work, the stacking of bands into a single file and metadata updates are performed.

`3. Image Comparison`: Finally, the pre- and post-flood event images are opened, compared using the NDWI (Normalized Difference Water Index), a pixel difference is performed, and then exported as raster and polygon.

## 4. Results



## 5. Conclusions