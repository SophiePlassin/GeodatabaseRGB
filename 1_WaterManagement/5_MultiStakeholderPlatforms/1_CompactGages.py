## Name: Gauges Compact.py
## Created on: 2019-07-06
## By: Sophie Plassin
## Description: Preparation of the gauges dataset used for the Rio Grande Compact
##              1. Select the gauges used for the RG Compact 
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\6_gauges\\final_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\final_output\\"
arcpy.env.workspace = dirpath

## ---------------------------------------------------------------------------
## 1. Select Compact gauges
## Description: Select Compact gauges from the USGS dataset, based on their name (ID), using Select Layer By Attribute

## List of gauges used for the Rio Grande Compact.
##(a) On the Rio Grande near Del Norte above the principal points of diversion to the San Luis Valley; 08220000
##(b) On the Conejos River near Mogote; 08246500
##(c) On the Los Pinos River near Ortiz; 08248000
##(d) On the San Antonio River at Ortiz; 08247500
##(e) On the Conejos River at its mouths near Lasauces; 08249000
##(f) On the Rio Grande near Lobatos; 08251500
##(g) On the Rio Chama below El Vado Reservoir; 08285500
##(h) On the Rio Grande at Otowi Bridge near San Ildefonso; 08313000
##(i) On the Rio Grande at San Acacia; 08355000
##(j) On the Rio Grande at San Marcial; 08358500
##(k) On the Rio Grande below Elephant Butte Reservoir; 08361000
##(l) On the Rio Grande below Caballo Reservoir. 08362500

print "\nStep 1 Select Compact gauges starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = "Gauges_usgs_ses.shp"
# Output name
out_fc = "RG_Compact_Gauges.shp"
# Selection
expression = """"SITE_ID" IN ('08220000', '08246500' , '08248000', '08247500', '08249000', '08251500', '08285500', '08313000', '08355000', '08358500', '08361000', '08362500')"""

# Execute
arcpy.MakeFeatureLayer_management(in_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
out_file = os.path.join(finalFolder, out_fc)
arcpy.CopyFeatures_management("temp", out_file)
print "Step 1 Select completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
