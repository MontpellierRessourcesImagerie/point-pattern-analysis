###############################################################################################
##
## generator.py
##
## Create synthetic 3D spots and nuclei with random uniform, clustered or dispersed spatial distribution. 
## 
## (c) 2023 INSERM
##
## written by Volker Baecker at the MRI-Center for Image Analysis (MRI-CIA - https://www.mri.cnrs.fr/en/data-analysis.html)
##
## generator.py is free software under the MIT license.
## 
## MIT License
##
## Copyright (c) 2023 INSERM
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
## 
################################################################################################

from __future__ import division
import math
import time
import datetime
import os
from java.awt import AWTEvent
from java.awt.event import TextEvent
from ij import IJ
from ij import WindowManager
from ij.plugin.filter import PlugInFilterRunner
from ij.plugin.filter import ExtendedPlugInFilter
from ij.process import ImageConverter
from ij.gui import DialogListener
from ij.process import StackStatistics
from ij.process import StackProcessor
from ij import ImagePlus
from ij.gui import ImageRoi
from ij.gui import Overlay
from ij.plugin import LutLoader
from ij.process import LUT 
from ij.measure import ResultsTable
from loci.plugins import BF
from inra.ijpb.binary.conncomp import FloodFillComponentsLabeling3D
from inra.ijpb.morphology.strel import CubeStrel
from imagescience.feature import Laplacian
from imagescience.image import Image
from mcib3d.image3d.processing import MaximaFinder
from mcib3d.image3d import ImageHandler
from fr.cnrs.mri.cialib.bfutil import BioformatsUtil



class SpotDetectionPlugInFilter(ExtendedPlugInFilter, DialogListener):

    
    def __init__(self):
        self.image = None
        self.settingUp = True
        self.spotDetector = SpotDetector()
        

    def run(self, ip):  
        if self.settingUp:
            self.settingUp = False
            return
        self.spotDetector.run(self.image)
        self.image.updateAndDraw()
        
      
    def dialogItemChanged(self, gd, e):
        if gd.invalidNumber():
            return False
        if e is None:
            return True
        if not e.getID() == TextEvent.TEXT_VALUE_CHANGED:
            return True
        textValue = e.getSource().getText()       
        name = e.getSource().getName()
        if name == "xy-diameter":
            self.spotDetector.spotDiameterXY = float(textValue)
        if name == "z-diameter":
            self.spotDetector.spotDiameterZ = float(textValue)
        if name == "prominence":
            self.spotDetector.prominence = float(textValue)   
        if name == "threshold":
            self.spotDetector.threshold = float(textValue) 
        return True
        
        
    def setup(self, arg, imp):
        self.image = imp
        return ExtendedPlugInFilter.DOES_ALL + ExtendedPlugInFilter.NO_CHANGES
    

    def setNPasses(self, nPasses):
        pass



class SpotDetector():


    def __init__(self):
        self.spotDiameterXY = 0.65 
        self.spotDiameterZ = 2.25
        self.prominence = 0.15
        self.threshold = 0.35    
        self.spots = []
        self.spotImage = None
        self.inputImage = None
        self.batchProcess = False
        self.inputFolder = None
        self.outputFolder = None
        self.lutName = "glasbey on dark"
        self.lut = LUT(LutLoader.getLut(self.lutName ), 0, 255)
        IJ.run("FeatureJ Options", "isotropic progress log")
        
   
    def run(self, inputImage):   
        IJ.log("start detecting spots")
        self.reportParameters()
        self.inputImage = inputImage
        image = inputImage.crop("stack")
        sigmaXY = (self.spotDiameterXY / 2) / math.sqrt(2)
        squaredSigmaXY = sigmaXY * sigmaXY
        spotRadiusPixelXY = image.getCalibration().getRawX(self.spotDiameterXY / 2.0)
        spotRadiusPixelZ = image.getCalibration().getRawZ(self.spotDiameterZ / 2.0)
        doScaling = ImageConverter.getDoScaling()
        ImageConverter.setDoScaling(False)
        logImage = LoGFilter(sigmaXY).run(image)
        IJ.run(logImage, "Multiply...", "value=" + str(squaredSigmaXY) + " stack")
        stats = StackStatistics(logImage)
        IJ.run(logImage, "Subtract...", "value=" + str(stats.min) + " stack")
        logImage.setDisplayRange(0, stats.max - stats.min)
        StackProcessor(logImage.getStack()).invert()
        stats = StackStatistics(logImage)
        thresholded = ImageHandler.wrap(logImage.duplicate())
        thresholded.thresholdCut(self.threshold, False, True)
        maxFinder = MaximaFinder(thresholded, spotRadiusPixelXY, spotRadiusPixelZ, self.prominence)
        self.spotImage = maxFinder.getImagePeaks().getImagePlus()      
        floodFiller = FloodFillComponentsLabeling3D(6, 16)
        res = floodFiller.computeResult(self.spotImage.getStack())
        self.spotImage.setStack(res.labelMap)
        self.spotImage.getChannelProcessor().setLut(self.lut)
        self.spots = list(maxFinder.getListPeaks())
        self.spotImage.setDisplayRange(0, len(self.spots))
        self.addSpotsToOverlay()
        ImageConverter.setDoScaling(doScaling)
        IJ.log("finished detecting spots")
   

    def runBatch(self):
        startTime = time.time()
        IJ.log("Started batch spot detection at " + str(datetime.datetime.fromtimestamp(startTime)))
        if not os.path.exists(self.inputFolder):
            IJ.log("Could not access the input folder: " + self.inputFolder)
        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)
        imagePaths = [os.path.join(self.inputFolder, f) for f in os.listdir(self.inputFolder) if os.path.isfile(os.path.join(self.inputFolder, f)) and BioformatsUtil.isImage(os.path.join(self.inputFolder, f))]
        numberOfImages = len(imagePaths)        
        for nrOfImage, imagePath in enumerate(imagePaths, 1):
            IJ.log("Processing image number " + str(nrOfImage) + " of " + str(numberOfImages))
            image = BF.openImagePlus(imagePath)[0]
            self.run(image)
            _, imageName = os.path.split(imagePath) 
            name, ext = os.path.splitext(imageName)
            path = os.path.join(self.outputFolder, name + ".tif")
            IJ.log("Saving image number " + str(nrOfImage) + " of " + str(numberOfImages))
            IJ.save(self.spotImage, path)
            table = self.getSpotsAsResultsTable()
            path = os.path.join(self.outputFolder, name + ".xls")
            table.save(path)
        endTime = time.time()
        IJ.log("Finished batch spot detection at " + str(datetime.datetime.fromtimestamp(endTime)))
        IJ.log("Duration: " + str(datetime.timedelta(seconds = endTime - startTime)))
        
        
    def reportParameters(self):
        IJ.log("xy-diameter: " + str(self.spotDiameterXY))
        IJ.log("z-diameter: " + str(self.spotDiameterZ))
        IJ.log("prominence: " + str(self.prominence))
        IJ.log("threshold: " + str(self.threshold))
        
    
    def getSpotsAsResultsTable(self):
        spotData = [(s.x, s.y, s.z, s.value) for s in self.spots]
        columns = list(zip(*spotData))
        table = ResultsTable()
        table.showRowIndexes(True)
        table.setValues("x", columns[0])
        table.setValues("y", columns[1])
        table.setValues("z", columns[2])
        table.setValues("v", columns[3])
        return table
        
    
    def addSpotsToOverlay(self):
        lutName = "glasbey on dark"
        roi = self.inputImage.getRoi()
        labelsStack = self.spotImage.getStack()
        strel = CubeStrel.fromRadius(2)
        labelsStack = strel.dilation(labelsStack)
        resImage = ImagePlus("labels", labelsStack)
        resImage.getChannelProcessor().setLut(self.lut)
        resImage.setDisplayRange(0, len(self.spots))
        rois = []
        x = 0
        y = 0
        if roi:
            x = roi.getBounds().x
            y = roi.getBounds().y
        for i in range(1, resImage.getStack().getSize()+1):
            roi = ImageRoi(x, y, resImage.getStack().getProcessor(i))
            roi.setOpacity(75)
            roi.setZeroTransparent(True)
            rois.append(roi)
        overlay = Overlay.createStackOverlay(rois)
        overlay.translate(x, y)
        self.inputImage.setOverlay(overlay)
    
    
    
class LoGFilter():
    
    
    def __init__(self, sigma):
        self.filter = Laplacian()
        self.sigma = sigma
    
    
    def run(self, image):
        imageScienceImage = Image.wrap(image.duplicate())
        logImage = self.filter.run(imageScienceImage, self.sigma)
        return logImage.imageplus()
        
    