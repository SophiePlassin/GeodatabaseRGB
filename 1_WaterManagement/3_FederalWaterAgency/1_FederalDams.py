## Name: Federal Dams.py
## Created on: 2019-06-29
## By: Sophie Plassin
## Description: Preparation of the federal point dataset for the Rio Grande/Bravo basin (RGB)
##              1. Select US federals dams from USACE-NID dataset
##              2. Select MX federals dams from CENAPRED dataset
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\4_dams\\final_output"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\3_federal_agency\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\3_federal_agency\\final_output\\"
arcpy.env.workspace = dirpath


# Set overwrite option
arcpy.env.overwriteOutput = True

# File
US_dams = ["Dams_us_bas.shp", "Dams_us_ses.shp"]
MX_dams = ["Dams_mx_bas.shp", "Dams_mx_ses.shp"]


## --------------------------------------------------------------------------- 
## 1. Select US federal dams
## Description: Select by attributes

print "\nStep 1 Select federal dams starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set Local variables:
expressionUS = "\"OWNER_TYPE\" = \'F\' AND \"FED_OWNER\" <> \'IBWC\'"

#Execute Selection
for fc in US_dams:
    arcpy.MakeFeatureLayer_management(fc, "temp") 
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expressionUS)
    tail = fc[-8:]
    output = os.path.join(finalFolder, "Federal_Dams_us" + tail)
    arcpy.CopyFeatures_management("temp", output)

print "Step 1 Select US federal dams completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## --------------------------------------------------------------------------- 
## 2. Select MX federal dams
## Description: Select by attributes

print "\nStep 2 Select MX federal dams starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

expressionMX = """\"OPER_NAME\" LIKE \'%COMISION NACIONAL DEL AGUA%\'
                OR \"OPER_NAME\" LIKE \'%CNA%\'"""


#Execute Selection
for fc in MX_dams:
    arcpy.MakeFeatureLayer_management(fc, "temp") 
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expressionMX)
    tail = fc[-8:]
    output = os.path.join(finalFolder, "Federal_Dams_mx" + tail)
    arcpy.CopyFeatures_management("temp", output)

print "Step 2 Select MX federal dams completed at", datetime.datetime.now().strftime("%I:%M:%S%p")







