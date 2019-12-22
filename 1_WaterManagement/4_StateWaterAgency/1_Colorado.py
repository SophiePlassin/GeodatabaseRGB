## Name: Colorado agencies.py
## Created on: 2019-06-30
## By: Sophie Plassin
## Description: Preparation of the Colorado state agency dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Rename and export feature class
##              3. Homogeneize fields
##              4. Project the dataset to North America Albers Equal Area Conic
##              5. Create a new feature class for Division 3 using Select by attribute
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\original_input\\CDWR\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\inter_output\\CDWR\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\final_output\\"
arcpy.env.workspace = dirpath

# Set overwrite option
arcpy.env.overwriteOutput = True


# List
featuresList = []
projList = []


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

featuresList.append("DIV3CO.shp")

root = "Div3_Boundaries.mdb\\Water Management Boundaries\\"
features = ["div3_districts"]
for fc in features:
    in_fc = root + fc
    featuresList.append(in_fc)

out_name = "Div3_Boundaries.gdb"
out_gdb = interFolder + out_name

#Execute
arcpy.CreateFileGDB_management(interFolder, out_name)
arcpy.FeatureClassToGeodatabase_conversion(featuresList, out_gdb)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Rename and export feature class
## Description: Rename feature class

print "\nStep 2 Rename and export feature class starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

listGdb =  ["div3_districts", "DIV3CO"]
data_type = "FeatureClass"
fieldName = "STATE_AGEN"
fieldAlias = 'STATE_AGENCY'
fieldType = "TEXT"
fieldsDel = ["AREA", "PERIMETER"]
newFiles =[]

for fc in listGdb:
    fc_gdb = os.path.join(out_gdb, fc)
    fieldList = arcpy.ListFields(fc_gdb)  #get a list of fields for each feature class
    for field in fieldList: #loop through each field
        if field.name == 'DIV':  #look for the name div and rename
            arcpy.AlterField_management(fc_gdb, field.name, 'CDWR_DIV', 'CDWR_DIV')
        if field.name == 'DIST':  #look for the name dist and rename
            arcpy.AlterField_management(fc_gdb, field.name, 'CDWR_DIST', 'CDWR_DIST')
    if fc.endswith("districts"):
        out_data = os.path.join(out_gdb,"CDWR_" + fc)
    else:
        out_data = os.path.join(out_gdb,"CDWR_divisions")
    arcpy.Rename_management(fc_gdb, out_data, data_type)
    newFiles.append(out_data)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Add and delete fields
## Description: Add and delete fields

print "\nStep 3 Add and delete fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in newFiles:
    arcpy.AddField_management(fc, fieldName, fieldType, "", "", 75, fieldAlias)

#Update lines
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        row.setValue(fieldName, 'CDWR')       
        cur.updateRow(row)
    arcpy.FeatureClassToShapefile_conversion(fc, interFolder)
    arcpy.DeleteField_management(fc, fieldsDel)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Project the polygon and calculate new area
## Description: Project to North America Albers Equal Area Conic

print "\nStep 4 Projection starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"

for infc in newFiles:
    name = os.path.split(infc)[1] + ".shp"
    projFile = os.path.join(finalFolder, name)
    arcpy.Project_management(infc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    arcpy.CalculateField_management(projFile, "Shape_Area", expressionArea, "PYTHON_9.3")
    arcpy.CalculateField_management(projFile, "Shape_Leng", expressionLength, "PYTHON_9.3")
    projList.append(projFile)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Create a feature class for Division 3
## Description: Select by attribute

print "\nStep 5 Select by attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_feature = os.path.join(finalFolder, "CDWR_divisions.shp")

expression = "\"CDWR_DIV\" = 3"
arcpy.MakeFeatureLayer_management(in_feature, "temp")
arcpy.SelectLayerByAttribute_management("temp",
                                       "NEW_SELECTION",
                                       expression)
output = os.path.join(finalFolder, "CDWR_div3.shp")
arcpy.CopyFeatures_management("temp", output)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


