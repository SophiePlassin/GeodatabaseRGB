# -*- coding: utf-8 -*-
## Name: Places.py
## Created on: 2019-07-07
## By: Sophie Plassin
## Description: Preparation of the Places dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Project the dataset to North America Albers Equal Area Conic
##              3. Merge US state datasets
##              4. Select by attribute the MX states (Coa, Chi, Dur, NL, Tam)
##              5. Homogeneize fields
##              6. Merge US and MX datasets
##              7. Clip to the boundary of the study area
##              8. Reorder fields
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\original_input\\Census\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\inter_output\\Census\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
arcpy.env.workspace = dirpath

# List
US_List = []
MX_List = []
finalList = []


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "Places.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1. Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Project the polygon and calculate new area
## Description: Project to North America Albers Equal Area Conic

print "\nStep 2 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Inputs
inputsUS = arcpy.ListFeatureClasses("*place*")
inputsMX = ["poligonos_localidades_urbanas_y_rurales.shp"]
inputs = [inputsUS, inputsMX]

# Execute projection
for li in inputs:
    for fc in li:
        name = os.path.splitext(fc)[0] + '_pr'
        projFile = os.path.join(out_gdb, name)
        arcpy.Project_management(fc, projFile, outCS)
        print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
        if name.startswith("tl"):
            US_List.append(projFile)


print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Merge the polygon
## Description: The script merges the places for the 3 states of the US.

print "\nStep 3 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output
output_us = os.path.join(out_gdb, "US_Places")

# Merge Places of CO, NM and TX into a single dataset
arcpy.Merge_management(US_List, output_us)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Select by attribute the MX states.
## Description: The script selects the 5 states for Mexico.

print "\nStep 4 Select by attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Expression
expression = "\"CVE_ENT\" IN ('05', '08', '10', '19', '28')"

# Input
input_mx = os.path.join(out_gdb, "poligonos_localidades_urbanas_y_rurales_pr")

# Output
output_mx = os.path.join(out_gdb, "MX_Places")

# Execute selection
arcpy.MakeFeatureLayer_management(input_mx, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", output_mx)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Homogeneize fields
## Description: The script selects the 5 states for Mexico.

print "\nStep 5 Homogeneize fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
inFeatures = [output_us, output_mx]
counties = os.path.join(finalFolder, "Counties.shp")

# New fields
fieldType = "TEXT"
fieldID0Country = "ID_0"
fieldCodeCountry = "ADM0_ID"
fieldID1State = "ID_1"
fieldCodeState = "ADM1_ID"
fieldCodePlace = "ADM3_ID"
fieldCodeIso = "ADM3_GEOID"
fieldNameCountry = "NAME_0"
fieldNameState = "NAME_1"
fieldNamePlace = "NAME_3"
fieldNames = [fieldNameCountry, fieldNameState, fieldNamePlace]
field2Code = [fieldCodeState]
field3Code = [fieldCodeCountry, fieldID0Country]
field10Code = [fieldID1State, fieldCodeIso]
# Expression
expression = "!ADM0_ID!+!ADM1_ID!+!ADM3_ID!"

# Fields to delete
fieldDel = ["GEOID", "NAMELSAD", "LSAD", "CLASSFP", "PCICBSA", "PCINECTA", "MTFCC", "FUNCSTAT", "PLACENS"]
fieldDelMX = ["CVE_ENT", "CVE_MUN", "CVE_LOC", "NOM_LOC"]
fieldDelUS = ["STATEFP", "PLACEFP", "NAME", "INTPTLAT", "INTPTLON", "ALAND", "AWATER", "Shape_Leng"]

# Execute
for infc in inFeatures:
    name = os.path.split(infc)[1]
    
    # Delete
    for fd in fieldDel:
        arcpy.DeleteField_management(infc,fieldDel)
        
    # Add fields
    for fd in field3Code:
        arcpy.AddField_management(infc, fd, fieldType, "", "", 3)
    for fd in fieldNames:
        arcpy.AddField_management(infc, fd, fieldType, "", "", 80)
    for fd in field2Code:
        arcpy.AddField_management(infc, fd, fieldType, "", "", 2)
    arcpy.AddField_management(infc, fieldCodePlace, fieldType, "", "", 5)
    for fd in field10Code:
        arcpy.AddField_management(infc, fd, fieldType, "", "", 10)
    
    #Update lines
    cur = arcpy.UpdateCursor(infc)
    for row in cur:
        if name.startswith("MX"):
            row.setValue(fieldCodeCountry, '484')
            row.setValue(fieldID0Country, 'MEX')
            row.setValue(fieldNameCountry, 'Mexico')
            value1 = row.getValue("CVE_ENT")
            row.setValue(fieldCodeState, value1)
            if value1 == '05':
                row.setValue(fieldID1State, 'COA')
                row.setValue(fieldNameState, 'Coahuila')
            elif value1 == '08':
                row.setValue(fieldID1State, 'CHI')
                row.setValue(fieldNameState, 'Chihuahua')
            elif value1 == '10':
                row.setValue(fieldID1State, 'DUR')
                row.setValue(fieldNameState, 'Durango')
            elif value1 == '19':
                row.setValue(fieldID1State, 'NVL')
                row.setValue(fieldNameState, 'Nuevo León')
            else:
                row.setValue(fieldID1State, 'TAM')
                row.setValue(fieldNameState, 'Tamaulipas')
            value2 = row.getValue("CVE_LOC")
            row.setValue(fieldCodePlace, value2)
            value3 = row.getValue("NOM_LOC")
            row.setValue(fieldNamePlace, value3)
        elif name.startswith ("US"):
            row.setValue(fieldCodeCountry, '840')
            row.setValue(fieldID0Country, 'USA')
            row.setValue(fieldNameCountry, 'United States')
            value4 = row.getValue("STATEFP")
            row.setValue(fieldCodeState, value4)
            if value4 == '08':
                row.setValue(fieldID1State, 'CO')
                row.setValue(fieldNameState, 'Colorado')
            elif value4 == '35':
                row.setValue(fieldID1State, 'NM')
                row.setValue(fieldNameState, 'New Mexico')
            else:
                row.setValue(fieldID1State, 'TX')
                row.setValue(fieldNameState, 'Texas')
            value5 = row.getValue("PLACEFP")
            row.setValue(fieldCodePlace, value5)
            value6 = row.getValue("NAME")
            row.setValue(fieldNamePlace, value6)
        cur.updateRow(row)

    # Update ADM4_GEOID  
    arcpy.CalculateField_management(infc, fieldCodeIso, expression, "PYTHON_9.3")
    
    # Delete fields
    if name.startswith("MX"):
        for fd in fieldDelMX:
            arcpy.DeleteField_management(infc,fieldDelMX)
    else:
        for fd in fieldDelUS:
            arcpy.DeleteField_management(infc,fieldDelUS)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Merge US and MX layers
## Description: The script merges US and MX layers.

print "\nStep 6 Merge US and MX layers starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

out_feature = os.path.join(out_gdb, "Places")

# Merge into a single dataset
arcpy.Merge_management(inFeatures, out_feature)
finalList.append(out_feature)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 7. Clip the layer to the RGB study area
## Description: The script clips the layer using the county dataset previsouly created

print "\nStep 7 Clip the datasets starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = finalFolder
listfc = ["Counties_and_Municipios_rgb.shp"]
xy_tolerance = ""
clip_features = []
for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute        
for clip in clip_features:
    temp = os.path.split(clip)[-1]
    root = os.path.split(out_feature)[1]
    name = os.path.split(root)[1] + '_cl'
    output_clip = os.path.join (out_gdb, name)
    arcpy.Clip_analysis(out_feature, clip, output_clip, xy_tolerance)
    finalList.append(output_clip)

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
## 8. Reorder fields
## Description: Reorder fields

print "\nStep 8 Reorder the fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

def reorder_fields(in_fc, out_fc, field_order, add_missing=True):
    existing_fieldList = arcpy.ListFields(in_fc)
    existing_fieldList_names = [field.name for field in existing_fieldList]

    existing_mapping = arcpy.FieldMappings()
    existing_mapping.addTable(in_fc)
    new_mapping = arcpy.FieldMappings()

    def add_mapping(field_name):
        mapping_index = existing_mapping.findFieldMapIndex(field_name)

        # required fields (OBJECTID, etc) will not be in existing mappings
        # they are added automatically
        if mapping_index != -1:
            field_map = existing_mapping.fieldMappings[mapping_index]
            new_mapping.addFieldMap(field_map)

    # add user fields from field_order
    for field_name in field_order:
        if field_name not in existing_fieldList_names:
            raise Exception("Field: {0} not in {1}".format(field_name, in_fc))

        add_mapping(field_name)

    # add missing fields at end
    if add_missing:
        missing_fields = [f for f in existing_fieldList_names if f not in field_order]
        for field_name in missing_fields:
            add_mapping(field_name)

    # use merge with single input just to use new field_mappings
    arcpy.Merge_management(in_fc, out_fc, new_mapping)
    return out_fc

# New field order State ADM_2
new_field_order_places = ["OBJECTID", "ADM0_ID", "NAME_0", "ID_0",
                          "ADM1_ID", "NAME_1", "ID_1",
                          "ADM3_ID", "NAME_3", "ADM3_GEOID"]

# Input
finalList = sorted(finalList)

# Output
outputs = ["Places.shp", "Places_rgb.shp"]

# Fields to delete
fieldsDel = ["OBJECTID", "Shape_Leng", "Shape_Area"]


# Execute reorder
for i in range(len(finalList)):
    output = os.path.join(finalFolder, outputs[i])
    reorder_fields(finalList[i], output, new_field_order_places)
    print "Reorder the fields", output, "completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

    # Delete fields
    arcpy.DeleteField_management(output, fieldsDel)

print "Step 8 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")




