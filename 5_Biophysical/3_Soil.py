## Name: Soil.py
## Created on: 2019-04-10
## By: Sophie Plassin
## Description: Preparation of the soil shapefile for the Rio Grande/Bravo basin (RGB)
##              1. Clip the shapefile (GCS: WGS 1984)
##              2. Project the shapefiles to North America Albers Equal Area Conic
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

### Workspace
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\3_soil\\original_input\\"
dirpath = arcpy.env.workspace

# Local variables:
fcList = arcpy.ListFeatureClasses()
interFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\3_soil\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\3_soil\\final_output\\"

# List
clippedList = []
clip_features = []


## ---------------------------------------------------------------------------
## 1. Clip
## Description: Clip the soil polygon for the study area.

print "\nStep 1 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin.shp", "RGB_Ses.shp"]
xy_tolerance = ""

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

print clip_features

# Execute Clip
for fc in fcList:
    name = "soil"
    print name
    for clip in clip_features:
        temp = os.path.split(clip)[-1]
        print temp
        if temp.startswith("RGB_Basin"):
            output = interFolder + name + "_bas.shp"
        else:
            output = interFolder + name + "_ses.shp"
        print output
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        clippedList.append(output)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 1 Clip completed at", datetime.datetime.now().strftime("%I:%M:%S%p")



## ---------------------------------------------------------------------------
## 2. Project the polygon
## Description: Project RGB soil polygon to North America Albers Equal Area Conic

print "\nStep 2 Project the polygon starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in clippedList:
    name = os.path.split(fc)[1]
    projFile = os.path.join(finalFolder, name)
    print projFile
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Project completed at", datetime.datetime.now().strftime("%I:%M:%S%p")






