## Name: Gauges.py
## Created on: 2019-04-15
## By: Sophie Plassin
## Description: Preparation of gauges for the Rio Grande/Bravo basin (RGB)
## For all:
##              1. Create a geodatabase

## For gauges of CONAGUA
##              2. Convert excel files to dbf
##              3. Creates a new point feature layer based on x- and y-coordinates.

## For gauges of USGS
##              4. Convert shapefile to gdb

## For gauges of IBWC
##              5. Select by attribute all gauges managed by IBWC

## For all
##              6. Clean and homogeneize the attribute tables
##              7. Project the shapefiles to North America Albers Equal Area Conic
##              8. Clip the gauges that overlay the RGB study area.
##              9. Convert to shapefiles
## ---------------------------------------------------------------------------


## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set environment settings
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\6_gauges\\original_input\\"
dirpath = arcpy.env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\6_gauges\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\6_gauges\\final_output\\"

# Set overwrite option
arcpy.env.overwriteOutput = True

# List
tabList = []
projList = []
clipList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a gdb to store all intermediary outputs.

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.CreateFileGDB_management(interFolder, "Gauges.gdb")
gdb = os.path.join(interFolder, "Gauges.gdb")

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## CONAGUA
## 2. Convert excel files to dbf
## Description: Converts Excel files into a table.

print "\nStep 2 Convert excel file to dbf starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set local variables
xlsFile = "CONAGUA\\Gauges_conagua.xls"

# Execute Excel to Dbf table
name = os.path.splitext(os.path.split(xlsFile)[-1])[0] + ".dbf"
print name
dbf_file = os.path.join(interFolder, name)
arcpy.ExcelToTable_conversion(xlsFile, dbf_file)

print "Convert excel file to dbf", xlsFile, "completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 3. Make XY Event Layer
## Description: Creates a new point feature layer based on x- and y-coordinates defined in a source table.

print "\nStep 3 Project the polygons starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

x_coords = "DD_X"
y_coords = "DD_Y"

# Execute layer
out_Layer = os.path.splitext(dbf_file)[0]
print out_Layer
arcpy.MakeXYEventLayer_management(dbf_file, x_coords, y_coords, out_Layer)
# Save to a layer file
saved_Layer = out_Layer + ".lyr"
arcpy.SaveToLayerFile_management(out_Layer, saved_Layer)
# Create Shapefile
shape = os.path.splitext(os.path.split(saved_Layer)[-1])[0]
output = os.path.join(gdb, shape)
arcpy.CopyFeatures_management(saved_Layer, output)
tabList.append(output)

print "Make XY Event Layer", dbf_file, "completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 4. Convert shapefile to feature class gdb
## Description: Copy and paste the feature classes into it.
print "\nStep 4 Convert mdb to gdb starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

shp = os.path.join(dirpath, "USGS\\USGS_Streamgages-NHD_Locations.shp")

#Execute 
arcpy.FeatureClassToGeodatabase_conversion(shp, gdb)

# Rename file
fc_gdb = os.path.join(gdb, "USGS_Streamgages_NHD_Locations")
out_data = os.path.join(gdb, "Gauges_usgs")
data_type = "FeatureClass"
arcpy.Rename_management(fc_gdb, out_data, data_type)
tabList.append(out_data)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

 
## ---------------------------------------------------------------------------
## 5. Select by attributes the gauges managed by IBWC
## Description: Select based on an attribute query: "IBWC_ID" is different of Null

print "\nStep 5 Select by attributes for IBWC starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_folder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\2_binational_agency\\original_input\\"
IBWC_gdb = "IBWCGDB_01282019.gdb"
fc = "\\fd_Environmental\\fc_US_WQMonStations_SFGages"
in_fc = in_folder + IBWC_gdb + fc


arcpy.MakeFeatureLayer_management(in_fc, "lyr_ibwc")
arcpy.SelectLayerByAttribute_management("lyr_ibwc", 'NEW_SELECTION',
                                         "\"LONG_ID\" LIKE \'IBWC%\' AND \"TYPE\" <> \'WQ\'")


output = gdb + "\\Gauges_ibwc"
arcpy.CopyFeatures_management("lyr_ibwc", output)
cur = arcpy.UpdateCursor(output)
for row in cur:
    value1 = row.getValue("TYPE")
    if value1 == "B":
        row.setValue("TYPE", 'SF & WQ')
    cur.updateRow(row)

tabList.append(output)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Clean datasets
## Description: Clean and standardize the information contained in the datasets.

print "\nStep 6 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\6_gauges\\inter_output\\Gauges.gdb\\"

# Fields types
fieldTypeTx = "TEXT"
fieldTypeNb = "DOUBLE"

# New fields names
fieldOperator = "AGENCY"
fieldHistorical = "HISTORICAL"
fieldGageName = "NAME"
fieldX = "DD_X"
fieldY = "DD_Y"
fieldWebPre = "WEB"
fieldWebPost = "HTM"

# Fields to delete
fieldDel= ["LINK", "MDB", "GAGE_ID", "FID_", "LON_SITE", "LAT_SITE",
           "WEB", "HTM"]


### Add field Operator and Country
print tabList
for fc in tabList:
    if fc.endswith("ibwc") or fc.endswith("tceq"):
        arcpy.AddField_management(fc, fieldHistorical, fieldTypeTx)
    if fc.endswith("usgs"):
        pass
    else:
        arcpy.AddField_management(fc, fieldOperator, fieldTypeTx)
        cur = arcpy.UpdateCursor(fc)
        name = os.path.split(fc)[-1]
        for row in cur:
            if name.endswith("conagua"):
                row.setValue(fieldOperator, 'CONAGUA')
            if name.endswith("ibwc"):
                row.setValue(fieldOperator, 'IBWC')
            if name.endswith("tceq"):
                row.setValue(fieldOperator, 'TCEQ')
            cur.updateRow(row)

## Rename fields
    fieldList = arcpy.ListFields(fc)
    for field in fieldList: #loop through each field
        if field.name == 'SITE_NO':  
            arcpy.AlterField_management(fc, field.name, 'SITE_ID', 'SITE_ID')
        if field.name == 'AGENCY_CD':  
            arcpy.AlterField_management(fc, field.name, 'AGENCY', 'AGENCY')
        if field.name == 'STATION_NM': 
            arcpy.AlterField_management(fc, field.name, 'NAME', 'NAME')
        if field.name == 'STATE_CD':  
            arcpy.AlterField_management(fc, field.name, 'STATE_ID', 'STATE_ID')                
        if field.name == 'LON_NHD':  
            arcpy.AlterField_management(fc, field.name, 'DD_X', 'DD_X')
        if field.name == 'LAT_NHD':  
            arcpy.AlterField_management(fc, field.name, 'DD_Y', 'DD_Y')
        if field.name == 'GAGE_ID':  
            arcpy.AlterField_management(fc, field.name, 'CONAGUA_ID', 'CONAGUA_ID')                        
        if field.name == 'USGSID':  
            arcpy.AlterField_management(fc, field.name, 'USGS_ID', 'USGS_ID')
        if field.name == 'NWISWEB':  
            arcpy.AlterField_management(fc, field.name, 'HISTORICAL', 'HISTORICAL')
            
# Create historical link
    if fc.endswith("conagua"):
        expression1 = "!LINK!+str(!CONAGUA_ID!)+!MDB!"
        arcpy.CalculateField_management(fc, fieldHistorical, expression1, "PYTHON_9.3")
    if fc.endswith("ibwc"):
        for field in [fieldWebPre, fieldWebPost]:
            arcpy.AddField_management(fc, field, fieldTypeTx)
        cur = arcpy.UpdateCursor(fc)
        for row in cur:
            row.setValue(fieldWebPre, 'http://www.ibwc.gov/wad/')
            row.setValue(fieldWebPost, '.htm')
            cur.updateRow(row)
        expression2 = "!WEB!+!BINARY_ID!+!HTM!"
        arcpy.MakeFeatureLayer_management(fc, "temp")
        arcpy.SelectLayerByAttribute_management("temp", 'NEW_SELECTION',
                                             "\"BINARY_ID\" <> \'\'")
        arcpy.CalculateField_management("temp", fieldHistorical, expression2, "PYTHON_9.3")


# Delete fields
    arcpy.DeleteField_management(fc, fieldDel)


print "Clean dataset" , fc, "completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 7. Project the polygons
## Description: Project polygons to North America Albers Equal Area Conic

print "\nStep 7 Project the polygons starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Execute Project
for fc in tabList:
    projFile = os.path.splitext(fc)[0] + "_pr"
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 8. Clip the gauges that overlay the RGB study area.
## Description: Clip the gauges for the study area.

print "\nStep 8 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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
            output = new_name + "_bas"
        else:
            output = new_name + "_ses"
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        clipList.append(output)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 8 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 9. Convert feature class to shapefile.
## Description: Convert feature class to shapefile and save in final Folder.

print "\nStep 9 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.FeatureClassToShapefile_conversion(clipList, finalFolder)

print "Step 9 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")





    
