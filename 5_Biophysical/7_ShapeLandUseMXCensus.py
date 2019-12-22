## Name: LandUse_MX_Census.py
## Created on: 2019-07-24
## By: Sophie Plassin
## Description: Preparation of the Land Use shapefile from Mexico Census for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Convert excel to table for US 
##              3. Join excel to shapefile for US
##              4. Convert shapefile to table for MX
##              5. Join dbf to shapefile for MX
##              6. Export files to final folder
## ---------------------------------------------------------------------------


## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *


# Set options
env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\MX_Census\\original_input\\"
dirpath = arcpy.env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\MX_Census\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\MX_Census\\final_output\\Census\\"


# List
tabList = []
outputList = []


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "MX_Census.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 2. Excel To Table
## Description: Convert excel files to dbf files.

print "\nStep 2 Excel To Table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_excels = ["percrop\\prepared\\percrop.xlsx",
             "ancrop\\prepared\\ancrop_winter.xlsx",
             "ancrop\\prepared\\ancrop_spring.xlsx"]
# Expression
expression = "'484' + !GEOID!"

for xl in in_excels:
    root = os.path.splitext(xl)[0]
    name = os.path.split(root)[1]
    dbf_file = os.path.join(interFolder, name + ".dbf")
    arcpy.ExcelToTable_conversion(xl, dbf_file, "Area_Planted")
    arcpy.AddField_management(dbf_file, "ISO_GEOID", "TEXT", "", "", "8")
    arcpy.CalculateField_management(dbf_file, "ISO_GEOID", expression, "PYTHON_9.3")
    tabList.append(dbf_file)
    print "Conversion" , xl, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")



## ---------------------------------------------------------------------------
## 3. Join excel to shapefile
## Description: Join excel to shapefile

print "\nStep 3 Join starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
input_folder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
input_fc = "Counties_and_Municipios_rgb.shp"
input_file = os.path.join(input_folder, input_fc)

# Expression
expression = "\"ADM0_ID\" = '484'"

# Join fields
joinFieldLayer = "ADM2_GEOID" 
joinFieldTable = "ISO_GEOID"

# Execute
for dbf in tabList:
    arcpy.MakeFeatureLayer_management(input_file, "temp")
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    arcpy.AddJoin_management("temp", joinFieldLayer, dbf, joinFieldTable)
    root = os.path.splitext(dbf)[0]
    name = os.path.split(root)[1]
    out_fc = os.path.join(out_gdb, "MX_" + name + "07")
    arcpy.CopyFeatures_management("temp", out_fc)
    outputList.append(out_fc)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 4. Export to final folder
## Description: Export to final folder

print "\nStep 4 Export to final folder  completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Fields to delete
fieldDel = ["GID_0", "GID_1", "GID_2", "VARNAME_2", "TYPE_2", "ENGTYPE_2", "HASC_2", 
            "OID_", "ISO_GEOID", "GEOID", "GEOID_1", "Name_Count", "Shape_Le_1", "Shape_Leng", "Shape_Area"]

for fc in outputList:
    root = os.path.splitext(fc)[0]
    name = os.path.split(root)[1]
    output = os.path.join(finalFolder, name + ".shp")
    arcpy.CopyFeatures_management(fc, output)
    arcpy.DeleteField_management(output, fieldDel)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")








