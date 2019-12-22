## Name: Consejo de Cuenca del Rio Bravo.py
## Created on: 2019-07-06
## By: Sophie Plassin
## Description: Preparation of the Consejo de Cuenca del Rio Bravo outline
##              1. Create a geodatabase
##              2. Select by attribute the outline of the Consejo de Cuenca del Rio Bravo
##              3. Homogeneize fields
##              4. Project the dataset to North America Albers Equal Area Conic            
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\original_input\\MX\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\inter_output\\MX\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\final_output\\"
arcpy.env.workspace = dirpath

# Set overwrite option
arcpy.env.overwriteOutput = True



## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = "rha250kgw.shp"
# Output name
gdb_name = "WS_Council.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------    
## 2. Select by attributes and export to the geodatabase
## Description: Select the Consejo de Cuenca Rio Bravo from the consejos de cuenca dataset for MX, based on its name (ID), using Select Layer By Attribute

print "\nStep 2 Select Layer by Attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output name
outname = "MX_Consejo_Cuenca"
# Selection
expression = "\"CLAVE\" = 6"
# Execute
arcpy.MakeFeatureLayer_management(in_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
out_fc = os.path.join(out_gdb, outname)
arcpy.CopyFeatures_management("temp", out_fc)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------    
## 3. Homogeneize fields
## Description: Translate from Spanish to English

print "\nStep 3 Homogeneize fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Rename fields
fieldList = arcpy.ListFields(out_fc)
for field in fieldList:
    if field.name == 'CLAVE':
        arcpy.AlterField_management(out_fc, field.name, 'HAR_ID', 'HAR_ID')
    if field.name == 'ORG_CUENCA':
        arcpy.AlterField_management(out_fc, field.name, 'WS_COUNCIL', 'WS_COUNCIL')
    if field.name == 'CLV_OC':
        arcpy.AlterField_management(out_fc, field.name, 'HAR_ID2', 'HAR_ID2')
        
# Remove fields
fieldsDel = ["COV_", "COV_ID", "AREA", "PERIMETER"]
for fd in fieldsDel:
    arcpy.DeleteField_management(out_fc,fieldsDel)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------    
## 4.  Project the polygon and calculate new area
## Description: Project to North America Albers Equal Area Conic
##              Recalculate area and perimeter
    
print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"

name = os.path.split(out_fc)[1] + ".shp"
projFile = os.path.join(finalFolder, name)
arcpy.Project_management(out_fc, projFile, outCS)
print "Projection" , out_fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

arcpy.CalculateField_management(projFile, "Shape_Area", expressionArea, "PYTHON_9.3")
arcpy.CalculateField_management(projFile, "Shape_Leng", expressionLength, "PYTHON_9.3")
fieldDel = ["OBJECTID"]
arcpy.DeleteField_management(projFile, fieldDel)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

