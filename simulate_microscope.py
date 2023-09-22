###############################################################################################
##
## simulate_microscope.py
##
## Answers a number of clustered points in the image or mask with a given number of cluster centers
## and a max. distance of the points from a center
## 
## (c) 2023 INSERM
##
## written by Volker Baecker at the MRI-Center for Image Analysis (MRI-CIA - https://www.mri.cnrs.fr/en/data-analysis.html)
##
## simulate_microscope.py is free software under the MIT license.
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
from fr.cnrs.mri.cialib.imaging import Microscope


URL = "https://github.com/MontpellierRessourcesImagerie/point-pattern-analysis/wiki/3D_Synthetic_Spots"

PSF_SIGMA_XY = 1
PSF_SIGMA_Z = 1.2
BACKGROUND_PHOTONS = 10
XY_GRADIENT = 0.01
Z_GRADIENT_STDDEV = 40
EXPOSURE_TIME = 10
READ_NOISE_STDDEV = 1
DETECTOR_GAIN = 1
DETECTOR_OFFSET = 100
BIT_DEPTH = 16
MAX_PHOTON_EMISSION = 25
BINNING = 1


SAVE_OPTIONS = True


def main():
    optionsOnly = Prefs.get("mri.options.only", "false")
    if  not showDialog():
        return
    if optionsOnly=="true":
        return
    startTime = time.time()
    IJ.log("Started acquiring image at " + str(datetime.datetime.fromtimestamp(startTime)))
    img = IJ.getImage()
    mic = Microscope()
    mic.mountSample(img)
    mic.acquireImage()
    mic.image.show()
    endTime = time.time()
    IJ.log("Finished acquiring image at " + str(datetime.datetime.fromtimestamp(endTime)))
    IJ.log("Duration of calculation: " + str(datetime.timedelta(seconds=endTime-startTime)))


def showDialog():
    global SAVE_OPTIONS, PSF_SIGMA_XY, PSF_SIGMA_Z, BACKGROUND_PHOTONS, XY_GRADIENT, \
           Z_GRADIENT_STDDEV, EXPOSURE_TIME, READ_NOISE_STDDEV, DETECTOR_GAIN, DETECTOR_OFFSET, \
           BIT_DEPTH, MAX_PHOTON_EMISSION, BINNING
    
    if  os.path.exists(getOptionsPath()):
        loadOptions()
    gd = GenericDialog("Simulate Microscope Options")
    gd.addNumericField("sigma_xy of psf: ", PSF_SIGMA_XY)
    gd.addNumericField("sigma_z of psf: ", PSF_SIGMA_Z)
    gd.addNumericField("background photons: ", BACKGROUND_PHOTONS)
    gd.addNumericField("gradient_xy: ", XY_GRADIENT)
    gd.addNumericField("gradient_z stddev: ", Z_GRADIENT_STDDEV)
    gd.addNumericField("exposure time: ", EXPOSURE_TIME)
    gd.addNumericField("read_noise stddev: ", READ_NOISE_STDDEV)
    gd.addNumericField("gain of the detector: ", DETECTOR_GAIN)
    gd.addNumericField("offset of the detector: ", DETECTOR_OFFSET)
    gd.addNumericField("bit depth: ", BIT_DEPTH)
    gd.addNumericField("max._photon emission: ", MAX_PHOTON_EMISSION)
    gd.addNumericField("binning: ", BINNING)
    gd.addCheckbox("Save Options", SAVE_OPTIONS)
    gd.showDialog()
    if gd.wasCanceled():
        return False
    PSF_SIGMA_XY = gd.getNextNumber()
    PSF_SIGMA_Z = gd.getNextNumber()
    BACKGROUND_PHOTONS = gd.getNextNumber()
    XY_GRADIENT = gd.getNextNumber()
    Z_GRADIENT_STDDEV = gd.getNextNumber()
    EXPOSURE_TIME = gd.getNextNumber()
    READ_NOISE_STDDEV = gd.getNextNumber()
    DETECTOR_GAIN = gd.getNextNumber()
    DETECTOR_OFFSET = gd.getNextNumber()
    BIT_DEPTH = gd.getNextNumber()
    MAX_PHOTON_EMISSION = gd.getNextNumber()
    BINNING = gd.getNextNumber()    
    SAVE_OPTIONS = gd.getNextBoolean()
    if SAVE_OPTIONS:
        saveOptions()
    return True
    
    
def getOptionsPath():
    pluginsPath = IJ.getDirectory("plugins")
    optionsPath = pluginsPath + "3D_Synthetic_Spots/simmic-options.txt"
    return optionsPath
    

def loadOptions(): 
    SAVE_OPTIONS, PSF_SIGMA_XY, PSF_SIGMA_Z, BACKGROUND_PHOTONS, XY_GRADIENT, \
           Z_GRADIENT_STDDEV, EXPOSURE_TIME, READ_NOISE_STDDEV, DETECTOR_GAIN, DETECTOR_OFFSET, \
           BIT_DEPTH, MAX_PHOTON_EMISSION, BINNING
    
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
        if key=="sigma_xy":
            PSF_SIGMA_XY = float(value)
        if key=="sigma_z":
            PSF_SIGMA_Z = float(value)
        if key=="background":
            BACKGROUND_PHOTONS = int(value)        
        if key=="gradient_xy":
            XY_GRADIENT = float(value)
        if key=="gradient_z":
            Z_GRADIENT_STDDEV = float(value)
        if key=="exposure":
            EXPOSURE_TIME = float(value)
        if key=="read_noise":
            READ_NOISE_STDDEV = float(value)
        if key=="gain":
            EXPOSURE_TIME = float(value)
        if key=="exposure":
            DETECTOR_GAIN = float(value)
        if key=="offset":
            DETECTOR_OFFSET = float(value)
        if key=="bit":
            BIT_DEPTH = int(value)
        if key=="max._photon":
            MAX_PHOTON_EMISSION = float(value)
        if key=="binning":
            BINNING = float(value)


def getOptionsString():
    optionsString = ""
    optionsString = optionsString + " sigma_xy=" + str(PSF_SIGMA_XY) 
    optionsString = optionsString + " sigma_z=" + str(PSF_SIGMA_Z) 
    optionsString = optionsString + " background=" + str(BACKGROUND_PHOTONS) 
    optionsString = optionsString + " gradient_xy=" + str(XY_GRADIENT) 
    optionsString = optionsString + " gradient_z=" + str(Z_GRADIENT_STDDEV) 
    optionsString = optionsString + " exposure=" + str(EXPOSURE_TIME) 
    optionsString = optionsString + u" unit=" + UNIT
    optionsString = optionsString + " number=" + str(NUMBER_OF_SAMPLES) 
    
    return optionsString


def saveOptions():
    optionsString = getOptionsString()
    optionsPath = getOptionsPath()
    IJ.saveString(optionsString, getOptionsPath())
    
    
main()