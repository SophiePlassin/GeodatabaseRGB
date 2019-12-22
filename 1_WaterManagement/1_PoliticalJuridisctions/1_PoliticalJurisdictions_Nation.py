## Name: NationBoundaries.py
## Created on: 2019-12-19
## By: Sophie Plassin
## Description: Preparation of the Nation boundaries dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Dissolve polygons
##              3. Project the Nation dataset to North America Albers Equal Area Conic
##              4. Add new fields and homogeneize
##              5. Merge US and MX polygons
##              6. Delete fields
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\original_input\\Census\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
arcpy.env.workspace = dirpath


# List
fcList = ["cb_2016_us_nation_5m.shp"]
projList = []


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "Nation.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1. Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## --------------------------------------------------------------------------- 
## 2. Dissolve the polygon for Mexico
## Description: Aggregates features based on country ID.

print "\nStep 2 Dissolve the polygons starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

inFeature = "areas_geoestadisticas_estatales.shp"
outFeatureClass = os.path.join(out_gdb, "areas_geoestadisticas_estatales_dissolve")
arcpy.Dissolve_management(inFeature, outFeatureClass)
fcList.append(outFeatureClass)

print "Step 2 Dissolve the polygons completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Project the polygons
## Description: Project the Nation dataset to North America Albers Equal Area Conic

print "\nStep 3 Project the polygon starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in fcList:
    if fc.startswith("cb_2016"):
        name = "US_Boundary"
    else:
        name = "MX_Boundary"
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 Project completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Add new fields
## Description: Add new fields

print "\nStep 4 Add new fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set local variables
fieldCodeCountry = "ADM0_ID"
fieldNameCountry = "NAME_0"
fieldID = "ID_0"
fieldType = "TEXT"
fieldLength = 3

# Execute add field
for fc in projList:
    arcpy.AddField_management(fc, fieldCodeCountry, fieldType, "", "", fieldLength)
    arcpy.AddField_management(fc, fieldNameCountry, fieldType, "", "", 50)
    arcpy.AddField_management(fc, fieldID, fieldType, "", "", 4)

    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        if fc.endswith ("US_Boundary"):
            row.setValue(fieldCodeCountry, '840')
            row.setValue(fieldNameCountry, 'United States')
            row.setValue(fieldID, 'USA')

        else:
            row.setValue(fieldCodeCountry, '484')
            row.setValue(fieldNameCountry, 'Mexico')
            row.setValue(fieldID, 'MEX')
        
        cur.updateRow(row)
    print "Add field" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 4 Add new fields completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Merge into a single output feature
## Description: Merge Country shapefiles into a single output feature

out_feature = "Nations.shp"

output = os.path.join(finalFolder, out_feature)
arcpy.Merge_management(projList, output)

# 6. Delete fields
fieldDel = ["AFFGEOID", "NAME", "GEOID", "CVE_ENT", "NOM_ENT", "Shape_Leng", "Shape_Area"]
for fd in fieldDel:
    arcpy.DeleteField_management(output,fieldDel)
