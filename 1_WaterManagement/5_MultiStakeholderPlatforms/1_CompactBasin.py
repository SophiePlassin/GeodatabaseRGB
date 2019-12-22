## Name: Compact Areas.py
## Created on: 2019-08-04
## By: Sophie Plassin
## Description: Preparation of the Inter-State Compact (ISC) shapefile for the Rio Grande/Bravo basin (RGB)
##              There are three ISC in the RG: the Rio Grande Compact, the Pecos Compact and the Costilla Creek Compact.

##              For all:
##              1. Erase duplicate features between the NHD basin dataset level 10 (HUC10) of CO, NM, TX 
##              2. Merge the new HUC10 of CO, NM and TX into a single output feature
##              3. Project the new combined dataset to a common projected coordinate system (North America Albers Equal Area Conic)

##              Costilla Creek Compact:
##              4. Create the Costilla Creek Compact feature (Select By Attribute the corresponding HUC)

##              Rio Grande Compact:
##              5. Create a new feature of all HUCs located in the upper RGB (Select by Attributes the corresponding HUCs)
##              6. Erase the Costilla Creek feature from this new feature, dissolve the HUCs into a single output feature
##              Add fields NAME and STATES and populate

##              Pecos Compact:
##              7. Create a new feature of all HUCs located in the Pecos basin (Select by Attributes the corresponding HUCs)
##              Dissolve the HUCs into a single output feature.
##              Add fields NAME and STATES and populate.

##              For all:
##              8. Merge all Interstate Compacts into a single output feature, populate field ID
##              9. Reorder fields
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

### Workspace
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\original_input\\Compact\\"
dirpath = arcpy.env.workspace
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\inter_output\\Compact"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\final_output"
basinFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrology\\1_basin\\final_output\\"

# Option
arcpy.env.overwriteOutput = True

# List
inputList = []
mergeList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Erase duplicate features
## Description: Erase duplicate features of the CO, NM, and TX NHD basin dataset level 10 (HUC10) to only have one feature per HUC

print "\nStep 1 Erase duplicate HUCs starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs
for path, dirs, files in os.walk(dirpath):
    for name in files:
        absFile=os.path.abspath(os.path.join(path,name))
        if name.endswith(".shp") and (path.endswith('CO') or path.endswith('TX')):
            inputList.append(absFile)
        if name.endswith(".shp") and path.endswith('NM'):
            NM_file = absFile # NM = file where we erase duplicate features
            mergeList.append (NM_file)

# Output
name_erase = os.path.join(interFolder, "WBDHU10")

# Erase
for in_file in inputList:
    state = in_file[-14:-12]
    output_feature = name_erase + state + ".shp"
    arcpy.Erase_analysis(in_file, NM_file, output_feature)
    mergeList.append(output_feature)

print "Step 1 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Merge HUCs into a single output feature
## Description: Combines the NHD basin input dataset level 10 (HUC10) of CO, NM and TX

print "\nStep 2 Merge HUCs starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output
name = os.path.split(mergeList[0])[1]
output = os.path.join(interFolder, name [0:4] + "_rgb.shp")
arcpy.Merge_management(mergeList, output, "NO_FID")

WBDHU10 = output

print "Step 2 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Project
## Description: Project new file to North America Albers Equal Area Conic

print "\nStep 3 Projection starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# PCS
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

name = os.path.splitext(WBDHU10)[0]
projFile = os.path.join(interFolder, name + '_pr.shp')
arcpy.Project_management(WBDHU10, projFile, outCS)
WBDHU10_pr = projFile
print "Projection" , name, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Costilla Creek Compact: Select by Attribute
## Description: Select sub-basin from NHD dataset level 10 (HUC10) and create new feature

print "\nStep 4  Create the Costilla Creek Compact feature starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Expression
expression = "\"HUC10\" = '1302010101'" # Costilla Creek (name)

# Output
out_feature = os.path.join(interFolder, "Costilla_Creek_Compact.shp")

# Create new feasture for Costilla creek
arcpy.MakeFeatureLayer_management(WBDHU10_pr, "temp")
arcpy.SelectLayerByAttribute_management("temp", 'NEW_SELECTION', expression)
arcpy.CopyFeatures_management("temp", out_feature)
arcpy.CalculateField_management(out_feature, "NAME", '"' + "Costilla Creek Compact" + '"', "PYTHON_9.3")
arcpy.CalculateField_management(out_feature, "STATES", '"' + "CO,NM" + '"', "PYTHON_9.3")

costilla = out_feature
finalList.append(costilla)

print "Step 4 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Rio Grande Compact: Select by Attributes
## Description: Select all HUCs located in the upper RGB from NHD dataset level 10 (HUC10) and create new feature

print "\nStep 5 Select by Attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_file = WBDHU10_pr

# Outputs
out_feature = os.path.join(interFolder, "RG_Compact_upper_rgb.shp")

# Expression
expression = """ "HUC10" LIKE '13010001%' OR "HUC10" LIKE '13010002%' OR "HUC10" LIKE '13010003%' OR "HUC10" LIKE '13010004%' OR\
"HUC10" LIKE '13010005%' OR "HUC10" LIKE '13020101%' OR "HUC10" LIKE '13020102%' OR "HUC10" LIKE '13020204%' OR \
"HUC10" LIKE '13020202%' OR "HUC10" LIKE '13020201%' OR "HUC10" LIKE '13020203%' OR "HUC10" LIKE '13020205%' OR \
"HUC10" LIKE '13020207%' OR "HUC10" LIKE '13020209%' OR "HUC10" LIKE '13020211%' OR "HUC10" LIKE '13030101%' OR \
"HUC10" IN ('1303010201', '1303010202', '1303010203', '1303010204', '1303010205', '1303010206', '1303010207', '1303010208', '1303010209', '1303010210') OR \
"HUC10" IN ('1302020606', '1302020607') OR \
"HUC10" = '1304010000'"""

# Execute selection
arcpy.MakeFeatureLayer_management(in_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", 'NEW_SELECTION', expression)
arcpy.CopyFeatures_management("temp", out_feature)
upper_rgb = out_feature

print "Step 5 Select By Attribute completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## ---------------------------------------------------------------------------
## 6. Rio Grande Compact: Erase and dissolve
## Description: Erase the Costilla Creek feature and aggregate the HUCs into a single output feature.
## Add fields NAME and STATES and populate.

print "\nStep 6 Erase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_file = upper_rgb
erase_file = costilla

# Output
output_erase = os.path.join(interFolder, "RG_Compact_basin.shp")
output_diss = os.path.join(interFolder, "RG_Compact_dissolve.shp")

# Erase
arcpy.Erase_analysis(in_file, erase_file, output_erase)

# New field
fieldName = "NAME"
fieldState = "STATES"
fieldList = [fieldName, fieldState]
fieldType = "TEXT"

# Dissolve
arcpy.Dissolve_management(output_erase, output_diss)

# Add fields
for fd in fieldList:
    arcpy.AddField_management(output_diss, fd, fieldType, "", "", 50)

# Populate new fields
arcpy.CalculateField_management(output_diss, fieldName, '"' + "Rio Grande Compact" + '"', "PYTHON_9.3")
arcpy.CalculateField_management(output_diss, fieldState, '"' + "CO,NM,TX" + '"', "PYTHON_9.3")

finalList.append(output_diss)

print "Step 6 Select By Attribute completed at", datetime.datetime.now().strftime("%I:%M:%S%p")
                    
## ---------------------------------------------------------------------------
## 7. Pecos Compact: Select by attribute and dissolve
## Description: Select all HUCs located in the upper RGB from NHD dataset level 10 (HUC10) and create new feature
## Aggregate the HUCs into a single output feature.
## Add fields NAME and STATES and populate.

print "\nStep 7 Select by Attributes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Inputs
in_file = WBDHU10_pr

# Outputs
out_feature_sel = os.path.join(interFolder, "Pecos_Compact.shp")
out_feature_diss = os.path.join(interFolder, "Pecos_Compact_dissolve.shp")

# Expression
expression = """\"HUC10\" LIKE '13060001%' OR \"HUC10\" LIKE '13060002%' OR \"HUC10\" LIKE '13060002%' OR \"HUC10\" LIKE '13060003%'
OR \"HUC10\" LIKE '13060004%' OR \"HUC10\" LIKE '13060005%' OR \"HUC10\" LIKE '13060006%' OR \"HUC10\" LIKE '13060007%' 
OR \"HUC10\" LIKE '13060008%' OR \"HUC10\" LIKE '13060009%' OR \"HUC10\" LIKE '13060010%' OR \"HUC10\" LIKE '13060011%'
OR \"HUC10\" LIKE '13070001%' OR \"HUC10\" LIKE '13070002%' OR \"HUC10\" LIKE '13070003%' OR \"HUC10\" LIKE '13070004%'
OR \"HUC10\" LIKE '13070005%' OR \"HUC10\" LIKE '13070006%' OR \"HUC10\" LIKE '13070007%' OR \"HUC10\" LIKE '13070008%'
OR \"HUC10\" LIKE '13070009%' OR \"HUC10\" LIKE '13070010%' OR \"HUC10\" LIKE '13070011%' OR \"HUC10\" LIKE '13070012%'"""

# Select by attribute
arcpy.MakeFeatureLayer_management(in_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", 'NEW_SELECTION', expression)
arcpy.CopyFeatures_management("temp", out_feature_sel)

# Dissolve
arcpy.Dissolve_management(out_feature_sel, out_feature_diss)

# Add fields
for fd in fieldList:
    arcpy.AddField_management(out_feature_diss, fd, fieldType, "", "", 50)

# Populate new fields
arcpy.CalculateField_management(out_feature_diss, fieldName, '"' + "Pecos Compact" + '"', "PYTHON_9.3")
arcpy.CalculateField_management(out_feature_diss, fieldState, '"' + "NM,TX" + '"', "PYTHON_9.3")
finalList.append(out_feature_diss)

print "Step 7 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 8. Merge all Interstate Compacts into a single output feature
## Description: Merge Costilla Creek Compact, Rio Grande Compact and Pecos Compact into a single feature

print "\nStep 8 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldDel = ["GEODB_OID", "OBJECTID", "TNMID", "METASOURCE", "SOURCEDATA",
            "SOURCEORIG", "SOURCEFEAT", "LOADDATE", "GNIS_ID", "AREAACRES",
            "HUC10", "HUTYPE", "HUMOD", "SHAPE_AREA", "SHAPE_LENG", "Id"]

output = os.path.join(interFolder, "Interstate_Compacts.shp")
arcpy.Merge_management(finalList, output)
arcpy.DeleteField_management(output, fieldDel)
arcpy.AddField_management(output, "ID", fieldType, "", "", 3)

# Update Id
cur = arcpy.UpdateCursor(output)
for row in cur:
    value1 = row.getValue("NAME")
    if value1.startswith('Costilla'):
        row.setValue('Id', '001')
    elif value1.startswith('Pecos'):
        row.setValue('Id', '002')
    else:
        row.setValue('Id', '003')
    cur.updateRow(row)

# Calculate area
arcpy.CalculateField_management(output, "AREASQKM", "!shape.area@squarekilometers!", "PYTHON_9.3")

print "Step 8 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


# ---------------------------------------------------------------------------
## 9. Reorder fields
## Description: Reorder fields

print "\nStep 9 Reorder the fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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


# Execute reorder
new_field_order = ["FID", "ID", "NAME", "STATES", "AREASQKM"]
reorder_output = os.path.join(finalFolder, "Interstate_Compacts.shp")
reorder_fields(output, reorder_output, new_field_order)

print "Step 9 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "Geoprocess Basin completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


