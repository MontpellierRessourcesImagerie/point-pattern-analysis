from __future__ import division
import math
from ij.process import ImageConverter
from ij.plugin import Duplicator
from ij.plugin import GaussianBlur3D
from ij.plugin import Binner
from imagescience.random import Randomizer
from imagescience.image import Image
from fr.cnrs.mri.cialib.options import Options

# Inspired by https://petebankhead.gitbooks.io/imagej-intro/content/chapters/macro_simulating/macro_simulating.html?q=



class Gaussian:
    
    
    def __init__(self, offset, height, mean, stdDev):
        self.offset = offset 
        self.height = height
        self.mean = mean
        self.stdDev = stdDev
        
    
    def f(self, x):
        result = self.offset + ((self.height - self.offset) * 
                           math.exp(-(x - self.mean) * (x - self.mean) / (2 * self.stdDev * self.stdDev)))
        return result
                       


class Microscope:

    def __init__(self, options=None, map=None):
        self.sample = None
        self.image = None
        self.psfSigmaXY = 1
        self.psfSigmaZ = 1.2
        self.backgroundPhotons = 10
        self.xyGradient = 0.01             # 0 means no gradient
        self.zGradientStdDev = 20        # 0 means no z-gradient
        self.exposureTime = 10
        self.readStdDev = 1
        self.detectorGain = 1
        self.detectorOffset = 100
        self.bitDepth = 16
        self.maxPhotonEmission = 10
        self.binning = 1                # 1 means no binning
        if options:
            if map:
                options.setMapping(map, id(self))
            self.setOptions(options)
                                  
                                                    
    def mountSample(self, aPhantomImage):
        self.sample = aPhantomImage
        
    
    def acquireImage(self):
        self.image = Duplicator().run(self.sample)
        ImageConverter(self.image).convertToGray32()
        self.normalizeImage()
        self.multiplyExposureTime()
        self.addPhotonNoise()
        self.addBackground()
        self.convolveWithPSF()
        self.applyDetectorGain()
        if self.binning > 1:
            self.applyBinning()
        self.applyDetectorOffset()
        self.addReadoutNoise()
        self.clipAndRound()
        self.image.updateAndDraw()
        self.image.resetDisplayRange()
        
   
    def normalizeImage(self):
        stack = self.image.getStack()
        minValue, maxValue = self.getStackMinAndMax(self.image)
        for i in range(1, stack.size()+1):
            processor = stack.getProcessor(i)
            processor.subtract(minValue)
            processor.multiply((1 / (maxValue - minValue)) * self.maxPhotonEmission)
            
    
    def getStackMinAndMax(self, image):
        stack = image.getStack()
        mins = []
        maxs = []
        for i in range(1, stack.size()+1):
            processor = stack.getProcessor(i)
            stats = processor.getStats()
            mins.append(stats.min)
            maxs.append(stats.max)
        minValue = min(mins)
        maxValue = max(maxs)
        return minValue, maxValue
        
    
    def addBackground(self):
        '''Background can be constant, contain a gradient in x,y and a grandient in z'''
        
        stack = self.image.getStack()
               
        for i in range(1, stack.size()+1):
            processor = stack.getProcessor(i)
            processor.add(self.backgroundPhotons)
            if self.xyGradient:
                processor.applyMacro("code=v=v+((x+y)*" + str(self.xyGradient) + ")") 
        
        if self.zGradientStdDev:
            offset, height = self.getStackMinAndMax(self.image)
            gaussian = Gaussian(offset, height, 0, self.zGradientStdDev)
            for i in range(1, stack.size()+1):
                processor = stack.getProcessor(i)
                processor.add(gaussian.f(i))
                
                
    def addPhotonNoise(self):
        image = Image.wrap(self.image)
        randomizer = Randomizer()
        randomizer.poisson(image, 1, 2, False)  # Mean param unused, intensity is the mean
        self.image.updateAndDraw()


    def convolveWithPSF(self):
        GaussianBlur3D.blur(self.image, self.psfSigmaXY, self.psfSigmaXY, self.psfSigmaZ)
        
        
    def multiplyExposureTime(self):
         stack = self.image.getStack()
         for i in range(1, stack.size()+1):
            stack.getProcessor(i).multiply(self.exposureTime)
            
            
    def applyDetectorGain(self):
        stack = self.image.getStack()
        for i in range(1, stack.size()+1):
            stack.getProcessor(i).multiply(self.detectorGain) # (note this should really add Poisson noise too!)            
            
      
    def applyDetectorOffset(self):
        stack = self.image.getStack()
        for i in range(1, stack.size()+1):          
            stack.getProcessor(i).add(self.detectorOffset)
            
            
    def applyBinning(self):
        binner = Binner()
        self.image = binner.shrink(self.image, self.binning, self.binning, 1, Binner.SUM)
       
            
    def addReadoutNoise(self):
        stack = self.image.getStack()
        for i in range(1, stack.size()+1):          
            stack.getProcessor(i).noise(self.readStdDev)
            
            
    def clipAndRound(self):
        stack = self.image.getStack()
        maxVal = pow(2, self.bitDepth) - 1
        for i in range(1, stack.size()+1):
            processor = stack.getProcessor(i)
            processor.min(0)
            processor.max(maxVal)
            pixels = stack.getPixels(i)
            for p in range(len(pixels)):
                pixels[p] = round(pixels[p])
            stack.setPixels(pixels, i)
                
                
    def setOptions(self, options):
        for key, value in options.getMapping(id(self)).items():
            setattr(self, key, options.convertedValue(value))