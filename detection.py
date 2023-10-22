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
from ij import IJ
from ij import WindowManager
from ij.plugin.filter import PlugInFilterRunner
from ij.plugin.filter import ExtendedPlugInFilter
from ij.process import ImageConverter
from ij.gui import DialogListener
from ij.process import StackStatistics
from ij.process import StackProcessor
from imagescience.feature import Laplacian
from imagescience.image import Image
from mcib3d.image3d.processing import MaximaFinder
from mcib3d.image3d import ImageHandler


class SpotDetectionPlugInFilter(ExtendedPlugInFilter, DialogListener):

    
    def __init__(self):
        print("init")
        self.image = None


    def run(self, ip):  
        print("detector running")
        self.image.getProcessor().invert()        
    
    
    def dialogItemChanged(self, gd, e):
        print("detector", e)
        return not gd.invalidNumber()
        
        
    def setup(self, arg, imp):
        self.image = imp
        print("filter setup image:", self.image)
        return ExtendedPlugInFilter.DOES_ALL
    

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
        IJ.run("FeatureJ Options", "isotropic progress log")
        
   
    def run(self, inputImage):        
        image = inputImage.crop("stack")
        sigmaXY = (self.spotDiameterXY / 2) / math.sqrt(2)
        squaredSigmaXY = sigmaXY * sigmaXY
        spotRadiusPixelXY = image.getCalibration().getRawX(self.spotDiameterXY / 2.0)
        spotRadiusPixelZ = image.getCalibration().getRawZ(self.spotDiameterZ / 2.0)
        doScaling = ImageConverter.getDoScaling()
        ImageConverter.setDoScaling(False)
        print(sigmaXY)
        print(spotRadiusPixelXY)
        print(spotRadiusPixelZ)
        logImage = LoGFilter(sigmaXY).run(image)
        IJ.run(logImage, "Multiply...", "value=" + str(squaredSigmaXY) + " stack")
        stats = StackStatistics(logImage)
        IJ.run(logImage, "Subtract...", "value=" + str(stats.min) + " stack")
        logImage.getProcessor().setMinAndMax(0, stats.max - stats.min)
        StackProcessor(logImage.getStack()).invert()
        stats = StackStatistics(logImage)
        thresholded = ImageHandler.wrap(logImage.duplicate())
        thresholded.thresholdCut(self.threshold, False, True)
        maxFinder = MaximaFinder(thresholded, spotRadiusPixelXY, spotRadiusPixelZ, self.prominence)
        self.spotImage = maxFinder.getImagePeaks().getImagePlus()  
        self.spots = list(maxFinder.getListPeaks())
        ImageConverter.setDoScaling(doScaling)
       
   
   
class LoGFilter():
    
    
    def __init__(self, sigma):
        self.filter = Laplacian()
        self.sigma = sigma
    
    
    def run(self, image):
        imageScienceImage = Image.wrap(image.duplicate())
        logImage = self.filter.run(imageScienceImage, self.sigma)
        return logImage.imageplus()
        
    