## Name: Augmentation_Replacement_Plans.py
## Created on: 2019-07-06
## By: Sophie Plassin
## Description: Preparation of the CO Augmentation Replacement Plans dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Rename and export feature class
##              3. Select the plans in division 3 (Rio Grande)
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

# Set overwrite option
arcpy.env.overwriteOutput = True

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\final_output\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\inter_output\\CO\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\final_output\\"
arcpy.env.workspace = dirpath


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = "CO_WaterRights.shp"
gdb_name = "Augm_Repl_Plan.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Rename and export feature class
## Description: Rename feature class

print "\nStep 2 Rename and export feature class starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdbList =[]
in_file = "CO_WaterRights"

arcpy.FeatureClassToGeodatabase_conversion(in_file + ".shp", out_gdb)
feature = in_file.split(".shp")[0]
fc_gdb = os.path.join(out_gdb, feature)
outName = "CO_Structure"
out_featureclass = os.path.join(out_gdb, outName)
arcpy.Rename_management(fc_gdb, out_featureclass, data_type)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Select the Augmentation/Replacement plans in division 3 (Rio Grande)
## Description: Select all the structures for Divison 3 using Select layer by attribute

print "\nStep 3 Select the plans in Division 3 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

#Selection
expression = "\"StructType\" = \'Augmentation/Replacement Plan\'"

# Execute
arcpy.MakeFeatureLayer_management(out_featureclass, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
name = "CO_Augment_replacement_plans.shp"
selectFile = os.path.join(finalFolder, name)
arcpy.CopyFeatures_management("temp", selectFile)

# Delete unecessary fields
fieldsDel2 = ["OBJECTID"]
arcpy.DeleteField_management(selectFile, fieldsDel2)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")





