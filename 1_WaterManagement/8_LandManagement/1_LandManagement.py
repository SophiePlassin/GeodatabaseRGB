## Name: Land_Ownership.py
## Created on: 2019-07-07
## By: Sophie Plassin
## Description: Preparation of the Land Ownership dataset for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
## For US BLM dataset:
##              2. Extract package
##              3. Export feature class to geodatabase
## For MX RAN dataset:     
##              4. Export shapefiles in geodatabase
##              5. Merge State datasets
## For both datasets:
##              6. Edit attribute table
##              7. Project the datasets to North America Albers Equal Area Conic
##              8. Clip the datasets
##              9. Merge US and MX feature class
##              10. Symmetrical difference
##              11. Merge Public and Private lands datasets
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
dirpath = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\8_land_management\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\8_land_management\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\8_land_management\\final_output\\"
arcpy.env.workspace = dirpath

# List
cntry_List = []
inputs_bas = []
inputs_ses = []
finalList = []
list1 = []
list2 = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features and export

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input name
gdb_name = "LandOwnership.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)

#Execute
arcpy.CreateFileGDB_management(interFolder, gdb_name)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Extract Package
## Description: Extract the contents of the BLM package to the geodatabase

print "\nStep 2 Extract package starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

#Execute Extract Package
arcpy.ExtractPackage_management('BLM_National_Surface_Management_Agency.lpk', interFolder + "\\Unpacked\\")

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 3. Export Feature Class to geodatabase
## Description: Export US land management feature to the geodatabase

print "\nStep 3 Export US land management feature to gdb starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

us_gdb = interFolder + "\\Unpacked\\v101\\sma_wm.gdb\\"
feature = "SurfaceManagementAgency"
fc = os.path.join(us_gdb, feature)
arcpy.FeatureClassToShapefile_conversion(fc, out_gdb)
fc_gdb = os.path.join(out_gdb, feature)
out_featureclass = os.path.join(out_gdb, "US_Land_Management")
arcpy.Rename_management(fc_gdb, out_featureclass, data_type)
cntry_List.append(out_featureclass)

print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Export kml to geodatabase
## Description: Export MX land management feature  to the geodatabase

print "\nStep 4 Export MX land management feature to gdb starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


outputList = []

for path, dirs, files in os.walk(dirpath):
    for fc in files:
        if fc.startswith("PERIMETRAL") and fc.endswith(".shp"):
            out_name = os.path.splitext(fc)[0]
            in_fc = os.path.abspath(os.path.join(path, fc))
            arcpy.FeatureClassToFeatureClass_conversion(in_fc, out_gdb, out_name)
            out_feature = os.path.join(out_gdb, out_name)
            outputList.append(out_feature)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Merge MX datasets
## Description: Merge MX datasets into one layer

print "\nStep 5 Export feature class to gdb starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

name = "MX_Edijo_Communal_Land"
output = os.path.join(out_gdb, name)
arcpy.Merge_management(outputList, output)
cntry_List.append(output)

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
##
## ---------------------------------------------------------------------------
## 6. Edit attribute tables in the US and MX dataset
## Description: Add and delete fields for consistency

print "\nStep 6 Add and delete fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldTypeTx = "TEXT"
fieldDel= ["EDO_CLV", "MUN_CLV", "NUC_CLV", "PROGRAMA", "CLAVE", "Clv_Unica", "Fol_Matriz", "MUNICIPIO",
           "HOLD_DEPT_CODE", "HOLD_AGENCY_CODE", "HOLD_ID"]
field_2 = "MANGTYPE_2"
field_1 = "MANGTYPE_1"
newFields = [field_1, field_2]

# Delete fields
for infc in cntry_List:
    arcpy.DeleteField_management(infc, fieldDel)

# Add fields
    for fd in newFields:
        arcpy.AddField_management(infc, fd, fieldTypeTx, "", "", "100")

# Populate new field with values of ADMIN_UNIT_NAME
    name = os.path.split(infc)[1]
    if name.startswith("US"):
        arcpy.CalculateField_management(infc, field_2, "!ADMIN_UNIT_NAME!", "PYTHON_9.3")
#Update lines
    cur = arcpy.UpdateCursor(infc)
    for row in cur:
        
        if name.startswith("MX"):
            row.setValue(field_1, 'Certified Ejido & Communal Land')
            value2 = row.getValue("tipo")
            if value2 == 'Ejido':
                row.setValue(field_2, 'Ejido')
            if value2 == 'Comunidad':
                row.setValue(field_2, 'Comunidad')
        if name.startswith("US"):
            value1 = row.getValue("ADMIN_AGENCY_CODE")
            if value1 == 'BIA':
                row.setValue(field_1, 'Native American/tribal')
            elif value1 == 'PVT':
                row.setValue(field_2, 'Private or Not Reported')
                row.setValue(field_1, 'Private or Not Reported')
            else:
                row.setValue(field_1, 'Public')
        cur.updateRow(row)

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 7. Project the polygon
## Description: Project to North America Albers Equal Area Conic

print "\nStep 7 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

projList = []

for fc in cntry_List:
    name = os.path.split(fc)[1] + '_pr'
    projFile = os.path.join(out_gdb, name)
    arcpy.Project_management(fc, projFile, outCS)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    projList.append(projFile)

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")



## ---------------------------------------------------------------------------
## 8. Clip
## Description: Clip the feature class with the study area layer

print "\nStep 8 Clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the select_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clipped_features = []

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clipped_features.append(out_shp)

# Execute Select by location and delete fields
for fc in projList:
    root = fc.split('_pr')[0]
    name = os.path.split(root)[1]
    for clip in clipped_features:
        temp = os.path.split(clip)[-1]
        if temp.startswith("RGB_Basin"):
            output = out_gdb + "\\" + name + "_bas"
        else:
            output = out_gdb + "\\" + name + "_ses"
        arcpy.Clip_analysis(fc, clip, output, xy_tolerance)
        print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 8 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## ---------------------------------------------------------------------------
## 9. Merge US and MX feature class
## Description: Merge US and MX feature class

print "\nStep 9 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Water_Governance\\8_land_management\\inter_output\\LandOwnership.gdb"

# Input names
inputs_bas = arcpy.ListFeatureClasses("*_bas")
inputs_ses = arcpy.ListFeatureClasses("*_ses")

# Output names
output = "Land_Management_NoSymetricDiff"
output_bas = output + "_bas"
output_ses = output + "_ses"

finalList = []

# Execute
arcpy.Merge_management(inputs_bas, output_bas)
arcpy.Merge_management(inputs_ses, output_ses)
finalList.extend([output_bas, output_ses]) 

# Update Attribute table
for fc in finalList:
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        value1 = row.getValue(field_1)
        if value1 == "Certified Ejido & Communal Land":
            row.setValue("ADMIN_AGENCY_CODE", 'RAN')
            row.setValue("ADMIN_DEPT_CODE", 'RAN')
        cur.updateRow(row)
    arcpy.AlterField_management(fc, "NOM_NUC", "NAME")


print "Step 9 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## ---------------------------------------------------------------------------
## 10. Symmetrical difference
## Description: Portions of the RGB that do not overlap with the BLM and certified edjido dataset is classified as private/undetermined in the output feature class

print "\nStep 10 Symmetrical Difference starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Input
inFeatures = arcpy.ListFeatureClasses("Land_Management_NoSymetricDiff*")

# Execute SymDiff
newList =[]
delFields = ["FID_RGB_BO", "Id", "Area", "FID_RGB_Ba", "MAJ_BAS", "Shape_Le_1", "Shape_Ar_1"]

name = "NotReported"
for fc in inFeatures:
    for clip in clipped_features:
        temp = os.path.split(clip)[-1]
        if temp.startswith("RGB_Basin") and fc.endswith("_bas"):
            output = out_gdb + "\\" + name + "_bas"
            arcpy.SymDiff_analysis(fc, clip, output)
        if temp.startswith("RGB_Ses") and fc.endswith("_ses"):
            output = out_gdb + "\\" + name + "_ses"
            arcpy.SymDiff_analysis(fc, clip, output)
        cur = arcpy.UpdateCursor(output)
        for row in cur:
            row.setValue("MANGTYPE_2", 'Private or Not Reported')
            row.setValue("ADMIN_AGENCY_CODE", 'PVT')
            row.setValue("ADMIN_DEPT_CODE", 'PVT')
            row.setValue("MANGTYPE_1", 'Private or Not Reported')
            row.setValue("ADMIN_UNIT_TYPE", 'Not Applicable')
            cur.updateRow(row)
        arcpy.DeleteField_management(output,delFields)
        
print "Step 10 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## ---------------------------------------------------------------------------
## 11. Merge Public and communal lands with Private/Undetermined into a new feature class
## Description: Merge Public and communal lands with Private/Undetermined into a new dataset

print "\nStep 11 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Name Input
inputs = []
list1 = arcpy.ListFeatureClasses("*Symetric*")
list2 = arcpy.ListFeatureClasses("*NotReported*")
inputs.extend([list1, list2])

# Name output
output = "Land_Management"

# Merge into a single dataset
inputsBas =[]
inputsSes =[]
outputs = []
for List in inputs:
    for fc in List:
        if fc.endswith ("_bas"):
            inputsBas.append (fc)
            if len(inputsBas)== 2:
                out_feature = os.path.join(finalFolder, output + "_bas.shp")
                arcpy.Merge_management(inputsBas, out_feature)
                outputs.append(out_feature)
        if fc.endswith("_ses"):
            inputsSes.append (fc)
            if len(inputsSes)== 2:
                out_feature = os.path.join(finalFolder, output + "_ses.shp")
                arcpy.Merge_management(inputsSes, out_feature)
                outputs.append(out_feature)

# Recalculate geometry and delete fields
expressionArea = "!shape.area@squarekilometers!"
expressionLength = "!shape.length@kilometers!"
# Fields to delete
delFields = ["SMA_ID", "DE_UNIT_CO", "FID_Land_M", "tipo", "FID_RGB_Bo",
             "FID_RGB_Se", "Id", "Area", "ADMIN_UN_1", "ADMIN_UNIT"]


for fc in outputs:
    arcpy.CalculateField_management(fc, "Shape_Area", expressionArea, "PYTHON_9.3")
    arcpy.CalculateField_management(fc, "Shape_Leng", expressionLength, "PYTHON_9.3")
    # Delete
    for fd in delFields:
        arcpy.DeleteField_management(fc, delFields)

print "Step 11 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

print "\nGeoprocess completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")











