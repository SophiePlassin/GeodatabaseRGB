# DamsNID.py
## Created on: 2019-05-17
## By: Sophie Plassin
## Description: Preparation of the NID Dams shapefile for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Generate XY Layer for CO, NM, TX tables
##              3. Project the features class to North America Albers Equal Area Conic
##              4. Merge the State files into a single feature class
##              5. Clip the area of the RGB
##              6. Clean the dataset: change name fields, conversion of the U.S. standard units (feet, acre feet,
##              acres, square miles) to the metric system (m, cubic meters, hectares, square kilometers)
##              7. Save output data to final folder
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
arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\4_dams\\original_input\\"
dirpath = arcpy.env.workspace

# Options
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

# Directories
interFolder =  "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\4_dams\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Hydrau_WaterUse\\4_dams\\final_output\\"

# Lists
geoList = []
projList = []
clipList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "Dams_NID.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Generate XY Layer event 
## Description: Creates a new point feature layer based on x- and y-coordinates defined in a source table.

print "\nStep 2 Generate XY Layer event starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

xlsFiles = arcpy.ListFiles("*_join.xlsx")
x_coords = "LONGITUDE"
y_coords = "LATITUDE"
mergeList = []
finalList = []

# Execute Excel to Dbf table
for xls in xlsFiles:
    name = os.path.splitext(xls)[0] 
    dbf_file = os.path.join(interFolder, name + ".dbf")
    arcpy.ExcelToTable_conversion(xls,
                                  dbf_file)

# Make the XY event layer
    nameLayer = os.path.splitext(dbf_file)[0]
    outLayer = nameLayer.split("_join")[0] + "_points"
    arcpy.MakeXYEventLayer_management(dbf_file,
                                      x_coords,
                                      y_coords,
                                      outLayer)

# Save to a layer file
    saved_Layer = outLayer + ".lyr"
    arcpy.SaveToLayerFile_management(outLayer,
                                     saved_Layer)
    
# Create Shapefile
    root = os.path.split(saved_Layer)[1]
    name = root.split("_points.lyr")[0] + "_dams"
    output = os.path.join(out_gdb, name)
    arcpy.CopyFeatures_management(saved_Layer,
                                  output)

# Add STATEID
    cur = arcpy.UpdateCursor(output)
    state_id = "STATEID"
    for row in cur:
        state = name[0:2]
        if state == 'CO':
            row.setValue(state_id, '08')
        if state == 'NM':
            row.setValue(state_id, '35')
        if state == 'TX':
            row.setValue(state_id, '48')
        cur.updateRow(row)
    geoList.append(output)

 
print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 3. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 3 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

for fc in geoList:
    projFile = os.path.splitext(fc)[0] + '_pr'
    arcpy.Project_management(fc, projFile, outCS)
    projList.append(projFile)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Merge features
## Description: Merge three states

print "\nStep 4 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Output
mergeFile = os.path.join(out_gdb, "Dams_us")

arcpy.Merge_management(projList,
                       mergeFile)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 5. Clip
## Description: Clip to the boundaries of the study area

print "\nStep 5 Clip the features starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp",
          "RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute Clip
for clip in clip_features:
    fc = mergeFile
    # Create name
    new_name = fc
    temp = os.path.split(clip)[-1]
    # Add Ses or Bas according to the clip feature name
    if temp.startswith("RGB_Basin"):
        output = new_name + "_bas"
    else:
        output = new_name + "_ses"
    arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
    clipList.append(output)
    print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Clean the dataset
## Description: Rename fields, Add new fields (units in U.S. system)

print "\nStep 6 Clean the dataset starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# New fields International Units
fieldHgtM =         "DAM_HGT_m"
fieldLgtM =         "DAM_LGTH_m"
fieldCapMM =        "MAXSTO_mcm"
fieldCapMNo =       "NORSTO_mcm"
fieldSurHa =        "SURFACE_ha"
fieldDrainSqk =     "DRAIN_SqKm"
newFields = [fieldHgtM, fieldLgtM, fieldCapMM, fieldCapMNo, fieldSurHa, fieldDrainSqk]

# Fields to altere (lentgh <= 10 characters)
alterFields= [["OTHER_DAM_",            "OTHER_NAME"],
              ["DAM_FORMER",            "FORMER_NAME"],
              ["LONGITUDE",             "LONG_DD"],
              ["LATITUDE",              "LAT_DD"],
              ["DAM_DESIGN",            "DAM_DESIGN"],
              ["PRIVATE_DA",            "PRIVATE"],
              ["YEAR_COMPL",            "YEAR_COMPL"],
              ["YEAR_MODIF",            "YEAR_MODIF"],
              ["DAM_LENGTH",            "DAM_LGTH_f"],
              ["DAM_HEIGHT",            "DAM_HGT_f"],
              ["STRUCTURAL",            "STRC_HGT_f"],
              ["HYDRAULIC_",            "HYD_HGT_f"],
              ["NID_HEIGHT",            "NID_HGT_f"],
              ["MAX_DISCHA",            "MAX_DISCHA"],
              ["MAX_STORAG",            "MAXSTO_af"],
              ["NORMAL_STO",            "NORSTO_af"],
              ["NID_STORAG",            "NIDSTO_af"],
              ["SURFACE_AR",            "SURFACE_ac"],
              ["DRAINAGE_A",            "DRAIN_SqMi"],
              ["INSPECTION",            "INSPECTION"],
              ["INSPECTI_1",            "INSPE_FREQ"],
              ["STATE_REG_",            "STATE_DAM"],
              ["STATE_RE_1",            "STATE_AGEN"],
              ["SPILLWAY_T",            "SPILL_TYPE"],
              ["SPILLWAY_W",            "SPILL_WD"],
              ["OUTLET_GAT",            "OUTLET_GAT"],
              ["NUMBER_OF_",            "NUM_LOCKS"],
              ["LENGTH_OF_",            "LGTH_LOCKS"],
              ["WIDTH_OF_L",            "WD_LOCKS"],
              ["FED_FUNDIN",            "FED_FUNDIN"],
              ["FED_CONSTR",            "FED_CONSTR"],
              ["FED_REGULA",            "FED_REGULA"],
              ["FED_INSPEC",            "FED_INSPEC"],
              ["FED_OPERAT",            "FED_OPERAT"],
              ["SOURCE_AGE",            "SOURCE_AGE"],
              ["SUBMIT_DAT",            "SUBMIT_DAT"],
              ["URL_ADDRES",            "URL"],
              ["OTHERSTRUC",            "OTHER_ID"],
              ["NUMSEPARAT",            "NUM_STRC"],
              ["PERMITTING",            "PERMIT_AUT"],
              ["INSPECTI_2",            "INSPEC_AUT"],
              ["ENFORCEMEN",            "ENFORC_AUT"],
              ["JURISDICTI",            "JURISD_DAM"],
              ["EAP_LAST_R",            "EAP_DATE"]]    

# Alter fields
for fc in clipList:
    for old, new in alterFields:
        tmpName = ("{0}_tmp".format(old))
        arcpy.AlterField_management(fc, old, tmpName)
        arcpy.AlterField_management(fc, tmpName, new)

# Set local variables
fieldType = "FLOAT"
fieldPrecision = 12
    
# Add fields
for fc in clipList:
    for fd in newFields:
        arcpy.AddField_management(fc, fd, fieldType, fieldPrecision)
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        value1 = row.getValue("DAM_HGT_f")
        if value1 == 0:
            row.setValue("DAM_HGT_f", "-99")
        value2 = row.getValue("DAM_LGTH_f")
        if value2 == 0:
            row.setValue("DAM_LGTH_f", "-99")
        value3 = row.getValue("MAXSTO_af")
        if value3 == 0:
            row.setValue("MAXSTO_af", "-99")
        value4 = row.getValue("NORSTO_af")
        if value4 == 0:
            row.setValue("NORSTO_af", "-99")
        value5 = row.getValue("SURFACE_ac")
        if value5 == 0:
            row.setValue("SURFACE_ac", "-99")
        value6 = row.getValue("DRAIN_SqMi")
        if value6 == 0:
            row.setValue("DRAIN_SqMi", "-99")
        value7 = row.getValue("NID_HGT_f")
        if value7 == 0:
            row.setValue("NID_HGT_f", "-99")
        value8 = row.getValue("Max_Discha")
        if value8 == 0:
            row.setValue("MAX_DISCHA", "-99")
        value9 = row.getValue("MAX_DISCHA")
        if value9 == 0:
            row.setValue("NIDSTO_af", "-99")
        cur.updateRow(row)

# Calculate Dams capacity, height and lenthg in international units
    arcpy.CalculateField_management(fc, fieldHgtM, "!DAM_HGT_f! * 0.3048", "PYTHON_9.3") # Height in m
    arcpy.CalculateField_management(fc, fieldLgtM, "!DAM_LGTH_f! * 0.3048", "PYTHON_9.3") # Length in m
    arcpy.CalculateField_management(fc, fieldCapMM, "!MAXSTO_af! * 0.00123348", "PYTHON_9.3") # Max storage in mcm
    arcpy.CalculateField_management(fc, fieldCapMNo, "!NORSTO_af! * 0.00123348 ", "PYTHON_9.3") # Normal storage in mcm
    arcpy.CalculateField_management(fc, fieldSurHa, "!SURFACE_ac! * 0.404686", "PYTHON_9.3") # Surface in ha
    arcpy.CalculateField_management(fc, fieldDrainSqk, "!Drain_SqMi! * 2.58999", "PYTHON_9.3") # drainage area in sqkm.

    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        value11 = row.getValue(fieldHgtM)
        if value11 < 0:
            row.setValue(fieldHgtM, "-99")
        value12 = row.getValue(fieldLgtM)
        if value12 < 0:
            row.setValue(fieldLgtM, "-99")
        value13 = row.getValue(fieldCapMM)
        if value13 < 0:
            row.setValue(fieldCapMM, "-99")
        value14 = row.getValue(fieldCapMNo)
        if value14 < 0:
            row.setValue(fieldCapMNo, "-99")
        value15 = row.getValue(fieldSurHa)
        if value15 < 0:
            row.setValue(fieldSurHa, "-99")
        value16 = row.getValue(fieldDrainSqk)
        if value16 < 0:
            row.setValue(fieldDrainSqk, "-99")
        cur.updateRow(row)


print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 7. Export the feature class
## Description: Rename fields, Add new fields (units in U.S. system)

print "\nStep 7 Export starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in clipList:
    name = os.path.split(fc)[1]
    out_feature = os.path.join(finalFolder, name + ".shp")
    arcpy.CopyFeatures_management(fc, out_feature)
    arcpy.DeleteField_management(out_feature, "OID_")

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "Geoprocess Dams completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
