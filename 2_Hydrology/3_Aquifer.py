## Name: Aquifer.py
## Created on: 2019-04-15
## By: Sophie Plassin
## Description: Preparation of aquifer shapefiles for the Rio Grande/Bravo basin (RGB)
##              1. Project the shapefiles to North America Albers Equal Area Conic
##              2. Select by location the US and MX aquifers
##              3. Edit the attribute table
##              4. Merge US and MX aquifers shapefiles
## ---------------------------------------------------------------------------


## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set environment settings
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\5_aquifer\\original_input\\"
dirpath = arcpy.env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\5_aquifer\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\5_aquifer\\final_output\\"

# Set overwrite option
arcpy.env.overwriteOutput = True

# List
fcList = arcpy.ListFeatureClasses()
projList = []
selectList = []


## ---------------------------------------------------------------------------
## 1. Project the polygon
## Description: Project aquifer polygons to North America Albers Equal Area Conic

print "\nStep 1 Project the polygons starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Execute Project
for fc in fcList:
    projName = os.path.splitext(fc)[0] + "_pr.shp"
    projFile = os.path.join(interFolder, projName)
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")



## ---------------------------------------------------------------------------
## 2. Select by Location
## Description: Selects aquifers features that overlap the RGB.

print "\nStep 2 Select by Location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\5_aquifer\\inter_output\\"

# Create a temp layer
rgbShape = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\RGB_Ses_na_albers.shp"

arcpy.MakeFeatureLayer_management(rgbShape, "lyr_rgb")

for fc in projList:
    arcpy.MakeFeatureLayer_management(fc, "temp")
    name = os.path.split(fc)[1]
    if name.startswith("aquif"):
        output = "Aquifer_US.shp"
    else:
        output = "Aquifer_MX.shp"
    arcpy.SelectLayerByLocation_management("temp",
                                           "INTERSECT",
                                           "lyr_rgb",
                                           "",
                                           "NEW_SELECTION")
    arcpy.CopyFeatures_management("temp", output)
    selectList.append(output)
    print "Select by Location" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Clean datasets
## Description: Selects aquifers features that overlap the RGB.
    
print "\nStep 3 Clean the datasets starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# New field names for US and MX
fieldCodeCountry = "COUNTRYISO"
fieldIDAquifer = "AQ_ID"
fieldCodeRHA = "HAR_ID"
fieldNameRHA = "HAR_NAME"
fieldCodeAvail = "AVAILAB"
fieldCodeVol = "AVAIL_MCM"

# New fields for MX
fieldNameAquifer = "AQ_NAME"
fieldCodeAquifer = "AQ_CODE"
fieldNameRock = "ROCK_NAME"
fieldTypeRock = "ROCK_TYPE"

# Expression
expression1 = "!id_acuif!"
expression2 = "!OBJECTID!"
expression3 = "!AQ_CODE!"
expression4 = "!ROCK_TYPE!"
expression5 = "!AQCODE!"
expression6 = "!ROCKTYPE!"


# Type of fields
fieldTypeTx = "TEXT"
fieldTypeNb = "DOUBLE"
fieldTypeInt = "LONG"

# List fields for US and MX
fieldShText = [fieldIDAquifer, fieldCodeCountry, fieldCodeRHA]
fieldLgText= [fieldCodeAvail, fieldNameRHA]

# List fields for MX
fieldLgIntMX = [fieldCodeAquifer, fieldTypeRock]
fieldLgTxMX = [fieldNameRock, fieldNameAquifer]


for fc in selectList:
    for fn in fieldShText:
        arcpy.AddField_management(fc, fn, fieldTypeTx, "", "", "10")
    for fn in fieldLgText:
        arcpy.AddField_management(fc, fn, fieldTypeTx, "", "", "50")
    if fc.endswith("MX.shp"):    
        for fn in fieldLgIntMX:
            arcpy.AddField_management(fc, fn, fieldTypeInt)
        for fn in fieldLgTxMX:
            arcpy.AddField_management(fc, fn, fieldTypeTx, "", "", "50")
    arcpy.AddField_management(fc, fieldCodeVol, fieldTypeNb)

#Update lines
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        if fc.endswith("US.shp"):
            row.setValue(fieldCodeCountry, '840')
            row.setValue(fieldCodeAvail, "NA")
            row.setValue(fieldCodeRHA, "NA")
            row.setValue(fieldNameRHA, "NA")
        else:
            row.setValue(fieldCodeCountry, '484')
            value5 = row.getValue("nom_acuif")
            row.setValue(fieldNameAquifer, value5)
            value7 = row.getValue("id_rha")
            row.setValue(fieldNameRHA, value7)
            value8 = row.getValue("nom_rha")
            row.setValue(fieldCodeRHA, value8)
            value9 = row.getValue("dispon")
            if value9 == "Con disponibilidad":
                row.setValue(fieldCodeAvail, "Availability")
            else:
                row.setValue(fieldCodeAvail, "No Availability")
            value10 = row.getValue("disp_hm3")
            row.setValue(fieldCodeVol, value10)
            row.setValue(fieldCodeAquifer, -99)
            row.setValue(fieldNameRock, "NA")
            row.setValue(fieldTypeRock, -99)
        cur.updateRow(row)
    if fc.endswith("MX.shp"):
        arcpy.CalculateField_management(fc, fieldIDAquifer, expression1, "PYTHON_9.3")
    if fc.endswith("US.shp"):
        arcpy.CalculateField_management(fc, fieldIDAquifer, expression2, "PYTHON_9.3")

# Delete useless fields
    fieldDel = ["id_acuif", "nom_acuif", "id_edo", "nom_edo", "id_rha", "nom_rha", "dispon", "disp_hm3",
                "fecha_dof", "OBJECTID",  "Shape_len"]
    for fn in fieldDel:
        arcpy.DeleteField_management(fc,fn)
    print "Merge" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Merge US and MX aquifers shapefiles
## Description: Merge US and MX into one shapefile

print "\nStep 4 Merge US and MX aquifers shapefiles starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.Merge_management(selectList, finalFolder + "Aquifer.shp")

print "Merge US and MX aquifers shapefiles completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



print "Geoprocess ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


















    
