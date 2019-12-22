## Name: CDL_LandUse_RGB.py
## Created on: 2019-04-09
## By: Sophie Plassin
## Description: Preparation of the [2008:2018] CDL Land-Use dataset for the Rio Grande/Bravo basin (RGB)
##              1. Convert TIFF to GRID
##              2. Run Set Null where "VALUE" = 0 from the GRID
##              3. Create a Mosaic that merges the state datasets (08, 35, 48) for each year
##              4. Project the boundaries of the study area (RGB) to the same projection of the CDL Land-Use dataset (USA Contiguous Albers Conic)
##              5. Extract by Mask: Extracts the cells of the land-use raster dataset that correspond to the area defined by the study area (mask).
##              6. Project the land-use raster dataset of the study area to the North America Albers Equal Area Conic
##              7. Add CDL Land-Use names
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

# Workspace
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\original_input\\"
yearList = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]

# Extension
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True


# Create a Function that Counts the Number of Pixels in Raster
def countPixels(listRasters):
        
    countList = [] 
    for year in yearList:
        countStateList = []
        pixels = []
        for raster in listRasters:
            # for raster mosaic
            if raster.startswith("cdl" + year):
                pixels = []
                rows = arcpy.SearchCursor(raster)
                for row in rows:
                    if row.getValue("Value") > 0:
                        pixels.append(row.getValue("Count"))
                        temp = sum(pixels)
                print "NumberPixels_" + year, "=", temp
                countList.append(temp)

            # for list of states
            if raster.startswith("cdl_" + year):
                pixels_state = []
                rows = arcpy.SearchCursor(raster)
                for row in rows:
                    if row.getValue("Value") > 0:
                        pixels_state.append(row.getValue("Count"))
                total_state = sum(pixels_state)
                print str(raster), ": ", total_state
                pixels.append(total_state)
                countStateList.append(raster)
                if len(countStateList) == 3:
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

## ---------------------------------------------------------------------------
## 1. Convert TIFF to GRID
## Description: We convert the raw raster data (.TIF) in grid and save the grid in the folder "inter_output" 

print "\nStep 1 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\"
tifList = arcpy.ListRasters("*", "TIF")

## Loop on the list and export tif to grid
for i in range(len(tifList)):
    oName = os.path.splitext(tifList[i])[0]
    outRaster = os.path.join(outFolder, oName)
    arcpy.CopyRaster_management(tifList[i], outRaster, "","","","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE")
    print "Export tif to grid" , tifList[i] , "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 1 Tif to Grid completed at", datetime.datetime.now().strftime("%I:%M:%S%p")
          

## 1.a. Count the number of pixels in Raster Grid

env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\"

gridList = arcpy.ListRasters("*", "GRID")
gridList = sorted(gridList)

# Execute
print "\nCount the number of pixels in GridList"
countPixels (gridList)


## ---------------------------------------------------------------------------
## 2. Set Null
## Description: We run the tool "Set Null" to set to NoData the cells of the grid where VALUE = 0.
## This enable to remove  the background of the grid before runing the mosaic.

print "\nStep 2 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

## Process Set Null
for i in range(len(gridList)):
    inRaster = gridList[i]
    inFalseRaster = gridList[i]
    whereClause = '"VALUE" = 0'
    outSetNull = SetNull(inRaster, inFalseRaster, whereClause)
    outSetNull.save(gridList[i] + "SN")

    print "Grid to SetNull" , gridList[i] , "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Set Null completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## 2.a. Count the number of pixels in SetNull
setNullList = arcpy.ListRasters("*SN", "")
setNullList = sorted(setNullList)
print "\n Count the number of pixels in setNullList"
countPixels(setNullList)

print "\nCalculate the difference between gridList and setNullList"
soustraction(gridList, setNullList)




## ---------------------------------------------------------------------------
## 3. Mosaic to New Raster 
## Description: We run the tool "Mosaic to New Raster"  to create a mosaic of the 3 states for each year
## from the following input rasters: cdl_YY_08sn, cdl_YY_35sn, cdl_YY_48sn.
## All the input rasters have the same projected coordinate system (USA Contiguous Albers Conic)


coordinate_system = ""
pixel_type="8_BIT_UNSIGNED"
cellsize=""
number_of_bands="1"
mosaic_method="LAST"
mosaic_colormap_mode="FIRST"                  

print "\nStep 3 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Run Mosaic to New Raster
mosaicList = []
for i in range(len(yearList)):
    newList = []
    for raster in setNullList:
        if raster.startswith("cdl_" + yearList[i]):
            newList.append(raster)
            if len(newList) == 3:
                print newList
                outRaster = "CDL" + yearList[i] + "_MC"
                arcpy.MosaicToNewRaster_management(newList, outFolder, outRaster, coordinate_system, pixel_type, cellsize, number_of_bands, mosaic_method, mosaic_colormap_mode)
                mosaicList.append(outRaster)
    print "Mosaic" , yearList[i] , "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 3 Mosaic completed at", datetime.datetime.now().strftime("%I:%M:%S%p")

## 3.a. Count the number of pixels in MosaicList
print "\nCount the number of pixels in mosaicList"
countPixels (mosaicList)

print "\nCalculate the difference between setNullList and mosaicList"
soustraction (setNullList, mosaicList)




## ---------------------------------------------------------------------------
## 4. Project the boundary of the Study Area (RGB)
## Description: We run the tool "Project" to project the boundary of the study area (RGB)
## to the same projected coordinate system (USA Contiguous Albers Conic USGS) of the land-use raster dataset.


folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin", "RGB_Ses"]
cs = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")
maskList= []

print "\nStep 4 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for fc in listfc:
    in_shp = os.path.join(folderShapefiles, fc + ".shp")
    out_shp = os.path.join(folderShapefiles, fc + "_usa_contiguous_albers.shp")
    arcpy.Project_management(in_shp, out_shp, cs)
    maskList.append(out_shp)
    print "Projection" , fc, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 4 Projection completed at", datetime.datetime.now().strftime("%I:%M:%S%p")




## ---------------------------------------------------------------------------
## 5. Extract By Mask
## Description: Extracts the cells of a raster (land-use rasters) that correspond to the areas defined by a mask (study area).

outFolderUSAContiguous = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\USA_contiguous_USGS\\"

print "\nStep 5 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

mosaicList = arcpy.ListRasters("*MC", "")
print mosaicList

for raster in mosaicList:
    newname = raster.split('_mc')[0]
    newname = os.path.split(newname)[-1]
    newname = newname.lower()
    for mask in maskList:
        temp = os.path.split(mask)[-1]
        if temp.startswith("RGB_Basin"):
            output = outFolderUSAContiguous + "Basin\\" + newname + "bas"
        else:
            output = outFolderUSAContiguous + "Ses\\" + newname + "ses"
        # Execute ExtractByMask
        outExtractByMask = ExtractByMask(raster, mask)
        # Save the output 
        outExtractByMask.save(output)
        print "Extract By Mask" , str(raster), "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 5 Extract By Mask completed at", datetime.datetime.now().strftime("%I:%M:%S%p")


## 5.a. Count the number of pixels in MaskedList
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\USA_contiguous_USGS\\Ses\\"

sesList = arcpy.ListRasters("*ses", "GRID")
print sesList
sesList = sorted(sesList)
print "\nCount the number of pixels in Ses List"
countPixels(sesList)

env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\USA_contiguous_USGS\\Basin\\"

basinList = arcpy.ListRasters("*bas", "GRID")
basinList = sorted(basinList)
print "\nCount the number of pixels in Basin List"
countPixels (basinList)


## ---------------------------------------------------------------------------
## 6. Project rasters
## Description: Project all land-use rasters to North America Albers Equal Area Conic

env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\USA_contiguous_USGS\\"
dirpath = env.workspace

NAFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\NA_albers_conic\\"

tempList = []
outCS = arcpy.SpatialReference("North America Albers Equal Area Conic")

print "\nStep 6 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

for (path, dirs, files) in os.walk(dirpath):
    for dirname in dirs:
        if (dirname == "Basin"):
            arcpy.env.workspace = dirname
            print dirpath + dirname
            files = glob.glob(os.path.join(dirpath + "\\" + dirname, "*bas"))
            print files
            tempList.extend(files)
        if (dirname == "Ses"):
            arcpy.env.workspace = dirname
            files = glob.glob(os.path.join(dirpath + "\\" + dirname, "*ses"))
            tempList.extend(files)

listRasters = []

for raster in tempList:
    temp = Raster(raster)
    listRasters.append(temp)

projList = []

# Project
for raster in listRasters:
    path, name = os.path.split(str(raster))
    projFile = os.path.join(NAFolder, name)
    arcpy.ProjectRaster_management(raster, projFile, outCS)
    projList.append(projFile)
    print "Projection" , raster, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 6 Projection completed at", datetime.datetime.now().strftime("%I:%M:%S%p")



## 6.a. Count the number of pixels in NA List
env.workspace = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\NA_albers_conic\\"

sesList = arcpy.ListRasters("*ses", "GRID")
sesList = sorted(sesList)
print "\nCount the number of pixels in Ses List"
countPixels(sesList)

basinList = arcpy.ListRasters("*bas", "GRID")
basinList = sorted(basinList)
print "\nCount the number of pixels in Basin List"
countPixels(basinList)


## ---------------------------------------------------------------------------
## 7. Add CDL Land-Use names
## Description: Add names of the Cropland Data Layer
## List of the names:
## https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/2014_cultivated_layer_metadata.php

print "\nStep 7 Add Names starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

finalFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\final_output\\"

projList = arcpy.ListRasters("*", "")

# Add new column
fieldName = "NAME"
fieldType = "TEXT"

for raster in projList:
    path, name = os.path.split(str(raster))
    out_raster = os.path.join(finalFolder, name)
    arcpy.CopyRaster_management(raster, out_raster)
    arcpy.AddField_management(out_raster, fieldName, fieldType)

    
# Add names
    cur = arcpy.UpdateCursor(out_raster)
    for row in cur:
        value1 = row.getValue("VALUE")
        if value1 == 1:
            row.setValue(fieldName, "Corn")
        elif value1 == 2:
            row.setValue(fieldName, "Cotton")
        elif value1 == 3:
            row.setValue(fieldName, "Rice")
        elif value1 == 4:
            row.setValue(fieldName, "Sorghum")
        elif value1 == 5:
            row.setValue(fieldName, "Soybeans")
        elif value1 == 6:
            row.setValue(fieldName, "Sunflower")
        elif value1 == 10:
            row.setValue(fieldName, "Peanuts")
        elif value1 == 11:
            row.setValue(fieldName, "Tobacco")
        elif value1 == 12:
            row.setValue(fieldName, "Sweet Corn")
        elif value1 == 13:
            row.setValue(fieldName, "Pop or Orn Corn")
        elif value1 == 14:
            row.setValue(fieldName, "Mint")
        elif value1 == 21:
            row.setValue(fieldName, "Barley")
        elif value1 == 22:
            row.setValue(fieldName, "Durum Wheat")
        elif value1 == 23:
            row.setValue(fieldName, "Spring Wheat")
        elif value1 == 24:
            row.setValue(fieldName, "Winter Wheat")
        elif value1 == 25:
            row.setValue(fieldName, "Other Small Grains")
        elif value1 == 26:
            row.setValue(fieldName, "Dbl Crop WinWht/Soybeans")
        elif value1 == 27:
            row.setValue(fieldName, "Rye")
        elif value1 == 28:
            row.setValue(fieldName, "Oats")
        elif value1 == 29:
            row.setValue(fieldName, "Millet")
        elif value1 == 30:
            row.setValue(fieldName, "Speltz")
        elif value1 == 31:
            row.setValue(fieldName, "Canola")
        elif value1 == 32:
            row.setValue(fieldName, "Flaxseed")
        elif value1 == 33:
            row.setValue(fieldName, "Safflower")
        elif value1 == 34:
            row.setValue(fieldName, "Rape Seed")
        elif value1 == 35:
            row.setValue(fieldName, "Mustard")
        elif value1 == 36:
            row.setValue(fieldName, "Alfalfa")
        elif value1 == 37:
            row.setValue(fieldName, "Other Hay/Non Alfalfa")
        elif value1 == 38:
            row.setValue(fieldName, "Camelina")
        elif value1 == 39:
            row.setValue(fieldName, "Buckwheat")
        elif value1 == 41:
            row.setValue(fieldName, "Sugarbeets")
        elif value1 == 42:
            row.setValue(fieldName, "Dry Beans")
        elif value1 == 43:
            row.setValue(fieldName, "Potatoes")
        elif value1 == 44:
            row.setValue(fieldName, "Other Crops")
        elif value1 == 45:
            row.setValue(fieldName, "Sugarcane")
        elif value1 == 46:
            row.setValue(fieldName, "Sweet Potatoes")
        elif value1 == 47:
            row.setValue(fieldName, "Misc Vegs & Fruits")
        elif value1 == 48:
            row.setValue(fieldName, "Watermelons")
        elif value1 == 49:
            row.setValue(fieldName, "Onions")
        elif value1 == 50:
            row.setValue(fieldName, "Cucumbers")
        elif value1 == 51:
            row.setValue(fieldName, "Chick Peas")
        elif value1 == 52:
            row.setValue(fieldName, "Lentils")
        elif value1 == 53:
            row.setValue(fieldName, "Peas")
        elif value1 == 54:
            row.setValue(fieldName, "Tomatoes")
        elif value1 == 55:
            row.setValue(fieldName, "Caneberries")
        elif value1 == 56:
            row.setValue(fieldName, "Hops")
        elif value1 == 57:
            row.setValue(fieldName, "Herbs")
        elif value1 == 58:
            row.setValue(fieldName, "Clover/Wildflowers")
        elif value1 == 59:
            row.setValue(fieldName, "Sod/Grass Seed")
        elif value1 == 60:
            row.setValue(fieldName, "Switchgrass")
        elif value1 == 61:
            row.setValue(fieldName, "Fallow/Idle Cropland")
        elif value1 == 63:
            row.setValue(fieldName, "Forest")
        elif value1 == 64:
            row.setValue(fieldName, "Shrubland")
        elif value1 == 65:
            row.setValue(fieldName, "Barren")
        elif value1 == 66:
            row.setValue(fieldName, "Cherries")
        elif value1 == 67:
            row.setValue(fieldName, "Peaches")
        elif value1 == 68:
            row.setValue(fieldName, "Apples")
        elif value1 == 69:
            row.setValue(fieldName, "Grapes")
        elif value1 == 70:
            row.setValue(fieldName, "Christmas Trees")
        elif value1 == 71:
            row.setValue(fieldName, "Other Tree Crops")
        elif value1 == 72:
            row.setValue(fieldName, "Citrus")
        elif value1 == 74:
            row.setValue(fieldName, "Pecans")
        elif value1 == 75:
            row.setValue(fieldName, "Almonds")
        elif value1 == 76:
            row.setValue(fieldName, "Walnuts")
        elif value1 == 77:
            row.setValue(fieldName, "Pears")
        elif value1 == 81:
            row.setValue(fieldName, "Clouds/No Data")
        elif value1 == 82:
            row.setValue(fieldName, "Developed")
        elif value1 == 83:
            row.setValue(fieldName, "Water")
        elif value1 == 87:
            row.setValue(fieldName, "Wetlands")
        elif value1 == 88:
            row.setValue(fieldName, "Nonag/Undefined")
        elif value1 == 92:
            row.setValue(fieldName, "Aquaculture")
        elif value1 == 111:
            row.setValue(fieldName, "Open Water")
        elif value1 == 112:
            row.setValue(fieldName, "Perennial Ice/Snow")
        elif value1 == 121:
            row.setValue(fieldName, "Developed/Open Space")
        elif value1 == 122:
            row.setValue(fieldName, "Developed/Low Intensity")
        elif value1 == 123:
            row.setValue(fieldName, "Developed/Med Intensity")
        elif value1 == 124:
            row.setValue(fieldName, "Developed/High Intensity")
        elif value1 == 131:
            row.setValue(fieldName, "Barren")
        elif value1 == 141:
            row.setValue(fieldName, "Deciduous Forest")
        elif value1 == 142:
            row.setValue(fieldName, "Evergreen Forest")
        elif value1 == 143:
            row.setValue(fieldName, "Mixed Forest")
        elif value1 == 152:
            row.setValue(fieldName, "Shrubland")
        elif value1 == 176:
            row.setValue(fieldName, "Grass/Pasture")
        elif value1 == 181:
            row.setValue(fieldName, "Pasture/Hay")
        elif value1 == 190:
            row.setValue(fieldName, "Woody Wetland")
        elif value1 == 195:
            row.setValue(fieldName, "Herbaceous Wetland")
        elif value1 == 204:
            row.setValue(fieldName, "Pistachios")
        elif value1 == 205:
            row.setValue(fieldName, "Triticale")
        elif value1 == 206:
            row.setValue(fieldName, "Carrots")
        elif value1 == 207:
            row.setValue(fieldName, "Asparagus")
        elif value1 == 208:
            row.setValue(fieldName, "Garlic")
        elif value1 == 209:
            row.setValue(fieldName, "Cantaloupes")
        elif value1 == 210:
            row.setValue(fieldName, "Prunes")
        elif value1 == 211:
            row.setValue(fieldName, "Olives")
        elif value1 == 212:
            row.setValue(fieldName, "Oranges")
        elif value1 == 213:
            row.setValue(fieldName, "Honeydew Melons")
        elif value1 == 214:
            row.setValue(fieldName, "Broccoli")
        elif value1 == 216:
            row.setValue(fieldName, "Peppers")
        elif value1 == 217:
            row.setValue(fieldName, "Pomegranates")
        elif value1 == 218:
            row.setValue(fieldName, "Nectarines")
        elif value1 == 219:
            row.setValue(fieldName, "Greens")
        elif value1 == 220:
            row.setValue(fieldName, "Plums")
        elif value1 == 221:
            row.setValue(fieldName, "Strawberries")
        elif value1 == 222:
            row.setValue(fieldName, "Squash")
        elif value1 == 223:
            row.setValue(fieldName, "Apricots")
        elif value1 == 224:
            row.setValue(fieldName, "Vetch")
        elif value1 == 225:
            row.setValue(fieldName, "Dbl Crop WinWht/Corn")
        elif value1 == 226:
            row.setValue(fieldName, "Dbl Crop Oats/Corn")
        elif value1 == 227:
            row.setValue(fieldName, "Lettuce")
        elif value1 == 229:
            row.setValue(fieldName, "Pumpkins")
        elif value1 == 230:
            row.setValue(fieldName, "Dbl Crop Lettuce/Durum Wht")
        elif value1 == 231:
            row.setValue(fieldName, "Dbl Crop Lettuce/Cantaloupe")
        elif value1 == 232:
            row.setValue(fieldName, "Dbl Crop Lettuce/Cotton")
        elif value1 == 233:
            row.setValue(fieldName, "Dbl Crop Lettuce/Barley")
        elif value1 == 234:
            row.setValue(fieldName, "Dbl Crop Durum Wht/Sorghum")
        elif value1 == 235:
            row.setValue(fieldName, "Dbl Crop Barley/Sorghum")
        elif value1 == 236:
            row.setValue(fieldName, "Dbl Crop WinWht/Sorghum")
        elif value1 == 237:
            row.setValue(fieldName, "Dbl Crop Barley/Corn")
        elif value1 == 238:
            row.setValue(fieldName, "Dbl Crop WinWht/Cotton")
        elif value1 == 239:
            row.setValue(fieldName, "Dbl Crop Soybeans/Cotton")
        elif value1 == 240:
            row.setValue(fieldName, "Dbl Crop Soybeans/Oats")
        elif value1 == 241:
            row.setValue(fieldName, "Dbl Crop Corn/Soybeans")
        elif value1 == 242:
            row.setValue(fieldName, "Blueberries")
        elif value1 == 243:
            row.setValue(fieldName, "Cabbage")
        elif value1 == 244:
            row.setValue(fieldName, "Cauliflower")
        elif value1 == 245:
            row.setValue(fieldName, "Celery")
        elif value1 == 246:
            row.setValue(fieldName, "Radishes")
        elif value1 == 247:
            row.setValue(fieldName, "Turnips")
        elif value1 == 248:
            row.setValue(fieldName, "Eggplants")
        elif value1 == 249:
            row.setValue(fieldName, "Gourds")
        elif value1 == 250:
            row.setValue(fieldName, "Cranberries")
        elif value1 == 254:
            row.setValue(fieldName, "Dbl Crop Barley/Soybeans")
        cur.updateRow(row)


print "\nStep 7 Add Names completed at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

