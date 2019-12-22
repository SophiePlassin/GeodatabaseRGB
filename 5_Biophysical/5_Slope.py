## Name: Slope.py
## Created on: 2019-04-11
## By: Sophie Plassin
## Description: Compute the slope from each cell of the elevation raster for the Rio Grande/Bravo basin (RGB)
##              1. Slope in degree
##              2. Slope in percent
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
import glob
import itertools
from arcpy import env
from arcpy.sa import *

# Check out the ArcGIS extension
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

### Workspace
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\4_elevation\\final_output\\"
dirpath = env.workspace

## Set local variables
inRasterList = arcpy.ListRasters()
outRaster = "slope"
outFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\5_slope\\final_output\\"


## ---------------------------------------------------------------------------
## 1. Slope in Degree
## Description: Compute the slope in degree

print "\nStep 1 Slope in Degree starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute Slope in Degree
for raster in inRasterList:
    outSlope = Slope(raster, "DEGREE")
# Save the output
    if raster.endswith("bas"):
        name = outRaster + "deg" + "bas"
    else:
        name = outRaster + "deg" + "ses"
    outSlope.save(outFolder + name)
    print "Slope in degree" , raster, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "\nStep 1 Slope in Degree completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Slope in percent
## Description: Compute the slope in percent

print "\nStep 2 Slope in Percent starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute Slope in Percent
for raster in inRasterList:
    outSlope = Slope(raster, "PERCENT_RISE")
# Save the output
    if raster.endswith("bas"):
        name = outRaster + "pct" + "bas"
    else:
        name = outRaster + "pct" + "ses"
    outSlope.save(outFolder + name)
    print "Slope in Percent" , raster, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "\nStep 2 Slope in Percent completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

