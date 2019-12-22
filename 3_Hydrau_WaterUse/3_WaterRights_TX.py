## Name: WaterRights_Texas.py
## Created on: 2018-12-01
## By: Sophie Plassin
## Description: Preparation of the water right shapefile for the state of Texas in the Rio Grande/Bravo basin (RGB)
##              1. Project the shapefiles to North America Albers Equal Area Conic
##              2. Add field WR_SOURCE and poulate with the value SW for surface water
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
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\original_input\\TX\\"
dirpath = arcpy.env.workspace

# Options
arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

# Directories
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\inter_output\\TX\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\final_output\\"


## ---------------------------------------------------------------------------
## 1. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 1 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_file = "Rio_Grande_unverified_WaterRights.shp"

# Output
out_file = os.path.join(finalFolder, "TX_WaterRights.shp")

# Execute
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")
arcpy.Project_management(in_file, out_file, outCS)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Add field Type of Water Rights
## Description: Add new field WR_Source and add the type of water source (Surface)

print "\nStep 2 Add field starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldSrce = "WR_Source"
arcpy.AddField_management(out_file, fieldSrce, "TEXT", "", "", 5)
arcpy.CalculateField_management(out_file, fieldSrce, '"' + "SW" + '"', "PYTHON_9.3")

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")





