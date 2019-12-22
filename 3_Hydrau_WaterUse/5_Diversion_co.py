## Name: Diversion_SurfaceWater_CO.py
## Created on: 2019-05-20
## By: Sophie Plassin
## Description: Preparation of the shapefile mapping all diversion structures of surface water for Division 3 in Colorado
##              1. Clean the data
##              2. Project the shapefile to North America Albers Equal Area Conic
##              3. Save output data to final folder
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Diversion_CO starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\5_Diversion\\original_input\\"
dirpath = arcpy.env.workspace

# Options
arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

# Directories
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\5_Diversion\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\5_Diversion\\final_output\\"

# List
cleanList = []
projList = []

## ---------------------------------------------------------------------------
## 1. Clean the data
## Description: Add a field to specify the name of diversion structures (canal, pipeline, artifical path...) 


print "\nStep 1 Clean the data starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_files = ["Div3_Canals.shp"]

for fc in in_files:
    output = os.path.join(interFolder, "Diversion_CO.shp")
    arcpy.CopyFeatures_management(fc, output)
    cleanList.append(output)

# Remove unecessary fields

for fc in cleanList:
    fieldDel = ["LENGTH", "created_us", "created_da", "last_edite", "last_edi_1", "SHAPE_Leng"]
    for fn in fieldDel:
        arcpy.DeleteField_management(fc, fieldDel)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 2 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Execute
for fc in cleanList:
    projFile = os.path.splitext(fc)[0] + "_pr.shp"
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Copy and paste to final location
## Description: Save shapefile into final folder

print "\nStep 3 Save to final location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in projList:
    oRoot, oExt = os.path.split(fc)
    name = oExt.split("_pr.shp")[0]
    out_feature = os.path.join(finalFolder, name)
    arcpy.CopyFeatures_management(fc, out_feature)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



