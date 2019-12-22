# -*- coding: cp1252 -*-
## Name: IrrigationOrganization.py
## Created on: 2019-07-07
## By: Sophie Plassin
## Description: Preparation of the Irrigation Organization dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Rename and export feature class
##              3. Edit attribute table
##              4. Project the dataset to North America Albers Equal Area Conic
##              5. Join the Mexican datasets (2015-2016 and 2016-2017)
##              6. Select the districts in the RGB
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
# -*- coding: utf-8 -*-

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Workspace
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\7_irrigation_organization\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\7_irrigation_organization\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\7_irrigation_organization\\final_output\\"
arcpy.env.workspace = dirpath

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
fcList = arcpy.ListFeatureClasses()
gdb_name = "IrrigationOrganization.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Rename and export feature class
## Description: Rename feature class

print "\nStep 2 Rename and export feature class starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

gdbList = []

outNameList = ["MX_Distritos_Riego_2015_2016", "MX_Distritos_Riego_2016_2017", "CO_Irrigation_Organizations",
               "NM_Irrigation_Districts", "TX_Water_Districts"]
sortedList = sorted(fcList)

for fc in sortedList:
    arcpy.FeatureClassToGeodatabase_conversion(fc, out_gdb)
    feature = fc.split(".shp")[0]
    fc_gdb = os.path.join(out_gdb, feature)
    if feature.startswith("NM"):
        gdbList.append(fc_gdb)
    else:
        index = fcList.index(fc)
        out_featureclass = os.path.join(out_gdb, outNameList[index])
        arcpy.Rename_management(fc_gdb, out_featureclass, data_type)
        gdbList.append(out_featureclass)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Edit attribute table
## Description: Rename and delete fields

print "\nStep 3 Add and delete fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldsDel = ["WD", "DITCH_STR", "created_us", "created_da", "last_edite", "last_edi_1", "DATE_ESTD",
             "Shape__Are", "Shape__Len", "SHAPE_Leng", "GlobalID", "PERIMETER", "SubDivisio", "PLAT_ACRES", "nom_rh", "año_agr"]

# Delete and add fields
# New fields
fieldDitchType = "Type"
fieldArea = "Area_ha"
fieldID = "ID_DIST"
fieldState = "State"
# List fields
fieldTypeTx = "TEXT"
fieldTypeNb = "DOUBLE"
# Execute
for infc in gdbList:
    arcpy.DeleteField_management(infc, fieldsDel)
    name = os.path.split(infc)[1]
    if name.startswith("NM"):
        arcpy.AddField_management(infc, fieldID, fieldTypeTx, "", "", "60")
    if name.startswith("TX"):
        pass
    else:
        arcpy.AddField_management(infc, fieldDitchType, fieldTypeTx, "", "", "60")
    if name.startswith("MX"):
        pass
    else:
        arcpy.AddField_management(infc, fieldArea, fieldTypeNb)
        arcpy.AddField_management(infc, fieldState, fieldTypeTx,"", "", "50")

# Rename fields
# List of fields to change
alterFieldsCO = [["DITCH_ID", "ID_DIST"], ["DITCH_NAME", "Name"], ["DITCH_ID6", "ID6_DIST"], ["DITCH_ID7", "ID7_DIST"],
                 ["ACREAGE", "Area_ac"], ["COMMENT", "Comment"], ["CHANGECOMM", "ChangeComm"]]
alterFieldsNM = [["District", "Name"], ["ACRES", "Area_ac"]]               
alterFieldsTX = [["DISTRICT_I", "ID_DIST"], ["NAME", "Name"], ["TYPE", "Type"], ["COUNTY", "County"], ["COGO_ACRES", "Area_ac"],
                 ["DIGITIZED", "Digitized"], ["STATUS", "Status"], ["CREATION_D", "Creation_D"], ["BNDRY_CHAN", "Bndry_Chan"],
                 ["METHOD", "Method"], ["SOURCE", "Source"], ["ACCURACY", "Accuracy"], ["COMMENTS", "Comments"],
                 ["INITIALS", "Initials"], ["UPDATED", "Updated"], ["TX_CNTY", "TX_Cnty"]]
alterFieldsMX = [["id_dr", "ID_DIST"], ["nom_dr", "Name"], ["nom_edo", "State"], ["nom_rha", "Name_RHA"]]
alterFieldsMX15 = [["num_usu", "User_1516"], ["sup_tot", "Area1516"], ["sup_rtot", "AreaIR1516"], ["sup_rasup", "AreaSW1516"],
                 ["sup_rasub", "AreaGW1516"], ["vol_asup", "VolSW1516"], ["vol_asub", "VolGW1516"], ["vol_atot", "VolTO1516"]]
alterFieldsMX16 = [["num_usu", "User_1617"], ["sup_tot", "Area1617"], ["sup_rtot", "AreaIR1617"], ["sup_rasup", "AreaSW1617"],
                 ["sup_rasub", "AreaGW1617"], ["vol_asup", "VolSW1617"], ["vol_asub", "VolGW1617"], ["vol_atot", "VolTO1617"]]

# Execute
for fc in gdbList:
    name = os.path.split(fc)[1]
    # Rename CO fields
    if name.startswith("CO"):
        for old, new in alterFieldsCO:
            tmpName = ("{0}_tmp".format(old))
            arcpy.AlterField_management(fc, old, tmpName)
            arcpy.AlterField_management(fc, tmpName, new)
        # Add name of state Colorado
        arcpy.CalculateField_management(fc,
                                        fieldState,
                                        "'{0}'".format(str("Colorado")),
                                        "PYTHON_9.3", "")
    # Rename NM fields
    if name.startswith("NM"):
        for old, new in alterFieldsNM:
            tmpName = ("{0}_tmp".format(old))
            arcpy.AlterField_management(fc, old, tmpName)
            arcpy.AlterField_management(fc, tmpName, new)
       # Add name of state New Mexico
        arcpy.CalculateField_management(fc,
                                        fieldState,
                                        "'{0}'".format(str("New Mexico")),
                                        "PYTHON_9.3", "")
    # Rename TX fields
    if name.startswith("TX"):
        for old, new in alterFieldsTX:
            tmpName = ("{0}_tmp".format(old))
            arcpy.AlterField_management(fc, old, tmpName)
            arcpy.AlterField_management(fc, tmpName, new)
       # Add name of state Texas
        arcpy.CalculateField_management(fc,
                                        fieldState,
                                        "'{0}'".format(str("Texas")),
                                        "PYTHON_9.3", "")
    # Rename MX fields
    if name.startswith("MX"):
        for old, new in alterFieldsMX:
            tmpName = ("{0}_tmp".format(old))
            arcpy.AlterField_management(fc, old, tmpName)
            arcpy.AlterField_management(fc, tmpName, new)
    if name.endswith("2015_2016"):
        for old, new in alterFieldsMX15:
            tmpName = ("{0}_tmp".format(old))
            arcpy.AlterField_management(fc, old, tmpName)
            arcpy.AlterField_management(fc, tmpName, new)
    if name.endswith("2016_2017"):
        for old, new in alterFieldsMX16:
            tmpName = ("{0}_tmp".format(old))
            arcpy.AlterField_management(fc, old, tmpName)
            arcpy.AlterField_management(fc, tmpName, new)

# Update lines
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        # Update for CO
        if name.startswith("CO"):
            value12 = row.getValue("Name")
            if value12.startswith('San Luis Valley ID'):
                row.setValue(fieldDitchType, 'ID')
            else:
                row.setValue(fieldDitchType, 'Ditch Companies or Community Ditch')
        # Update for NM
        if name.startswith("NM"):
            value1 = row.getValue("Name")
            if value1.startswith('Carlsbad Irrigation District'):
                row.setValue(fieldID, 'CID')
            elif value1.startswith('Elephant Butte Irrigation District'):
                row.setValue(fieldID, 'EBID')
            elif value1.startswith('Fort Sumner Irrigation District'):
                row.setValue(fieldID, 'FSID')
            elif value1.startswith('Middle Rio Grande Conservancy District'):
                row.setValue(fieldID, 'MRGCD')
            elif value1.startswith('Pecos Valley Artesian Conservancy District'):
                row.setValue(fieldID, 'PVACD')
            row.setValue(fieldDitchType, 'ID')
        if name.startswith("MX"):
            row.setValue(fieldDitchType, 'ID')
        cur.updateRow(row)

# Calculate Area in hectares
    if name.startswith ("MX"):
        pass
    else:
        arcpy.CalculateField_management(fc, fieldArea, "!Area_ac! * 0.404686", "PYTHON_9.3")
        
print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Project the polygon
## Description: Project to North America Albers Equal Area Conic

print "\nStep 4 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

projList = []

for fc in gdbList:
    name = os.path.split(fc)[1] + '_pr'
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    projList.append (projFile)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Join MX datasets 2015-2016 + 2016-2017
## Description: Join Mexican datasets with Union

print "\nStep 5 Merge MX datasets starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

MXList = []
finalList = []
for fc in projList:
    name = os.path.split(fc)[1] + '_pr'
    if name.startswith("MX"):
        MXList.append(fc)
    else:
        finalList.append(fc)

MXFieldsDel = ["ID_DIST_1", "Name_1", "State_1", "Name_RHA_1", "Type_1",
               "FID_MX_Distritos_Riego_2015_2016_pr", "FID_MX_Distritos_Riego_2015_2016_pr"]
output = os.path.join(out_gdb, "MX_Distritos_Riego")
arcpy.Union_analysis(MXList, output)
arcpy.DeleteField_management(output, MXFieldsDel)
finalList.append(output)
          
print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Select by location
## Description: Select all districts that intersect the study area

print "\nStep 6 Select by location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the select_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
xy_tolerance = ""
selectList = []

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    selectList.append(out_shp)

# Execute Select by location and delete fields
fiedlDel = ["FID_MX_Dis"]
for fc in finalList:
    root = fc.split('_pr')[0]
    name = os.path.split(root)[1]
    for clip in selectList:
        temp = os.path.split(clip)[-1]
        print temp
        if temp.startswith ("RGB_Basin"):
            output = finalFolder + name + "_bas.shp"
        else:
            output = finalFolder + name + "_ses.shp"
        arcpy.MakeFeatureLayer_management(fc, "temp")
        arcpy.SelectLayerByLocation_management("temp", 'INTERSECT', clip)
        arcpy.CopyFeatures_management("temp", output)
        arcpy.DeleteField_management(output, fiedlDel)
        print "Select by location" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 6 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

