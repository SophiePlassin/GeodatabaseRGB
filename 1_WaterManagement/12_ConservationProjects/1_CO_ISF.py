## Name: Colorado_Instream_Flow.py
## Created on: 2019-07-08
## By: Sophie Plassin
## Description: Preparation of the dataset related to Soil and Water Conservation Districts
##              in the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Export files into the geodatabase
##              3. Edit attribute table
##              4. Project the dataset to North America Albers Equal Area Conic
##              5. Clip the polygons with the study area shapefile
##              6. Merge the ISF Termini and ISF Reaches (decreed and pending) datasets
##              7. Export files to final folder
# ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
import glob
from arcpy import env
from arcpy.sa import *

# Set options
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\12_conservation_projects\\original_input\\CO\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\12_conservation_projects\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\12_conservation_projects\\final_output\\"
arcpy.env.workspace = dirpath


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
gdb_name = "ISF.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Export Feature Class to geodatabase
## Description: Export features to the geodatabase

print "\nStep 2 Export feature to gdb starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs:
fcList = arcpy.ListFeatureClasses()

gdbList =[]

for fc in fcList:
    arcpy.FeatureClassToGeodatabase_conversion(fc, out_gdb)
    path, feature = os.path.split(fc)
    out_featureclass = feature.split(".shp")[0]
    fc_gdb = os.path.join(out_gdb, out_featureclass)
    gdbList.append(fc_gdb)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Edit attribute table
## Description: Rename and delete fields

print "\nStep 3 Homogeneize fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in gdbList:
    # Rename fields
    fieldList = arcpy.ListFields(fc)
    feature = os.path.split(fc)[1]
    if feature.startswith("ISF_Termini"):
        alterFields = [["DirToSecLi", "DirSecLng"], ["DistToSecL", "DistSecLng"], ["DirToSec_1", "DirSecLat"], ["DistToSe_1", "DistSecLat"]]
        for old, new in alterFields:
            tmpName = ("{0}_tmp".format(old))
            arcpy.AlterField_management(fc, old, tmpName)
            arcpy.AlterField_management(fc, tmpName, new)
    if feature.startswith ("Lakes"):
        alterFields = [["CWCB_CASE_", "CWCB_CASE"], ["LAKE_NAME", "Lake_Name"]]
        for old, new in alterFields:
            tmpName = ("{0}_tmp".format(old))
            arcpy.AlterField_management(fc, old, tmpName)
            arcpy.AlterField_management(fc, tmpName, new)
    # Calculate
    if feature.startswith("ISF_Reaches"):
        arcpy.AddField_management(fc, "KILOMETERS", "FLOAT")
        arcpy.CalculateField_management(fc, "KILOMETERS", "!MILES! * 1.60934", "PYTHON_9.3")

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Project the polygon
## Description: Project to North America Albers Equal Area Conic

print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

projList =[]
for fc in gdbList:
    name = os.path.split(fc)[1] + '_pr'
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    projList.append(projFile)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Clip
## Description: Clip Crossing and fences for the study area.

print "\nStep 5 Clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output stored in
clipList = []

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []
for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)
    
# Execute Clip
for fc in projList:
    for clip in clip_features:
        temp = os.path.split(clip)[-1]
        root = os.path.split(fc)[1]
        name = root.split('_pr')[0]
        output = out_gdb + "\\" + "CO_" + name
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        clipList.append(output)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 5 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## ---------------------------------------------------------------------------
## 6. Merge ISF Termini (decreed and pending) and ISF Reaches (decreed and pending) into one layer
## Description: Merge features in one dataset 

print "\nStep 6 Merge state layer to a single dataset starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input list
mergeReach = []
mergeTermini = []
mergeList = []
for fc in clipList:
    oRoot, oExt = os.path.split(fc)
    if oExt.startswith("CO_ISF_Reaches"):
        mergeReach.append(fc)
    if oExt.startswith("CO_ISF_Termini"):
        mergeTermini.append(fc)
mergeList.extend([mergeReach, mergeTermini])
sorted(mergeList)
        
# Execute Merge
for li in mergeList:
    if li == mergeList[0]:
        output = os.path.join(out_gdb, "CO_ISF_Reaches")
    else:
        output = os.path.join(out_gdb, "CO_ISF_Termini")
    arcpy.Merge_management(li, output)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 7. Export files to final folder
## Description: Export files to final folder and delete unecessary fields

print "\nStep 7 Export files starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

inputs = ["CO_ISF_Reaches", "CO_ISF_Termini", "CO_Lakes"]

fieldsDel2 = ["Shape_Le_1", "Shape_Le_2", "SHAPE_Leng", "OBJECTID_2"]

for fc in inputs:
    in_fc = os.path.join(out_gdb, fc)
    arcpy.FeatureClassToShapefile_conversion(in_fc, finalFolder)
    output = os.path.join(finalFolder, fc + ".shp")
    arcpy.DeleteField_management(output, fieldsDel2)

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")







