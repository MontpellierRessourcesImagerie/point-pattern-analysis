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
from ij.plugin.filter import PlugInFilterRunner
from ij.plugin.filter import ExtendedPlugInFilter
from ij.process import ImageConverter
from ij.gui import DialogListener
from imagescience.feature import Laplacian
from imagescience.image import Image


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
        self.spotDiameterXY = 0.5 
        self.spotDiameterZ = 0.5
        self.prominence = 0.4
        
   
    def run(self, image):
        logFilter = Laplacian()
        sigmaXY = (self.spotDiameterXY / 2.0) / math.sqrt(3)
        doScaling = ImageConverter.getDoScaling()
        ImageConverter.setDoScaling(False)
        imageScienceImage = Image.wrap(image)
        logImage = logFilter.run(imageScienceImage, sigmaXY)
        logImage = logImage.imageplus()
        logImage.show()
        ImageConverter.setDoScaling(doScaling)
    
    