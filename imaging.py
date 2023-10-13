from __future__ import division
import os
import math
import time
import datetime
from copy import deepcopy
from java.lang import Runtime
from java.lang import Thread
from java.lang import Runnable
from ij import IJ
from ij.process import LUT 
from ij.process import ImageConverter
from ij.plugin import Duplicator
from ij.plugin import GaussianBlur3D
from ij.plugin import Binner
from ij.plugin import LutLoader
from loci.formats import ImageReader
from loci.plugins import BF
from imagescience.random import Randomizer  # For photon noise
from imagescience.image import Image        # Needed by Randomizer


# Inspired by https://petebankhead.gitbooks.io/imagej-intro/content/chapters/macro_simulating/macro_simulating.html?q=

def split(aList, numberOfChunks):
    size = int(math.ceil(len(aList) / numberOfChunks))
    return list(map(lambda x: aList[x * size:x * size + size], list(range(numberOfChunks))))

    
    
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

    def __init__(self):
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
        self.batchProcess = False
        self.outputFolder = None                    
        self.inputFolder = None                    
        
        
    def run(self, img, options=None, display=True):
        startTime = time.time()
        IJ.log("Started acquiring image at " + str(datetime.datetime.fromtimestamp(startTime)))
        if options:
            options.recordAndReport("simulate microscope", img)
        self.mountSample(img)
        self.acquireImage()
        lut = LUT(LutLoader.getLut( "Grays" ), 0, 255)
        self.image.getChannelProcessor().setLut(lut)
        self.image.resetDisplayRange()
        if display:
            self.image.show()
        endTime = time.time()
        IJ.log("Finished acquiring image at " + str(datetime.datetime.fromtimestamp(endTime)))
        IJ.log("Duration of calculation: " + str(datetime.timedelta(seconds = endTime - startTime)))
    
    
    def runBatch(self, options=None):
        startTime = time.time()
        IJ.log("Started batch simulate microscope at " + str(datetime.datetime.fromtimestamp(startTime)))
        if not os.path.exists(self.inputFolder):
            IJ.log("Could not access the input folder: " + self.inputFolder)
        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)
        imagePaths = [os.path.join(self.inputFolder, f) for f in os.listdir(self.inputFolder) if os.path.isfile(os.path.join(self.inputFolder, f)) and self.isImage(os.path.join(self.inputFolder, f))]
        numberOfImages = len(imagePaths)        
        for nrOfImage, imagePath in enumerate(imagePaths, 1):
            IJ.log("Acquiring image number " + str(nrOfImage) + " of " + str(numberOfImages))
            image = BF.openImagePlus(imagePath)[0]
            self.run(image, options=options, display=False)
            _, imageName = os.path.split(imagePath)          
            path = os.path.join(self.outputFolder, imageName)
            IJ.log("Saving image number " + str(nrOfImage) + " of " + str(numberOfImages))
            IJ.save(self.image, path)
        endTime = time.time()
        IJ.log("Finished batch simulate microscope at " + str(datetime.datetime.fromtimestamp(endTime)))
        IJ.log("Duration: " + str(datetime.timedelta(seconds = endTime - startTime)))

    
    def runBatchMT(self, options):
        startTime = time.time()
        IJ.log("Started batch simulate microscope at " + str(datetime.datetime.fromtimestamp(startTime)))
        if not os.path.exists(self.inputFolder):
            IJ.log("Could not access the input folder: " + self.inputFolder)
        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)
        imagePaths = [os.path.join(self.inputFolder, f) for f in os.listdir(self.inputFolder) if os.path.isfile(os.path.join(self.inputFolder, f)) and self.isImage(os.path.join(self.inputFolder, f))]
        numberOfCores = Runtime.getRuntime().availableProcessors()
        taskGroups = split(imagePaths, numberOfCores)
        threads = []
        for taskGroup in taskGroups:
            batchMic = BatchMicroscopeThread(self, taskGroup, options)
            thread = Thread(batchMic)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()         
        endTime = time.time()
        IJ.log("Finished batch simulate microscope at " + str(datetime.datetime.fromtimestamp(endTime)))
        IJ.log("Duration: " + str(datetime.timedelta(seconds = endTime - startTime)))
    
     
    def isImage(self, path):
        baseReader = ImageReader()
        readers = baseReader.getReaders()
        rtype = None
        for reader in readers:
            if reader.isThisType(path):
                rtype = reader        
        return not rtype is None
    
    
    def mountSample(self, aPhantomImage):
        self.sample = aPhantomImage
        
    
    def acquireImage(self):
        IJ.log("acquiring image...")
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
        IJ.log("normalizing image...")
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
        
        IJ.log("adding background...")
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
        IJ.log("adding photon noise...")
        image = Image.wrap(self.image)
        randomizer = Randomizer()
        randomizer.poisson(image, 1, 2, False)  # Mean param unused, intensity is the mean, poisson noise ~ sqrt(I)
        self.image.updateAndDraw()


    def convolveWithPSF(self):
        IJ.log("convolving...")
        GaussianBlur3D.blur(self.image, self.psfSigmaXY, self.psfSigmaXY, self.psfSigmaZ)
        
        
    def multiplyExposureTime(self):
         IJ.log("applying exposure time...")
         stack = self.image.getStack()
         for i in range(1, stack.size()+1):
            stack.getProcessor(i).multiply(self.exposureTime)
            
            
    def applyDetectorGain(self):
        IJ.log("applying detector gain...")
        stack = self.image.getStack()
        for i in range(1, stack.size()+1):
            stack.getProcessor(i).multiply(self.detectorGain) # (note this should really add Poisson noise too!)            
            
      
    def applyDetectorOffset(self):
        IJ.log("applying detector offset...")
        stack = self.image.getStack()
        for i in range(1, stack.size()+1):          
            stack.getProcessor(i).add(self.detectorOffset)
            
            
    def applyBinning(self):
        IJ.log("applying binning...")
        binner = Binner()
        self.image = binner.shrink(self.image, self.binning, self.binning, 1, Binner.SUM)
       
            
    def addReadoutNoise(self):
        IJ.log("adding read-out noise...")
        stack = self.image.getStack()
        for i in range(1, stack.size()+1):          
            stack.getProcessor(i).noise(self.readStdDev)
            
             
    def clipAndRound(self):
        IJ.log("clipping and rounding...")       
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
            
            
            
class BatchMicroscopeThread(Runnable):


    def __init__(self, microscope, tasks, options):
        self.microscope = deepcopy(microscope)
        self.options = options
        self.tasks = tasks
        
        
    def run(self):
        numberOfImages = len(self.tasks)
        for nrOfImage, imagePath in enumerate(self.tasks, 1):
            IJ.log("Acquiring image number " + str(nrOfImage) + " of " + str(numberOfImages))
            image = BF.openImagePlus(imagePath)[0]
            self.microscope.run(image, options=self.options, display=False)
            _, imageName = os.path.split(imagePath)          
            path = os.path.join(self.microscope.outputFolder, imageName)
            IJ.log("Saving image number " + str(nrOfImage) + " of " + str(numberOfImages))
            IJ.save(self.microscope.image, path)    