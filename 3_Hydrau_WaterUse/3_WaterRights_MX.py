## Name: WaterRights_Mexico.py
## Created on: 2018-11-29
## U[date on: 2019-08-04
## By: Sophie Plassin
## Description: Preparation of the water right shapefile for Mexico, Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase and save files into it
##              2. Project features to North America Albers Equal Area Conic
##              3. Clip features to the boundaries of the study area
##              4. Convert the clip files to csv
##              5. Make XY event layer to geolocate WR location
##              6. Merge the state datasets
##              7. Standardize datasets
##              8. Select points within a distance
##              9. Split layer by attribute
## ---------------------------------------------------------------------------

## HOW TO RUN THIS CODE ##
## Run steps 1 to 4 as a stand-alone script commenting all other steps after 4
## Run the script cleaning the dataset with Jupyter Pandas (3_WaterRights_MX_2_Clean_Data_Jupyter_Pandas)
## Run the code from step 5 as a stand-alone script, using the inputs datasets from the cleaning step

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\original_input\\MX\\"
dirpath = arcpy.env.workspace

# Options
arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

# Directories
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\inter_output\\MX\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\final_output\\"

## ---------------------------------------------------------------------------
## 1. Create a geodatabase and save files into it
## Description: Convert all KMZ and KML files found in the current workspace

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for kmz in arcpy.ListFiles('*.KM*'):
    arcpy.KMLToLayer_conversion(kmz, interFolder)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Project features
## Description: Project features to North America Albers Equal Area Conic

print "\nStep 2 Project features starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

arcpy.env.workspace = interFolder

# Loop through all the FileGeodatabases within the workspace
wks = arcpy.ListWorkspaces('*', 'FileGDB')

for fgdb in wks:
    for root, dirs, datasets in arcpy.da.Walk(fgdb):
        oPath, oExt = os.path.split (root)
        if oExt.endswith('gdb'):
            tail = oExt.split('.gdb')[0]
        for ds in datasets:
            in_fc = os.path.join(fgdb, 'Placemarks', ds)
            projFile = os.path.join(fgdb, 'Placemarks', tail + "_" + ds + '_pr')
            arcpy.Project_management(in_fc,
                                     projFile,
                                     outCS)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Clip features
## Description:  Clip features to the boundaries of the study area

print "\nStep 3 Clip features starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
            
clip_feature = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\RGB_Basin_pr.shp"
xy_tolerance = ""
for fgdb in wks:
    for root, dirs, datasets in arcpy.da.Walk(fgdb):
        for ds in datasets:
            if ds.endswith('_pr'):
                projFile = os.path.join(fgdb, 'Placemarks', ds)
                clipFile = os.path.join(fgdb, 'Placemarks', ds.split('_pr')[0] + '_cl')
                arcpy.Clip_analysis(projFile,
                                    clip_feature,
                                    clipFile,
                                    xy_tolerance)


txtLocation = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\inter_output\\MX\\Text"

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 4. Convert to .csv
## Description: Convert clipped features to csv files

print "\nStep 4 Convert to csv starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fgdb in wks:
    for root, dirs, datasets in arcpy.da.Walk(fgdb):
        for ds in datasets:
            if ds.endswith('_cl'):
                in_fc = os.path.join(fgdb, 'Placemarks', ds)
                txt_file = ds + '.txt'
                arcpy.TableToTable_conversion(in_fc,
                                              txtLocation,
                                              txt_file)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## Between 4 and 5, clean the data using code of Jupyter/Pandas and manually in Excel


## ---------------------------------------------------------------------------
## 5. Generate XY Layer event 
## Description: Creates a new point feature layer based on x- and y-coordinates defined in a source table.

print "\nStep 5 Generate XY Layer event starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\inter_output\\MX\\"

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

xlsFiles = arcpy.ListFiles("*_prepared.xlsx")
x_coords = "LONG_DD"
y_coords = "LAT_DD"
mergeList = []
finalList = []

# Execute Excel to Dbf table
for xls in xlsFiles:
    dbf_file = os.path.splitext(xls)[0] + ".dbf"
    arcpy.ExcelToTable_conversion(xls,
                                  dbf_file)

# Make the XY event layer
    nameLayer = os.path.splitext(dbf_file)[0]
    outLayer = nameLayer.split("_prepared")[0] + "_points"
    arcpy.MakeXYEventLayer_management(dbf_file,
                                      x_coords,
                                      y_coords,
                                      outLayer)

# Save to a layer file
    saved_Layer = outLayer + ".lyr"
    arcpy.SaveToLayerFile_management(outLayer,
                                     saved_Layer)
    
# Create Shapefile
    shape = saved_Layer.split("_points.lyr")[0] + ".shp"
    arcpy.CopyFeatures_management(saved_Layer,
                                  shape)

# Project
    projFile = os.path.splitext(shape)[0] + '_pr.shp'
    arcpy.Project_management(shape, projFile, outCS)
    if ("SW_WaterRights") in projFile:
        finalList.append(projFile)
    else:
        mergeList.append(projFile)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------      
## 6. Merge the GW state datasets into one feature class
## Description: Merge the state datasets into one shapefile 

print "\nStep 6 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

mergeFile = "MX_GW_WaterRights_pr.shp"

arcpy.Merge_management(mergeList,
                       mergeFile)

finalList.append(mergeFile)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 7. Homogeneize attribute tables datasets
## Description: Add and populate fields for State, Municipio, basin and aquifer ID

print "\nStep 7 Standardize datasets starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# New fields
stateID = "ADM1_GEOID"
municipioID = "ADM2_GEOID"
source = "WR_SOURCE"
aqui_id = "AQUI_ID"
aqui_nm = "AQUI_NAME"
basin_id = "BASIN_ID"
ABV = "ABV"

fieldType = "TEXT"

fieldsAdd = [stateID, municipioID, source, ABV]
fieldsDel = ["STATE", "MUNICIP", "OID_"]

## Add new field State ID, Municipio, basin and aquifer ID WR_Source
## For WR_Source and add the type of water source (Surface or groundwater)
for fc in finalList:
    for fd in fieldsAdd:
        arcpy.AddField_management(fc,
                                  fd,
                                  fieldType,
                                  "",
                                  "",
                                  10)
    if "SW" in fc:
        arcpy.AddField_management(fc, aqui_id, "LONG")
        arcpy.AddField_management(fc, aqui_nm, fieldType, "","", 100)
    else:
        arcpy.AddField_management(fc, basin_id, "LONG")

    # Use title format for values of "USE" and "AQUI_NAME"
    arcpy.CalculateField_management(fc, "USE", "!USE!.title()", "PYTHON_9.3")
    arcpy.CalculateField_management(fc, "AQUI_NAME", "!AQUI_NAME!.title()", "PYTHON_9.3")
    cur = arcpy.UpdateCursor(fc)
    
    # Update values in new fields
    for row in cur:
        value1 = row.getValue("STATE") # State
        if value1 < 10:
            row.setValue(stateID, '484' + '0' + str(value1))
        else:
            row.setValue(stateID, '484' + str(value1))
        if value1 == 5:
            row.setValue(ABV, "COA")
        elif value1 == 8:
            row.setValue(ABV, "CHI")
        elif value1 == 10:
            row.setValue(ABV, "DUR")
        elif value1 == 19:
            row.setValue(ABV, "NVL")
        elif value1 == 28:
            row.setValue(ABV, "TAM")
        cur.updateRow(row)
        value2 = row.getValue("MUNICIP") # Municipio
        value3 = row.getValue(stateID)
        if value2 < 10:
            row.setValue(municipioID, value3 + '00' + str(value2))
        elif value2 < 100:
            row.setValue(municipioID, value3 + '0' + str(value2))
        if "SW" in fc:
            row.setValue(source, "SW") # Type of WR_SOURCE
            row.setValue(aqui_id, -99)
            row.setValue(aqui_nm, "NA")            
        else:
            row.setValue(source, "GW")
            row.setValue(basin_id, -99)
        cur.updateRow(row)
    arcpy.DeleteField_management(fc,
                                 fieldsDel)
    

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------        
## 8. Merge SW and GW files
## Description: Save shapefile into final folder 

print "\nStep 8 Merge datasets starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output
mergeFile = os.path.join(interFolder, "MX_WaterRights.shp")

arcpy.Merge_management(finalList,
                       mergeFile)

print "Step 8 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 9. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 9 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Files
gdb_name = "Distance.gdb"
data_type = "FeatureClass"
arcpy.CreateFileGDB_management(interFolder, gdb_name)
out_gdb = os.path.join(interFolder, gdb_name)

print "Step 9 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------        
## 10. Select by location
## Description: Lots of WR points are out of the boundaries of MX.
## This script aims to select all points that are located within a distance of 2 km along the border

print "\nStep 10 Select by location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

def select_by_location(in_fc, target_fc, distance, out_fc):
    arcpy.MakeFeatureLayer_management(in_fc, "temp")
    arcpy.SelectLayerByLocation_management("temp",
                                           "WITHIN_A_DISTANCE",
                                           target_fc,
                                           distance,
                                           "NEW_SELECTION")
    arcpy.CopyFeatures_management("temp", out_fc)
    return out_fc

def select_by_attribute(in_fc, expression):
    arcpy.MakeFeatureLayer_management(in_fc, "temp_lyr")
    arcpy.SelectLayerByAttribute_management("temp_lyr", 'NEW_SELECTION', expression)
    return "temp_lyr"

# Input
Nation = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\Nations.shp"

# Output
name = os.path.splitext(mergeFile)[0]
output_name = os.path.split(name)[1] + "_distance"
output = os.path.join(out_gdb, output_name)

# Create a temp feature for Mexico
mexico = select_by_attribute(Nation, "\"ADM0_ID\" = '484'")
select_by_location(mergeFile, mexico, "2 Kilometers", output)

print "Step 10 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------        
## 11. Split By Attributes and Rename dataset
## Description: Split the dataset by state.

print "\nStep 11 Split by attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fields = [ABV]
arcpy.SplitByAttributes_analysis(output, finalFolder, fields)

arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\3_waterRights\\final_output\\"

list_fc = ["COA.shp", "CHI.shp", "DUR.shp", "NVL.shp", "TAM.shp"]

arcpy.Delete_management("T.shp")

for fc in list_fc:
    name = os.path.splitext(fc)[0]
    arcpy.Rename_management(fc, name + "_WaterRights")


print "Step 11 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "Geoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

