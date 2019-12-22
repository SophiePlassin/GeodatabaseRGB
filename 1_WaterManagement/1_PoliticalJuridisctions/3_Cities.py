## Name: Cities.py
## Created on: 2019-07-31
## By: Sophie Plassin
## Description: Preparation of the Railroads shapefiles for the Rio Grande/Bravo basin (RGB)
##              1. Project the shapefiles to North America Albers Equal Area Conic 
##              2. Clip the shapefiles
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module

import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


### Set environment settings
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\original_input\\Populated_Places\\"
dirpath = env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\"

# Local variables:
in_files = arcpy.ListFeatureClasses()
projList = []
clip_features = []


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "Populated_Places.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1. Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 2. Project the polygon
## Description: Project ecoregion polygon to North America Albers Equal Area Conic

print "\nStep 2 Project the polygon starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Project
for fc in in_files:
    projFile = os.path.join(out_gdb, "Populated_Places_pr")
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)    
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Clip
## Description: Clip the waterbody polygon for the study area.

print "\nStep 3 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp",
          "RGB_Ses_na_albers.shp"]
xy_tolerance = ""

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

    
#Execute Clip
for fc in projList:
    print fc
    for clip in clip_features:
        temp = os.path.split(clip)[-1]
        name = os.path.split(fc)[1]
        new_name = name.split('_pr')[0]
        if temp.startswith("RGB_Basin"):
            output = finalFolder + new_name + "_bas.shp"
        else:
            output = finalFolder + new_name + "_ses.shp"
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Clip completed at", datetime.datetime.now().strftime("%I:%M:%S%p")




