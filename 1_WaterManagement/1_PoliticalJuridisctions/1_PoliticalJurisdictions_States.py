## Name: StateBoundaries.py
## Created on: 2019-08-07
## By: Sophie Plassin
## Description: Preparation of the State boundaries dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Select States
##              3. Project the datasets to North America Albers Equal Area Conic
##              4. Add new fields and Homogeneize the fields
##              5. Merge US and MX polygons
## ---------------------------------------------------------------------------


## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

# Set environment settings
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\original_input\\Census"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
arcpy.env.workspace = dirpath

# Set overwrite option
arcpy.env.overwriteOutput = True

# List
outputList = []
projList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "State.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1. Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Select States
## Description: Select States crossing the boundaries of the RGB

print "\nStep 2 Select States starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs
fcList = ["tl_2016_us_state.shp", "areas_geoestadisticas_estatales.shp"]

# Expression
expressionUS = """"STATEFP" IN ('08', '35', '48')"""
expressionMX = """"CVE_ENT" IN ('05', '08', '10', '19', '28')"""

# Execute
for fc in fcList:
    arcpy.MakeFeatureLayer_management(fc, "temp")
    if fc.endswith("state.shp"):
        arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expressionUS)
        output = os.path.join(out_gdb, "Boundary_US")
        arcpy.CopyFeatures_management("temp", output)
    else:
        arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expressionMX)
        output = os.path.join(out_gdb, "Boundary_MX")
        arcpy.CopyFeatures_management("temp", output)
    projList.append(output)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Project
## Description: Project the Nation dataset to North America Albers Equal Area Conic

print "\nStep 3 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Spatial Reference
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

outputList = []
for fc in projList:
    projFile = os.path.splitext(fc)[0] +"_pr"
    arcpy.Project_management(fc, projFile, outCS)
    outputList.append(projFile)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 4. Add fields
## Description: Add fields ID

print "\nStep 4 Add fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldType = "TEXT"
fieldISO = "ADM0_ID"
fieldStateID = "ADM1_ID"
fieldCountryName = "NAME_0"
fieldStateName = "NAME_1"
fieldAbrevC = "ID_0"
fieldAbrevS = "ID_1"
stateGEOID = "ADM1_GEOID"
expression = "!ADM0_ID!+!ADM1_ID!"


for fc in outputList:
    arcpy.AddField_management(fc, fieldISO, fieldType, "", "", 3)
    arcpy.AddField_management(fc, fieldCountryName, fieldType, "", "", 50)
    arcpy.AddField_management(fc, fieldAbrevC, fieldType, "", "", 3)
    arcpy.AddField_management(fc, fieldStateID, fieldType, "", "", 3)
    arcpy.AddField_management(fc, fieldStateName, fieldType, "", "", 50)
    arcpy.AddField_management(fc, fieldAbrevS, fieldType, "", "", 3)
    arcpy.AddField_management(fc, stateGEOID, fieldType, "", "", 5)

#Update value MX
    if fc.endswith("MX_pr"):
        cur = arcpy.UpdateCursor(fc)
        for row in cur:
            value1 = row.getValue("CVE_ENT")
            row.setValue(fieldStateID, value1)
            value2 = row.getValue("NOM_ENT")
            row.setValue(fieldStateName, value2)
            if value1 == '05':
                row.setValue(fieldAbrevS, 'COA')
            if value1 == '08':
                row.setValue(fieldAbrevS, 'CHI')
            if value1 == '10':
                row.setValue(fieldAbrevS, 'DUR')
            if value1 == '19':
                row.setValue(fieldAbrevS, 'NVL')
            if value1 == '28':
                row.setValue(fieldAbrevS, 'TAM')
            row.setValue(fieldISO, '484')
            row.setValue(fieldAbrevC, 'MEX')
            row.setValue(fieldCountryName, 'Mexico')

            cur.updateRow(row)

# Update values US 
    if fc.endswith("US_pr"):
        cur = arcpy.UpdateCursor(fc)
        for row in cur:
            value1 = row.getValue("STATEFP")
            row.setValue(fieldStateID, value1)
            value2 = row.getValue ("STUSPS")
            row.setValue(fieldAbrevS, value2)
            value3 = row.getValue ("NAME")
            row.setValue(fieldStateName, value3)
            row.setValue(fieldISO, '840')
            row.setValue(fieldAbrevC, 'USA')
            row.setValue(fieldCountryName, 'United States')
            cur.updateRow(row)

# Update StateGEOID
    arcpy.CalculateField_management(fc, stateGEOID, expression, "PYTHON_9.3")

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 8. Merge into a single dataset
## Description: Add fields ID

print "\nStep 5 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

#8. Merge into a single dataset
out_feature = "States.shp"

output = os.path.join(finalFolder, out_feature)
arcpy.Merge_management(outputList, output)
fieldDel = ["CVE_ENT", "NOM_ENT", "REGION", "DIVISION", "STATEFP", "STATENS", "GEOID",
            "STUSPS", "NAME", "LSAD",  "MTFCC", "FUNCSTAT", "ALAND", "AWATER",
            "INTPTLAT", "INTPTLON", "Shape_Area", "Shape_Leng"]
for fd in fieldDel:
    arcpy.DeleteField_management(output,fieldDel)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



