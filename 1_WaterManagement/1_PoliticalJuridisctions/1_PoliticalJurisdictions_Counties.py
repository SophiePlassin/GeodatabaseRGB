## Name: CountiesBoundaries.py
## Created on: 2019-08-07
## By: Sophie Plassin
## Description: Preparation of the State boundaries dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Select counties in the RGB States
##              3. Add new fields and Homogeneize the fields
##              4. Project the datasets to North America Albers Equal Area Conic
##              5. Merge US and MX polygons
##              6. Select by location the counties/municipios in the study area
##              7. Export final output
## ---------------------------------------------------------------------------


## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\original_input\\Census"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
arcpy.env.workspace = dirpath


# Set options
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

# List
selectList = []
projList = []
mergeList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "Counties.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1. Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Select by Attribute
# The script selects the counties in the state of Colorado (08), New Mexico (35), Texas (48),
# and Coahuila (05), Chihuahua (08), Durango (10), Nuevo Leon (19), Tamaulipas (28)
# and make a new shapefile

print "\nStep 2 Select Counties starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# Inputs
filesList = ["tl_2016_us_county.shp", "areas_geoestadisticas_municipales.shp"]

# Set Local variables:
expressionUS = "\"STATEFP\" IN ('08', '35' , '48')"
expressionMX = "\"CVE_ENT\" IN ('05', '08', '10', '19', '28')"

#Execute Selection
for fc in filesList:
    arcpy.MakeFeatureLayer_management(fc, "temp") 
    if fc.endswith("2016_us_county.shp"):
        arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expressionUS)
        outputUS = "Counties_US"
        output = os.path.join(out_gdb, outputUS)
        arcpy.CopyFeatures_management("temp", output)
    else:
        arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expressionMX)
        outputMX = "Counties_MX"
        output = os.path.join(out_gdb, outputMX)
        arcpy.CopyFeatures_management("temp", output)
    selectList.append(output)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Edit Attibute table for US AND MEXICO:
# The script adds new fields (name of the state, ID...) and homogeneize the values for the counties'ID and the states'ID.
# Remove also not important fields

print "\nStep 3 Edit Attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# Set local variables
fieldType = "TEXT"
fieldCodeCountry = "ADM0_ID"
fieldCountryName = "NAME_0"
fieldAbrevC = "ID_0"
fieldCodeState = "ADM1_ID"
fieldStateName = "NAME_1"
fieldAbrevS = "ID_1"
stateGEOID = "ADM1_GEOID"
fieldCodeCounty = "ADM2_ID"
fieldNameCounty = "NAME_2"
fieldCodeIso = "ADM2_GEOID"
expression = "!ADM0_ID!+!ADM1_ID!"

fieldCodeStateISO = "STATEGEOID"

expression1 = "!ADM0_ID!+!ADM1_ID!"
expression2 = "!ADM0_ID!+!ADM1_ID!+!ADM2_ID!"

# Add fields and 
for infc in selectList:
    arcpy.AddField_management(infc, fieldCodeCountry, fieldType, "", "", 3)
    arcpy.AddField_management(infc, fieldCountryName, fieldType, "", "", 50)
    arcpy.AddField_management(infc, fieldAbrevC, fieldType, "", "", 3)
    arcpy.AddField_management(infc, fieldCodeState, fieldType, "", "", 3)
    arcpy.AddField_management(infc, fieldStateName, fieldType, "", "", 50)
    arcpy.AddField_management(infc, fieldAbrevS, fieldType, "", "", 3)
    arcpy.AddField_management(infc, stateGEOID, fieldType, "", "", 5)
    arcpy.AddField_management(infc, fieldCodeCounty, fieldType, "", "", 5)
    arcpy.AddField_management(infc, fieldNameCounty, fieldType, "", "", 75)
    arcpy.AddField_management(infc, fieldCodeIso, fieldType, "", "", 10)

#Update lines
    cur = arcpy.UpdateCursor(infc)
    for row in cur:
        if infc.endswith("US"):
            row.setValue(fieldCodeCountry, '840')
            row.setValue(fieldAbrevC, 'USA')
            row.setValue(fieldCountryName, 'United States')
            value2 = row.getValue("STATEFP")
            row.setValue(fieldCodeState, value2)
            if value2 == '08':
                row.setValue(fieldStateName, 'Colorado')
                row.setValue(fieldAbrevS, 'CO')
            if value2 == '35':
                row.setValue(fieldStateName, 'New Mexico')
                row.setValue(fieldAbrevS, 'NM')
            if value2 == '48':
                row.setValue(fieldStateName, 'Texas')
                row.setValue(fieldAbrevS, 'TX')
            value3 = row.getValue("COUNTYFP")
            row.setValue(fieldCodeCounty, value3)
            value3a = row.getValue ("NAME")
            row.setValue(fieldNameCounty, value3a)
           
        else:
            row.setValue(fieldCodeCountry, '484')
            row.setValue(fieldCountryName, 'Mexico')
            row.setValue(fieldAbrevC, 'MEX')
            value4 = row.getValue("NOM_MUN")
            row.setValue(fieldNameCounty, value4)
            value5 = row.getValue("CVE_ENT")
            row.setValue(fieldCodeState, value5)
            if value5 == '05':
                row.setValue(fieldStateName, 'Coahuila de Zaragoza')
                row.setValue(fieldAbrevS, 'COA')
            if value5 == '08':
                row.setValue(fieldStateName, 'Chihuahua')
                row.setValue(fieldAbrevS, 'CHI')
            if value5 == '10':
                row.setValue(fieldStateName, 'Durango')
                row.setValue(fieldAbrevS, 'DUR')
            if value5 == '19':
                row.setValue(fieldStateName, 'Nuevo Leon')
                row.setValue(fieldAbrevS, 'NVL')
            if value5 == '28':
                row.setValue(fieldStateName, 'Tamaulipas')
                row.setValue(fieldAbrevS, 'TAM')
            value6 = row.getValue("CVE_MUN")
            row.setValue(fieldCodeCounty, value6)
            value6a = row.getValue("NOM_MUN")
            row.setValue(fieldNameCounty, value6a)
        cur.updateRow(row)
    arcpy.CalculateField_management(infc, stateGEOID, expression1, "PYTHON_9.3")
    arcpy.CalculateField_management(infc, fieldCodeIso, expression2, "PYTHON_9.3")


    fieldDel = ["STATEFP", "COUNTYFP", "COUNTYNS", "NAME", "NAMELSAD", "LSAD", "CLASSFP", "MTFCC",
                "CSAFP", "CBSAFP", "METDIVFP", "FUNCSTAT",  "CVE_ENT", "CVE_MUN", "NOM_MUN",
                "INTPTLAT", "INTPTLON", "ALAND", "AWATER", "GEOID"]
    for fd in fieldDel:
        arcpy.DeleteField_management(infc,fieldDel)
        
    
print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Project
## Description: Project the Nation dataset to North America Albers Equal Area Conic

print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
           
# Set Local variables
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Project the files
for fc in selectList:
    projFile = os.path.splitext(fc)[0] +"_pr"
    arcpy.Project_management(fc, projFile, outCS)
    mergeList.append(projFile)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Merge the files
## Description: Merge the vector fetures into a single output feature

print "\nStep 5 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outfc = os.path.join(out_gdb, "Counties_and_Municipios")
arcpy.Merge_management(mergeList, outfc)
arcpy.FeatureClassToShapefile_conversion(outfc, finalFolder)
newFile = os.path.join(finalFolder, "Counties_and_Municipios.shp")
fieldsDel = ["Shape_Area", "Shape_Leng"]
arcpy.DeleteField_management(newFile, fieldsDel)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 6. Select by location
## Description: Select Counties and Municipios located in the RGB

print "\nStep 6 Select by location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_fc = outfc

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []
for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append (out_shp)

for clip in clip_features:
    temp = os.path.split(clip)[-1]
    root = in_fc.split('_join')[0]
    name = os.path.split(root)[1]
    if temp.startswith("RGB_Ses"):
        output = os.path.join(out_gdb, name + "_intersect")
    arcpy.MakeFeatureLayer_management(clip, "lyr_rgb")
    arcpy.MakeFeatureLayer_management(in_fc, "lyr_infc")
    arcpy.SelectLayerByLocation_management("lyr_infc",
                                           "INTERSECT",
                                           "lyr_rgb",
                                           "",
                                           "NEW_SELECTION")
    arcpy.CopyFeatures_management("lyr_infc", output)
    #projList.append(output)
    print "Select by location" , clip, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

    ## Tabulate intersection with restricted parameters
    zoneFC = output
    zoneFld = "ADM2_GEOID"
    classFC = clip
    outTab = os.path.join(interFolder, "TabulateIntersect.dbf")
    class_fields=""
    sum_fields=""
    xy_tolerance="-1 Unknown"
    out_unit="SQUARE_KILOMETERS"

    arcpy.TabulateIntersection_analysis(zoneFC,
                                        zoneFld,
                                        classFC,
                                        outTab,
                                        class_fields,
                                        sum_fields,
                                        xy_tolerance,
                                        out_unit)

    ## Spatial join
    joinField = "ADM2_GEOID"
    arcpy.MakeFeatureLayer_management(output, "temp")
    arcpy.AddJoin_management("temp", joinField, outTab, joinField, "KEEP_ALL")
    name = os.path.splitext(output)[0]
    ifc = os.path.join(out_gdb, name + "_join")
    arcpy.CopyFeatures_management("temp", ifc)


    ## Delete counties with small areas
    ## Area < 15 km2
    expression = "\"AREA\" < 15"
    expression2 = "\"ADM2_GEOID\" = '84048047'"
    arcpy.MakeFeatureLayer_management(ifc, "temp")
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    arcpy.SelectLayerByAttribute_management("temp", "SWITCH_SELECTION")
    arcpy.SelectLayerByAttribute_management("temp", "REMOVE_FROM_SELECTION", expression2)
    ifc2 = ifc.split("intersect_join")[0] + "rgb"
    arcpy.CopyFeatures_management("temp", ifc2)
    finalList.append(ifc2)


print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 7. Export new shapefile
## Description: Export features class to shapefiles

print "\nStep 7 Export new shapefile starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldsDel = ["OID_", "Shape_Leng", "Shape_Area", "AREA", "PERCENTAGE", "ADM2_GEO_1"]

for fc in finalList:
    oRoot, oExt = os.path.split(fc)
    finalName = oExt +".shp"
    out_feature = os.path.join(finalFolder, finalName)
    arcpy.CopyFeatures_management(fc, out_feature)
    arcpy.DeleteField_management(out_feature, fieldsDel)

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


