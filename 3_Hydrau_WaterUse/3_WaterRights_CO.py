## Name: WaterRights_Colorado.py
## Created on: 2018-11-29
## By: Sophie Plassin
## Description: Preparation of the water right shapefile for the state of Colorado in the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase 
##              2. Make XY event layer to geolocate WR location
##              3. Update names, add field WR_SOURCE and poulate with two values (SW for surface water or GW for groundwater)
##              4. Project the shapefile to North America Albers Equal Area Conic
##              5. Select by attribute WR location for Division 3 (RGB)
##              6. Save output data to final folder
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
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\original_input\\CO\\"
dirpath = arcpy.env.workspace

# Options
arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

# Directories
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\inter_output\\CO\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\final_output\\"


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "CODWR.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Generate XY Layer event 
## Description: Creates a new point feature layer based on x- and y-coordinates defined in a source table.

print "\nStep 2 Generate XY Layer event starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set local variables
xlsx = "DWR_Water_Right_-_Net_Amounts_import_astext.xlsx"
table = "DWR_Water_Right_Net_Amounts.dbf"
x_coords = "Longitude"
y_coords = "Latitude"

# Convert excel to dbf
in_Table = os.path.join(interFolder, table)
arcpy.ExcelToTable_conversion(xlsx, in_Table)

# Make the XY event layer
nameLayer = os.path.splitext(in_Table)[0] + '_prepared'
outLayer = os.path.join(interFolder, nameLayer)
arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, outLayer)

# Save to a layer file
saved_Layer = outLayer + ".lyr"
arcpy.SaveToLayerFile_management(outLayer, saved_Layer)
    
# Create Shapefile
arcpy.FeatureClassToGeodatabase_conversion(saved_Layer, out_gdb)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Change Names
## Description: Add alias

print "\nStep 3 Change Names starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

oRoot, fc = os.path.split(saved_Layer.split(".lyr")[0])
fc_gdb = os.path.join(out_gdb, fc)

# Alter fields
alterFields = [['Structure', 'StructName', 'Structure Name'],
               ['Structur_1', 'StructType', 'Structure Type'],
               ['Water_Sour', 'WaterSrce', 'Water Source'],
               ['Stream_Mil', 'StreamMile', 'Stream Mile'],
               ['Latitude', 'LAT_DD', 'Latitude'],
               ['Longitude', 'LONG_DD', 'LONG_DD'],
               ['Location_A', 'LocAccurac', 'Location Accuracy'],
               ['Adjudicati', 'AdjDate', 'Adjudication Date'],
               ['Previous_A', 'PreAdjDate', 'Previous Adj Date'],
               ['Appropriat', 'AppropDate', 'Appropriation Date'],
               ['Admin_No', 'AdminNo', 'Admin No'],
               ['Order_No', 'OrderNo', 'Order No'],
               ['Priority_N', 'PriorityNo', 'Priority No'],
               ['Associated', 'AssoCaseNo', 'Associated Case Numbers'],
               ['Decreed_Us', 'DecreedUse', 'Decreed Uses'],
               ['Net_Absolu', 'NetAbsolut', 'Net Absolute'],
               ['Net_Condit', 'NetConditi', 'Net Conditional'],               
               ['Net_APEX_A', 'NetAPEXAbs', 'Net APEX Absolute'],               
               ['Net_APEX_C', 'NetAPEXCon', 'Net APEX Conditional'],               
               ['Decreed_Un', 'DecreUnits', 'Decreed Units'],
               ['Seasonal_L', 'SeasoLimit', 'Seasonal Limits'],
               ['More_Infor', 'MoreInfo', 'More Information']]

for old, new, new_alias in alterFields:
    arcpy.AlterField_management(fc_gdb, old, new, new_alias)

# Add new field WR_Source and add the type of water source (Surface or groundwater)
fieldSrce = "WR_Source"
arcpy.AddField_management(fc_gdb, fieldSrce, "TEXT", "", "", "5")

# Populate field Source
cur = arcpy.UpdateCursor(fc_gdb)
for row in cur:
    value1 = row.getValue('StructType')
    if value1 == 'Well':
        row.setValue(fieldSrce, "GW")
    else:
        row.setValue(fieldSrce, "SW")
    cur.updateRow(row)    

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

name = "CO_WaterRights_pr"
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

projFile = os.path.join(out_gdb, name)
arcpy.Project_management(fc_gdb, projFile, outCS)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 5. Select By Attribute all Water Rights located in Division 3 with geographic coordinate
## Description: Select all points located in Division 3

print "\nStep 5 Select By Attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

expression = "\"DIV\" = '3' AND \"LAT_DD\" <> 0 AND \"LONG_DD\" <> 0"
arcpy.MakeFeatureLayer_management(projFile, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
selectFile = projFile.split("_pr")[0] + "_slct"
arcpy.CopyFeatures_management("temp", selectFile)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Copy and paste to final location
## Description: Save shapefile into final folder

print "\nStep 6 Save to final location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

oRoot, oExt = os.path.split(selectFile)
finalName = oExt.split('_slct')[0] + ".shp"
out_feature = os.path.join(finalFolder, finalName)
arcpy.CopyFeatures_management(selectFile, out_feature)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



