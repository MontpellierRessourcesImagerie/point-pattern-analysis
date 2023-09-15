from __future__ import division
import math
from ij.process import ImageConverter
from ij.plugin import Duplicator


class Gaussian:
    
    
    def __init__(self, offset, height, mean, stdDev):
        self.offset = offset 
        self.height = height
        self.mean = mean
        self.stdDev = stdDev
        
    
    def f(self, x):
        result = self.height + ((self.height - self.offset) * 
                           math.exp(-(x - self.mean) * (x - self.mean) / (2 * self.stdDev * self.stdDev)))
        return result
            

class Microscope:

    def __init__(self):
        self.sample = None
        self.image = None
        self.psfSigma = 2
        self.backgroundPhotons = 10
        self.xyGradient = 0.01             # 0 means no gradient
        self.zGradientStdDev = 20        # 0 means no z-gradient
        self.exposureTime = 10
        self.readStdDev = 5
        self.detectorGain = 1
        self.detectorOffset = 100
        self.bitDepth = 16
        self.maxPhotonEmission = 10
        self.binning = 1                # 1 means no binning
    
    
    def mountSample(self, aPhantomImage):
        self.sample = aPhantomImage
        
    
    def acquireImage(self):
        self.image = Duplicator().run(self.sample)
        ImageConverter(self.image).convertToGray32()
        self.normalizeImage()
        self.addBackground()
    
    
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