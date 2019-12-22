## Name: Dams Rio Grande Project.py
## Created on: 2019-12-07
## By: Sophie Plassin
## Description: Preparation of the dams dataset for the Rio Grande project 
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\4_dams\\final_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\final_output\\"
arcpy.env.workspace = dirpath


## ---------------------------------------------------------------------------
## 1. Select the dams in the Rio Grande project
## Description: Select the dams in the Rio Grande project, based on their name (ID), using Select Layer By Attribute
## List of Dams
## Elephant Butte: NM00129
## Caballo: NM00131
## Leasburg Diversion: NM00007
## Mesilla Diversion: NM00008
## Percha Diversion: NM00009 (NOT Percha Arroyo Diversion)
## Riverside Diversion Dam: TX00025
## International Diversion: TX01965
## American Diversion: TX01966


print "\nStep 1 Select Rio Grande Project dams starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
infc = "Dams_us_ses.shp"

# output name
outfc = "RG_Project_Dams.shp"

# Selection
expression = """\"NIDID\" IN ('NM00129', 'NM00131', 'NM00007', 'NM00008', 'NM00009', 'TX00025', 'TX01965', 'TX01966') \
AND \"DAM_NAME\" <> 'PERCHA ARROYO DIVERSION'"""

arcpy.MakeFeatureLayer_management(infc, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
output = os.path.join(finalFolder, outfc)
arcpy.CopyFeatures_management("temp", output)

print "Step 1 Select completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

