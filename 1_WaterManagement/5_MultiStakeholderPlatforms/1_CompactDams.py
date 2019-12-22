## Name: Dams Compact.py
## Created on: 2019-08-06
## By: Sophie Plassin
## Description: Preparation of the "post-Compact" dams dataset for the Rio Grande/Bravo basin (RGB)
##              1. Select Post-Compact dams from the prepared NID dataset
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

# Set overwrite option
arcpy.env.overwriteOutput = True

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\4_dams\\final_output"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\final_output\\"
arcpy.env.workspace = dirpath


## ---------------------------------------------------------------------------
## 1. Select Post-Compact dams
## Description: Select Post-Compact dams from the NID dataset, based on their name (ID), using Select Layer By Attribute

## List of Post-Compact dams used for the Rio Grande Compact.
## Alberta Park Reservoir: CO00762
## Big Meadows Reservoir: CO00764
## Fuchs Reservoir: CO00770
## Mill Creek Reservoir: CO00776
## Rito Hondo Reservoir: CO00778
## Shaw Nort and South Dam: CO02870 & CO00781
## Trujillo Meadows Reservoir: CO00788
## Squaw Lake: CO00810
## Troutvale Number 2: CO00813
## Jumper Creek Reservoir: CO00970
## Platoro & Platoro Dike Reservoir: CO01671
## Hermit #4: CO01750
## Abiquiu Reservoir: NM00001
## Galisteo Reservoir: NM00002
## Jemez Canyon Reservoir: NM00003
## Heron & Heron Dike Reservoir: NM00122
## Elephant Butte & Elephant Butte Dike Reservoir: NM00129
## Caballo Reservoir:NM00131
## Acomita Reservoir: NM00153
## Nichols Reservoir: NM00241
## McClure (Granite Point) Reservoir: NM00242
## Cochiti Lake: NM00404
## Nambe Falls Reservoir: NM00412
## Seama Reservoir: NM00703
## El Vado Reservoir: NM10008


print "\nStep 1 Select Post Compact dams starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input Name
in_file = "Dams_us_ses.shp"
# Output Name
out_fc = "RG_Compact_Dams.shp"
# Selection
expression = """"NIDID" IN ('CO00762', 'CO00764', 'CO00770', 'CO00776', 'CO00778', 'CO00781','CO02870',
'CO00788', 'CO00810', 'CO00813', 'CO00970', 'CO01671', 'CO01750', 
'NM00001', 'NM00002', 'NM00003', 'NM00122', 'NM00129', 'NM00131',  'NM00153', 'NM00241', 'NM00242', 'NM00404',
'NM00412', 'NM00703', 'NM10008')"""
# Execute
arcpy.MakeFeatureLayer_management(in_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
out_file = os.path.join(finalFolder, out_fc)
arcpy.CopyFeatures_management("temp", out_file)
print "Step 1 Select completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nProgram completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




