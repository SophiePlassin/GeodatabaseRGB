## Name: Wells_CO_cwcb.py
## Created on: 2019-05-20
## By: Sophie Plassin
## Description: Preparation of the shapefile mapping all diversion structures of surface water for the U.S. Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Project the shapefile to North America Albers Equal Area Conic
##              3. Clip to the boundary of the study area
##              4. Clean the dataset
##              5. Save output data to final folder
## ---------------------------------------------------------------------------


## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "\nWells_TX_twbd starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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
finalList = []


# List
projList = []
clipList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase 
## Description: Create a geodatabase and save raw data into it

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute
in_file = "TWDB_Groundwater"
gdb_name = "Wells_TX.gdb"
out_gdb = os.path.join(interFolder, gdb_name)
arcpy.CreateFileGDB_management(interFolder, gdb_name)
arcpy.FeatureClassToGeodatabase_conversion(in_file + ".shp", out_gdb)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 2 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

fc_gdb = os.path.join(out_gdb, in_file)
name = in_file + "_pr"
projFile = os.path.join(out_gdb, name)
arcpy.Project_management(fc_gdb, projFile, outCS)
projList.append(projFile)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Clip
## Description: Clip to the boundaries of the study area

print "\nStep 3 Clip the features starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute Clip
for fc in projList:
    for clip in clip_features:
        # Create name
        new_name = os.path.join(out_gdb, "Wells_tx_twdb")
        temp = os.path.split(clip)[-1]
        # Add Ses or Bas according to the clip feature name
        if temp.startswith("RGB_Basin"):
            output = new_name + "_bas"
        else:
            output = new_name + "_ses"
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        clipList.append(output)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Clean the dataset
## Description: Rename fields

print "\nStep 4 Clean the dataset starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Update lines
for fc in clipList:
    fieldList = arcpy.ListFields(fc)
    for field in fieldList:
        if field.name == 'CoordDDLat':
            arcpy.AlterField_management(fc, field.name, 'LAT_DD', 'LAT_DD')
        if field.name == 'CoordDDLon':
            arcpy.AlterField_management(fc, field.name, 'LONG_DD', 'LONG_DD')
        if field.name == 'CountyName':
            arcpy.AlterField_management(fc, field.name, 'County', 'County')
            
print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Copy and paste to final location
## Description: Save shapefile into final folder

print "\nStep 5 Save to final location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in clipList:
    oRoot, oExt = os.path.split(fc)
    out_feature = os.path.join(finalFolder, oExt)
    arcpy.CopyFeatures_management(fc, out_feature)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
