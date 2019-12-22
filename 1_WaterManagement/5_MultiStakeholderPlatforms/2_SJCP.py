# -*- coding: cp1252 -*-
## Name: San Juan Chama Project.py
## Created on: 2019-07-08
## By: Sophie Plassin
## Description: Preparation of the gauges dataset used for the Rio Grande Compact
##              1. Create a geodatabase
##              2. Create the SJCP Azotea tunnel
##              3. Create the SJCP Reservoirs
##              4. Create the SJCP users "Irrigation"
##              5. Create the SJCP users "Municipal"
##              6. Create the SJCP users "County"
##              7. Create the SJCP users "Tribe"
##              8. Create the SJCP users "Reservoir"
##              9. Merge the SJCP users vector features into a single output feature
##              10. Project the shapefiles to North America Albers Equal Area Conic
## ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
import glob
from arcpy import env
from arcpy.sa import *

# Set overwrite option
arcpy.env.overwriteOutput = True

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\original_input\\SJCP\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\inter_output\\SJCP\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\5_multi_stakeholders_platforms\\final_output\\"
arcpy.env.workspace = dirpath

# List
inputList = []
joinList = []
mergeList = []
userList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdb_name = "SJCP.gdb"
out_gdb = os.path.join(interFolder, gdb_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 Create a geodatabase completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 2. Create the Trans-mountain Diversion Infrastructure
## Description: Visual identification and selection of features based on attributes values, using Select Layer By Attribute

print "\nStep 2 Create the Azotea Tunnel starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_file = "CO_NHDFlowline.shp"

# Output
output = os.path.join(out_gdb, "SJCP_Tunnel_multipart")

# Selection
expression = "\"REACHCODE\" = \'13020102002424\' OR \"REACHCODE\" = \'14080101000663\'"

#Execute Selection
arcpy.MakeFeatureLayer_management(in_file, "temp") 
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", output)

output_dissolve = os.path.join(out_gdb, "SJCP_Tunnel")

# Dissolve the features into a single output feature
arcpy.Dissolve_management(output,
                          output_dissolve,
                          dissolve_field = ["FTYPE", "FCODE"],
                          statistics_fields = "",
                          multi_part = "MULTI_PART",
                          unsplit_lines = "DISSOLVE_LINES")

# Add field name
arcpy.AddField_management(output_dissolve, "FNAME", "TEXT", "", "", 50)


finalList.append(output_dissolve)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 3. Create the reservoirs used for importation and storage of SJCP water 
## Description: Select the SJCP reservoirs, using Select Layer By Attribute

print "\nStep 3 Create the SJCP Reservoirs starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## Erase duplicate features
## Description: Erase duplicate features of the CO, NM, and TX NHD Flowline dataset

# Inputs
for path, dirs, files in os.walk(dirpath):
    for name in files:
        absFile=os.path.abspath(os.path.join(path,name))
        if name.endswith(".shp") and (path.endswith('CO') or path.endswith('TX')):
            inputList.append(absFile)
        if name.endswith(".shp") and path.endswith('NM'):
            NM_file = absFile # NM = file where we erase duplicate features
            mergeList.append(NM_file)

# Output
name_erase = os.path.join(out_gdb, "NHDWaterbody")

# Erase
for in_file in inputList:
    state = in_file[-19:-17]
    output_feature = name_erase + state
    arcpy.Erase_analysis(in_file, NM_file, output_feature)
    mergeList.append(output_feature)


## Merge HUCs into a single output feature
## Description: Combines the NHD Flowline of CO, NM and TX

# Output
name = os.path.split(mergeList[0])[1]
output = os.path.join(out_gdb, "WaterBody")
arcpy.Merge_management(mergeList, output, "NO_FID")
joinList.append(output)

# List of dams and corresponding REACHCODE
# Heron Reservoir: 13020102002516
# El Vado Reservoir: 13020102002525
# Abiquiu Lake: 13020102002576
# Cochiti Lake: 13020201001130
# Nambe Lake: 13020101001949
expression = "\"REACHCODE\" IN ('13020102002516', '13020102002525', '13020102002576', '13020201001130', '13020101001949')"

#Execute Selection
for fc in joinList:
    arcpy.MakeFeatureLayer_management(fc, "temp") 
    arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
    output = os.path.join(out_gdb, "SJCP_Reservoirs")
    arcpy.CopyFeatures_management("temp", output)
    # Create update cursor for feature class
    field = "GNIS_NAME"
    cursor = arcpy.UpdateCursor(output)
    # For each row, evaluate the REACHCODE value
        # Update the values in GNIS_NAME
    for row in cursor:
        value1 = row.getValue("REACHCODE")
        if value1 == '13020101001949':
            row.setValue(field, 'Nambe Falls')
        # Update the cursor
        cursor.updateRow(row)
    finalList.append(output)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Create the SJCP users "Irrigation"
## Description: Select the irrigation districts using SJCP water, with Select Layer By Attribute

print "\nStep 4 Create the SJCP irrigation districts starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\7_irrigation_organization\\final_output\\NM_Irrigation_Districts_ses.shp"

# Output name
output = os.path.join(out_gdb, "SJCP_UserIrrigation")

#Name Irrigation District using SJCP waters
#Middle Rio Grande Conservancy District
expression = "\"ID_DIST\" = 'MRGCD'"

#Execute Selection
arcpy.MakeFeatureLayer_management(in_file, "temp") 
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", output)
arcpy.AlterField_management(output, "Name", "NAME")
arcpy.AddField_management(output, "USE", "TEXT", "", "", 50)
arcpy.CalculateField_management(output, "USE", "'" + 'Irrigation District' + "'", "PYTHON_9.3")
# Create list of all fields
fieldNameList = [field.name for field in arcpy.ListFields(output)]

# Items to be removed from the list of field
del fieldNameList[4]

unwanted = {"FID", "Shape", "USE", "OBJECTID_1", "Shape_Length", "Shape_Area"}

fieldNameList = [elem for elem in fieldNameList if elem not in unwanted]

arcpy.DeleteField_management(output, fieldNameList)
    
userList.append(output)


print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Create the SJCP municipalities 
## Description: Select the municipalities using SJCP water, using Select Layer By Attribute

print "\nStep 5 Create the SJCP municipalities starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Places.shp"

# Output name
output = os.path.join(out_gdb, "SJCP_UserMunicipal")

#Name places using SJCP waters
# Cities/Town:
# Albuquerque: 8403502000
# Santa Fe: 8403570500
# Española: 8403525170
# Belen: 8403506480
# Taos: 8403576200
# Los Lunas: 8403543370
# Bernalillo: 8403506970
# Red River: 8403562200

expression = """"ADM3_GEOID" IN ('8403502000', '8403570500',
'8403525170', '8403506480', '8403576200', '8403543370', '8403506970',
'8403562200')"""

#Execute Selection
arcpy.MakeFeatureLayer_management(in_file, "temp") 
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", output)
arcpy.AlterField_management(output, "NAME_3", "NAME")
arcpy.AddField_management(output, "USE", "TEXT", "", "", 50)
arcpy.CalculateField_management(output, "USE", "'" + 'Municipality' + "'", "PYTHON_9.3")

# Create list of all fields
fieldNameList = [field.name for field in arcpy.ListFields(output)]

del fieldNameList[9]
unwanted = {"FID", "Shape", "OBJECTID", "USE", "Shape_Length", "Shape_Area"}

fieldNameList = [elem for elem in fieldNameList if elem not in unwanted]

arcpy.DeleteField_management(output, fieldNameList)
    
userList.append(output)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Create the SJCP county 
## Description: Select the county using SJCP water, using Select Layer By Attribute

print "\nStep 6 Create the SJCP municipalities starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
in_file = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\1_political_jurisdictions\\final_output\\Census\\Counties_and_Municipios.shp"

# Output name
output = os.path.join(out_gdb, "SJCP_UserCounty")

# Counties
# Los Alamos: 84035028
# Santa Fe: 84035049
expression = """"ADM2_GEOID" IN ('84035028', '84035049')"""

#Execute Selection
arcpy.MakeFeatureLayer_management(in_file, "temp") 
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", output)
arcpy.AlterField_management(output, "NAME_2", "NAME")
arcpy.AddField_management(output, "USE", "TEXT", "", "", 50)
arcpy.CalculateField_management(output, "USE", "'" + 'County' + "'", "PYTHON_9.3")

# Create list of all fields
fieldNameList = [field.name for field in arcpy.ListFields(output)]

del fieldNameList[10]

unwanted = {"FID", "Shape", "OBJECTID", "USE", "Shape_Length", "Shape_Area"}

fieldNameList = [elem for elem in fieldNameList if elem not in unwanted]

arcpy.DeleteField_management(output, fieldNameList)
    
userList.append(output)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 7. Create the SJCP Tribes
## Description: Select the tribes using SJCP water, using Select Layer By Attribute

print "\nStep 7 Create the SJCP tribes starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_file = "tl_2016_us_aiannh.shp"

# Output
output = os.path.join(out_gdb, "SJCP_UserTribe")

# Expression
# Jicarilla Apache Nation
expression = "\"AIANNHNS\" = '01934339'"

#Execute Selection
arcpy.MakeFeatureLayer_management(in_file, "temp") 
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", output)
arcpy.AddField_management(output, "USE", "TEXT", "", "", 50)
arcpy.CalculateField_management(output, "USE", "'" + 'Tribe' + "'", "PYTHON_9.3")

# Create list of all fields
fieldNameList = [field.name for field in arcpy.ListFields(output)]

del fieldNameList[6]

unwanted = {"FID", "Shape", "NAME", "OBJECTID", "OBJECTID_1", "USE", "Shape_Length", "Shape_Area"}

fieldNameList = [elem for elem in fieldNameList if elem not in unwanted]

arcpy.DeleteField_management(output, fieldNameList)

userList.append(output)

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 8. Create the SJCP Reservoir User
## Description: Select the tribes using SJCP water, using Select Layer By Attribute

print "\nStep 8 Create the SJCP Reservoir User starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
in_file = os.path.join(out_gdb, "SJCP_Reservoirs")

# Output
output = os.path.join(out_gdb, "SJCP_UserCochiti")
# Expression
# Cochiti Lake: 13020201001130
expression = "\"REACHCODE\" = '13020201001130'"

#Execute Selection
arcpy.MakeFeatureLayer_management(in_file, "temp") 
arcpy.SelectLayerByAttribute_management("temp", "NEW_SELECTION", expression)
arcpy.CopyFeatures_management("temp", output)
arcpy.AlterField_management(output, "GNIS_NAME", "NAME")
arcpy.AddField_management(output, "USE", "TEXT", "", "", 50)
arcpy.CalculateField_management(output, "USE", "'" + 'Recreation, fish and wildlife' + "'", "PYTHON_9.3")
# Create list of all fields
fieldNameList = [field.name for field in arcpy.ListFields(output)]

del fieldNameList[6]

unwanted = {"FID", "Shape", "OBJECTID", "NAME", "USE", "Shape_Length", "Shape_Area"}

fieldNameList = [elem for elem in fieldNameList if elem not in unwanted]

arcpy.DeleteField_management(output, fieldNameList)
userList.append(output)


print "Step 8 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 9. Merge SJCP Users into a single output feature
## Description: Select the tribes using SJCP water, using Select Layer By Attribute

print "\nStep 9 Create the SJCP Reservoir User starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

output = os.path.join(out_gdb, "SJCP_Users")
arcpy.Merge_management(userList, output)
## Add a field VOLUME
arcpy.AddField_management(output, "VOLUME", "FLOAT")
arcpy.AddField_management(output, "SJCPID", "TEXT")

fieldVolume = "VOLUME"
fieldID = "SJCPID"
cursor = arcpy.UpdateCursor(output)
# For each row, evaluate the REACHCODE value
    # Update the values in VOLUME
for row in cursor:
    value1 = row.getValue("NAME")
    if value1 == 'Albuquerque':
        row.setValue(fieldVolume, '48200')
        row.setValue(fieldID, '01')
    if value1 == 'Middle Rio Grande Conservancy District':
        row.setValue(fieldVolume, '20900')
        row.setValue(fieldID, '02')
    if value1 == 'Jicarilla Apache Nation':
        row.setValue(fieldVolume, '6500')
        row.setValue(fieldID, '03')
    if value1 == 'Santa Fe':
        row.setValue(fieldVolume, '5605')
        value2 = row.getValue("USE")
        if value2 == 'County':
            row.setValue(fieldID, '04')
        if value2 == 'Municipality':
            row.setValue(fieldID, '05')        
    if value1 == 'Cochiti Lake':
        row.setValue(fieldVolume, '5000')
        row.setValue(fieldID, '06')
    if value1 == 'Los Alamos':
        row.setValue(fieldVolume, '1200')
        row.setValue(fieldID, '07')
    if value1.startswith('Espa'):
        row.setValue(fieldVolume, '1000')
        row.setValue(fieldID, '08')
    if value1 == 'Belen':
        row.setValue(fieldVolume, '500')
        row.setValue(fieldID, '09')
    if value1 == 'Los Lunas':
        row.setValue(fieldVolume, '400')
        row.setValue(fieldID, '10')
    if value1 == 'Taos':
        row.setValue(fieldVolume, '400')
        row.setValue(fieldID, '11')
    if value1 == 'Bernalillo':
        row.setValue(fieldVolume, '400')
        row.setValue(fieldID, '12')
    if value1 == 'Red River':
        row.setValue(fieldVolume, '60')
        row.setValue(fieldID, '13')

# Update the cursor
    cursor.updateRow(row)

finalList.append(output)

print "Step 9 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 10. Project the polygon
## Description: Project to North America Albers Equal Area Conic

print "\nStep 10 Projection starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

fieldsDel = ["OBJECTID", "OBJECTID_1", "Shape_Area", "Shape_Leng", "SHAPE_LENG", "Shape_Length", "Shape_Le_1"]

for fc in finalList:
    name = os.path.split(fc)[1] + '.shp'
    projFile = os.path.join(finalFolder, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    arcpy.DeleteField_management(projFile, fieldsDel) 
print "Step 10 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



