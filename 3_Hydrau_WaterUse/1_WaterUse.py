# -*- coding: cp1252 -*-
## Name: Water Use.py
## Created on: 2019-07-23
## By: Sophie Plassin
## Description: Preparation of the Water Use dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Convert excel to dbf
##              3. Join US counties shapefile with dbf
##              4. Convert shapefile to feature and homogeneize fields in MX shapefiles
##              5. Union Mexican features
##              6. Export attribute table to dbf
##              7. Join excel to shapefile
##              8. Reorder fields
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\1_waterUse\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\1_waterUse\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\1_waterUse\\final_output\\Census\\"
arcpy.env.workspace = dirpath


# List
projList = []
MXList = []
mergeList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "WaterUse.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Convert excel to dbf
## Description: Convert excel file to dbf for US dataset

print "\nStep 2 Convert excel to dbf starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
xlsFiles = arcpy.ListFiles("*.xlsx")

# Execute Excel to Dbf table
for xls in xlsFiles:
    dbf_file = os.path.splitext(xls)[0][0:8] + ".dbf"
    out_dbf_file = os.path.join(interFolder, dbf_file)
    arcpy.ExcelToTable_conversion(xls, out_dbf_file, "Mcm_Year")
    arcpy.AddField_management(out_dbf_file, "GEOID", "TEXT", "", "", "8")
    arcpy.CalculateField_management(out_dbf_file, "GEOID", "'840' + !FIPS!", "PYTHON_9.3")

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
expression_us = "\"ADM0_ID\" = '840'"

# Join fields
joinFieldLayer = "ADM2_GEOID" 
joinFieldTable = "GEOID"

# Output
outname = "Withdrawals_US"
out_fc = os.path.join(out_gdb, outname)

# Execute
arcpy.MakeFeatureLayer_management(input_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression_us)
arcpy.AddJoin_management("temp", joinFieldLayer, out_dbf_file, joinFieldTable)
arcpy.CopyFeatures_management("temp", out_fc)
mergeList.append(out_fc) # Append US dataset for merge

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Convert shapefile to feature in gdb and homogeneize fields
## Description: Convert MX shapefile to feature and homogeneize fields

print "\nStep 4 Homogeneize starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
fcList = arcpy.ListFeatureClasses()

# Fields to alter
alterFields_intensidad = [["agricola", "AG_Wtotl"], ["abast_pub", "PS_Wtotl"], ["indus_auto", "IN_Wtotl"],
                          ["termo", "PT_Wtotl"], ["vol_conc", "TO_Wtotl"], ["año", "YEAR"]]

alterFields_fuente = [["vol_superf", "TO_WSWTo"],["vol_subter", "TO_WGWTo"], ["vol_conc", "TO_Wtotl"],
                      ["año", "YEAR"]]

alterFields = [alterFields_fuente, alterFields_intensidad]

# New fields
fieldGEOID = "GEOID"
fieldCodeState = "STATE_ID"
fieldCodeMuni = "MUNI_ID"
fieldType = "TEXT"
expression1 = "\"0\" + str(!id_edo!)"
expression2 = "\"0\" + str(!id_mpio!)"
expression3 = "\"484\" +!MUNI_ID!"


# Convert shapefile to feature in gdb
fcList = sorted(fcList)
for i in range(len(fcList)):
    arcpy.FeatureClassToGeodatabase_conversion(fcList[i], out_gdb)
    out_name = os.path.splitext(fcList[i])[0]
    out_feature = os.path.join(out_gdb, out_name)
    # Alter fields
    for old, new in alterFields[i]:
        tmpName = ("{0}_tmp".format(old))
        arcpy.AlterField_management(out_feature, old, tmpName)
        arcpy.AlterField_management(out_feature, tmpName, new)

    # Add fields
    fieldText = [fieldCodeState, fieldCodeMuni, fieldGEOID]
    for fn in fieldText:
        arcpy.AddField_management(out_feature, fn, fieldType)      

    #Add ID into the new fields        
    cur = arcpy.UpdateCursor(out_feature)
    for row in cur:
        value1 = row.getValue("id_edo")
        if value1 < 10: #Rename the ID by adding a '0' in front when missing (1 to 9 => 01 to 09)
            row.setValue(fieldCodeState, "0" + str(value1))
        else:
            row.setValue(fieldCodeState, str(value1))
        value2 = row.getValue("id_mpio")
        if value2 < 10000: #Rename the ID by adding a '0' in front when missing (1 to 9 => 01 to 09) 
            row.setValue(fieldCodeMuni, "0" + str(value2))
        else:
            row.setValue(fieldCodeMuni, str(value2))
        cur.updateRow(row)
    arcpy.CalculateField_management(out_feature, fieldGEOID, expression3, "PYTHON_9.3")

    # Delete fields
    fieldDel = ("id_mpio", "id_edo",  "fuen_pred")
    arcpy.DeleteField_management(out_feature, fieldDel)
    MXList.append(out_feature)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Union
## Description: Create one feature from the two features

print "\nStep 5 Union starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

union = os.path.join(out_gdb, "MX_Union")
arcpy.Union_analysis(MXList, union, "NO_FID")

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 6. Export attribute table to dbf
## Description: Export MX attribute table to dbf

print "\nStep 6 Export attribute table to dbf starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

name = os.path.split(union)[1]
output_dbf = name + ".dbf"
arcpy.TableToTable_conversion(union, interFolder, output_dbf)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 7. Join excel to shapefile
## Description: Join excel to shapefile for MX dataset

print "\nStep 7 Join starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
input_folder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
input_fc = "Counties_and_Municipios_rgb.shp"
input_file = os.path.join(input_folder, input_fc)
input_table = os.path.join(interFolder, output_dbf)

# Expression
expression_mx = "\"ADM0_ID\" = '484'"

# Join fields
joinFieldLayer = "ADM2_GEOID" 
joinFieldTable = "GEOID"

# Output
outname = "Withdrawals_MX"
out_fc = os.path.join(out_gdb, outname)

# Execute
arcpy.MakeFeatureLayer_management(input_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression_mx)

arcpy.AddJoin_management("temp", joinFieldLayer, input_table, joinFieldTable)
arcpy.CopyFeatures_management("temp", out_fc)

mergeList.append(out_fc) # Append MX dataset for merge

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 8. Merge US and MX datasets
## Description: Merge US and MX datasets

print "\nStep 8 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs
inputs = mergeList

# Clean fields
fieldsDel = ["OID", "STATE", "STATEFIPS", "COUNTY", "COUNTYFIPS",
             "FIPS", "GEOID", "GEOID_1", "nom_mun", "nom_edo", "STATE_ID",
             "MUNI_ID","nom_mun_1", "nom_edo_1", "STATE_ID_1",
             "MUNI_ID_1", "TO_WTotl_1", "YEAR_1", "Shape_Leng"]

for fc in mergeList:
    arcpy.DeleteField_management(fc, fieldsDel)

 
# Execute Merge
output = os.path.join(finalFolder, "Withdrawals_2015.shp")
arcpy.Merge_management(inputs, output)

## ---------------------------------------------------------------------------
## 9. Edit attribute table 
## Description: Remove duplicate fields and convert to -99 all values in MX with NoData.

fieldsDel = ["Shape_Le_1"]
arcpy.DeleteField_management(output, fieldsDel)

# Create list of all fields
fieldNameList = [field.name for field in arcpy.ListFields(output)]

# Items to be removed from the list of field
del fieldNameList[0:13]

unwanted = {"AG_Wtotl", "PS_Wtotl", "IN_Wtotl", "PT_Wtotl", "TO_Wtotl", "TO_WSWTo",
            "TO_WGWTo", "Shape_Leng", "Shape_Area"}

fieldNameList = [elem for elem in fieldNameList if elem not in unwanted]

for fd in fieldNameList:
    cur = arcpy.UpdateCursor(output)
    for row in cur:
        value1 = row.getValue("ADM0_ID")
        if value1 == '484':
            row.setValue (fd, -99)
        cur.updateRow(row)
print "Step 8 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

