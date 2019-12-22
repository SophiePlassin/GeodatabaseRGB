## Name: landCover_RGB.py
## Created on: 2019-04-10
## By: Sophie Plassin
## Description: Preparation of the 2010 Land-Cover dataset for the Rio Grande/Bravo basin (RGB)
##              1. Clip a subset of the original dataset
##              2. Run Set Null where "VALUE" is equal to 0
##              3. Project the raster to North America Albers Equal Area Conic
##              4. Extract by Mask
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

### Workspace
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\6_landcover\\original_input\\"
interFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\6_landcover\\inter_output\\"
finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\6_landcover\\final_output\\"
dirpath = env.workspace

# Extension
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True

# Yearlist
yearList = ["10"]


## Create a Function that Counts the Number of Pixels in Raster
def countPixels(listRasters):
    countList = []
    for year in yearList:
        countSceneList = []
        pixels = []
        for raster in listRasters:
            # for raster mosaic
            if raster.startswith("lc" + year):
                pixels = []
                rows = arcpy.SearchCursor(raster)
                for row in rows:
                    value = row.getValue("Value")
                    if value > 0 and value < 255:
                        pixels.append(row.getValue("Count"))
                        temp = sum(pixels)
                print "NumberPixels_" + year, "=", temp
                countList.append(temp)

            # for list of scenes
            if raster.startswith("N") & (year in str(raster)):
                pixels_scene = []
                rows = arcpy.SearchCursor(raster)
                for row in rows:
                    value = row.getValue("Value")
                    if value > 0 and value < 255:
                        pixels_scene.append(row.getValue("Count"))
                total_scene = sum(pixels_scene)
                print str(raster), ": ", total_scene
                pixels.append(total_scene)
                countSceneList.append(raster)
                if len(countSceneList) == 8:
                    temp = sum(pixels)
                    print "NumberPixels_" + year, "=", temp
                    countList.append(temp)

    for year, i in itertools.izip(yearList, countList):
        print "year:", year, " NumberPixels:", i
    return countList


def soustraction(listA, listB):  
    for year, a, b in itertools.izip(yearList, countPixels(listA), countPixels(listB)):
        difference = a - b
        if difference == 0:
            print "year:", year, "Same number of pixels"
        if difference != 0:
            print "year:", year, "ERROR: different number of pixels"



clipList = []


## ---------------------------------------------------------------------------
## 1. Clip square
## Description: We clip the input tif to a smaller area

print "\nStep 1 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Variables
rectangle="-892063.312 -2324078.498 489064.45 -593700.037"

tifList = arcpy.ListRasters()

for i in range(len(tifList)):
    name = str(tifList[i][3:9])+ yearList[i]
    out_raster = os.path.join(interFolder, name)
    arcpy.Clip_management(tifList[i],
                          rectangle,
                          out_raster, in_template_dataset="",
                          nodata_value="#", clipping_geometry="NONE",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    clipList.append(out_raster)
    print "Clip", tifList[i] , "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
 
## ---------------------------------------------------------------------------
## 2. SetNull
## Description: We run the tool "Set Null" to set to NoData the cells of the grid
## where VALUE is different from 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
## This enable to remove the background of the grid before running the mosaic.

## Run on ArcMap
print "\nStep 2 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

setNullList = []

## Process Set Null
for i in range(len(clipList)):
    inRaster = clipList[i]
    inFalseRaster = clipList[i]
    whereClause = '"VALUE" = 0'
    outRaster = clipList[i] + "_sn"
    outSetNull = SetNull(inRaster, inFalseRaster, whereClause)
    outSetNull.save(outRaster)
    setNullList.append(outRaster)
    print "Grid to SetNull" , clipList[i] , "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Set Null completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## 2.a. Count the number of pixels in SetNull
setNullList = sorted(setNullList)
print "\n Count the number of pixels in setNullList"
countPixels(setNullList)
        
print "\nCalculate the difference between clipList and setNullList"
soustraction(clipList, setNullList)



## ---------------------------------------------------------------------------
## 3. Project rasters
## Description: Project all land-cover rasters to North America Albers Equal Area Conic

print "\nStep 3 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

projList = []

for i in range(len(setNullList)):
    name = str(setNullList[i]).split("sn")[0] + "pr"
    print name
    projFile = os.path.join(interFolder, name)
    print projFile
    arcpy.ProjectRaster_management(setNullList[i], projFile, outCS)
    projList.append(projFile)
    print "Projection" , setNullList[i], "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 Projection completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## 3.a. Count the number of pixels in projList
projList = sorted(projList)

print "\nCount the number of pixels in projList"
countPixels(projList)

print "\nCalculate the difference between setNullList and projList"
soustraction(setNullList, projList)

## ---------------------------------------------------------------------------
## 4. Extract by Mask
## Description: Extracts the cells of the land-cover raster datasets that correspond to the study area (mask).

finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\6_landcover\\final_output\\"

print "\nStep 4 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Mask
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin_na_albers.shp", "RGB_Ses_na_albers.shp"]
maskList = []
finalList = []

for fc in listfc:
        out_shp = os.path.join(folderShapefiles, fc)
        maskList.append(out_shp)

# Execute Extract By Mask
for i in range(len(projList)):
    newname = "lc" + yearList[i]
    for mask in maskList:
        temp = os.path.split(mask)[-1]
        if temp.startswith("RGB_Basin"):
            output = finalFolder + newname + "bas"
        else:
            output = finalFolder + newname + "ses"
        # Execute ExtractByMask
        outExtractByMask = ExtractByMask(projList[i], mask)
        # Save the output 
        outExtractByMask.save(output)
        print "Extract By Mask" , str(projList[i]), "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
        finalList.append(output)

print "Step 4 Extract By Mask completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## 4.a. Count the number of pixels in final List
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\6_landcover\\final_output\\"

finalList = sorted(finalList)
print "\nCount the number of pixels in Final List"
countPixels(finalList)


## ---------------------------------------------------------------------------
## 5. Add Land-cover names
## Description: Add a new field NAME and populate with the list of the names based on
## North American Land Change Monitoring System Land Cover Class Definition Level 2 Classifications

print "\nStep 5 Add Names starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

finalFolder = env.workspace

projList = arcpy.ListRasters("*", "")

# Add new column
fieldName = "NAME"
fieldType = "TEXT"

for raster in projList:
    arcpy.AddField_management(raster, fieldName, fieldType)

# Add names   
    cur = arcpy.UpdateCursor(raster)
    for row in cur:
        value1 = row.getValue("VALUE")
        if value1 == 1:
            row.setValue(fieldName, "Temperate or sub-polar needleleaf forest")
        elif value1 == 2:
            row.setValue(fieldName, "Sub-polar taiga needleleaf forest")
        elif value1 == 3:
            row.setValue(fieldName, "Tropical or sub-tropical broadleaf evergreen forest")
        elif value1 == 4:
            row.setValue(fieldName, "Tropical or sub-tropical broadleaf deciduous forest")
        elif value1 == 5:
            row.setValue(fieldName, "Temperate or sub-polar broadleaf deciduous forest")
        elif value1 == 6:
            row.setValue(fieldName, "Mixed Forest")
        elif value1 == 7:
            row.setValue(fieldName, "Tropical or sub-tropical shrubland")
        elif value1 == 8:
            row.setValue(fieldName, "Temperate or sub-polar shrubland")
        elif value1 == 9:
            row.setValue(fieldName, "Tropical or sub-tropical grassland")
        elif value1 == 10:
            row.setValue(fieldName, "Temperate or sub-polar grassland")
        elif value1 == 11:
            row.setValue(fieldName, "Sub-polar or polar shrubland-lichen-moss")
        elif value1 == 12:
            row.setValue(fieldName, "Sub-polar or polar grassland-lichen-moss")
        elif value1 == 13:
            row.setValue(fieldName, "Sub-polar or polar barren-lichen-moss")
        elif value1 == 14:
            row.setValue(fieldName, "Wetland")
        elif value1 == 15:
            row.setValue(fieldName, "Cropland")
        elif value1 == 16:
            row.setValue(fieldName, "Barren Lands")
        elif value1 == 17:
            row.setValue(fieldName, "Urban and Built-up")
        elif value1 == 18:
            row.setValue(fieldName, "Water")
        elif value1 == 19:
            row.setValue(fieldName, "Snow and Ice")
        cur.updateRow(row)

print "Step 5 completed at", datetime.datetime.now().strftime("%I:%M:%S%p")
