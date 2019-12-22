# -*- coding: cp1252 -*-
## Name: RiverNetwork.py
## Created on: 2019-08-02
## By: Sophie Plassin
## Description: Preparation of the river network shapefiles for the Rio Grande/Bravo basin (RGB)
##              1. Select By Attributes all rivers, part of the RGB
##              2. Project the shapefiles to North America Albers Equal Area Conic
##              3. Rename field MAJ_NAME to "Rio Grande - Bravo" because of special characters issues
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

### Set environment settings
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\2_river\\original_input\\"
dirpath = arcpy.env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\2_river\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\2_river\\final_output\\"

# List
fcList = arcpy.ListFeatureClasses()
selectList = []
finalList = []


## ---------------------------------------------------------------------------
## 1. Select by Attributes
## Description: Select all rivers located in the RGB, i.e. with MAJ_BAS = 2001

print "\nStep 1 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

expression = "\"MAJ_BAS\" = 2001"

for fc in fcList:
    arcpy.MakeFeatureLayer_management(fc, "temp")
    arcpy.SelectLayerByAttribute_management("temp", 'NEW_SELECTION', expression)
    name = "Rivers_wgs84.shp"
    out_feature = os.path.join(interFolder, name)
    arcpy.CopyFeatures_management("temp", out_feature)
    selectList.append(out_feature)      
    print "Select by attribute" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 1 Select By Attribute completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Project the polygon
## Description: Project RGB soil polygon to North America Albers Equal Area Conic

print "\nStep 2 Project the polygon starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in selectList:
    name = os.path.split(fc)[1]
    name = name [0:6] + ".shp"
    projFile = os.path.join(finalFolder, name)
    arcpy.Project_management(fc, projFile, outCS)
    finalList.append(projFile)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Project completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Rename field MAJ_NAME
## Description: Rename field MAJ_NAME to "Rio Grande - Bravo" because of special characters issues

print "\nStep 3 Rename field MAJ_NAME starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

field = "MAJ_NAME"
for fc in finalList:
    arcpy.CalculateField_management(fc, field, '"' + "Río Grande - Bravo" + '"', "PYTHON_9.3")

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "Geoprocess Rivers completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")






