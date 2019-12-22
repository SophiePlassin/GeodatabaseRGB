## Name: FarmSize.py
## Created on: 2019-07-23
## By: Sophie Plassin
## Description: Preparation of the farm size shapefiles for the Rio Grande/Bravo basin (RGB)
##              1. Convert prepared excel files into tables
##              2. Join excel tables with prepared county shapefiles (clipped and projected)

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
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\4_farmSize\\original_input\\prepared\\"
dirpath = env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\4_farmSize\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\4_farmSize\\final_output\\Census\\"


# List
tabList = []
finalList = []


## ---------------------------------------------------------------------------
## 1. Convert Excel to Table
## Description: Convert Excel Files to Tables

print "\nStep 1 Convert Excel to Table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs
xlsFiles = ["Farms_US2007.xlsx", "Farms_US2012.xlsx", "Farms_MX2007.xlsx"]

# Perform the conversion
for xl in xlsFiles:
    root = os.path.splitext(xl)[0]
    name = os.path.split(root)[1]
    dbf_file = os.path.join(interFolder, name + ".dbf")
    arcpy.ExcelToTable_conversion(xl, dbf_file)
    arcpy.AddField_management(dbf_file, "ISO_GEOID", "TEXT", "", "", "8")
    if name.startswith("Farms_US"):
        expression = "'840' + !GEOID!"
    else:
        expression = "'484' + !GEOID!"
    arcpy.CalculateField_management(dbf_file, "ISO_GEOID", expression, "PYTHON_9.3")
    tabList.append(dbf_file)
    print "Conversion" , xl, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Join dbf tables with shapefiles
## Description: Clip the waterbody polygon for the study area.

print "\nStep 2 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
input_folder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
input_fc = "Counties_and_Municipios_rgb.shp"
input_file = os.path.join(input_folder, input_fc)

# Set local variables
countiesList = []
year = ["2007", "2012"]

# Join fields
joinFieldLayer = "ADM2_GEOID"
joinFieldTable = "ISO_GEOID"

# Fields to delete
fieldDelJoin = ["County", "GEOID", "GEOID_1", "OID_", "MUNICIPIO", "ISO_GEOID",
                "Shape_Area", "Shape_Leng"]


# Create a feature layer from the featureclass
for dbf in tabList:
    arcpy.MakeFeatureLayer_management(input_file, "temp")
    name = os.path.split(dbf)[1]
    if name.startswith ("Farms_US"):
        expression = "\"ADM0_ID\" = '840'"
        arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
        arcpy.AddJoin_management("temp", joinFieldLayer, dbf, joinFieldTable)
        out_fc = os.path.join(finalFolder, name)
        arcpy.CopyFeatures_management("temp", out_fc)
        print "Join" , name, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
        finalList.append(out_fc)
    else:
        expression = "\"ADM0_ID\" = '484'"
        arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
        arcpy.AddJoin_management("temp", joinFieldLayer, dbf, joinFieldTable)       
        name = os.path.split(dbf)[1]
        out_fc = os.path.join(finalFolder, name)
        arcpy.CopyFeatures_management("temp", out_fc)
        print "Join" , name, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
        finalList.append (out_fc)

for fc in finalList:
    arcpy.DeleteField_management(fc, fieldDelJoin)


