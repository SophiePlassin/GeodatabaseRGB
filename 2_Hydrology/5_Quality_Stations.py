## Name: Quality Stations.py
## Created on: 2019-06-29
## By: Sophie Plassin
## Description: Preparation of the Water Quality Stations point dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Select by attributes all water quality stations
##              3. Project the shapefiles to North America Albers Equal Area Conic
##              4. Clip the gauges that overlay the RGB study area.
##              5. Convert to shapefiles
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
arcpy.env.workspace = dirpath 
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\7_quality_stations\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\7_quality_stations\\final_output\\"

# Set overwrite option
arcpy.env.overwriteOutput = True


# List
clippedList = []
clip_features = []
projList = []


# File
IBWC_gdb = "IBWCGDB_01282019.gdb"
fc = "\\fd_Environmental\\fc_US_WQMonStations_SFGages"
in_fc = IBWC_gdb + fc


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a gdb to store all intermediary outputs.

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.CreateFileGDB_management(interFolder, "Stations.gdb")
gdb = os.path.join(interFolder, "Stations.gdb")

print "Step 1 Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Select by attributes all water quality stations
## Description: Select based on an attribute query: "TYPE" is different from SF

print "\nStep 2 Select by attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.MakeFeatureLayer_management(in_fc, "lyr_stations")
arcpy.SelectLayerByAttribute_management("lyr_stations", 'NEW_SELECTION',
                                         "\"TYPE\" <> \'SF\'")
selection = gdb + "\\Quality_Stations"
arcpy.CopyFeatures_management("lyr_stations", selection)
cur = arcpy.UpdateCursor(selection)
for row in cur:
    value1 = row.getValue("TYPE")
    if value1 == "B":
        row.setValue("TYPE", 'SF & WQ') 
    cur.updateRow(row)

print "\nStep 2 Select by attributes completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Project the polygons
## Description: Project polygons to North America Albers Equal Area Conic

print "\nStep 3 Project the polygons starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Execute Project
projFile = os.path.splitext(selection)[0] + "_pr"
arcpy.Project_management(selection, projFile, outCS)
print "Projection" , selection, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 4. Clip the stations that overlay the RGB study area (GCS: WGS 1984).
## Description: Clip the stations for the study area.

print "\nStep 4 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
xy_tolerance = ""

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute Clip
for clip in clip_features:
    # Create name
    new_name = projFile.split('_pr')[0]
    temp = os.path.split(clip)[-1]
    # Add Ses or Bas according to the clip feature name
    if temp.startswith("RGB_Basin"):
        output = new_name + "_bas"
    else:
        output = new_name + "_ses"
    arcpy.Clip_analysis(projFile, clip, output, xy_tolerance)
    clippedList.append(output)
    print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Convert feature class to shapefile.
## Description: Convert feature class to shapefile and save in final Folder.

print "\nStep 5 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.FeatureClassToShapefile_conversion(clippedList, finalFolder)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




