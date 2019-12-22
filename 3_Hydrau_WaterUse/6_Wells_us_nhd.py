## Name: Wells_US_nhd.py
## Created on: 2019-05-20
## By: Sophie Plassin
## Description: Preparation of the shapefile mapping all diversion structures of surface water for the U.S. Rio Grande/Bravo basin (RGB)
##              1. Merge input data
##              2. Populate new fields
##              3. Project the shapefile to North America Albers Equal Area Conic
##              4. Clip to the boundary of the study area
##              5. Select by attributes all diversion structures that are not "Stream"
##              6. Save output data to final folder
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "\nWells_US_nhd starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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
mergeList = []
projList = []
clipList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Merge input data
## Description: Merge the files CO_NHDPoint, NM_NHDPoint and TX_NHDPoint

print "\nStep 1 Merge input data starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute
in_files = ["CO_NHDPoint.shp", "NM_NHDPoint.shp", "TX_NHDPoint.shp"]
output = os.path.join(interFolder, "US_nhd_points.shp")
arcpy.Merge_management(in_files, output)
mergeList.append(output)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Populate new fields
## Description: Add a field to specify the type of wells 

print "\nStep 2 Populate new fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Add field
fieldFeat = "FEATURE"
fieldType = "TEXT"
for fc in mergeList:
    arcpy.AddField_management(fc, fieldFeat, fieldType)

#Update lines

    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        value = row.getValue("FCODE")
        if value == 36700:
             row.setValue(fieldFeat, "GAGING STATION")
        if value == 39800:
             row.setValue(fieldFeat, "LOCK CHAMBER")
        if value == 43100:
             row.setValue(fieldFeat, "RAPIDS")
        if value == 44101:
             row.setValue(fieldFeat, "ROCK ABOVE WATER")
        if value == 45800:
             row.setValue(fieldFeat, "SPRING/SEEP")
        if value == 48700:
            row.setValue(fieldFeat, "WATERFALL")
        if value == 48800:
            row.setValue(fieldFeat, "WELL")
        cur.updateRow(row)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 3 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in mergeList:
    projFile = os.path.splitext(fc)[0] + "_pr.shp"
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4.  Clip
## Description: Clip to the boundaries of the study area

print "\nStep 4  Clip the features starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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
        new_name = fc.split('_pr')[0]
        temp = os.path.split(clip)[-1]
        # Add Ses or Bas according to the clip feature name
        if temp.startswith("RGB_Basin"):
            output = new_name + "_bas.shp"
        else:
            output = new_name + "_ses.shp"
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        clipList.append(output)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Select by attributes 
## Description: Select all Wells with FCODE = 48800

print "\nStep 5 Select by attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set local variables

expression = "\"FCODE\" = 48800"

#Execute Selection
for fc in clipList:
    arcpy.MakeFeatureLayer_management(fc, "temp") 
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    suf = str(fc)[-8:]
    output = os.path.join(interFolder, "Wells_us_nhd" + suf)
    arcpy.CopyFeatures_management("temp", output)
    finalList.append(output)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 6. Copy and paste to final location
## Description: Save shapefile into final folder

print "\nStep 6 Save to final location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in finalList:
    oRoot, oExt = os.path.split(fc)
    out_feature = os.path.join(finalFolder, oExt)
    arcpy.CopyFeatures_management(fc, out_feature)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



