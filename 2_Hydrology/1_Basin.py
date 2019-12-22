## Name: Basin.py
## Created on: 2019-08-02
## By: Sophie Plassin
## Description: Preparation of the basin shapefile for the Rio Grande/Bravo basin (RGB)
##              1. Select By Attributes all sub-basins part of the RGB
##              2. Project the shapefiles to North America Albers Equal Area Conic
##              3. Dissolve: Aggregate all sub-basin in one feature
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
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\1_basin\\original_input\\"
dirpath = arcpy.env.workspace

# Local variables:
fcList = arcpy.ListFeatureClasses()
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\1_basin\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\1_basin\\final_output\\"

# List
fcList = arcpy.ListFeatureClasses()
selectList = []
finalList = []


## ---------------------------------------------------------------------------
## 1. Select by Attributes
## Description: Select all sub-basins located in the RGB, i.e. with MAJ_BAS = 2001

print "\nStep 1 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

expression = "\"MAJ_BAS\" = 2001"

for fc in fcList:
    arcpy.MakeFeatureLayer_management(fc, "temp")
    arcpy.SelectLayerByAttribute_management("temp", 'NEW_SELECTION', expression)
    name = "Sub_Basins_wgs84.shp"
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
    name = "Sub_Basins.shp"
    projFile = os.path.join(finalFolder, name)
    arcpy.Project_management(fc, projFile, outCS)
    finalList.append(projFile)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Project completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Dissolve
## Description: Dissolve the sub-basins MAJ_BAS = 2001 to create the boundaries of the RGB 

print "\nStep 3 Dissolve starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

dissolveField = ["MAJ_BAS", "MAJ_NAME", "MAJ_AREA"]

for fc in finalList:
    name = "RGB_Basin.shp"
    dissolveFile = os.path.join(finalFolder, name)
    arcpy.Dissolve_management(fc, dissolveFile, dissolveField)
    print "Dissolve" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 Project completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


print "Geoprocess Basin completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")













