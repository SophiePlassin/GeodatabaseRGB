## Name: MX_INEGI_LandUse_RGB.py
## Created on: 2019-06-08
## By: Sophie Plassin
## Description: Preparation of the Land-Use dataset for the Mexico Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Project the land-use dataset for the Mexico RGB to North America Albers Equal Area Conic
##              3. Clip the shapefile
##              4. Translate the categories of land use to English
##              5. Reorder fields
## ---------------------------------------------------------------------------


## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
import glob
import itertools
from arcpy import env
from arcpy.sa import *

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\MX_inegi\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\MX_inegi\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\MX_inegi\\final_output\\"

# Extension
env.overwriteOutput = True


fcList = arcpy.ListFeatureClasses()
projList = []
clip_features = []
clippedList = []
finalList = []


## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
gdb_name = "MX_LandUse.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Project the polygons
## Description: Project the land-use dataset for the Mexico RGB to North America Albers Equal Area Conic

print "\nStep 2 Project the polygon starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in fcList:
    root = os.path.splitext(fc)[0]
    name = os.path.split(root)[1]
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Project completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Clip
## Description: Clip the MX INEGI dataset for the study area.

print "\nStep 3 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Ses_na_albers.shp"]
xy_tolerance = ""
expression = "\"CVE_UNION\" <> \'P/E\'"

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute Clip
for fc in projList:
    arcpy.MakeFeatureLayer_management(fc, "temp") 
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    tail = os.path.split(fc)[-1]
    name = os.path.splitext(tail)[0]
    for clip in clip_features:
        temp_name = os.path.split(clip)[-1]
        if temp_name.startswith("RGB_Basin"):
            output = os.path.join(out_gdb, name + "_bas")
        else:
            output = os.path.join(out_gdb, name + "_ses")
        arcpy.Clip_analysis("temp", clip, output, xy_tolerance)
        clippedList.append(output)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 Clip completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Translate the values of the fields into English
## Description: Translate the values of the fields into English

print "\nStep 4 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Set local variables
fieldType = "TEXT"
fieldNameEN = "NAME"
fieldCode = "CVE_UNION"

# Field to delete
fieldDel = ["AREA"]

# Rename field
for fc in clippedList:
    fieldList = arcpy.ListFields(fc)  #get a list of fields for each feature class
    for field in fieldList: #loop through each field
        if field.name == 'DESCRIPCIO':  #look for the name DESCRIPCIO
            arcpy.AlterField_management(fc, field.name, 'ORIG_NAME', 'ORIG_NAME')
# Remove field
    arcpy.DeleteField_management(fc, fieldDel)

# Add field NAME 
    arcpy.AddField_management(fc, fieldNameEN, fieldType)

# Add translation from Spanish to English in NAME
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        value1 = row.getValue(fieldCode)
        if value1 == "ADV":
            row.setValue(fieldNameEN, "Unvegetated Land")
        if value1 == "AH":
            row.setValue(fieldNameEN, "Human Settlements")
        if value1 == "BA":
            row.setValue(fieldNameEN, "Boreal Forest")
        if value1 == "BG":
            row.setValue(fieldNameEN, "Gallery Forest")         
        if value1 == "BJ":
            row.setValue(fieldNameEN, "Juniperus Forest")
        if value1 == "BP":
            row.setValue(fieldNameEN, "Pine Forest")  
        if value1 == "BPQ":
            row.setValue(fieldNameEN, "Pine-Oak Forest")
        if value1 == "BQ":
            row.setValue(fieldNameEN, "Oak Forest")
        if value1 == "BQP":
            row.setValue(fieldNameEN, "Oak-Pine Forest")
        if value1 == "BS":
            row.setValue(fieldNameEN, "Douglas-Fir and Spruce Forest")
        if value1 == "DV":
            row.setValue(fieldNameEN, "Without Vegetation")
        if value1 == "H2O":
            row.setValue(fieldNameEN, "Water Body")
        if value1 == "HA":
            row.setValue(fieldNameEN, "Wetland Agriculture")
        if value1 == "MC":
            row.setValue(fieldNameEN, "Pachycaulous Shrubland/Pachycaulous Scrub")
        if value1 == "MDM":
            row.setValue(fieldNameEN, "Desertic Microphyllous Shrubland/Desertic Microphyllous Scrub")
        if value1 == "MDR":
            row.setValue(fieldNameEN, "Desertic Rosetophyllous Shrubland/Desertic Rosetophyllous Scrub")
        if value1 == "MET":
            row.setValue(fieldNameEN, "Tamaulipan Thorn Shrubland/Tamaulipan Thorn Scrub")
        if value1 == "MK":
            row.setValue(fieldNameEN, "Thorn Forest")
        if value1 == "MKX":
            row.setValue(fieldNameEN, "Desertic Thorn Forest")
        if value1 == "ML":
            row.setValue(fieldNameEN, "Chaparral")
        if value1 == "MSM":
            row.setValue(fieldNameEN, "Piedmont Shrubland/Piedmont Scrub")
        if value1 == "PC":
            row.setValue(fieldNameEN, "Cultivated Grassland")
        if value1 == "PH":
            row.setValue(fieldNameEN, "Halophilous Grassland")
        if value1 == "PI":
            row.setValue(fieldNameEN, "Induced Grassland")
        if value1 == "PN":
            row.setValue(fieldNameEN, "Natural Grassland")
        if value1 == "RA":
            row.setValue(fieldNameEN, "Annual Irrigated Crop")
        if value1 == "RAP":
            row.setValue(fieldNameEN, "Annual and Perennial Irrigated Crop")
        if value1 == "RAS":
            row.setValue(fieldNameEN, "Annual and Semi-Perennial Irrigated Crop")
        if value1 == "RP":
            row.setValue(fieldNameEN, "Perennial Irrigated Crop")
        if value1 == "RS":
            row.setValue(fieldNameEN, "Semi-Perennial Irrigated Crop")
        if value1 == "RSP":
            row.setValue(fieldNameEN, "Perennial and Semi-Perennial Irrigated Crop")
        if value1 == "TA":
            row.setValue(fieldNameEN, "Annual Rainfed Crop")
        if value1 == "TAP":
            row.setValue(fieldNameEN, "Annual and Perennial Rainfed Crop")
        if value1 == "TAS":
            row.setValue(fieldNameEN, "Annual and Semi-Perennial Rainfed Crop")
        if value1 == "TP":
            row.setValue(fieldNameEN, "Perennial Rainfed Crop")
        if value1 == "VD":
            row.setValue(fieldNameEN, "Sand Desertic Vegetation")
        if value1 == "VG":
            row.setValue(fieldNameEN, "Gallery Vegetation")
        if value1 == "VH":
            row.setValue(fieldNameEN, "Halophilous Vegetation")
        if value1 == "VHH":
            row.setValue(fieldNameEN, "Halophilous Hydrophilous Vegetation")
        if value1 == "VPI":
            row.setValue(fieldNameEN, "Induced Palms")
        if value1 == "VSa/BA":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Boreal Forest")
        if value1 == "VSa/BB":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Cypressus Forest")
        if value1 == "VSa/BG":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Galley Forest")
        if value1 == "VSa/BJ":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Juniperus Forest")
        if value1 == "VSA/BP":
            row.setValue(fieldNameEN, "Secondary Arboreal Vegetation derived from Pine Forest")
        if value1 == "VSa/BP":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Pine Forest")
        if value1 == "VSA/BPQ":
            row.setValue(fieldNameEN, "Secondary Arboreal Vegetation derived from Pine-Oak Forest")
        if value1 == "VSa/BPQ":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Pine-Oak Forest")
        if value1 == "VSA/BQ":
            row.setValue(fieldNameEN, "Secondary Arboreal Vegetation derived from Oak Forest")
        if value1 == "VSa/BQ":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Oak Forest")
        if value1 == "VSA/BQP":
            row.setValue(fieldNameEN, "Secondary Arboreal Vegetation derived from Oak-Pine Forest")
        if value1 == "VSa/BQP":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Oak-Pine Forest")
        if value1 == "VSa/BS":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Douglas-Fir and Spruce Forest")
        if value1 == "VSa/MDM":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Desertic Microphyllous Scrub")
        if value1 == "VSa/MDR":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Desertic Rosetophyllous Scrub")
        if value1 == "VSa/MET":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Tamaulipan Thorn Scrub")
        if value1 == "VSA/MK":
            row.setValue(fieldNameEN, "Secondary Arboreal Vegetation derived from Thorn Forest")
        if value1 == "VSa/MK":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Thorn Forest")
        if value1 == "VSa/MKX":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Desertic Thorn Forest")
        if value1 == "VSa/ML":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Chaparral")
        if value1 == "VSa/MSM":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Piedmont Scrub")
        if value1 == "VSa/PH":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Halophilous Grassland")
        if value1 == "VSa/PN":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Natural Grassland")
        if value1 == "VSa/VG":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Gallery Vegetation")
        if value1 == "VSa/VH":
            row.setValue(fieldNameEN, "Secondary Shrub Vegetation derived from Halophilous Xerophilous Vegetation")
        if value1 == "VSh/BP":
            row.setValue(fieldNameEN, "Secondary Herbaceous Vegetation derived from Pine Forest")
        if value1 == "VSh/MET":
            row.setValue(fieldNameEN, "Secondary Herbaceous Vegetation derived from Tamaulipan Thorn Scrub")
        if value1 == "VSh/PN":
            row.setValue(fieldNameEN, "Secondary Herbaceous Vegetation derived from Natural Grassland")
        if value1 == "VT":
            row.setValue(fieldNameEN, "Marsh Grasses")
        if value1 == "VU":
            row.setValue(fieldNameEN, "Coastal Dune Vegetation")
        if value1 == "VY":
            row.setValue(fieldNameEN, "Gypsophilous Vegetation")
        if value1 == "ZU":
            row.setValue(fieldNameEN, "Urban Area")
        cur.updateRow(row)
    
print "Step 4 Fields translated completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

# ---------------------------------------------------------------------------
## 5. Reorder fields
## Description: Reorder fields

print "\nStep 5 Reorder the fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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

new_field_order = ["OBJECTID", "CVE_UNION", "ORIG_NAME",
                   "NAME"]

for fc in clippedList:
    path, name = os.path.split(fc)
    begin = 0
    first_under = name.find("_")
    second_under = name.find("_", first_under + 1)
    output = name[begin :second_under] + "_reorder"
    out_feature = os.path.join(path, output)
    reorder_fields(fc, out_feature, new_field_order)
    finalList.append(out_feature)
    print "Reorder the fields", fc, "completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "Step 5 Reorder fields completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

# ---------------------------------------------------------------------------
## 6. Copy feature to final folder
## Description: Copy feature to final folder

print "\nStep 6 Copy features to final folder starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in finalList:
    name = os.path.split(fc)[-1]
    if name.startswith("usv250s6"):
        name = "MX_LU_2014.shp"
    else:
        name = "MX_LU_2011.shp"
    outfeature = os.path.join(finalFolder, name)
    arcpy.CopyFeatures_management(fc, outfeature)

print "Step 6 Copy feature to final folder completed at", datetime.datetime.now().strftime("%I:%M:%S%p")
