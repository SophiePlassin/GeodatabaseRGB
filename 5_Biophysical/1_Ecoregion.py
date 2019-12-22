## Name: Ecoregion.py
## Created on: 2019-04-11
## By: Sophie Plassin
## Description: Preparation of the ecoregions shapefiles for the Rio Grande/Bravo basin (RGB)
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
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\1_ecoregion\\original_input\\"
dirpath = env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\1_ecoregion\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\1_ecoregion\\final_output\\"

# Local variables:
in_files = arcpy.ListFeatureClasses()
projList = []
clip_features = []
#in_files = ["us_eco_l4_no_st.shp", "NA_CEC_Eco_Level3.shp"]
## ---------------------------------------------------------------------------
## 1. Project the polygon
## Description: Project ecoregion polygon to North America Albers Equal Area Conic

print "\nStep 1 Project the polygon starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Project
for fc in in_files:
    if fc.startswith("us_eco"):
        projName = os.path.join(interFolder, "US_ECO_4")
    else:
        projName = os.path.join(interFolder, "NA_ECO_3")
    projFile = projName + "_pr.shp"
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)    
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Clip
## Description: Clip the waterbody polygon for the study area.

print "\nStep 2 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
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
        new_name = name.split('_pr.shp')[0]
        if temp.startswith("RGB_Basin"):
            output = finalFolder + new_name + "_bas.shp"
        else:
            output = finalFolder + new_name + "_ses.shp"
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Clip completed at", datetime.datetime.now().strftime("%I:%M:%S%p")
