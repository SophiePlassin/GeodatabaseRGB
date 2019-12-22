## Name: Habitat_MX_2.py
## Created on: 2019-12-09
## By: Sophie Plassin
## Description: Preparation of the dataset related to Habitat in the MX portion of the Rio Grande/Bravo basin (RGB)
##              RAMSAR: Site classified under the Convention on Wetlands of International Importance especially as Waterfowl Habitat 
##              1. Project and clip
##              2. Clean the outputs (Translate in English)
##              3. Export final files
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

# Geodatabase
gdb = os.path.join(interFolder, "HabMX.gdb")


## ---------------------------------------------------------------------------
## 1. Project and clip the files
## Description: Project all features to North America Albers Equal Area Conic,
##              and clip the projected features with the clip of the RGB.
##              Copy int the gdb

print "\nStep 1. Project and clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Define projection
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Define clip variables
clip = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\RGB_Ses_na_albers.shp"
xy_tolerance = ""

input_file = "Sitios_Ramsar_Geo_ITRF92_2015.shp"
outputList = []

# Project
path, name = os.path.split(input_file)
projName = os.path.splitext(name)[0] +"_pr"
projFile = os.path.join(gdb, projName)
arcpy.Project_management(input_file, projFile, outCS)
print "Project", projName, "ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Clip
clipName = projName.split('_pr')[0] +"_clip"
clipFile = os.path.join(gdb, clipName)
arcpy.Clip_analysis(projFile, clip, clipFile, xy_tolerance)
outputList.append(clipFile)

print "Clip", clipName, "ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "Step 1 Project and clip ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
# 2. Clean the outputs
## Description: Translate Spanish to English (fields and field headers). Remve unecessary fields

print "\nStep 2 Clean the output starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Fields to remove
dropFields = ["objectid"]


# Fields to altere (lentgh <= 10 characters)
alterFields= [["ESTADO",        "STATE"],
              ["FECHA",         "DATE"],
              ["NUMERO",        "NUMBER"],
              ["wdpaid",              "WDPAID"]]

# Alter fields
for fc in outputList:
    arcpy.DeleteField_management(fc,dropFields)
    for old, new in alterFields:
        tmpName = ("{0}_tmp".format(old))
        arcpy.AlterField_management(fc, old, tmpName)
        arcpy.AlterField_management(fc, tmpName, new)

print "Step 2 Clean the output ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
## 3. Export final files
## Description: Export final files

print "\nStep 3 Export final files starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in outputList:
    name = os.path.split(fc)[1]
    first_under = name.find("_")
    second_under = name.find("_", first_under + 1)
    inter_name = name[first_under :second_under]
    final_name = "MX" + inter_name + "_Site"
    arcpy.CopyFeatures_management(fc, finalFolder + final_name)

print "Step 3 Export final files ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


print "Geoprocess ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
