## Name: Binational Dams.py
## Created on: 2019-06-29
## By: Sophie Plassin
## Description: Preparation of the binational point dataset for the Rio Grande/Bravo basin (RGB)
##              1. Select binational dams from USACE-NID dataset
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\4_dams\\final_output\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\2_binational_agency\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\2_binational_agency\\final_output\\"
arcpy.env.workspace = dirpath


# Set overwrite option
arcpy.env.overwriteOutput = True

# File
NID_dataset = ["Dams_us_bas.shp", "Dams_us_ses.shp"]


## --------------------------------------------------------------------------- 
## 1. Select binational dams
## Description: Select binational dams managed by IBWC.

print "\nStep 1 Select binational dams starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## List of dams
## FOR STORAGE
## AMISTAD TX02296
## FALCON TX00024

## FOR DIVERSION
## AMERICAN DIVERSION TX01966
## ANZALDUAS DIVERSION TX07036
## INTERNATIONAL DIVERSION TX01965
## RETAMAL DIVERSION TX07037
expression = "\"FED_OWNER\" = \'IBWC\'"


#Execute Selection
for fc in NID_dataset:
    arcpy.MakeFeatureLayer_management(fc, "temp") 
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    tail = fc[-8:]
    output = os.path.join(finalFolder, "Binational_Dams" + tail)
    arcpy.CopyFeatures_management("temp", output)


print "Step 1 Select binational dams completed at", datetime.datetime.now().strftime("%I:%M:%S%p")







