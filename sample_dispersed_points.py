###############################################################################################
##
## sample_dispersed_points.py
##
## Answers a number of dispersed points in the image or mask with a given maximal distance of
## each point from the grid points.
## 
## (c) 2023 INSERM
##
## written by Volker Baecker at the MRI-Center for Image Analysis (MRI-CIA - https://www.mri.cnrs.fr/en/data-analysis.html)
##
## sample_dispersed_points.py is free software under the MIT license.
## 
## MIT License
##
## Copyright (c) 2023 INSERM
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
## 
################################################################################################

import os
import time
import datetime
from ij import IJ
from ij import Prefs
from ij import WindowManager
from ij.gui import GenericDialog
from fr.cnrs.mri.cialib.generator import SpotGenerator
from fr.cnrs.mri.cialib.imaging import Microscope

URL = "https://github.com/MontpellierRessourcesImagerie/point-pattern-analysis/wiki/3D_Synthetic_Spots";

IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
IMAGE_DEPTH = 64 
IMAGE_TYPE = "16-bit"
IMAGE_TYPES = ["8-bit", "16-bit", "32-bit"]
VOXEL_SIZE_XY = 0.7 
VOXEL_SIZE_Z = 5
UNIT = chr(181) + "m"
MASK = None
NUMBER_OF_SAMPLES = 1000
MAX_DIST_FROM_GRID = 30
SAVE_OPTIONS = True

def main():
    optionsOnly = Prefs.get("mri.options.only", "false")
    if  not showDialog():
        return
    if optionsOnly=="true":
        return
    startTime = time.time()
    IJ.log("Started sampling at " + str(datetime.datetime.fromtimestamp(startTime)))
    gen = SpotGenerator()
    if MASK:
        gen.setMask(IJ.getImage(MASK))
    gen.width = IMAGE_WIDTH
    gen.height = IMAGE_HEIGHT
    gen.depth = IMAGE_DEPTH
    if IMAGE_TYPE == "8-bit":
        gen.bitDepth = 8
    if IMAGE_TYPE == "16-bit":
        gen.bitDepth = 16
    if IMAGE_TYPE == "32-bit":
        gen.bitDepth = 32    
    gen.calibration.pixelWidth = VOXEL_SIZE_XY
    gen.calibration.pixelHeight = VOXEL_SIZE_XY
    gen.calibration.pixelDepth = VOXEL_SIZE_Z
    gen.calibration.setUnit(UNIT)
    gen.numberOfSamples = NUMBER_OF_SAMPLES
    gen.maxDistFromGrid = MAX_DIST_FROM_GRID
    gen.sampleDispersedPoints()
    gen.createGroundTruthImage()
    gen.groundTruthImage.show()
    table = gen.getGroundTruthTable()
    table.show("Dispersed Random Points")
    endTime = time.time()
    IJ.log("Finished sampling at " + str(datetime.datetime.fromtimestamp(endTime)))
    IJ.log("Duration of calculation: " + str(datetime.timedelta(seconds=endTime-startTime)))
    
    
def showDialog():
    global IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_DEPTH, IMAGE_TYPE, VOXEL_SIZE_XY, VOXEL_SIZE_Z, UNIT, \
           MASK, NUMBER_OF_SAMPLES, MAX_DIST_FROM_GRID, SAVE_OPTIONS
    
    images = ["None"] + list(WindowManager.getImageTitles())
    if  os.path.exists(getOptionsPath()):
        loadOptions()
    gd = GenericDialog("Sample Dispersed Random Points Options"); 
    gd.addNumericField("Width Of Image: ", IMAGE_WIDTH)
    gd.addNumericField("Height Of Image: ", IMAGE_HEIGHT)
    gd.addNumericField("Depth Of Image: ", IMAGE_DEPTH)
    gd.addChoice("Type of Image: ", IMAGE_TYPES, IMAGE_TYPE)
    gd.addNumericField("XY-size of voxel: ", VOXEL_SIZE_XY)
    gd.addNumericField("Z-size of Voxel: ", VOXEL_SIZE_Z)
    gd.addStringField("Unit: ", UNIT)
    gd.addNumericField("Number Of Samples: ", NUMBER_OF_SAMPLES)
    gd.addNumericField("Max.-Dist. from grid", MAX_DIST_FROM_GRID) 
    if images:
        gd.addChoice("Mask: ", images, MASK)
    gd.addCheckbox("Save Options", SAVE_OPTIONS)
    gd.addHelp(URL)
    gd.showDialog()
    if gd.wasCanceled():
        return False
    IMAGE_WIDTH = int(gd.getNextNumber())
    IMAGE_HEIGHT = int(gd.getNextNumber())
    IMAGE_DEPTH = int(gd.getNextNumber())
    IMAGE_TYPE = gd.getNextChoice()
    VOXEL_SIZE_XY = gd.getNextNumber()
    VOXEL_SIZE_Z = gd.getNextNumber()
    UNIT = gd.getNextString()
    NUMBER_OF_SAMPLES = int(gd.getNextNumber())
    MAX_DIST_FROM_GRID = float(gd.getNextNumber())
    if images:
        MASK = gd.getNextChoice()
        if MASK=="None":
            MASK = None
    SAVE_OPTIONS = gd.getNextBoolean()
    if SAVE_OPTIONS:
        saveOptions()
    return True
  
  
def getOptionsPath():
    pluginsPath = IJ.getDirectory("plugins")
    optionsPath = pluginsPath + "3D_Synthetic_Spots/3dsdp-options.txt"
    return optionsPath
 

def getOptionsString():
    optionsString = ""
    optionsString = optionsString + " width=" + str(IMAGE_WIDTH) 
    optionsString = optionsString + " height=" + str(IMAGE_HEIGHT) 
    optionsString = optionsString + " depth=" + str(IMAGE_DEPTH) 
    optionsString = optionsString + " type=" + str(IMAGE_TYPE) 
    optionsString = optionsString + " xy-size=" + str(VOXEL_SIZE_XY) 
    optionsString = optionsString + " z-size=" + str(VOXEL_SIZE_Z) 
    optionsString = optionsString + u" unit=" + UNIT
    optionsString = optionsString + " number=" + str(NUMBER_OF_SAMPLES) 
    optionsString = optionsString + " max-dist=" + str(MAX_DIST_FROM_GRID) 
      
    return optionsString
    
    
def loadOptions(): 
    global IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_DEPTH, IMAGE_TYPE, VOXEL_SIZE_XY, VOXEL_SIZE_Z, \
           UNIT, MASK, NUMBER_OF_SAMPLES, MAX_DIST_FROM_GRID
    
    optionsPath = getOptionsPath()
    optionsString = IJ.openAsString(optionsPath)
    optionsString = optionsString.replace("\n", "")
    options = optionsString.split(" ")
    for option in options:
        parts = option.split("=")
        key = parts[0]
        value = ""
        if "=" in option:
            value = parts[1]
        if key=="width":
            IMAGE_WIDTH = int(value)
        if key=="height":
            IMAGE_HEIGHT = int(value)
        if key=="depth":
            IMAGE_DEPTH = int(value)        
        if key=="type":
            IMAGE_TYPE = value
        if key=="xy-size":
            VOXEL_SIZE_XY = float(value)
        if key=="z-size":
            VOXEL_SIZE_z = float(value)
        if key=="unit":
            UNIT = value
        if key=="number":
            NUMBER_OF_SAMPLES = int(value)    
        if key=="max-dist":
            MAX_DIST_FROM_GRID = float(value)    


def saveOptions():
    optionsString = getOptionsString()
    optionsPath = getOptionsPath()
    IJ.saveString(optionsString, getOptionsPath())
    
    
main()