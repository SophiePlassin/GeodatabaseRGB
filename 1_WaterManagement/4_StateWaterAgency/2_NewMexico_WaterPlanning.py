## Name: New Mexico agencies.py
## Created on: 2019-06-30
## By: Sophie Plassin
## Description: Preparation of the NM Water Planning Regions dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Rename and export feature class
##              3. Homogeneize fields
##              4. Project the dataset to North America Albers Equal Area Conic
##              5. Select by attribute all regions in the RGB.
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\original_input\\NMOSE\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\inter_output\\NMOSE\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\final_output\\"
arcpy.env.workspace = dirpath


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_file = "Water_Planning_Regions"
gdb_name = "WPR_Boundaries.gdb"
data_type = "FeatureClass"
out_gdb = interFolder + gdb_name
outname = "NMOSE_WaterPlanningRegions"

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)
arcpy.FeatureClassToGeodatabase_conversion(in_file + ".shp", out_gdb)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Rename and export feature class
## Description: Rename feature class

print "\nStep 2 Rename and export feature class starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fc_gdb = os.path.join(out_gdb, in_file)
out_featureclass = os.path.join(out_gdb, outname)
arcpy.Rename_management(fc_gdb, out_featureclass, data_type)
fieldList = arcpy.ListFields(out_featureclass)

for field in fieldList:
    if field.name == 'wpr_id':
        arcpy.AlterField_management(out_featureclass, field.name, 'ID_WPR', 'ID_WPR')
    if field.name == 'name':
        tmp = ("{0}_tmp".format('name'))
        arcpy.AlterField_management(out_featureclass, 'name', tmp)
        title = field.name.title()
        arcpy.AlterField_management(out_featureclass, tmp, title) 
        
print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Homogeneize fields
## Description: Delete fields

print "\nStep 3 Add and delete fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldsDel = ["OBJECTID", "GlobalID", "Shape__Are", "Shape__Len"]
arcpy.DeleteField_management(out_featureclass, fieldsDel)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 4. Project the polygon and calculate new area
## Description: Project to North America Albers Equal Area Conic

print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"

name = os.path.split(out_featureclass)[1] + ".shp"
projFile = os.path.join(finalFolder, name)
arcpy.Project_management(out_featureclass, projFile, outCS)
print "Projection" , out_featureclass, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
arcpy.CalculateField_management(projFile, "Shape_Area", expressionArea, "PYTHON_9.3")
arcpy.CalculateField_management(projFile, "Shape_Leng", expressionLength, "PYTHON_9.3")
fieldDel = ["OBJECTID_1"]
arcpy.DeleteField_management(projFile, fieldDel)
print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 5. Select by attribute
## Description: Select all districts located in the RGB.

print "\nStep 5 Select by Attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Convert to temp features
expression = "\"ID_WPR\" IN (1, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16)"
arcpy.MakeFeatureLayer_management(projFile, "temp")
arcpy.SelectLayerByAttribute_management("temp",
                                       "NEW_SELECTION",
                                       expression)
output = os.path.join(finalFolder, "NMOSE_WaterPlanningRegions_RG.shp")
arcpy.CopyFeatures_management("temp", output)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



