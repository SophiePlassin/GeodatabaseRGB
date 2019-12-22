## Name: Protected_Areas.py
## Created on: 2019-07-07
## By: Sophie Plassin
## Description: Preparation of the Land Ownership dataset for the Rio Grande/Bravo basin (RGB)
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

# Set options
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False


print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\9_protected_areas\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\9_protected_areas\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\9_protected_areas\\final_output\\"
arcpy.env.workspace = dirpath

# List
projList = []

## ---------------------------------------------------------------------------
## 1. Project the polygon
## Description: Project RGB soil polygon to North America Albers Equal Area Conic

print "\nStep 1 Project the polygon starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for path, dirs, files in os.walk(dirpath):
    for fc in files:
        if fc.endswith(".shp"):
            absFile=os.path.abspath(os.path.join(path, fc))
            name = os.path.splitext(fc)[0]
            projFile = os.path.join(interFolder, name + ".shp")
            arcpy.Project_management(absFile, projFile, outCS)
            print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
            projList.append (projFile)
            

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Clip
## Description: Clip the Protected Areas polygon for the study area.

print "\nStep 2 Clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin.shp", "RGB_Ses.shp"]
xy_tolerance = ""
clip_features = []
for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute Clip
for fc in projList:
    for clip in clip_features:
        temp = os.path.split(clip)[-1]
        name = "CEC_Protected_Areas"
        if temp.startswith("RGB_Basin"):
            output = finalFolder + "\\" + name + "_bas.shp"
        else:
            output = finalFolder + "\\" + name + "_ses.shp"
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")





