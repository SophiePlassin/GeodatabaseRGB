## Name: TX_Groundwater_Agencies.py
## Created on: 2019-07-06
## By: Sophie Plassin
## Description: Preparation of the TX Groundwater Agencies dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Rename and export feature class
##              3. Edit attribute table
##              4. Project the dataset to North America Albers Equal Area Conic
##              5. Select by location all features located in the Rio Grande/Bravo basin (RGB)
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\original_input\\TX\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\inter_output\\TX\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\final_output\\"
arcpy.env.workspace = dirpath

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fcList = ["Groundwater_Management_Areas_082615", "TCEQ_GCD", "TCEQ_PGMA"]
gdb_name = "TX_GW.gdb"
data_type = "FeatureClass"

# Output
out_gdb = os.path.join(interFolder, gdb_name)
outNameList = ["TX_GMA", "TX_GCD", "TX_PGMA"]
gdbList =[]

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)



## ---------------------------------------------------------------------------
## 2. Rename and export feature class
## Description: Rename feature class

print "\nStep 2 Rename and export feature class starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdbList = []
for fc in fcList:
    arcpy.FeatureClassToGeodatabase_conversion(fc + ".shp", out_gdb)
    fc_gdb = os.path.join(out_gdb, fc)
    index = fcList.index(fc)
    out_featureclass = os.path.join(out_gdb, outNameList[index])
    arcpy.Rename_management(fc_gdb, out_featureclass, data_type)
    gdbList.append(out_featureclass)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Edit attribute table
## Description: Add, rename and delete fields

print "\nStep 3 Edit attribute table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Rename fields
for fc in gdbList:
    fieldList = arcpy.ListFields(fc)
    for field in fieldList:
        if fc.endswith("_GMA"):
            if field.name == 'GMAnum':
                arcpy.AlterField_management(fc, field.name, 'GMA_ID', 'GMA_ID')
        if fc.endswith("GCD"):
            if field.name == 'SHORTNAM':
                arcpy.AlterField_management(fc, field.name, 'GCD_NAME', 'GCD_NAME')
            if field.name == 'DISTNAM':
                arcpy.AlterField_management(fc, field.name, 'COMPL_NAME', 'COMPL_NAME')
            if field.name == 'Yr':
                arcpy.AlterField_management(fc, field.name, 'YEAR', 'YEAR')
        if fc.endswith("PGMA"):
            if field.name == 'IDENT_ORDE':
                arcpy.AlterField_management(fc, field.name, 'PGMA_ID', 'PGMA_ID')

# Fields to delete   
fieldsDel = ["Shape_Leng", "OBJECTID", "AREA_SQMI", "CREATDT", 
             "LEGALDES", "TXT_4YR", "Decade", "Decade_txt", "Count_by1"]
# Field to add
fieldArea = "AREA_HA"

# Add and delete fields
for infc in gdbList:
    arcpy.DeleteField_management(infc, fieldsDel)
    if infc.endswith("GCD"):
        # Add field
        arcpy.AddField_management(infc, fieldArea, "FLOAT")
        arcpy.CalculateField_management(infc, fieldArea, "!ACREAGE! * 0.404686", "PYTHON_9.3")
        # Delete field
        arcpy.DeleteField_management(infc, "ACREAGE")

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
                                  

## ---------------------------------------------------------------------------
## 4. Project the polygon
## Description: Project to North America Albers Equal Area Conic

print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

outputList = []

for fc in gdbList:
    name = fc + "_pr"
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    outputList.append(projFile)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Select by location
## Description: Select by location

print "\nStep 5 Select by location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the select_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
xy_tolerance = ""
selectList = []

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    selectList.append(out_shp)

# Execute Select by location
for fc in outputList:
    root = fc.split('_pr')[0]
    name = os.path.split(root)[1]
    for clip in selectList:
        temp = os.path.split(clip)[-1]
        print temp
        if temp.startswith("RGB_Basin"):
            output = finalFolder + name + "_bas.shp"
        else:
            output = finalFolder + name + "_ses.shp"
        arcpy.MakeFeatureLayer_management(fc, "temp")
        arcpy.SelectLayerByLocation_management("temp", 'INTERSECT', clip)
        arcpy.CopyFeatures_management("temp", output)
        print "Select by location" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 5 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


