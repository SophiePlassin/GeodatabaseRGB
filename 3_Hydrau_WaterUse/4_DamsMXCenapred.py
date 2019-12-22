# -*- coding: cp1252 -*-
# -*- coding: utf-8 -*-

# DamsCENAPRED.py
## Created on: 2019-05-17
## By: Sophie Plassin
## Description: Preparation of the NID Dams shapefile for the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Project the shapefile to North America Albers Equal Area Conic
##              3. Edit attribute tables
##              4. Convert excel to dbf and join
##              3. Clip to the boundary of the study area
##              4. Clean the dataset
##              5. Save output data to final folder
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
projList = []
clipList = []
finalList = []

## ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a geodatabase to store features

print "\nStep 1 Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_file = "presas"
gdb_name = "Dams_CENAPRED.gdb"
data_type = "FeatureClass"
out_gdb = os.path.join(interFolder, gdb_name)
arcpy.CreateFileGDB_management(interFolder, gdb_name)
arcpy.FeatureClassToGeodatabase_conversion(in_file + ".shp", out_gdb)

print "Step 1 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 2. Project
## Description: Project to North America Albers Equal Area Conic

print "\nStep 2 Project starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

fc_gdb = os.path.join(out_gdb, in_file)
name = "Dams_mx_pr"
projFile = os.path.join(out_gdb, name)
arcpy.Project_management(fc_gdb, projFile, outCS)
projList.append(projFile)

print "Step 2 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 3. Edit attribute table
## Description: Add new fields (units in U.S. system)

print "\nStep 3 Clean the dataset starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Add new fields
fieldTypeTX = "TEXT"
fieldID = "CENAPR_ID"

arcpy.AddField_management(projFile, fieldID, fieldTypeTX) # field ID

arcpy.CalculateField_management(projFile, fieldID, "!ID_CT!", "PYTHON_9.3") # Populate field ID

# Del fields
fieldsDel = ["NUM", "NOM_OFICIA", "NOM_COM", "ESTADO", "ZONA_SISM",
             "USO", "PROPÓSITO", "CORRIENTE", "ORG_RESP", "MUN",
             "LONGITUD", "LATITUD", "VOL_NAMO", "ALT_MAX_CO"]

arcpy.DeleteField_management(projFile, fieldsDel)


print "Step 3 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Convert excel to dbf and Join table with shapefile
## Description: Convert excel to dbf and Join table with shapefile

print "\nStep 4. Convert excel to dbf starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

in_excel = "\\prepared\\Presas_prepared.xlsx"
name = os.path.split(in_excel)[1] 
dbf_file = os.path.splitext(name)[0]+ ".dbf"
out_dbf_file = os.path.join(interFolder, dbf_file)
arcpy.ExcelToTable_conversion(in_excel, out_dbf_file)


# FIelds for join
joinFieldLayer = "CENAPR_ID"
joinFieldTable = "ID_CT"

# Output
outname = "Dams_mx_join"
out_fc = os.path.join(out_gdb, outname)

arcpy.MakeFeatureLayer_management(projFile, "temp")
arcpy.AddJoin_management("temp",
                         joinFieldLayer,
                         out_dbf_file,
                         joinFieldTable)
arcpy.CopyFeatures_management("temp", out_fc)

print "Step 4 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 5. Clip
## Description: Clip to the boundaries of the study area

print "\nStep 5 Clip the features starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Create the clip_features
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
xy_tolerance = ""
clip_features = []

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    clip_features.append(out_shp)

# Execute Clip
in_fc = out_fc
for clip in clip_features:
    # Create name
    new_name = in_fc.split('_join')[0]
    temp = os.path.split(clip)[-1]
    # Add Ses or Bas according to the clip feature name
    if temp.startswith("RGB_Basin"):
        output = new_name + "_bas"
    else:
        output = new_name + "_ses"
    arcpy.Clip_analysis(in_fc, clip, output, xy_tolerance)
    clipList.append(output)
    print "Clip" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 5 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 6. Clean the attribute table
## Description: Clip to the boundaries of the study area


print "\nStep 6 Clean the attribute table starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Add new fields
fieldTypeNb = "FLOAT"
fieldHgtF = "DAM_HGT_f"
fieldCapMF = "MAXSTO_af"
fieldListNb= [fieldHgtF, fieldCapMF]

for fc in clipList:
    for fn in fieldListNb:
        arcpy.AddField_management(fc, fn, fieldTypeNb) #  fields acre feet
# Translate values of fields from Spanish to English
    cur = arcpy.UpdateCursor(fc)
    for row in cur:

        # Translate English Values SEISMIC_Z       
        value1 = row.getValue("SEISMIC_Z")
        if value1 == "Asismica":
            row.setValue("SEISMIC_Z", "Aseismic")
        elif value1 == "Baja Sismicidad":
            row.setValue("SEISMIC_Z", "Low Seismicity")
        elif value1 == "Alta Sismicidad":
            row.setValue("SEISMIC_Z", "High Seismicity")        
        elif value1 == "Media Sismicidad":
            row.setValue("SEISMIC_Z", "Medium Seismicity")
        else:
            row.setValue("SEISMIC_Z", "N/A")

        # Translate English Values USE
        use = "USE"
        value2 = row.getValue(use)
        if value2 == "Abrevadero":
            row.setValue(use, "Livestock")
               
        elif value2 == "Abrevadero Y Recreativo":
            row.setValue(use, "Livestock, Recreation")
               
        elif value2 == "Abrevadero, Acuacultura Y Pesca":
            row.setValue(use, "Livestock, Aquaculture, Fishing")
               
        elif value2 == "Acuacultura, Pesca Y Recreativo":
            row.setValue(use, "Aquaculture, Fishing, Recreation")
               
        elif value2 == "Abrevadero, Acuacultura, Pesca Y Recreativo":
            row.setValue(use, "Livestock, Aquaculture, Fishing, Recreation")

        elif value2 == "Agua Potable":
            row.setValue(use, "Potable Water")
               
        elif value2 == "Agua Potable Y Abrevadero":
            row.setValue(use, "Potable Water, Livestock")
               
        elif value2. startswith ("Generaci") and value2.endswith ("ctrica"):
            row.setValue(use, "Electrical Generation")
               
        elif value2.startswith ("Infiltraci"):
            row.setValue(use, "Infiltration")
               
        elif value2 == "Riego":
            row.setValue(use, "Irrigation")
               
        elif value2 == "Riego Y Agua Potable":
            row.setValue(use, "Irrigation, Potable Water")
               
        elif value2 == "Riego Y Abrevadero":
            row.setValue("USE", "Irrigation, Livestock")
               
        elif value2.startswith ("Riego y generaci"):
            row.setValue(use, "Irrigation, Electrical generation")
               
        elif value2 == "Riego Y Recreativo":
            row.setValue(use, "Irrigation, Recreation")
               
        elif value2 == "Riego, Acuacultura Y Pesca":
            row.setValue(use, "Irrigation, Aquaculture, Fishing")
               
        elif value2 == "Riego, Abrevadero Y Recreativo":
            row.setValue(use, "Irrigation, Livestock, Recreation")
               
        elif value2 == "Riego, Agua potable Y Abrevadero":
            row.setValue("USE", "Irrigation, Potable Water, Livestock")
               
        elif value2 == "Riego, Acuacultura, Pesca Y Abrevadero":
            row.setValue(use, "Irrigation, Aquaculture, Fishing, Livestock")

        elif value2.startswith ("Riego, Generaci") and value2.endswith ("Potable"):
            row.setValue(use, "Irrigation, Electrical generation, Potable Water")
               
        elif value2.startswith ("Riego, Agua Potable, Abrevadero"):
            row.setValue(use, "Irrigation, Potable Water, Livestock, Infiltration")
               
        elif value2.startswith ("Riego, Generaci") and value2.endswith ("Recreativo"):
            row.setValue("USE", "Irrigation, Electrical generation, Aquaculture, Fishing, Recreation")
               
        elif value2 == "":
             row.setValue(use, "N/A")        

        # Translate in English Values of field PURPOSES
        purpose = 'PURPOSES'
        value3 = row.getValue(purpose)
        if value3 == "Almacenamiento":
            row.setValue(purpose, "Storage")
            
        elif value3 == "Control De Avenidas":
            row.setValue(purpose, "Flood Control")
            
        elif value3 == "Control De Azolves":
            row.setValue(purpose, "Sediment Control")
            
        elif value3.endswith ("Jales"):
            row.setValue(purpose, "Sediment Control")
            
        elif value3.startswith ("Derivaci"):
            row.setValue(purpose, "Diversion")
            
        elif value3 == "Fuera De Uso":
            row.setValue(purpose, "Out of Use")
            
        elif value3 == "Otros Fines":
            row.setValue(purpose, "Other Purposes")
            
        elif value3.endswith("Inundaciones"):
            row.setValue(purpose, "Flood Protection")
            
        elif value3.startswith("Regulaci"):
            row.setValue(purpose, "Streamflow Change Regulation")

        # Change ID States
        value4 = row.getValue("STATEID")
        if value4 == "Coahuila De Zaragoza":
            row.setValue("STATEID", "05")
            
        elif value4 == "Chihuahua":
            row.setValue("STATEID", "08")
            
        elif value4 == "Durango":
            row.setValue("STATEID", "10")
            
        elif value4 == "Nuevo Leon":
            row.setValue("STATEID", "19")
            
        elif value4 == "Tamaulipas":
            row.setValue("STATEID", "28")            
        cur.updateRow(row)
           

# Convert values: Mcm => Acre feet // Meter => feet
    arcpy.CalculateField_management(fc, fieldHgtF, "!DAM_HGT_m! * 3.28084", "PYTHON_9.3")
    arcpy.CalculateField_management(fc, fieldCapMF, "!MAXSTO_mcm! * 810.714", "PYTHON_9.3")

print "Step 6 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 7. Copy and paste to final location
## Description: Save shapefile into final folder

print "\nStep 7 Save to final location starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

fieldsDel = ["ID_CT", "ID_CT_1", "OID_", "FID_",
             "OBJECTID", "OBJECTID_2", "NUM"]

for fc in clipList:
    oRoot, oExt = os.path.split(fc)
    out_feature = os.path.join(finalFolder, oExt + ".shp")
    arcpy.CopyFeatures_management(fc, out_feature)
    arcpy.DeleteField_management(out_feature, fieldsDel)

print "Step 7 completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


