## Name: TransboundaryProjects_RGB.py
## Created on: 2019-07-08
## By: Sophie Plassin
## Description: Preparation of the dataset related to Transboundary Conservation Projects in the Rio Grande/Bravo basin (RGB)
##              1. Create a gdb
##              2. Project the dataset to North America Albers Equal Area Conic
##              3. Select by location the polygons
##              4. Edit attribute table
##              5. Export feature class to final Folder
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\12_conservation_projects\\original_input\\Transboundary\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\12_conservation_projects\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\12_conservation_projects\\final_output\\"
arcpy.env.workspace = dirpath



## ---------------------------------------------------------------------------
## 1. Create a gdb
## Description: Create a gdb to store the intermediary output files

print "\nStep 1 Create a gdb starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.CreateFileGDB_management(interFolder, "TransboundGDB.gdb")
out_gdb = os.path.join(interFolder, "TransboundGDB.gdb")

print "Step 1 Create a gdb ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




## ---------------------------------------------------------------------------
## 2. Project
## Description: Project the dataset to North America Albers Equal Area Conic

print "\nStep 2 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Define projection
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Definte list of inputs and outputs
inputList = arcpy.ListFeatureClasses()

# Execute project
projList =[]
for fc in inputList:
    if fc.startswith("2015"):
        name = "LCC_networks_pr"
    else:
        name = "Bird_Conservation_JoinVentures_pr"
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    projList.append (projFile)

print "Step 2 Project ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 3. Select by location
## Description: Select all areas that cross the boundaries of the RGB

print "\nStep 3 Select by location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []
for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# output list
selectList = []

## Execute select layer by location
for clip in clip_features:
    arcpy.MakeFeatureLayer_management(clip, "lyr_rgb")
    for fc in projList:
        arcpy.MakeFeatureLayer_management(fc, "lyr_temp")
        expression = arcpy.AddFieldDelimiters("lyr_temp", "area_names") + "= 'Unclassified'"
        arcpy.SelectLayerByLocation_management("lyr_temp",
                                               "INTERSECT",
                                               "lyr_rgb",
                                               "",
                                               "NEW_SELECTION")
        if "LCC" in fc:
            arcpy.SelectLayerByAttribute_management("lyr_temp",
                                                    "REMOVE_FROM_SELECTION",
                                                    expression)
        projName = os.path.split(fc)[1]
        outfc_name = projName.split('_pr')[0]
        outfc_file = os.path.join(out_gdb, outfc_name)
        arcpy.CopyFeatures_management("lyr_temp", outfc_file)
        selectList.append(outfc_file)

print "Step 3 Select by location ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




## ---------------------------------------------------------------------------
## 4. Edit attribute table
## Description: Rename fields and remove unecessary fields

print "\nStep 4 Edit attribute table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
delFields = ["Acres"]

for fc in selectList:
    ## Add field Area in square kilometers
    arcpy.AddField_management(fc, "Area_sqkm", "FLOAT")
    arcpy.CalculateField_management(fc, "Area_sqkm", "!SHAPE.area@SQUAREKILOMETERS!", "PYTHON_9.3")
    ## Rename
    fieldList = arcpy.ListFields(fc)
    for field in fieldList:
        if field.name == 'JV':
            arcpy.AlterField_management(fc, field.name, 'JV_name', 'JV_name')
        if field.name == 'area_names':
            arcpy.AlterField_management(fc, field.name, 'LCC_name', 'LCC_name')
    arcpy.DeleteField_management(fc, delFields)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 5. Copy to final output folder
## Description: Copy files to final folder
print "\nStep 5 Copy the final outputs starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in selectList:
    name = os.path.split(fc)[1]
    arcpy.CopyFeatures_management(fc, finalFolder + name + ".shp")

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

