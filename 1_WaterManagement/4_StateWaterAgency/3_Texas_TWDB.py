## Name: TWDB agencies.py
## Created on: 2019-06-30
## By: Sophie Plassin
## Description: Preparation of the TWDB state agency dataset for the Rio Grande/Bravo basin (RGB)
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\original_input\\TWDB\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\inter_output\\TWDB\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\final_output\\"
arcpy.env.workspace = dirpath

# Set option
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Analysis")  
arcpy.CheckOutExtension("Data Management")

# List
projList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Files
in_files = arcpy.ListFeatureClasses()
gdb_name = "twdb_boundaries.gdb"
data_type = "FeatureClass"
out_gdb = interFolder + gdb_name

# Fields
fieldName = "STATE_AGEN"
fieldNameList = [fieldName]
fieldAlias = 'STATE_AGENCY'
fieldType = "TEXT"


#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)
for fc in in_files:
    arcpy.FeatureClassToGeodatabase_conversion(fc, out_gdb)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Rename and export feature class
## Description: Rename feature class

print "\nStep 2 Rename and export feature class starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\inter_output\\TWDB\\twdb_boundaries.gdb"

fcList = arcpy.ListFeatureClasses()

for fc in fcList:
    if fc.startswith ("TWDB"):
        fc_newname = fc.split("_2014")[0]
    else:
        fc_newname = "TWDB_" + fc
    out_featureclass = os.path.join(out_gdb,fc_newname)
    arcpy.Rename_management(fc, out_featureclass, data_type)
    fieldList = arcpy.ListFields(out_featureclass)
    for field in fieldList:
        if field.name.startswith('Office'):
            arcpy.AlterField_management(out_featureclass, field.name, 'IFSSOffice', 'IFSSOffice')
        if field.name.startswith('Region'):
            arcpy.AlterField_management(out_featureclass, field.name, 'RPT_Region', 'RPT_Region')
        if field.name.startswith('REG_NAME'):
            arcpy.AlterField_management(out_featureclass, field.name, 'RWPARegion', 'RWPARegion')

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Homogeneize fields
## Description: Add and delete fields

fieldsDel = ["AREA", "PERIMETER", "Shape_Le_1"]

fcList = arcpy.ListFeatureClasses()

for fc in fcList:
    for x in fieldNameList:
        arcpy.AddField_management(fc, x, fieldType, "", "", 75, fieldAlias)
    arcpy.DeleteField_management(fc, fieldsDel)

#Update lines
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        row.setValue(fieldName, 'TWDB')
        cur.updateRow(row)


## ---------------------------------------------------------------------------
## 4. Project the polygon and calculate new area
## Description: Project to North America Albers Equal Area Conic

print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"

for fc in fcList:
    name = os.path.split(fc)[1] + ".shp"
    projFile = os.path.join(finalFolder, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    arcpy.CalculateField_management(projFile, "Shape_Area", expressionArea, "PYTHON_9.3")
    arcpy.CalculateField_management(projFile, "Shape_Leng", expressionLength, "PYTHON_9.3")
    projList.append(projFile)
    fieldDel = ["OBJECTID", "OBJECTID_1", "Shape_Le_1"]
    arcpy.DeleteField_management(projFile, fieldDel)
print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Select by Location
## Description: Select all districts located in the RGB.

print "\nStep 5 Select by Attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

studyArea = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\RGB_Ses_na_albers.shp"

for fc in projList:
    arcpy.MakeFeatureLayer_management(fc, "temp")
    arcpy.MakeFeatureLayer_management(studyArea, "lyr_rgb")
    arcpy.SelectLayerByLocation_management("temp", 'INTERSECT', "lyr_rgb")
    root = os.path.splitext(fc)[0]
    name = os.path.split(root)[1]
    begin = name.find("_", 1)
    output = name[:begin] + name[begin:] + '_RG'
    output_fc = os.path.join(finalFolder, output)
    arcpy.CopyFeatures_management("temp", output_fc)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

