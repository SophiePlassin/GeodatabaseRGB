## Name: Irrigation Districts Rio Grande Project.py
## Created on: 2019-07-06
## By: Sophie Plassin
## Description: Preparation of the  irrigation district dataset for the Rio Grande project
##              1. Select Irrigation districts of the Rio Grande project
##              2. Merge selected irrigation districts into one layer
##              3. Homogeneize fields
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

# Set overwrite option
arcpy.env.overwriteOutput = True

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\7_irrigation_organization\\final_output\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\inter_output\\RG_Project\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\final_output\\"
arcpy.env.workspace = dirpath

# Set overwrite option
arcpy.env.overwriteOutput = True

## ---------------------------------------------------------------------------
## 1. Select Rio Grande project irrigation districts
## Description: Select Rio Grande project irrigation districts from the NM, TX and MX dataset, based on their name (ID), using Select Layer By Attribute
## List of Irrigation Districts
## Valle Juarez District: DR-009
## Elephant Butte District: EBID
## El Paso Water Improvement District#1: 2870000
## Hudspeth County Conservation & Reclamation District 1: 4680000

print "\nStep 1 Select Rio Grande Project dams starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input names
in_files = ["TX_Water_Districts_ses.shp", "NM_Irrigation_Districts_ses.shp", "MX_Distritos_Riego_ses.shp"]

# Output list
outputList = []

# Selection
expression = "\"ID_DIST\" IN ('009', 'EBID', '2870000', '4680000')"

for infc in in_files:
    arcpy.MakeFeatureLayer_management(infc, "temp")
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    output = os.path.join(interFolder, infc)
    arcpy.CopyFeatures_management("temp", output)
    outputList.append(output)

print "Step 1 Select completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Merge selected irrigation districts into one layer
## Description: Merge features in one dataset and delete unecessary fields

print "\nStep 2 Merge state layer to a single dataset starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output Name
outFeatureClass = "RG_Project_Irrigation_Districts.shp"

## Merge
out_fc = os.path.join(finalFolder, outFeatureClass)
arcpy.Merge_management(outputList, out_fc)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Homogeneize fields
## Description: Delete fields for consistency between data sources

print "\nStep 3 Homogeneize fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## Fields to delete
fieldsDel = ["OBJECTID", "County", "Digitized", "Status", "Creation_D", "Bndry_Chan", "Method", "Source", "Accuracy",
           "Initials",  "Updated", "Tx_Cnty", "FIPS", "Comments",
             "URL", 
             "User_1516", "User_1617", "Area1516", "Area1617", "AreaSW1516", "AreaSW1617", "AreaGW1516",
             "AreaGW1617","AreaIR1516", "AreaIR1617", "VolSW1516", "VolSW1617", "VolGW1516", "VolGW1617",
             "VolTO1516", "VolTO1617", "Name_RHA",
             "Shape_Leng", "Shape_Area"]

arcpy.DeleteField_management(out_fc, fieldsDel)

## Recalculate areas
arcpy.CalculateField_management(out_fc, "Area_ac", "!shape.area@acres!", "PYTHON_9.3")
arcpy.CalculateField_management(out_fc, "Area_ha", "!shape.area@hectares!", "PYTHON_9.3")

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

