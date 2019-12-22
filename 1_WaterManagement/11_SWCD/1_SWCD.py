## Name: SWCD.py
## Created on: 2019-03-25
## By: Sophie Plassin
## Description: Preparation of the dataset related to Soil and Water Conservation Districts
##              in the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Select the SWCDs that cross the RGB in CO, merge the polygons, save in the GDB
##              3. Select the SWCDs that cross the RGB in NM
##              4. Select the SWCDs that cross the RGB in TX
##              5. Project the dataset to North America Albers Equal Area Conic
##              6. Homogeneize the fields 
##              7. Merge the state datasets
# ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
import glob
from arcpy import env
from arcpy.sa import *

# Set options
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False


print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\11_SWCD\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\11_SWCD\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\11_SWCD\\final_output\\"
arcpy.env.workspace = dirpath

# Field to add
fieldState = "State"

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "SWCD.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1. Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Select polygons in Colorado and merge them
## Description: Create a list of polygons to merge

print "\nStep 2. Merge polygons in CO starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
fcList = ["CO\\conejos.shp", "CO\\center.shp", "CO\\costilla.shp", "CO\\mosca_hooper.shp",
          "CO\\rio_grande.shp"] # select CO shapefile

# Output name
mergeList = []

for fc in fcList:
    shape = os.path.join(dirpath, fc)
    mergeList.append(shape)
    
inputList = []

out_feature = os.path.join(out_gdb, "SWCD_CO")
arcpy.Merge_management(mergeList, out_feature)

# Add field for State
arcpy.AddField_management(out_feature, fieldState, "TEXT", "", "", 30)
arcpy.CalculateField_management(out_feature,
                                fieldState,
                                "'{0}'".format(str("Colorado")),
                                "PYTHON_9.3", "")

inputList.append(out_feature)

print "Step 2. Merge polygons in CO completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. Select SWCD in NM
## Description: Select polygons in New Mexico, save into the gdb

print "\nStep 3. Select polygons in NM starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Ses_NAD83_13N.shp"]
xy_tolerance = ""
clip_features = []
for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)


in_file = glob.glob(dirpath + "NM\\*.shp")[0] # select NM shapefile
out_fc = os.path.join(out_gdb, "SWCD_NM")

for clip in clip_features:
    arcpy.MakeFeatureLayer_management(clip, "lyr_rgb")
    arcpy.MakeFeatureLayer_management(in_file, "temp")
    arcpy.SelectLayerByLocation_management("temp",
                                           "INTERSECT",
                                           "lyr_rgb",
                                           "",
                                           "NEW_SELECTION")
    temp = os.path.split(clip)[-1]
    arcpy.CopyFeatures_management("temp", out_fc)
     

## Remove mimatches of boundaries in NM
## Run TabulateIntersection with restricted parameters
    zoneFC = out_fc 
    zoneFld = "Abbr"
    classFC = clip
    outTab = "TabulateIntersect.dbf"
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


    ## Spatial Join
    joinField = "Abbr"
    arcpy.MakeFeatureLayer_management(out_fc, "temp")
    arcpy.AddJoin_management("temp", joinField, outTab, joinField, "KEEP_ALL")
    ifc = os.path.join(out_gdb, "SWCD_NM_Join")
    arcpy.CopyFeatures_management("temp", ifc)


## Delete SWCD with small areas
## Area < 15 km2
    expression = "\"AREA\" > 15"
    arcpy.MakeFeatureLayer_management(ifc, "temp")
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    ifc2 = ifc.split("_Join")[0] + "_select"
    arcpy.CopyFeatures_management("temp", ifc2)
    # Add field for State
    arcpy.AddField_management(ifc2, fieldState, "TEXT", "", "", 30)
    arcpy.CalculateField_management(ifc2,
                                    fieldState,
                                    "'{0}'".format(str("New Mexico")),
                                    "PYTHON_9.3", "")
    # Add NM to the list for projection
    inputList.append(ifc2)

print "Step 3. Select polygons in NM completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Select TX in SWCD
## Description: Select By Attribute

print "\nStep 4. Select polygons in TX starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_file = glob.glob(dirpath + "TX\\*.shp")[0] # select TX shapefile
out_file = os.path.join(out_gdb, "SWCD_TX")
expression = "\"SWCD__\" <> \'326\' AND \"SWCD__\" <> \'328\'"

arcpy.MakeFeatureLayer_management(in_file, "temp")
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", out_file)
# Add field for State
arcpy.AddField_management(out_file, fieldState, "TEXT", "", "", 30)
arcpy.CalculateField_management(out_file,
                                fieldState,
                                "'{0}'".format(str("Texas")),
                                "PYTHON_9.3", "")
inputList.append(out_file)

print "Step 4. Select polygons in TX completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 5. Project the polygon
## Description: Project to North America Albers Equal Area Conic

print "\nStep 5. Projection starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

projList =[]
for fc in inputList:
    name = os.path.split(fc)[1] + '_pr'
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    projList.append(projFile)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 6. Homogeneize fields
## Description: Add, delete and rename fields

print "\nStep 6. Homogeneize starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

delFields = ["DONE", "AREA", "PERIMETER", "Area", "Shape_Leng",
             "SCD_", "SCD_ID", "CONEJOS_", "CONEJOS_ID", "COSTILLA_", "COSTILLA_I",
             "MOSCA_HOOP", "MOSCA_HO_1", "RIO_GRANDE", "RIO_GRAN_1", "SQMI",
             "calc_acres", "Shape__Are", "Shape__Len"] # fields to delete

expressionArea = "!shape.area@squarekilometers!" #expression for calcultaing the area
expressionLength = "!shape.length@kilometers!" #expression for calcultaing the length

mergedList = []

for in_fc in projList:
    # AddArea in kilometers
    arcpy.AddField_management(in_fc, "Area_sqkm", "FLOAT", "", "", 50)
    arcpy.AddField_management(in_fc, "Length_km", "FLOAT", "", "", 50)
    arcpy.CalculateField_management(in_fc, "Area_sqkm", expressionArea, "PYTHON_9.3")
    arcpy.CalculateField_management(in_fc, "Length_km", expressionLength, "PYTHON_9.3")
    # Round with 3 decimales
    cur = arcpy.UpdateCursor(in_fc)
    for row in cur:
        valueArea = row.getValue("Area_sqkm")
        row.setValue("Area_sqkm", round(valueArea, 3))
        valueLg = row.getValue("Length_km")
        row.setValue("Length_km", round(valueLg, 3))
        cur.updateRow(row)
    # Prepare Colorado feature
    if in_fc.endswith("CO_pr"):
        fieldList = arcpy.ListFields(in_fc)
    # Rename fields
        for field in fieldList:
            if field.name == 'SCD':
                arcpy.AlterField_management(in_fc, field.name, 'Name', 'Name')                
        arcpy.AddField_management(in_fc, "SWCD_ID", "TEXT")
    #  Change format (Title) for the name of the SWCD
        arcpy.CalculateField_management(in_fc,
                                        "Name",
                                        "!Name!.title()",
                                        "PYTHON_9.3", "")
    # Update lines
        cur = arcpy.UpdateCursor(in_fc)
        for row in cur:
            value1 = row.getValue ("Name")
            if value1 == 'Costilla':
                row.setValue("SWCD_ID", 2266)
            elif value1 == 'Center':
                row.setValue("SWCD_ID", 1814)
            elif value1.startswith ('Mosca'):
                row.setValue("SWCD_ID", 2193)
            elif value1.startswith ('Rio'):
                row.setValue("SWCD_ID", 2078)
            value1.title()
            value2 = row.getValue("CONEJOS_ID")
            if value2 == 2453:
                row.setValue("SWCD_ID", 2453)
            elif value2 == 2461:
                row.setValue("SWCD_ID", 2461)
            cur.updateRow(row)
    # Prepare NM feature
    if in_fc.endswith("NM_select_pr"):
        fieldList = arcpy.ListFields(in_fc)
        for field in fieldList:
            if field.name == 'NAME':
                arcpy.AlterField_management(in_fc, field.name, 'Name', 'Name')
        arcpy.AddField_management(in_fc, "SWCD_ID", "TEXT")
        cur = arcpy.UpdateCursor(in_fc)
        for row in cur:
            value = row.getValue("Abbr")
            row.setValue ("SWCD_ID", value)
            cur.updateRow(row)
    # Prepare TX feature
    if in_fc.endswith("TX_pr"):
        fieldList2 = arcpy.ListFields(in_fc)
        for field in fieldList2:
            # Rename field
            if field.name == 'SWCD__':
                arcpy.AlterField_management(in_fc, field.name, 'SWCD_ID', 'SWCD_ID')
            if field.name == "SWCD_NAME":
                arcpy.AlterField_management(in_fc, field.name, 'Name', 'Name')
    # Delete unecessary fields
    arcpy.DeleteField_management(in_fc, delFields)
    # Add to list for merge
    mergedList.append(in_fc)

print "Step 6. Clean files completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 7. Merge SWCD into one layer
## Description: Merge features in one dataset and delete unecessary fields

print "\nStep 7. Merge state layer to a single dataset starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

delFields2 = ["OBJECTID", "AREA", "PERCENTAGE", "Abbr", "OID_", "OID_1", "Abbr_1"]

# Output name
out_name = "SWCD.shp"
out_file = os.path.join(finalFolder, out_name)
# Execute
arcpy.Merge_management(mergedList, out_file)
arcpy.DeleteField_management(out_file, delFields2)

print "Step 7. Merge state layer to a single dataset completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


