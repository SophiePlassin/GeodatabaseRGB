# -*- coding: cp1252 -*-
## Name: MX_State_Water_Sewerage_Agencies.py
## Created on: 2019-12-06
## By: Sophie Plassin
## Description: Preparation of the MX Drinking Water and Sewerage agency dataset for the MX RGB
##              1. Create a geodatabase
##              2. Select by attribute
##              3. Homogeneize fields
##              4. Reorder fields
##              5. Split by attributes
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\inter_output\\MX\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\final_output\\"
arcpy.env.workspace = dirpath

# Set option
arcpy.env.overwriteOutput = True

# List
featuresList = []
selectList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Files
in_files = arcpy.ListFeatureClasses("*State*")
gdb_name = "Water_Sewerage.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)
for fc in in_files:
    arcpy.FeatureClassToGeodatabase_conversion(fc, out_gdb)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Select by attribute
## Description: Select the states of Mexico from the State file previously prepared

print "\nStep 2 Select by attribute starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Dir folder
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\4_state_agency\\inter_output\\MX\\Water_Sewerage.gdb"

# Inputs
fcList = arcpy.ListFeatureClasses()

# Expression
expression = "\"ADM0_ID\" = \'484\'"

# Execute
for fc in fcList:
    arcpy.MakeFeatureLayer_management(fc, "temp")
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    outFeature = os.path.join(out_gdb, "MX_State_Water_Sewerage_Agencies")
    arcpy.CopyFeatures_management("temp", outFeature)
    selectList.append(outFeature)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Homogeneize fields
## Description: Add and delete fields

print "\nStep 3 Homogeneize fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Fields
field_State = "STATE"
field_Agency = "AGENCY"
field_ABV = "ABV"
fieldType = "TEXT"
fieldStateName = "NAME_1"
fieldsDel = ["ID_0", "ADM0_ID", "NAME_0",
             "ID_1", "ADM1_ID", "NAME_1", "ADM1_GEOID"]
fieldsAdd = [field_State, field_Agency, field_ABV]

# Execute
for fc in selectList:
    for fd in fieldsAdd:
        arcpy.AddField_management(fc, fd, fieldType, "", "", 75)
        # Update values
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        value = row.getValue(fieldStateName)
        row.setValue(field_State, value)
        if value == "Coahuila de Zaragoza":
            row.setValue(field_Agency, "Comisión Estatal de Aguas y Saneamiento de Coahuila")
            row.setValue(field_ABV, "CEAS")
        elif value == "Chihuahua":
            row.setValue(field_Agency, "Junta Central del Agua y Saneamiento de Chihuahua")
            row.setValue(field_ABV, "JCAS")            
        elif value == "Durango":
            row.setValue(field_Agency, "Comisión de Agua del Estado de Durango")
            row.setValue(field_ABV, "CAED")
        elif value.startswith("Nuevo"):
            row.setValue(field_Agency, "Servicios de Agua y Drenaje de Monterrey")
            row.setValue(field_ABV, "SADM")
        elif value == "Tamaulipas":
            row.setValue(field_Agency, "Comisión Estatal del Agua de Tamaulipas")
            row.setValue(field_ABV, "CEAT")            
        cur.updateRow(row)
    # Delete field
    arcpy.DeleteField_management(fc, fieldsDel)
    
print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
## 4. Reorder fields
## Description: Reorder fields

print "\nStep 4 Reorder the fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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

# New field order State ADM_0
new_field_order = ["STATE", "AGENCY", "ABV", "Shape_Length", "Shape_Area"]

# New fields to delete
fieldDel = ["Shape_Le_1"]

# Execute reorder
for fc in selectList:
    output = fc + "_reorder"
    reorder_fields(fc, output, new_field_order)
    print "Reorder the fields", fc, "completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
    # Delete fields
    arcpy.DeleteField_management(output, fieldDel)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
## 5. Split by attributes
## Description: Reorder fields

print "\nStep 5 Split by attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fields = [field_ABV, field_State]
arcpy.SplitByAttributes_analysis(output, finalFolder, fields)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

