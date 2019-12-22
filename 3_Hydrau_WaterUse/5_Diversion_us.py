## Name: Diversion_SurfaceWater_US.py
## Created on: 2019-05-20
## By: Sophie Plassin
## Description: Preparation of the shapefile mapping all diversion structures of surface water for the U.S. Rio Grande/Bravo basin (RGB)
##              1. Merge input data
##              2. Populate new fields
##              3. Project the shapefile to North America Albers Equal Area Conic
##              4. Clip to the boundary of the study area
##              5. Select by ayttributes all diversion structures that are not "Stream"
##              6. Save output data to final folder
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Diversion_SurfaceWater_US starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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
inputList = []
mergeList = []
joinList = []
projList = []
clipList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Erase duplicate features
## Description: Erase duplicate features of the CO, NM, and TX NHD Flowline dataset

print "\nStep 1 Erase duplicate HUCs starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs
for path, dirs, files in os.walk(dirpath):
    for name in files:
        absFile=os.path.abspath(os.path.join(path,name))
        if name.endswith(".shp") and (path.endswith('CO') or path.endswith('TX')):
            inputList.append (absFile)
        if name.endswith(".shp") and path.endswith('NM'):
            NM_file = absFile # NM = file where we erase duplicate features
            mergeList.append(NM_file)

# Output
name_erase = os.path.join (interFolder, "Flowline")

# Erase
for in_file in inputList:
    state = in_file[-18:-16]
    output_feature = name_erase + state + ".shp"
    arcpy.Erase_analysis(in_file, NM_file, output_feature)
    mergeList.append(output_feature)

print "Step 1 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Merge HUCs into a single output feature
## Description: Combines the NHD Flowline of CO, NM and TX

print "\nStep 2 Merge HUCs starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output
name = os.path.split(mergeList[0])[1]
output = os.path.join(interFolder, "Diversion_US.shp")
arcpy.Merge_management(mergeList, output, "NO_FID")
joinList.append(output)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Populate new fields
## Description: Add a field to specify the name of diversion structures (canal, pipeline, artifical path...) 


print "\nStep 3 Populate new fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldFeat = "FEATURE"
fieldType = "TEXT"
listCodeCanal = [33600, 33601, 33603]
listCodePipeline = [42800, 42801, 42802, 42803, 42804, 42805, 42806, 42807, 42808, 42809, 42810, 42811, 42812, 42813, 42814, 42815, 42816]
listCodeStream = [46000, 46003, 46006, 46007]
listCodeConduit = [42000, 42001, 42002, 42003]

# Add field
for fc in joinList:
    arcpy.AddField_management(fc, fieldFeat, fieldType)

#Update lines
cur = arcpy.UpdateCursor(fc)
for row in cur:
    value = row.getValue("FCODE")
    if value == 55800:
         row.setValue(fieldFeat, "ARTIFICIAL PATH")
    for x in listCodeCanal:
        if value == x:
            row.setValue(fieldFeat, "CANAL/DITCH")  
    if value == 56600:
         row.setValue(fieldFeat, "COASTLINE")
    if value == 33400:
         row.setValue(fieldFeat, "CONNECTOR")
    for x in listCodePipeline:
        if value == x:
            row.setValue(fieldFeat, "PIPELINE")
    for x in listCodeStream:
        if value == x:
            row.setValue(fieldFeat, "STREAM/RIVER")
    for x in listCodeConduit:
        if value == x:
            row.setValue(fieldFeat, "UNDERGROUND CONDUIT")  
    cur.updateRow(row)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 3 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in joinList:
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
## Description: Select all diversion structures that are not "Stream"

print "\nStep 5 Select by attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set local variables

expression = "\"FEATURE\" <> \'STREAM/RIVER\' AND \"FEATURE\" <> \'COASTLINE\' AND \"FEATURE\" <> \'ARTIFICIAL PATH\'"

#Execute Selection
for fc in clipList:
    arcpy.MakeFeatureLayer_management(fc, "temp") 
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    output = os.path.splitext(fc)[0] + "_select.shp"
    arcpy.CopyFeatures_management("temp", output)
    finalList.append(output)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 6. Copy and paste to final location
## Description: Save shapefile into final folder

print "\nStep 6 Save to final location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in finalList:
    oRoot, oExt = os.path.split(fc)
    name = oExt.split("_select.shp")[0]
    out_feature = os.path.join(finalFolder, name)
    arcpy.CopyFeatures_management(fc, out_feature)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




