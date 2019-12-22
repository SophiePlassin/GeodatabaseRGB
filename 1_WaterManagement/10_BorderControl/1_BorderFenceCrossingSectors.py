## Name: Border_Control.py
## Created on: 2019-07-07
## By: Sophie Plassin
## Description: Preparation of the Border Control dataset (crossing, fences and patrol sectors) for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Export feature class to geodatabase and rename
##              3. Edit attribute table (remove unecessary fields)
##              4. Join the Statistics of Apprehension to the border patrol sectors feature class
##              5. Project the datasets to North America Albers Equal Area Conic
##              6. Clip the datasets (fences and crossings)
##              7. Select by attribute (border sectors)
##              8. Recalculate geometry
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\10_border_control\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\10_border_control\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\10_border_control\\final_output\\"
arcpy.env.workspace = dirpath



## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
gdb_name = "Border.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Export Feature Class to geodatabase
## Description: Export features to the geodatabase

print "\nStep 2 Export feature to gdb starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs:
fcList = arcpy.ListFeatureClasses()

gdbList = []
outNameList = ["Border_Fences", "Border_Crossings", "Border_Sectors_raw"]

for fc in fcList:
    arcpy.FeatureClassToGeodatabase_conversion(fc, out_gdb)
    feature = fc.split(".shp")[0]
    fc_gdb = os.path.join(out_gdb, feature)
    index = fcList.index (fc)
    out_featureclass = os.path.join(out_gdb, outNameList[index])
    arcpy.Rename_management(fc_gdb, out_featureclass, data_type)
    gdbList.append(out_featureclass)


print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Edit and join attribute table
## Description: Rename and delete fields

print "\nStep 3 Edit attribute table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldsDel = ["FID_1", "Shape__Are", "Shape__Len",
             "FY2016YTD", "FY2017YTD", "FY162FY17_"]
# Delete fields
for fc in gdbList:
    arcpy.DeleteField_management(fc, fieldsDel)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Join table with feature
## Description: Join table of statistics of apprehension with the US Border Patrol Sectors feature

print "\nStep 4 Join starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Convert excel table to dbf
in_excel = "StatisticsApprehension.xlsx"
dbf_file = os.path.splitext(in_excel)[0]
joinTable = os.path.join(interFolder, dbf_file)
arcpy.ExcelToTable_conversion(in_excel, joinTable, "stats_gis")

# Fields to join
joinFieldLayer = "SEC_NAME"
joinFieldTable = "Sector"

# Fields to delete after join
fieldsDel = ["Sector", "Rowid"]

# Input
in_fc = os.path.join(out_gdb, "Border_Sectors_raw")

# Output
output = os.path.join(out_gdb, "Border_Sectors")

# Execute join
arcpy.MakeFeatureLayer_management(in_fc, "temp")
arcpy.AddJoin_management("temp", joinFieldLayer, joinTable, joinFieldTable, "KEEP_ALL")
arcpy.CopyFeatures_management("temp", output)
arcpy.DeleteField_management(output, fieldsDel)
gdbList.remove(in_fc)
gdbList.append(output)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 5. Project the polygon
## Description: Project to North America Albers Equal Area Conic

print "\nStep 5 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

projList =[]
for fc in gdbList:
    name = os.path.split(fc)[1] + '_pr'
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    projList.append (projFile)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Clip
## Description: Clip Crossing and fences for the study area.

print "\nStep 6 Clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []
for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Input name
featuresList = ["Border_Fences_pr", "Border_Crossings_pr"]
clipList = []
finalList = []
for fc in featuresList:
    out_shp = os.path.join(out_gdb, fc)
    clipList.append(out_shp)
    
# Execute Clip
for fc in clipList:
    for clip in clip_features:
        temp = os.path.split(clip)[-1]
        root = os.path.split(fc)[1]
        name = root.split('_pr')[0]
        if temp.startswith("RGB_Basin"):
            output = finalFolder + "\\" + name + "_bas.shp"
        else:
            output = finalFolder + "\\" + name + "_ses.shp"
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        finalList.append(output)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 6 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 7. Select Layer By Attribute
## Description: Select Layer By Attribute.

print "\nStep 7 Select Layer By Attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = os.path.join(out_gdb, "Border_Sectors_pr")

# BorderSector in the RGB:
# BigBend [MAR], Del Rio [DRT], El Paso [EPT], Laredo [LRT], RG Valley [MCA]

# Selection
expression = "\"SEC_CODE\" IN ('MAR', 'DRT', 'EPT', 'LRT', 'MCA')"

# Execute
arcpy.MakeFeatureLayer_management(in_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
out_feature = os.path.join(finalFolder, "Border_Sectors.shp")
arcpy.CopyFeatures_management("temp", out_feature)
finalList.append(out_feature)

print "Step 7 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## ---------------------------------------------------------------------------
## 8. Recalculate geometry and delete fields
## Description: Recalculate areas and delete fields

print "\nStep 8 Recaculate geometry starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"
fieldsDel2 = ["OBJECTID", "OBJECTID_1"]

for shp in finalList:
    arcpy.DeleteField_management(shp, fieldsDel2)
    if shp.endswith("Sectors.shp"):
        arcpy.CalculateField_management(shp, "Shape_Area", expressionArea, "PYTHON_9.3")
        arcpy.CalculateField_management(shp, "Shape_Leng", expressionLength, "PYTHON_9.3")
    if shp.endswith("Fences.shp"):
        arcpy.CalculateField_management(shp, "Shape_Leng", expressionLength, "PYTHON_9.3")
    if shp.endswith("Fences_RGB.shp"):
        arcpy.CalculateField_management(shp, "Shape_Leng", expressionLength, "PYTHON_9.3")

print "Step 8 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


