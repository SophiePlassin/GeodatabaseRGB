## Name: IBWC_Offices.py
## Created on: 2019-06-29
## By: Sophie Plassin
## Description: Preparation of the binational point dataset for the Rio Grande/Bravo basin (RGB)
##              1. Clip the IBWC's office dataset (GCS: WGS 1984)
##              2. Project the IBWC's office dataset to North America Albers Equal Area Conic
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\2_binational_agency\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\2_binational_agency\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\2_binational_agency\\final_output\\"
arcpy.env.workspace = dirpath


# Set overwrite option
arcpy.env.overwriteOutput = True


# List
clippedList = []
clip_features = []


# File
IBWC_gdb = "IBWCGDB_01282019.gdb"
fc = "\\fd_LandManagement\\fc_US_OfficeLocations"
in_fc = IBWC_gdb + fc
print in_fc

## ---------------------------------------------------------------------------
## 1. Clip (GCS: WGS 1984)
## Description: Clip the polygon for the study area.

print "\nStep 1 Clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin.shp", "RGB_Ses.shp"]
xy_tolerance = ""

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute Clip
name = "IBWC_Offices"
for clip in clip_features:
    temp = os.path.split(clip)[-1]
    if temp.startswith ("RGB_Basin"):
        output = interFolder + name + "_bas.shp"
    else:
        output = interFolder + name + "_ses.shp"
    arcpy.Clip_analysis(in_fc, clip, output, xy_tolerance)
    clippedList.append(output)
    print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 1 Clip completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Project the polygon
## Description: Project RGB soil polygon to North America Albers Equal Area Conic

print "\nStep 2 Project the polygon starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in clippedList:
    name = os.path.split(fc)[1]
    projFile = os.path.join(finalFolder, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Project completed at", datetime.datetime.now().strftime("%I:%M:%S%p")



