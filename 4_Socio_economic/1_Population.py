## Name: Population.py
## Created on: 2019-12-06
## By: Sophie Plassin
## Description: Preparation of the population shapefile for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Convert excel to table for US 
##              3. Join excel to shapefile for US
##              4. Convert excel to table for MX 
##              5. Join excel to shapefile for MX
##              6. Merge MX and US datasets
##              7. Join all years in one dataset
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
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\1_Population\\original_input\\"
dirpath = arcpy.env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\1_Population\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\1_Population\\final_output\\Census\\"


# List
mergeList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "Population.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




## ---------------------------------------------------------------------------
## 2. Excel To Table
## Description: Convert excel files to dbf files for US.

print "\nStep 2 Excel To Table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_excel = "US\\Demo_cleaned.xlsx"
output_tab_us = os.path.join(interFolder, "DemoUS.dbf")
arcpy.ExcelToTable_conversion(in_excel, output_tab_us, "Population")
arcpy.AddField_management(output_tab_us, "ISO_GEOID", "TEXT", "", "", "8")
arcpy.CalculateField_management(output_tab_us, "ISO_GEOID", "'840' + !ID!", "PYTHON_9.3")

print "Step 2 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")



## ---------------------------------------------------------------------------
## 3. Join excel to shapefile
## Description: Join excel to shapefile for US dataset

print "\nStep 3 Join starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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
outname = "Population_US"

# Execute
arcpy.MakeFeatureLayer_management(input_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression_us)
arcpy.AddJoin_management("temp", joinFieldLayer, output_tab_us, joinFieldTable)
name = os.path.split(output_tab_us)[1]
begin = name.find("_")
end = name.find(".")
tail = name[begin : end]
out_fc = os.path.join(out_gdb, outname + tail)
arcpy.CopyFeatures_management("temp", out_fc)
mergeList.append(out_fc)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 4. Excel To Table
## Description: Convert excel files to dbf files for MX.

print "\nStep 4 Excel To Table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_excel = "MEX\\CPy_Population.xlsx"
output_tab_mx = os.path.join(interFolder, "DemoMX.dbf")
arcpy.ExcelToTable_conversion(in_excel, output_tab_mx, "Population")
arcpy.AddField_management(output_tab_mx, "ISO_GEOID", "TEXT", "", "", "8")
arcpy.CalculateField_management(output_tab_mx, "ISO_GEOID", "'484' + !ID!", "PYTHON_9.3")

print "Step 4 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")



## ---------------------------------------------------------------------------
## 5. Join excel to shapefile
## Description: Join excel to shapefile for MX dataset

print "\nStep 5 Join starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
input_folder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
input_fc = "Counties_and_Municipios_rgb.shp"
input_file = os.path.join(input_folder, input_fc)

# Expression
expression_mx = "\"ADM0_ID\" = '484'"

# Join fields
joinFieldLayer = "ADM2_GEOID" 
joinFieldTable = "ISO_GEOID"

# Output
outname = "Population_MX"

# Execute
arcpy.MakeFeatureLayer_management(input_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression_mx)
arcpy.AddJoin_management("temp", joinFieldLayer, output_tab_mx, joinFieldTable)
name = os.path.split(output_tab_mx)[1]
begin = name.find("_")
end = name.find(".")
tail = name[begin : end]
out_fc = os.path.join(out_gdb, outname + tail)
arcpy.CopyFeatures_management("temp", out_fc)
mergeList.append(out_fc)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 6. Merge national datasets into binational datasets
## Description: For each year, merge US and MX datasets into a single dataset

print "\nStep 6 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

merged = os.path.join(out_gdb, "Population")
arcpy.Merge_management(mergeList, merged)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
## 7. Reorder fields
## Description: Reorder fields

print "\nStep 7 Reorder fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

path, name = os.path.split(merged)
output = os.path.join(finalFolder, name + ".shp")
arcpy.CopyFeatures_management(merged, output)

fieldDel = ["ISO_GEOID", "OID", "ID", "County", "Municipio", "Shape_Length", "Shape_Area", "Shape_Leng", "OID_1"]

arcpy.DeleteField_management(output, fieldDel)

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")








