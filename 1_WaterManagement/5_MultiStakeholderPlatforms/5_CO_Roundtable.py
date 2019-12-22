## Name: Rio Grande Roundtable in Colorado.py
## Created on: 2019-07-06
## By: Sophie Plassin
## Description: Preparation of the Rio Grande Roundtable outline
##              1. Select Rio Grande Roundtable outline (State of Colorado)
##              2. Clip to the boundary of the study area
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\inter_output\\RG_Roundtable\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\final_output\\"
arcpy.env.workspace = dirpath

# Set overwrite option
arcpy.env.overwriteOutput = True

# List
clipList = []

## ---------------------------------------------------------------------------    
## 1. Select by attributes and export to the geodatabase
## Description: Select the RG Roundtable outline (CO state) from the Counties shapefile, based on its GEOID, using Select Layer By Attribute

print "\nStep 1 Select Layer by Attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = "States.shp"
# Output name
outname = "CO_RGRoundtable.shp"
# Selection
expression = "\"ADM1_GEOID\" = '84008'"
# Execute
arcpy.MakeFeatureLayer_management(in_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
out_fc = os.path.join(interFolder, outname)
arcpy.CopyFeatures_management("temp", out_fc)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------    
## 2. Clip 
## Description: Clip to the boundary of the RGB outline

print "\nStep 2 Clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []
for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# output
Input = out_fc

# Execute Clip
for clip in clip_features:
    temp = os.path.split(clip)[-1]
    name = os.path.split(Input)[1]
    output = os.path.join(finalFolder, name)
    arcpy.Clip_analysis(Input, clip, output, xy_tolerance)
    clipList.append(output)
    print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------    
## 3. Homogeneize fields 
## Description: Delete fields

print "\nStep 3 Delete fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

newField = "NAME"
typeField = "TEXT"
fieldsDel = ["ADM0_ID", "NAME_0", "ID_0", "ADM1_ID", "NAME_1",
            "ID_1", "ADM1_GEOID", "Shape_Leng", "Shape_Area"]


for fc in clipList:
    arcpy.AddField_management(fc, newField, typeField, "", "", 50)
    arcpy.CalculateField_management(fc, "NAME", "'" + "Rio Grande Basin Roundtable" + "'", "PYTHON_9.3")
    arcpy.DeleteField_management(fc, fieldsDel)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




