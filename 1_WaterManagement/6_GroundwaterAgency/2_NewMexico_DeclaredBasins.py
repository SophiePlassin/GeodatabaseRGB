## Name: NM Declared GW basins.py
## Created on: 2019-07-06
## By: Sophie Plassin
## Description: Preparation of the NM Declared GW basins dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Edit attribute table
##              3. Select by attribute (all groundwater located in the RGB)
##              4. Project the dataset to North America Albers Equal Area Conic
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\original_input\\NM\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\inter_output\\NM\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\final_output\\"
arcpy.env.workspace = dirpath

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = "Declared_Groundwater_Basins"
gdb_name = "GW_Basins.gdb"
data_type = "FeatureClass"
# Output
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)
arcpy.FeatureClassToGeodatabase_conversion(in_file + ".shp", out_gdb)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Edit attribute table
## Description: Delete fields

print "\nStep 2 Add and delete fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output
out_featureclass = os.path.join(out_gdb, in_file)

fieldList = arcpy.ListFields(out_featureclass)
fieldsDel = ["Shape_Leng", "OBJECTID_1", "GlobalID", "Shape__Are", "Shape__Len"]

for field in fieldList:
    if field.name == 'Basin':
        arcpy.AlterField_management(out_featureclass, field.name, 'Basin_Name', 'Basin_Name')
arcpy.DeleteField_management(out_featureclass, fieldsDel)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Select by attribute
## Description: Select all groundwater basins located in the RGB

print "\nStep 3 Select layer by attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Selection
expression = "\"OBJECTID\" IN (37, 36, 34, 31, 30, 29, 26, 22, 20, 19, 17, 16, 15, 11, 10, 5, 4, 2)"

# Execute
arcpy.MakeFeatureLayer_management(out_featureclass, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
final_name = os.path.split(out_featureclass)[-1]
outfile = os.path.join(out_gdb, "NM_declared_GW_basins")
arcpy.CopyFeatures_management("temp", outfile)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 4. Project the polygon and calculate new area
## Description: Project to North America Albers Equal Area Conic

print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"

name = os.path.split(outfile)[1] + ".shp"
projFile = os.path.join(finalFolder, name)
arcpy.Project_management(outfile, projFile, outCS)
print "Projection", outfile, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
arcpy.CalculateField_management(projFile, "Shape_Area", expressionArea, "PYTHON_9.3")
arcpy.CalculateField_management(projFile, "Shape_Leng", expressionLength, "PYTHON_9.3")

# Fields to delete
fieldDel = ["OBJECTID_1"]

arcpy.DeleteField_management(projFile, fieldDel)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")






