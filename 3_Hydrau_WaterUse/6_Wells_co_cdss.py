## Name: Wells_CO_cwcb.py
## Created on: 2019-05-20
## By: Sophie Plassin
## Description: Preparation of the shapefile mapping all diversion structures of surface water for the U.S. Rio Grande/Bravo basin (RGB)
##              1. Project the shapefile to North America Albers Equal Area Conic
##              2. Select by Attributes all wells applications located in Division 3 and clip the study area
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "\nWells_CO_cwcb starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\6_Wells\\original_input\\"
dirpath = arcpy.env.workspace

# Options
arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

# Directories
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\6_Wells\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\6_Wells\\final_output\\"

# List
projList = []
clipList = []

## ---------------------------------------------------------------------------
## 1. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 1 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_files = ["WellPermitPublic.shp"]

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in in_files:
    name = "Wells_co_cdss"
    projFile = os.path.join(interFolder, name + "_pr.shp")
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 2. Select by attributes 
## Description: Select all wells in Division 3

print "\nStep 2 Select by attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []

# Expression for selection
expression = "\"Div\" = 3"

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute Clip
for fc in projList:
    for clip in clip_features:
        # Create Output
        root = fc.split('_pr.shp')[0]
        name = os.path.split (root)[1]
        out_feature = os.path.join(finalFolder, name + '.shp')
        #Execute Selection
        arcpy.MakeFeatureLayer_management(fc, "temp") 
        arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
        arcpy.Clip_analysis("temp", clip, out_feature, xy_tolerance)
        clipList.append(out_feature)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")







