## Name: Transboundary.py
## Created on: 2019-12-10
## By: Sophie Plassin
## Description: Preparation of the datasets related to the TAAP (Transboundary Aquifer Assessment Program) for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. For the U.S.: Select the aquifers (Mesilla and Hueco-Bolson) and Project
##              3. For the U.S.: Add new field
##              4. For Mexico: Select the aquifers (Conejos - Medanos and Valle de Juarez) and split by attributes
##              5. For Mexico: Clean the outputs
##              6. Merge U.S. and MX datasets
##              7. Export final files and adjust fields
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
## 2. Select and Project the polygons for the U.S.
## Description: Select the polygons Mesilla and Hueco-Bolson
##              Project features to North America Albers Equal Area Conic

print "\nStep 2. Select and Project the polygons for the U.S. starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Define projection
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Inputs and Outputs
longpath = "\\sir2013-5079_Groundwater_Depletion_Study_Files\\database\\aquifers\\"
inputList = ["MesillaBasin.shp", "HuecoBolson.shp"]
outputList = []

# Project
for infc in inputList:
    aquifer = longpath + infc
    path, name = os.path.split(aquifer)
    projName = os.path.splitext(name)[0] +"_pr"
    projFile = os.path.join(gdb, projName)
    arcpy.Project_management(aquifer, projFile, outCS)
    print "Project", projName, "ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
    outputList.append(projFile)            

print "Step 2 Select and Project the polygons for the U.S. ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
# 3. Add new field for the U.S. files
## Description: Add new field for the U.S. files

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
        aquif_id = row.getValue("aquif_id")
        if aquif_id == "wab_mesbas":
            row.setValue(field_name, "Mesilla Aquifer")
        if aquif_id == "wab_hb":
            row.setValue(field_name, "Hueco Bolson Aquifer")
        cur.updateRow(row)
        
print "Step 3 Add new field ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
# 4. Select the polygons for Mexico and split by attribute
## Description: Select the polygons Conejos - Medanos and Valle de Juarez

print "\nStep 4. Select the polygons for Mexico starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input and output
infc = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\5_aquifer\\final_output\\Aquifer.shp"
outfc = os.path.join(gdb, "MX_aquifers")


# Expression
# Aquifer ID: Conejos - Medanos: 823
# Aquifer ID: Valle de Juarez: 833

expression = """"AQ_ID" IN ('823', '833')"""

# Select polygons with AQ_NAME = Conejos - Medanos; Valle de Juarez
arcpy.MakeFeatureLayer_management(infc, "temp") 
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", outfc)

# Split by attribute
fields = ["AQ_NAME"]
arcpy.SplitByAttributes_analysis(outfc, gdb, fields)

print "Step 4 Select the polygons ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
# 5. Clean the dataset for Mexico 
## Description: Remove unecessary fields and ajust fields names.

print "\nStep 5. Clean the datasets for Mexico starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# Fields to remove
dropFields = ["COUNTRYISO", "HAR_ID", "AVAILAB", "HAR_NAME", "AQ_CODE", "ROCK_TYPE", "ROCK_NAME", "AVAIL_MCM"]

# Fields to altere (lentgh <= 10 characters)
alterFields= [["AQ_NAME",     "Aquif_Name"],
              ["AQ_ID",          "map_id"]]

# Remove and Alter fields
listMX = [gdb + "\\Conejos___Medanos", gdb + "\\Valle_de_Juarez"]
for fc in listMX:
    arcpy.DeleteField_management(fc,
                                 dropFields)
    for old, new in alterFields:
        tmpName = ("{0}_tmp".format(old))
        arcpy.AlterField_management(fc, old, tmpName)
        arcpy.AlterField_management(fc, tmpName, new)


print "Step 5 Clean the datasets for Mexico ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
# 6. Merge the U.S. and MX files
## Description: Merge the Mesilla polygo (U.S.) with the 'Conejos - Medanos' polygon (MX)
##              Merge the Hueco-Bolson (U.S.) with the Valle de Juarez (MX)

print "\nStep 6. Merge the datasets for Mexico starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs
Mesilla_Inputs = [gdb + "\\MesillaBasin_pr", gdb + "\\Conejos___Medanos"]
Hueco_Inputs = [gdb + "\\HuecoBolson_pr", gdb + "\\Valle_de_Juarez"]

# Outputs
Mesilla_output = os.path.join(gdb, "Mesilla_Conejos_Medanos")
Hueco_output = os.path.join(gdb,"Hueco_Bolson_Juarez")

arcpy.Merge_management(Mesilla_Inputs, Mesilla_output)
arcpy.Merge_management(Hueco_Inputs, Hueco_output)

finalList = []
finalList.extend([Mesilla_output, Hueco_output])

print "Step 6 Merge the datasets ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
## 7. Export final files and adjust fields
## Description: Export final files and adjust fields

print "\nStep 7 Export final files starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# fields to delete
fieldsDel = ["Shape_Le_1"]

# Expression Area and Length
expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"

for infc in finalList:
    name = os.path.split(infc)[1]
    if "Mesilla" in name:
        name = "MesillaConejosMedanos"
    else:
        name = "HuecoBolsonJuarez"
    final_name = "TAAP_" + name + ".shp"
    final_file = finalFolder + final_name
    arcpy.CopyFeatures_management(infc, final_file)
    arcpy.DeleteField_management(final_file, fieldsDel)
    arcpy.CalculateField_management(final_file, "Shape_Area", expressionArea, "PYTHON_9.3")
    arcpy.CalculateField_management(final_file, "Shape_Leng", expressionLength, "PYTHON_9.3")

print "Step 7 Export final files ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




print "Geoprocess ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
