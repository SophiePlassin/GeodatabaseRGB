## Name: TCEQ agencies.py
## Created on: 2019-06-30
## By: Sophie Plassin
## Description: Preparation of the TCEQ state agency dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Rename and export feature class
##              3. Homogeneize fields
##              4. Project the dataset to North America Albers Equal Area Conic
##              5. Select by location all regions in the RGB.
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\original_input\\TCEQ\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\inter_output\\TCEQ\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\final_output\\"
arcpy.env.workspace = dirpath

# Set option
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Analysis")  
arcpy.CheckOutExtension("Data Management")  


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_file = "tceq_regions"
gdb_name = "tceq_boundaries.gdb"
data_type = "FeatureClass"
out_gdb = interFolder + gdb_name
outname = "TCEQ_service_regions"

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
    if field.name == 'REGION':
        arcpy.AlterField_management(out_featureclass, field.name, 'TCEQ_REG', 'TCEQ_REGION')
    if field.name == 'HQ':
        arcpy.AlterField_management(out_featureclass, field.name, 'Name', 'Name')

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Homogeneize fields
## Description: Add and delete fields

print "\nStep 3 Add and delete fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldName = "STATE_AGEN"
fieldNameList = [fieldName]
fieldAlias = 'STATE_AGENCY'
fieldType = "TEXT"
fieldsDel = ["AREA", "PERIMETER"]

# Add field
for x in fieldNameList:
    arcpy.AddField_management(out_featureclass, x, fieldType, "", "", 75, fieldAlias)
    arcpy.DeleteField_management(out_featureclass, fieldsDel)

#Update lines
cur = arcpy.UpdateCursor(out_featureclass)
for row in cur:
    row.setValue(fieldName, 'TCEQ')
    cur.updateRow(row)

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
fieldDel = ["OBJECTID"]
arcpy.DeleteField_management(projFile, fieldDel)
print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Select by Location
## Description: Select all districts located in the RGB.

print "\nStep 5 Select by location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

studyArea = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\RGB_Ses_na_albers.shp"

arcpy.MakeFeatureLayer_management(projFile, "temp")
arcpy.MakeFeatureLayer_management(studyArea, "lyr_rgb")
arcpy.SelectLayerByLocation_management("temp", 'INTERSECT', "lyr_rgb")
output = "TCEQ_service_regions_RG.shp"
output_fc = os.path.join(finalFolder, output)
arcpy.CopyFeatures_management("temp", output_fc)


print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

