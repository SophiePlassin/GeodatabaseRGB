## Name: Habitat_MX_1.py
## Created on: 2019-12-09
## By: Sophie Plassin
## Description: Preparation of the datasets related to Habitat in the MX portion of the Rio Grande/Bravo basin (RGB)
##              SAP: Sitios de atencion prioritaria para la conservacion de la biodiversidad
##              SPR: Sitios prioritarios para la restauracion (SPR)
##              1. Create a geodatabase
##              2. Project and clip
##              3. Clean the outputs (Translate in English)
##              4. Export final files
# ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import arcpy, os
import datetime

# Directories:
dirpath = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\2_Habitat\\raw_data\\MX\\"
arcpy.env.workspace = dirpath
interFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\2_Habitat\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\2_Habitat\\final_output\\"


# ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a gdb to work with a table format

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(interFolder, "HabMX.gdb")
gdb = os.path.join(interFolder, "HabMX.gdb")


print "Step 1. Create a geodatabase ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Project and clip the files
## Description: Project all features to North America Albers Equal Area Conic,
##              and clip the projected features with the clip of the RGB.
##              Copy int the gdb

print "\nStep 2. Project and clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Define projection
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Define clip variables
clip = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\RGB_Ses_na_albers.shp"
xy_tolerance = ""

inputList = ["sap_gw.shp", "spr_gw.shp"]
outputList = []

for infc in inputList:
    if infc.endswith(".shp"):
        # Project
        path, name = os.path.split(infc)
        projName = os.path.splitext(name)[0] +"_pr"
        projFile = os.path.join(gdb, projName)
        arcpy.Project_management(infc, projFile, outCS)
        print "Project", projName, "ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
        # Clip
        clipName = projName.split('_pr')[0] +"_clip"
        clipFile = os.path.join(gdb, clipName)
        arcpy.Clip_analysis(projFile, clip, clipFile, xy_tolerance)
        outputList.append(clipFile)            
        print "Clip", clipName, "ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "Step 2 Project and clip ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
# 3. Clean the outputs
## Description: Translate Spanish to English (fields and field headers). Remove unecessary fields

print "\nStep 3 Clean the output starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Fields to remove
dropFields = ["Cov_", "Cov_id"]

# Fields to altere (lentgh <= 10 characters)
alterFields= [["PRIORIDAD",     "PRIORITY"],
              ["tipo",          "TYPE"]]

# Remove and Alter fields
for fc in outputList:
    arcpy.DeleteField_management(fc,
                                 dropFields)
    for old, new in alterFields:
        tmpName = ("{0}_tmp".format(old))
        arcpy.AlterField_management(fc, old, tmpName)
        arcpy.AlterField_management(fc, tmpName, new)

# Translate in English
    cur = arcpy.UpdateCursor(fc)
    for row in cur:
        value1 = row.getValue("PRIORITY")
        if value1 == "SAP_media" or value1 == "SPR_media":
            row.setValue("PRIORITY", "Medium")
        elif value1 == "SAP_alta" or value1 == "SPR_alta":
            row.setValue("PRIORITY", "High")
        elif value1 == "SAP_extrema" or value1 == "SPR_extrema":
            row.setValue("PRIORITY", "Extreme")
        cur.updateRow(row)
        
print "Step 3 Clean the output ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
## 4. Export final files
## Description: Export final files

print "\nStep 4 Export final files starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in outputList:
    name = os.path.split(fc)[1]
    begin = name[0:3]
    upper = begin.upper()
    final_name = "MX_" + upper
    arcpy.CopyFeatures_management(fc, finalFolder + final_name)

print "Step 4 Export final files ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "Geoprocess ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
