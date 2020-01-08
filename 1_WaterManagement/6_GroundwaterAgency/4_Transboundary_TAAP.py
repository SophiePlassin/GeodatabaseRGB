## Name: Transboundary.py
## Created on: 2019-12-10
## By: Sophie Plassin
## Description: Preparation of the datasets related to the TAAP (Transboundary Aquifer Assessment Program) for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Project the Mesilla-Conejos Medanos and Hueco Bolson to North America Albers Equal Area Conic
##              3. Add new field with the name of the aquifer
##              4. Clean the datasets
##              5. Merge the Mesilla-Conejos Medanos and Hueco Bolson datasets
##              6. Export final files
# ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import arcpy, os
import datetime

# Directories:
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\original_input\\Transboundary\\"
arcpy.env.workspace = dirpath
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\inter_output\\Transboundary\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\6_groundwater_agency\\final_output\\"


# ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a gdb to work with a table format

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, "TAAP.gdb")
gdb = os.path.join(interFolder, "TAAP.gdb")


print "Step 1. Create a geodatabase ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Project the polygons
## Description: Project features to North America Albers Equal Area Conic

print "\nStep 2. Project the polygons for the U.S. starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Define projection
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Inputs and Outputs
inputList = arcpy.ListFeatureClasses()
outputList = []

# Project
for infc in inputList:
    path, name = os.path.split(infc)
    projName = os.path.splitext(name)[0] +"_pr"
    projFile = os.path.join(gdb, projName)
    arcpy.Project_management(infc, projFile, outCS)
    print "Project", projName, "ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
    outputList.append(projFile)            

print "Step 2 Select and Project the polygons for the U.S. ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
# 3. Add new field with the name of the aquifer
## Description: Add new field with the name of the aquifer

print "\nStep 3 Add new field starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Fields to add
field_name = "Aquif_Name"

# Add fields
for fc in outputList:
    arcpy.AddField_management(fc, field_name, "TEXT", "", "", 50)

# Populate fields
    cur = arcpy.UpdateCursor(fc)
    name = os.path.split(fc)[1]
    for row in cur:
        if fc.endswith("2016_pr"):
            row.setValue(field_name, "Hueco Bolson Aquifer")
        else:
            row.setValue(field_name, "Mesilla/Conejos-Médanos Aquifer")
        cur.updateRow(row)
        
print "Step 3 Add new field ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
# 4. Clean the dataset 
## Description: Remove unecessary fields and ajust fields names.

print "\nStep 4. Clean the datasets for Mexico starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Fields to remove
dropFields = ["BasinName", "ID", "Id"]

# Remove fields

for fc in outputList:
    arcpy.DeleteField_management(fc,
                                 dropFields)

print "Step 4 Clean the datasets for Mexico ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
# 5. Merge the files
## Description: Merge the Mesilla with Hueco-Bolson polygons

print "\nStep 5. Merge the datasets starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs
Aquifer_inputs = [gdb + "\\editedMesilla_ConejosMedanos_pg_pr", gdb + "\\Hueco_Driscoll_Sherson_2016_pr"]

# Outputs
Aquifer_output = os.path.join(gdb, "TAAP_Aquifers")

arcpy.Merge_management(Aquifer_inputs, Aquifer_output)

finalList = []
finalList.append(Aquifer_output)

print "Step 5 Merge the datasets ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
## 6. Export final files and adjust fields
## Description: Export final files and adjust fields

print "\nStep 6 Export final files starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Expression Area and Length
expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"

for infc in finalList:
    name = os.path.split(infc)[1]
    final_name = name + ".shp"
    final_file = finalFolder + final_name
    arcpy.CopyFeatures_management(infc, final_file)
    arcpy.CalculateField_management(final_file, "Shape_Area", expressionArea, "PYTHON_9.3")
    arcpy.CalculateField_management(final_file, "Shape_Leng", expressionLength, "PYTHON_9.3")

print "Step 6 Export final files ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "Geoprocess ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
