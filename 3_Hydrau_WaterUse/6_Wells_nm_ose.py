## Name: Wells_NM_ose.py
## Created on: 2019-05-20
## By: Sophie Plassin
## Description: Preparation of the shapefile mapping wells in Mexico
##              1. Select by attributes all PODs that are groundwater wells
##              2. Save output data to final folder
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Wells_NM_ose starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\final_output\\"
dirpath = arcpy.env.workspace

# Options
arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

# Directories
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\6_Wells\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\6_Wells\\final_output\\"

## ---------------------------------------------------------------------------
## 1. Select by attributes
## Description: Select all PODs that are groundwater wells

print "\nStep 1 Select by attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_file = "NM_WaterRights.shp"

# Expression
expression = "\"pod_basin\" <> \'SD\' AND \"pod_basin\" <> \'SP\'"

#Execute Selection
arcpy.MakeFeatureLayer_management(in_file, "temp") 
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
output = os.path.join(finalFolder, "Wells_nm_nmose.shp")
arcpy.CopyFeatures_management("temp", output)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


