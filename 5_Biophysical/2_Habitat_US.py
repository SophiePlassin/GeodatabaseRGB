## Name: Habitat_RGB.py
## Created on: 2019-03-20
## By: Sophie Plassin
## Description: Preparation of the dataset related to Habitat in the Rio Grande/Bravo basin (RGB)
##              1. Create a geodatabase
##              2. Project and clip
##              3. MultipartToSinglepart
##              4. Merge the state datasets for Riparian and Wetlands into a single dataset
##              5. Clean the outputs
##              6. Reorder fields
##              7. Export final files
# ---------------------------------------------------------------------------

## Import packages and define the path name of the directories

# Import arcpy module
import arcpy, os
import datetime

# Directories:
dirpath = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\2_Habitat\\raw_data\\"
arcpy.env.workspace = dirpath
inter_outfolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\2_Habitat\\inter_output\\"
final_outfolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\2_Habitat\\final_output\\"


# ---------------------------------------------------------------------------
## 1. Create a geodatabase
## Description: Create a gdb to work with a table format

print "\nStep 1. Create a geodatabase starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(inter_outfolder, "HabGDB.gdb")
gdb = os.path.join(inter_outfolder, "HabGDB.gdb")


print "Step 1. Create a geodatabase ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 2. Project and clip the files
## Description: Project all features to North America Albers Equal Area Conic,
##              and clip the projected features with the clip of the RGB.
##              Copy int the gdb


# Define projection
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

# Define clip variables
clip = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\RGB_Ses_na_albers.shp"
xy_tolerance = ""

print "\nStep 2. Project and clip starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outputList = []

for path, dirs, files in os.walk(dirpath):
    for shp in files:
        if shp.endswith(".shp"):
            # Project
            absFile = os.path.abspath(os.path.join(path, shp))
            projName = os.path.splitext(shp)[0] +"_pr"
            projFile = os.path.join(gdb, projName)
            arcpy.Project_management(absFile, projFile, outCS)
            print "Project", projName, "ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
            # Clip
            clipName = projName.split('_pr')[0] +"_clip"
            clipFile = os.path.join(gdb, clipName)
            arcpy.Clip_analysis(projFile, clip, clipFile, xy_tolerance)
            outputList.append(clipFile)            
            print "Clip", clipName, "ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "Step 2 Project and clip ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## ---------------------------------------------------------------------------
## 3. MultipartToSinglepart
## Description: Break all multipart features into singlepart features,
##              and report which features were separated.


print "\nStep 3. MultipartToSinglepart starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in outputList:
    print fc
    try:
        # Create list of all fields in inFeatureClass
        fieldNameList = [field.name for field in arcpy.ListFields(fc)]

        # Add a field to the input this will be used as a unique identifier
        arcpy.AddField_management(fc, "tmpOID", "double")
     
        # Determine what the name of the Object ID is 
        OIDFieldName = arcpy.Describe(fc).OIDFieldName

        # Calculate the tmpUID to the OID
        arcpy.CalculateField_management(fc, "tmpOID",
                                        "!" + OIDFieldName + "!", "PYTHON")

        # Create an outFeatureClass
        name = os.path.split(fc)[1]
        outFeatureName = name.split('clip')[0] + "_Singlepart"
        outFeatureClass = os.path.join(gdb, outFeatureName)
        
        # Run the tool to create a new fc with only singlepart features
        arcpy.MultipartToSinglepart_management(fc, outFeatureClass)
     
        # Check if there is a different number of features in the output
        #   than there was in the input
        inCount = int(arcpy.GetCount_management(fc).getOutput(0))
        outCount = int(arcpy.GetCount_management(outFeatureClass).getOutput(0))
        
        if inCount != outCount:
            # If there is a difference, print out the FID of the input 
            #   features which were multipart
            arcpy.Frequency_analysis(outFeatureClass,
                                     outFeatureClass + "_freq", "tmpOID")
     
            # Use a search cursor to go through the table, and print the tmpUID 
            print("Multipart features from {0}".format(fc))
            for row in arcpy.da.SearchCursor(outFeatureClass + "_freq",
                                             ["tmpOID"], "FREQUENCY > 1"):
                print(int(row[0]))
        else:
            print("No multipart features were found")

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
    except Exception as err:
        print(err.args[0])

print "Step 3 MultipartToSinglepart ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


## ---------------------------------------------------------------------------
## 4. Merge states' Wetlands and Riparian feature classes into a single dataset
## Description: Project all singlepart features to North America Albers Equal Area Conic,
##              and clip the projected features with the clip of the RGB.
## Code created from:
## https://pro.arcgis.com/fr/pro-app/tool-reference/data-management/project.htm
##

print "\nStep 4 Merge starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

arcpy.env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\2_Habitat\\inter_output\\HabGDB.gdb"

# Define list of inputs to be merged
listRiparian = arcpy.ListFeatureClasses("*Riparian*Singlepart")
listWetland = arcpy.ListFeatureClasses("*Wetlands*Singlepart")

print listRiparian, listWetland

# Create a name Riparian
path, name = os.path.split(listRiparian[0])
begin = name.find("_")
end = name.find("_", begin+1)
nameRip = name[begin+1 :end]

# Create a name Wetlands
path, name = os.path.split(listWetland[0])
begin = name.find("_")
end = name.find("_", begin+1)
nameWet = name[begin+1 :end]
print nameRip, nameWet

# Merge Riparian and Wetlands into a single shapefile
mergeRip = os.path.join(gdb, nameRip)
mergeWet = os.path.join(gdb, nameWet)
arcpy.Merge_management(listRiparian, mergeRip)
print "Merge", nameRip, "completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
arcpy.Merge_management(listWetland, mergeWet)
print "Merge", nameWet, "completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

print "Step 4 Merge ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
# 5. Clean the outputs
## Description: Remove columns with American metrics and unrelevant fields and
##              Convert the length and area in the metric system.


listHab = arcpy.ListFeatureClasses("*CRITHAB*Singlepart")
inputList = [mergeRip, mergeWet]

inputList.extend(listHab)
dropFields = ["ACRES", "SHAPE_Leng", "tmpOID", "ORIG_FID", "singlmulti",
              "unit", "subunit", "unitname", "subunitnam", "coopoffice",
              "coopofmore", "effectdate", "vacatedate", "accuracy" ]
print inputList
print "\nStep 5 Clean the output starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for infc in inputList:
    arcpy.DeleteField_management(infc,
                                 dropFields)
    arcpy.AddField_management(infc, "Area_sqkm", "FLOAT")
    arcpy.AddField_management(infc, "Length_km", "FLOAT")
    arcpy.CalculateField_management(infc, "Length_km", "!SHAPE.length@KILOMETERS!", "PYTHON_9.3")
    arcpy.CalculateField_management(infc, "Area_sqkm", "!SHAPE.area@SQUAREKILOMETERS!", "PYTHON_9.3")

print "Step 5 Clean the output starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# ---------------------------------------------------------------------------
## 6. Reorder fields
## Description: Reorder fields

print "\nStep 6 Reorder the fields starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

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

finalListHab = []
new_field_order = ["objectid", "source_id", "comname", "sciname", "spcode", "vipcode", "listing_st", "status", "fedreg",
                   "pubdate", "Area_sqkm", "Length_km"]
for fc in listHab:
    path, name = os.path.split(fc)
    begin = 0
    first_under = name.find("_")
    second_under = name.find("_", first_under + 1)
    output = name[begin :second_under] + "_reorder"
    reorder_fields(fc, output, new_field_order)
    finalListHab.append(output)
    print "Reorder the fields", fc, "completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")


# ---------------------------------------------------------------------------
## 7. Export final files
## Description: Export final files from two list (reordered files)

print "\nStep 7 Export final files starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for i in range(len(listHab)):
    name = os.path.split(finalListHab[i])[1]
    begin = 0
    first_under = name.find("_")
    second_under = name.find("_", first_under + 1)
    inter_name = name[begin :second_under]
    final_name = inter_name.title()
    arcpy.CopyFeatures_management(finalListHab[i], final_outfolder + "\\US_" + final_name)

finalListWet = [mergeWet, mergeRip]

for i in range(len(finalListWet)):
    name = os.path.split(finalListWet[i])[1]
    arcpy.CopyFeatures_management(finalListWet[i], final_outfolder + "\\US_" + name)

print "Step 7 Export final files ends at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

