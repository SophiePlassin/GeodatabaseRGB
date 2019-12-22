## Name: WaterRights_NewMexico.py
## Created on: 2018-11-30
## By: Sophie Plassin
## Description: Preparation of the water right shapefile for the state of New Mexico in the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase and save raw data into it
##              2. Clean raw data: remove unnecessary fields, add field WR_SOURCE and poulate with two values (SW for surface water or GW for groundwater)
##              3. Project data to North America Albers Equal Area Conic
##              4. Clip to the boundary of the study area
##              5. Save clipped file into final folder 
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
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\original_input\\NM\\"
dirpath = arcpy.env.workspace

# Options
arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

# Directories
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\inter_output\\NM\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\final_output\\"


## ---------------------------------------------------------------------------
## 1. Create a geodatabase 
## Description: Create a geodatabase and save raw data into it

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute
in_file = "OSE_Points_of_Diversion"
gdb_name = "NM_WR.gdb"
out_gdb = os.path.join(interFolder, gdb_name)
arcpy.CreateFileGDB_management(interFolder, gdb_name)
arcpy.FeatureClassToGeodatabase_conversion(in_file + ".shp", out_gdb)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Clean raw data 
## Description: Add new field and Remove unecessary fields

print "\nStep 2 Clean raw data starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

delFields = ["OBJECTID_1"]

fc_gdb = os.path.join(out_gdb, in_file)
arcpy.DeleteField_management(fc_gdb, delFields)

# Add new field WR_Source and add the type of water source (Surface or groundwater)
fieldSrce = "WR_Source"
arcpy.AddField_management(fc_gdb, fieldSrce, "TEXT", "", "", "5")

# Populate field Source
cur = arcpy.UpdateCursor(fc_gdb)
for row in cur:
    value1 = row.getValue('pod_basin')
    if value1 == 'SD' or value1 == 'SP':
        row.setValue(fieldSrce, "SW")
    else:
        row.setValue(fieldSrce, "GW")
    cur.updateRow(row)
print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 3 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

name = "NM_WaterRights_pr"
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")
projFile = os.path.join(out_gdb, name)
arcpy.Project_management(fc_gdb, projFile, outCS)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Clip
## Description: Clip to the boundaries of the study area

print "\nStep 4 Clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

clip_feature = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\RGB_Basin_na_albers.shp"
xy_tolerance = ""
clipFile = projFile.split("_pr")[0] + "_cl"
arcpy.Clip_analysis(projFile, clip_feature, clipFile, xy_tolerance)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Copy and paste to final location
## Description: Save shapefile into final folder

print "\nStep 5 Save to final location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

oRoot, oExt = os.path.split(clipFile)
finalName = oExt.split('_cl')[0] + ".shp"
out_feature = os.path.join(finalFolder, finalName)
arcpy.CopyFeatures_management(clipFile, out_feature)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


