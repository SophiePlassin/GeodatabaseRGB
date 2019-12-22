# -*- coding: cp1252 -*-
## Name: Irrgation.py
## Created on: 2019-07-23
## By: Sophie Plassin
## Description: Preparation of the Irrigation dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Convert excel to table for MX 
##              3. Join table with MX counties feature
##              4. Convert excel to table for US 
##              5. Join table with US counties feature
##              6. Export features to final folder and clean data
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\2_Irrigation\\original_input\\prepared\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\2_Irrigation\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\2_Irrigation\\final_output\\Census\\"
arcpy.env.workspace = dirpath


# List
MXList = []
finalList = []
tableList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "Irrigation.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Convert excel to dbf
## Description: Convert excel file to dbf for MX dataset

print "\nStep 2 Convert excel to dbf starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
xlsFiles = ["mxcensus2007.xlsx"]

# Execute Excel to Dbf table
for xls in xlsFiles:
    dbf_file = os.path.splitext(xls)[0] + ".dbf"
    out_dbf_file = os.path.join(interFolder, dbf_file)
    arcpy.ExcelToTable_conversion(xls, out_dbf_file, "Table")
    arcpy.AddField_management(out_dbf_file, "ISO_GEOID", "TEXT", "", "", "8")
    arcpy.CalculateField_management(out_dbf_file, "ISO_GEOID", "'484' + !GEOID!", "PYTHON_9.3")

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 3. Join excel to shapefile
## Description: Join excel to shapefile for US dataset

print "\nStep 3 Join starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
input_folder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
input_fc = "Counties_and_Municipios_rgb.shp"
input_file = os.path.join(input_folder, input_fc)

# Expression
expression_us = "\"ADM0_ID\" = '484'"

# Join fields
joinFieldLayer = "ADM2_GEOID" 
joinFieldTable = "ISO_GEOID"

# Output
outname = "Irrigation_MX"
out_fc = os.path.join(out_gdb, outname)

# Execute
arcpy.MakeFeatureLayer_management(input_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression_us)
arcpy.AddJoin_management("temp", joinFieldLayer, out_dbf_file, joinFieldTable)
arcpy.CopyFeatures_management("temp", out_fc)
finalList.append(out_fc)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Convert excel to dbf
## Description: Convert excel file to dbf for US dataset

print "\nStep 4 Convert excel to dbf starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
xlsFiles = ["usco2015Area.xlsx"]

# Execute Excel to Dbf table
for xls in xlsFiles:
    name = os.path.splitext(xls)[0] 
    dbf_file = os.path.join(interFolder, name)
    arcpy.ExcelToTable_conversion(xls, out_dbf_file, "Hectares")
    arcpy.AddField_management(out_dbf_file, "ISO_GEOID", "TEXT", "", "", "8")
    arcpy.CalculateField_management(out_dbf_file, "ISO_GEOID", "'840' + !FIPS!", "PYTHON_9.3")
    tableList.append(out_dbf_file)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Join excel to shapefile
## Description: Join excel to shapefile for US dataset

print "\nStep 5 Join starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
input_folder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
input_fc = "Counties_and_Municipios_rgb.shp"
input_file = os.path.join(input_folder, input_fc)

# Expression
expression_us = "\"ADM0_ID\" = '840'"

# Join fields
joinFieldLayer = "ADM2_GEOID" 
joinFieldTable = "ISO_GEOID"

# Output
outname = "Irrigation_US"

# Execute
for tab in tableList:
    arcpy.MakeFeatureLayer_management(input_file, "temp")
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression_us)
    arcpy.AddJoin_management("temp", joinFieldLayer, tab, joinFieldTable)
    name = os.path.split(tab)[1]
    begin = name.find("_")
    end = name.find(".")
    tail = name[begin : end]
    out_fc = os.path.join(out_gdb, outname + tail)
    arcpy.CopyFeatures_management("temp", out_fc)
    finalList.append(out_fc)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Export feature to final folder
## Description: Join excel to shapefile for US dataset

print "\nStep 6 Export feature starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Delete fields
fieldDel = ["OID_", "STATE", "COUNTY", "STATEFIPS", "COUNTYFIPS", "GEOID", "ISO_GEOID", "FIPS",
            "Shape_Leng", "Shape_Le_1", "Shape_area"]
for fc in finalList:
    name = os.path.split(fc)[1]
    output = os.path.join(finalFolder, name + ".shp")
    arcpy.CopyFeatures_management(fc, output)
    arcpy.DeleteField_management(output, fieldDel)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")





