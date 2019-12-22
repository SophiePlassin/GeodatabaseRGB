## Name: Colorado Groundwater Agencies (RGWCD, subdistricts).py
## Created on: 2019-06-30
## By: Sophie Plassin
## Description: Preparation of the CO Groundwater Agencies dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Rename and export feature class
##              3. Homogeneize fields
##              4. Merge subdistricts files.
##              5. Project the dataset to North America Albers Equal Area Conic
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\original_input\\CO\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\inter_output\\CO\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\final_output\\"
arcpy.env.workspace = dirpath


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
fcList = ["ClosedBasinBoundary.shp", "District_Boundary.shp", "SD2_Boundary.shp",
          "SD3_Boundary.shp", "SD4_Boundary.shp", "SD5_Boundary.shp", "SD6_Boundary.shp",
         "Subdistrict_1_bndry2006Mar_polygon.shp"]
gdb_name = "RGWCD.gdb"

# Output name
out_gdb = os.path.join(interFolder, gdb_name)

# Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)


## ---------------------------------------------------------------------------
## 2. Rename and export feature class
## Description: Rename feature class

print "\nStep 2 Rename and export feature class starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdbList =[]
outNameList = ["CO_ClosedBasin_bound", "CO_RGWCD_bound", "SD2_bound", "SD3_bound", "SD4_bound",
               "SD5_bound", "SD6_bound", "SD1_bound"]
data_type = "FeatureClass"

# Execute
for fc in fcList:
    arcpy.FeatureClassToGeodatabase_conversion(fc, out_gdb)
    feature = fc.split(".shp")[0]
    fc_gdb = os.path.join(out_gdb, feature)
    index = fcList.index(fc)
    out_featureclass = os.path.join(out_gdb, outNameList[index])
    arcpy.Rename_management(fc_gdb, out_featureclass, data_type)
    gdbList.append(out_featureclass)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Homogeneize fields
## Description: Add and delete fields

print "\nStep 3 Add and delete fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldHectare = "HECTARES"
field_ID = "SD_ID"
fieldName = "Name"
newFields = [field_ID, fieldName]
fieldTypeNb = "FLOAT"
fieldTypeTx = "TEXT"
fieldsDel = ["FID_COUNTI", "SQ_MI", "CO_FIPS", "SHAPE_Leng"]

finalList =[]
mergeList = []

for in_fc in gdbList:
    arcpy.DeleteField_management(in_fc, fieldsDel)
    if in_fc.endswith("RGWCD_bound"):
        arcpy.AddField_management(in_fc, fieldHectare, fieldTypeNb)
        arcpy.CalculateField_management(in_fc, fieldHectare, "!ACRES! * 0.404686", "PYTHON_9.3")
        finalList.append(in_fc)
    elif in_fc.endswith("ClosedBasin_bound"):
        finalList.append(in_fc)       
    else:
        for x in newFields:
            arcpy.AddField_management(in_fc, x, fieldTypeTx, "", "", 50)
        cur = arcpy.UpdateCursor(in_fc)
        for row in cur:
            if in_fc.endswith("SD1_bound"):
                row.setValue(field_ID, '1')
                row.setValue(fieldName, 'Closed Basin Subdistrict')
            elif in_fc.endswith("SD2_bound"):
                row.setValue(field_ID, "2")
                row.setValue(fieldName, 'Rio Grande Alluvial Subdistrict')
            elif in_fc.endswith("SD3_bound"):
                row.setValue(field_ID, "3")
                row.setValue(fieldName, 'Conejos Subdistrict')
            elif in_fc.endswith("SD4_bound"):
                row.setValue(field_ID, "4")
                row.setValue(fieldName, 'San Luis Creek Subdistrict')
            elif in_fc.endswith("SD5_bound"):
                row.setValue(field_ID, "5")
                row.setValue(fieldName, 'Saguache Subdistrict')
            elif in_fc.endswith("SD6_bound"):
                row.setValue(field_ID, "6")
                row.setValue(fieldName, 'Alamosa La Jara Subdistrict')
            cur.updateRow(row)
        mergeList.append(in_fc)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 4. Merge subdistricts files
## Description: Merge the subdistricts in one file

print "\nStep 4 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output
mergeName = "CO_Subdistricts_bound"
mergeFile = os.path.join(out_gdb, mergeName)
#Execute
arcpy.Merge_management(mergeList, mergeFile)
finalList.append(mergeFile)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Project the polygon and calculate new area
## Description: Project to North America Albers Equal Area Conic

print "\nStep 5 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Expression for area and perimeter
expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"
# Fields to remove
fieldsDel2 = ["ACRES", "Id", "Area", "COUNTY", "OBJECTID", "TNMID",
              "METASOURCE", "SOURCEDATA", "SOURCEORIG", "SOURCEFEAT",
              "COV_", "COV_ID", "NOMBRE", "DESCRIPCI", "TIPO"]

for in_fc in finalList:
    name = os.path.split(in_fc)[1] + ".shp"
    projFile = os.path.join(finalFolder, name)
    arcpy.Project_management(in_fc, projFile, outCS)
    print "Projection" , out_featureclass, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    arcpy.CalculateField_management(projFile, "Shape_Area", expressionArea, "PYTHON_9.3")
    arcpy.CalculateField_management(projFile, "Shape_Leng", expressionLength, "PYTHON_9.3")
    arcpy.DeleteField_management(projFile, fieldsDel2)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




