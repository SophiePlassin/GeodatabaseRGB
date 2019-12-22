## Name: Elevation.py
## Created on: 2019-04-10
## By: Sophie Plassin
## Description: Preparation of the elevation raster dataset for the Rio Grande/Bravo basin (RGB)
##              1. ASCII to Raster
##              2. Extract by Mask (using GCS: WGS 1984)
##              3. Project the raster to North America Albers Equal Area Conic
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

# Extension
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

### Workspace
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\4_elevation\\original_input\\"
dirpath = arcpy.env.workspace


## ---------------------------------------------------------------------------
## 1. ASCII to Raster
## Description: Converts an ASCII file representing raster data to a raster dataset.

print "\nStep 1 ASCII to Raster starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set local variables
inASCII = os.path.join(dirpath, "GloElev_30as.asc")
outRaster = "elev"
outFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\4_elevation\\inter_output\\"

# Execute ASCIIToRaster
arcpy.ASCIIToRaster_conversion(inASCII, outFolder + outRaster)

print "\nStep 1 ASCII to Raster completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Extract by Mask
## Description: Extracts the cells of the elevation raster dataset that correspond to the study area (mask).

print "\nStep 2 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Mask
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin.shp", "RGB_Ses.shp"]
maskList = []

for fc in listfc:
        out_shp = os.path.join(folderShapefiles, fc)
        maskList.append(out_shp)

outputList =[]

# Execute Extract By Mask
for mask in maskList:
    temp = os.path.split(mask)[-1]
    if temp.startswith("RGB_Basin"):
        output = outFolder + outRaster + "_bas"
    else:
        output = outFolder + outRaster + "_ses"
    # Execute ExtractByMask
    inRaster = outFolder + outRaster
    outExtractByMask = ExtractByMask(inRaster, mask)
    # Save the output 
    outExtractByMask.save(output)
    outputList.append(output)
    print "Extract By Mask" , outRaster, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Extract By Mask completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Project rasters
## Description: Project RGB elevation raster dataset to North America Albers Equal Area Conic

print "\nStep 3 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\4_elevation\\final_output\\"
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

projList = []

for i in range(len(outputList)):
    name = os.path.split(outputList[i])[1]
    projFile = os.path.join(finalFolder, name)
    print projFile
    arcpy.ProjectRaster_management(outputList[i], projFile, outCS)
    print "Projection" , outputList[i], "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 Projection completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


