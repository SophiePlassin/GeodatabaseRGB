## Name: RGWCD Wells.py
## Created on: 2019-07-06
## By: Sophie Plassin
## Description: Preparation of the RGWCD Wells dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Convert KMZ to Layers
##              3. Rename and export feature layers to geodatabase
##              4. Edit attribute table
##              5. Convert excel files with USGS links to dbf
##              6. Join dbf table with USGS links to well layers
##              7. Project the dataset to North America Albers Equal Area Conic
##              8. Merge and Save to final Location
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

# Set options
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\original_input\\CO\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\inter_output\\CO\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\final_output\\"
arcpy.env.workspace = dirpath

# List
gdbList =[]


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
gdb_name = "RGWCD_Wells.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Export KMZ files as layers in new geodatabases
## Description: Convert all KMZ found in the current workspace

print "\nStep 2 Export KMZ files starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for kmz in arcpy.ListFiles('*.KM*'):
    arcpy.KMLToLayer_conversion(kmz, interFolder)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Export feature class
## Description: Export feature class in the geodatabase

print "\nStep 3 Rename and export feature class starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.env.workspace = interFolder


# Loop through all the FileGeodatabases within the workspace
wks = arcpy.ListWorkspaces('*Confined*', 'FileGDB')

for fgdb in wks:
    for root, dirs, datasets in arcpy.da.Walk(fgdb):
        oPath, oExt = os.path.split(root)
        if oExt.endswith('gdb'):
            tail = oExt.split('.gdb')[0]
        for ds in datasets:
            in_fc = os.path.join(fgdb, 'Placemarks', ds)
            output = os.path.join(out_gdb, "CO_RGWCD_" + tail)
            arcpy.CopyFeatures_management(in_fc,
                                          output)
            gdbList.append(output)     

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 4. Edit attribute table
## Description: Rename and delete fields

print "\nStep 4 Edit attribute table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Fields to delete
fieldsDel = ["FolderPath", "SymbolID", "AltMode", "Base", "Snippet", "PopupInfo", "HasLabel", "LabelID"]

for fc in gdbList:
    arcpy.AddField_management(fc, "Type", "TEXT")
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        if fc.endswith("Unconfined"):
            row.setValue("Type", 'UnConfined Well')
        else:
            row.setValue("Type", 'Confined Well')
        cur.updateRow(row)
    arcpy.DeleteField_management(fc, fieldsDel)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 5. Convert excel files to dbf
## Description: Convert excel files (with USGS links) to dbf

print "\nStep 5 Convert excel files to dbf starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

xlsfiles = ["RGWCD_confined.xlsx", "RGWCD_unconfined.xlsx"]

for xl in xlsfiles:
    in_file = os.path.join(dirpath, xl)
    if xl.startswith("RGWCD_confined"):
        dbf_file = "RGWCD_confined.gdb"
    if xl.startswith("RGWCD_unconfined"):
        dbf_file = "RGWCD_unconfined.gdb"
    out_file = os.path.join(interFolder, dbf_file)
    arcpy.ExcelToTable_conversion(in_file, out_file)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 6. Join table with USGS links to layer
## Description: Join table to layer

print "Step 6 Join table to layer completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

layerTemp = "temp"
joinFieldLayer = "Name" 
joinFieldTable = "Name"
fieldsDel2 = ["Name_1", "OID"]
newList =[]

for fc in gdbList:
    arcpy.MakeFeatureLayer_management(fc, layerTemp)
    if fc.endswith ("Unconfined") :
        joinTable = os.path.join(interFolder, "RGWCD_unconfined.dbf")
    else:
        joinTable = os.path.join(interFolder, "RGWCD_confined.dbf")
    arcpy.AddJoin_management(layerTemp, joinFieldLayer, joinTable, joinFieldTable, "KEEP_ALL")
    newFile = os.path.join(out_gdb, fc + "_cl")  
    arcpy.CopyFeatures_management(layerTemp, newFile)
    arcpy.DeleteField_management(newFile, fieldsDel2)
    newList.append(newFile)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 7. Project the polygon and calculate new area
## Description: Project to North America Albers Equal Area Conic

print "\nStep 7 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

projList =[]

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in newList:
    root = os.path.split(fc)[1]
    name = root.split('_cl')[0] + '_pr'
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    projList.append(projFile)

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 8. Merge and Save to final Location
## Description: Merge RGWCD_unconfined and RGWCD_confined in one file

print "\nStep 8 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

mergeFile = os.path.join(finalFolder, "CO_RGWCD_Wells.shp")
arcpy.Merge_management(projList, mergeFile)

print "Step 8 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



