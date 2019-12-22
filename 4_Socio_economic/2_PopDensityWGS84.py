## Name: Population Density.py
## Created on: 2019-08-01
## By: Sophie Plassin
## Description: Preparation of the population density raster for the Rio Grande/Bravo basin (RGB)
##              1. Convert TIF to GRID
##              2. Extract by Mask (using GCS: WGS 1984)
## ---------------------------------------------------------------------------


## Import packages and define the path name of the directories

# Import arcpy module
import datetime
import arcpy
import os
from arcpy import env
from arcpy.sa import *


# Extension
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True

print "Geoprocess starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

### Workspace
dirpath = "E:\\GIS_RGB\\Geodatabase\\Socio_Economics\\2_PopulationDensity\\original_input\\"
interFolder = "E:\\GIS_RGB\\Geodatabase\\Socio_Economics\\2_PopulationDensity\\inter_output\\"
finalFolder = "E:\\GIS_RGB\\Geodatabase\\Socio_Economics\\2_PopulationDensity\\final_output\\"
arcpy.env.workspace = dirpath

## ---------------------------------------------------------------------------
## 1. Convert TIFF to GRID
## Description: We convert the raw raster data (.TIF) in grid and save the grid in the folder "inter_output" 

print "\nStep 1 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

outFolder = "C:\\GIS_RGB\\Geodatabase\\Biophysical\\7_landuse\\US_nass\\inter_output\\"
tifList = arcpy.ListRasters("*", "TIF")

gridList = []

## Loop on the list and export tif to grid
for i in range(len(tifList)):
    year = tifList[i] [-13:-11]
    oName = "popdens" + year
    outRaster = os.path.join(interFolder, oName)
    arcpy.CopyRaster_management(tifList[i], outRaster, "","","","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE")
    print "Export tif to grid" , tifList[i] , "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")
    gridList.append(outRaster)
print "Step 1 Tif to Grid completed at", datetime.datetime.now().strftime("%I:%M:%S%p")
          


## ---------------------------------------------------------------------------
## 2. Extract by Mask
## Description: Extracts the cells of the population density raster dataset that correspond to the study area (mask).

print "\nStep 2 starts at", datetime.datetime.now().strftime("%A, %B %d %Y %I:%M:%S%p")

# Mask
folderShapefiles = "C:\\GIS_RGB\\Geodatabase\\rgb_bound\\"
listfc = ["RGB_Basin.shp", "RGB_Ses.shp"]
maskList = []

for fc in listfc:
    out_shp = os.path.join(folderShapefiles, fc)
    maskList.append(out_shp)

outputList =[]

# Execute Extract By Mask
for raster in gridList:
    for mask in maskList:
        temp = os.path.split(mask)[-1]
        name = os.path.split(raster)[1]
        if temp.startswith("RGB_Basin"):
            output = os.path.join(finalFolder, name + "_bas")
        else:
            output = os.path.join(finalFolder, name + "_ses")
        # Execute ExtractByMask
        outExtractByMask = ExtractByMask(raster, mask)
        # Save the output 
        outExtractByMask.save(output)
        print "Extract By Mask" , raster, "completed at" , datetime.datetime.now().strftime("%I:%M:%S%p")

print "Step 2 Extract By Mask completed at", datetime.datetime.now().strftime("%I:%M:%S%p")






