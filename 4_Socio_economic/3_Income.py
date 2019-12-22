## Name: Income.py
## Created on: 2019-07-24
## By: Sophie Plassin
## Description: Preparation of the population shapefile for the Rio Grande/Bravo basin (RGB)
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
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\3_income\\original_input\\"
dirpath = arcpy.env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\3_income\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Socio_Economics\\3_income\\final_output\\Census\\"


# List
dbfList_US = []
dbfList_MX = []
outputList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "Income.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




## ---------------------------------------------------------------------------
## 2. Excel To Table
## Description: Convert excel files to dbf files for US.

print "\nStep 2 Excel To Table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_excel = "US\\CA1_1969_2015_personalIncome.xlsx"
output = os.path.join(interFolder, "Income_US.dbf")
arcpy.ExcelToTable_conversion(in_excel, output)
arcpy.AddField_management(output, "ISO_GEOID", "TEXT", "", "", "8")
arcpy.CalculateField_management(output, "ISO_GEOID", "'840' + !GeoFIPS!", "PYTHON_9.3")
dbfList_US.append(output)

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
outname = "Income_US"

# Execute
for dbf in dbfList_US:
    arcpy.MakeFeatureLayer_management(input_file, "temp")
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression_us)
    arcpy.AddJoin_management("temp", joinFieldLayer, dbf, joinFieldTable)
    name = os.path.split(dbf)[1]
    out_fc = os.path.join(out_gdb, outname)
    arcpy.CopyFeatures_management("temp", out_fc)
    outputList.append(out_fc)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 4. Shapefile To Table
## Description: Convert shapefile to dbf files for MX.

print "\nStep 4 Shapefile To Table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

yearList = ["90", "00", "10"]
fcList = ["ingmun90gw.dbf", "ingmun00gw.dbf", "ingmun10gw.dbf"]
for year in yearList:
    for fc in fcList:
        in_fc = "MX\\" + fc
        if fc.startswith("ingmun" + year):
            arcpy.TableToDBASE_conversion(in_fc, interFolder)
            in_data = os.path.join(interFolder, fc)
            out_data = os.path.join(interFolder, "IncomeMX_" + year + ".dbf")
            arcpy.Rename_management(in_data, out_data)
            arcpy.AddField_management(out_data, "ISO_GEOID", "TEXT", "", "", "8")
            if out_data.endswith("90.dbf"):
                arcpy.CalculateField_management(out_data, "ISO_GEOID", "'484' + !CLAVE!", "PYTHON_9.3")
            elif out_data.endswith("00.dbf"):
                arcpy.CalculateField_management(out_data, "ISO_GEOID", "'484' + !CVE_MUN!", "PYTHON_9.3")
            elif out_data.endswith("10.dbf"):
                arcpy.CalculateField_management(out_data, "ISO_GEOID", "'484' + !MUN_OFICIA!", "PYTHON_9.3")
            dbfList_MX.append(out_data)

print "Step 4 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")




## ---------------------------------------------------------------------------
## 5. Join dbf to shapefile
## Description: Join dbf to shapefile for US dataset

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

# Fields to altere
alterFields_90 = [["POTO90", "Pop_90"]]
alterFields_00 = [["POTO00", "Pop_00"]]
alterFields_10 = [["POTO10", "Pop_10"]]

alterFields = [alterFields_90, alterFields_00, alterFields_10]

# Output
outname = "DistributionIncome_MX"

# Execute
for i in range(len(dbfList_MX)):
    arcpy.MakeFeatureLayer_management(input_file, "temp")
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression_mx)
    arcpy.AddJoin_management("temp", joinFieldLayer, dbfList_MX[i], joinFieldTable)
    name = os.path.split(dbfList_MX[i])[1]
    begin = name.find("_")
    end = name.find(".")
    tail = name[begin + 1 : end]
    out_fc = os.path.join(out_gdb, outname + tail)
    arcpy.CopyFeatures_management("temp", out_fc)   
    # Alter fields
    for old, new in alterFields[i]:
        tmpName = ("{0}_tmp".format(old))
        arcpy.AlterField_management(out_fc, old, tmpName)
        arcpy.AlterField_management(out_fc, tmpName, new)
    # Delete fields
    fieldsDel = ["MUN_OFICIA", "CLAVE", 
                 "COV_", "COV_ID", "CVE_MUN", "CVE_ENT", "EDO_NOM", "NOM_ENT",
                 "NOM_MUN", "DISTRITO", "NOM_DIST", "ISO_GEOID",
                 "COUNTRYISO", "STATEFP", "COUNTY", "COUNTYID"]
    arcpy.DeleteField_management(out_fc, fieldsDel)
    outputList.append(out_fc)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Export to final folder
## Description: Export to final folder

print "\nStep 6 Export to final folder  completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Fields to delete
fieldDel = ["GID_0", "GID_1", "GID_2", "TYPE_2", "ENGTYPE_2", "HASC_2",
            "VARNAME_2", "OID_", "ISO_GEOID",  "AREA", "PERIMETER", "PERCENTAGE",
            "AREA_1", "GeoFIPS", "County", "Shape_Le_1", "Shape_Leng",
            "Shape_Area"]

for fc in outputList:
    root = os.path.splitext(fc)[0]
    name = os.path.split(root)[1]
    output = os.path.join(finalFolder, name + ".shp")
    arcpy.CopyFeatures_management(fc, output)
    arcpy.DeleteField_management(output, fieldDel)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")








