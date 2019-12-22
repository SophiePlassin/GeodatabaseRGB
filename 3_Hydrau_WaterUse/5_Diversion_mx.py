## Name: Diversion_SurfaceWater_MX.py
## Created on: 2019-05-20
## By: Sophie Plassin
## Description: Preparation of the shapefile mapping all diversion structures of surface water for the U.S. Rio Grande/Bravo basin (RGB)
##              1. Merge input data
##              2. Populate new fields
##              3. Project the shapefile to North America Albers Equal Area Conic
##              4. Clip to the boundary of the study area
##              5. Save output data to final folder
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Diversion_SurfaceWater_MX starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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
mergeList = []
projList = []
clipList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Merge input data for the states of CO, NM and TX
## Description: Merge the files CO_NHDFlowline, NM_NHDFlowline and TX_NHDFlowline

print "\nStep 1 Merge input data starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute
in_files = ["Acueducto.shp", "Canal.shp"]
output = os.path.join(interFolder, "Diversion_MX.shp")
arcpy.Merge_management(in_files, output)
mergeList.append(output)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Populate new fields
## Description: Add a field to specify the name of diversion structures (canal, pipeline, artifical path...) 


print "\nStep 2 Populate new fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

#Set Local Variables
fieldEntity = "FEATURE"
fieldLocationGround = "TYPE"
fieldType = "TEXT"
fieldList = [fieldEntity, fieldLocationGround]

#AddField
for fc in mergeList:
    for fn in fieldList:
        arcpy.AddField_management(fc, fn, fieldType)

#Clean
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        value1 = row.getValue("ENTIDAD")
        if value1 == "CANAL":
            row.setValue(fieldEntity, "CANAL")
        else:
            row.setValue(fieldEntity, "AQUEDUCTS")
        value2 = row.getValue("RELSUELO")
        if value2 == "Superficial":
            row.setValue(fieldLocationGround, "SURFACE")
        elif value2.startswith("Subterr"):
            row.setValue(fieldLocationGround, "UNDERGROUND")
        else:
            row.setValue(fieldLocationGround, "NA")
        cur.updateRow(row)

#Delete Spanish fields
    fieldDel = ["ENTIDAD", "RELSUELO", "SHAPE_len"]
    for fn in fieldDel:
        arcpy.DeleteField_management(fc, fieldDel)
        
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
## 5. Copy and paste to final location
## Description: Save shapefile into final folder

print "\nStep 5 Save to final location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldsDel = ["OBJECTID"]
for fc in clipList:
    oRoot, oExt = os.path.split(fc)
    out_feature = os.path.join(finalFolder, oExt)
    arcpy.CopyFeatures_management(fc, out_feature)
    arcpy.DeleteField_management(out_feature, fieldsDel)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



